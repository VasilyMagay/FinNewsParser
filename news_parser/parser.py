"""
news_parser/parser.py
"""
import abc
import datetime
import logging.config
import socket

from os import path
from argparse import ArgumentParser

import requests
import pymysql
import pymysql.cursors

from grab import Grab
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
DEBUG = bool(socket.gethostname() == 'magv-hp')

logging.config.fileConfig(path.join(BASE_DIR, 'news_parser', 'logging.conf'))
logger = logging.getLogger('parsing')

FIREFOX_EXECUTABLE_PATH = r'C:\Program Files\Geckodriver\geckodriver.exe'
if not DEBUG:
    FIREFOX_EXECUTABLE_PATH = r'/usr/local/bin/geckodriver'


class NewsProvider(metaclass=abc.ABCMeta):
    """
    Общий провайдер новостей
    """
    site_ref = ''
    site_id = None
    SITE_DBNAME = 'mainapp_site'
    NEWS_DBNAME = 'mainapp_news'
    TOPIC_DBNAME = 'mainapp_topic'
    USERS_DBNAME = 'authapp_siteuser'
    TOPIC_NEWS_DBNAME = 'mainapp_topicnews'
    TOPIC_SITE_DBNAME = 'mainapp_topicsite'

    def __init__(self):
        self.site_name = ''

    @abc.abstractmethod
    def collect_news(self, news_date):
        """
        Собрать новости с сайта за выбранную дату и сохранить их в базе.
        :param news_date:
        :return:
        """

    def get_site_info(self):
        """
        Возвращает ссылку на сайт в базе.
        :return:
        """
        if self.site_ref:
            return

        con = NewsProvider.connect_db(logger)
        cur = con.cursor()
        # cur.execute(f"SELECT * FROM {self.SITE_DBNAME} WHERE name=%s", self.site_name)
        exec_sql(
            logger,
            cur,
            f"SELECT * FROM {self.SITE_DBNAME} WHERE name=%s",
            self.site_name)

        site = cur.fetchone()
        if len(site) > 0:
            self.site_ref = site['ref']
            self.site_id = site['id']

        con.close()

    @staticmethod
    def connect_db(connect_logger):
        """
        Соединение с базой данных
        :return: connect()
        """
        try:
            mysql_config = {}
            with open(path.join(BASE_DIR, 'mysql.cnf'), 'r') as file:
                lines = file.read().splitlines()
                for line in lines:
                    pair = line.split('=')
                    if len(pair) == 2:
                        mysql_config[pair[0].strip()] = pair[1].strip()
            connect = pymysql.connect(
                mysql_config['host'],
                mysql_config['user'],
                mysql_config['password'],
                mysql_config['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info('The connection is established')
            return connect
        except Exception as err:
            connect_logger.exception(f'Error DB connecting ({err})')
        return None


class FinamNewsProvider(NewsProvider):
    """
    Провайдер новостей Финам
    """

    def __init__(self):
        super().__init__()
        self.site_name = 'Финам'
        self.get_site_info()

    def collect_news(self, news_date):
        """
        Собираем новости
        :param news_date: дата в формате '14.02.2020' или datetime
        :return:
        """
        logger.info(
            f'FireFox, collecting news from \'{self.site_name}\', Date: {news_date}')
        logger.info('Connecting to the browser...')
        # browser = BrowserFabric.create_browser('Grab')
        browser = BrowserFabric.create_browser('FireFox')
        browser.connect()
        if not browser.is_connected():
            logger.error(browser.connect_error)
            browser.disconnect()
            return
        logger.info('Browser is connected')
        if isinstance(news_date, str):
            date_str = news_date
            date_date = datetime.datetime.strptime(news_date, "%d.%m.%Y")
        elif isinstance(news_date, datetime.datetime):
            date_str = news_date.strftime("%d.%m.%Y")
            date_date = news_date

        # url = "https://www.finam.ru/analysis/united/rqdate0E027E4"
        maim_url = str(self.site_ref)
        if maim_url[-1] != '/':
            maim_url += '/'
        maim_url += format(self.date_ref(date_str))

        page_num = 0
        news = []
        check_ref = []

        while True:
            page_num += 1

            if page_num == 1:
                url = maim_url
            else:
                url = maim_url + '/?page=' + str(page_num)
            # print(f'URL={url}')
            logger.info(f'URL: {url}')
            logger.info(f'Reading page...')
            read_page = browser.get_html(url, show_message=False)

            if read_page['error']:
                logger.error(read_page['error'])
                break

            html_doc = read_page['html']
            logger.info(f'Parsing titles...')
            try:
                bs_obj = BeautifulSoup(html_doc, features="html.parser")
            except Exception as err:
                msg = f'{url}\n{str(err)}'
                logger.exception(msg)
                bs_obj = None

            lines_cnt = 0
            if bs_obj:
                for obj in bs_obj.findAll("div", class_="ln"):
                    lines_cnt += 1
                    for link in obj.find_all(
                            lambda tag: tag.name == 'a' and tag.get('class') != ['section']):
                        try:
                            date_s = obj.find("span", class_="date").text
                        except Exception:
                            date_s = None
                        if not date_s:
                            date_s = '00:00'
                        link_text = ''
                        try:
                            link_text = link.attrs['href']
                        except Exception as err:
                            logger.exception(f'{err}')
                        finally:
                            pass
                        if link_text:
                            brief_info = str(obj.p.text).strip()
                            if brief_info:
                                if not link_text.startswith('/webinars') and \
                                        not link_text.startswith('/infinity') and \
                                        link_text not in check_ref:
                                    if link_text.startswith('http'):
                                        news_ref = link_text
                                    else:
                                        news_ref = f'https://www.finam.ru{link_text}'
                                    news.append(
                                        {
                                            'news_date': datetime.datetime.strptime(
                                                date_str + ' ' + date_s,
                                                '%d.%m.%Y %H:%M'),
                                            'ref': news_ref,
                                            'brief_info': brief_info,
                                            'raw_info': '',
                                        })
                                    check_ref.append(link_text)

            if lines_cnt == 0:
                break

        logger.info(f'{len(news)} news items is found')

        # Поучение полного текста новостей для возможности полноценной
        # фильтрации
        logger.info('Parsing full info...')
        for item in news:
            item['raw_info'] = FinamNewsProvider.get_news_info(
                browser, item['ref'])
            # print(f'Info={item["info"]}')
            # break

        # Запись новостей в базу
        logger.info('Writing to the database...')
        if self.site_id is not None:
            # print(news)
            logger.info('Connecting to the database...')
            con = NewsProvider.connect_db(logger)
            cur = con.cursor()

            sql = f"DELETE FROM {self.NEWS_DBNAME} WHERE id > 0 AND site_id={self.site_id} AND " \
                  f"news_date >= '{beg_date_str(date_date)}' AND " \
                  f"news_date <= '{end_date_str(date_date)}';"
            # print(sql)
            exec_sql(logger, cur, sql)
            # cur.execute(sql)

            for one_news in news:
                try:
                    raw_text_info = FinamNewsProvider.prepare_news_text(
                        one_news['raw_info'])
                    brief_info = FinamNewsProvider.prepare_news_text(one_news['brief_info'])
                    sql = f"INSERT INTO {self.NEWS_DBNAME} " \
                          f"(site_id, news_date, ref, brief_info, raw_info, info, " \
                          f"raw_converted) VALUES ({self.site_id}, '{one_news['news_date']}', " \
                          f"'{one_news['ref']}', '{brief_info}', '{raw_text_info}', " \
                          f"'', False);"
                    # print(sql)
                    cur.execute(sql)
                    con.commit()
                except Exception as err:
                    logger.exception(f'{err}')
                    logger.info(f'ERROR: {sql}, INFO=\'{raw_text_info}\'')

            con.close()
            logger.info('Connection closed')

    @staticmethod
    def date_ref(date_str):
        """
        Преобразует дату из строки в шестнадцатиричное представление
        :param date_str: "14.02.2020"
        :return: 0E027E4
        """
        return 'rqdate{0}{1}{2}'.format(hex(int(date_str[:2]))[2:].rjust(2, '0').upper(),
                                        hex(int(date_str[3:5]))[2:].rjust(2, '0').upper(),
                                        hex(int(date_str[6:]))[2:].rjust(3, '0').upper())

    @staticmethod
    def get_news_info(browser, url, show_message=False):
        """
        Получение тескта новости по ссылке
        :param browser:
        :param url:
        :param show_message:
        :return:
        """
        result = ''

        try:
            read_page = browser.get_html(url, show_message=show_message)

            if not read_page['error']:
                html_doc = read_page['html']
                bs_obj = BeautifulSoup(html_doc, features="html.parser")

                if url.startswith('http://bonds'):
                    lines_cnt = 0
                    for obj in bs_obj.findAll("td", id="content-block"):
                        lines_cnt += 1
                        for link in obj.find_all("p"):
                            current_p = link.text
                            result += current_p
                else:
                    lines_cnt = 0
                    for obj in bs_obj.findAll("div", class_="f-newsitem-text"):
                        lines_cnt += 1
                        for link in obj.find_all("p"):
                            current_p = link.text
                            result += current_p
        except Exception as err:
            msg = f'{url}\n{str(err)}'
            logger.exception(msg)
        return result

    @staticmethod
    def prepare_news_text(info):
        """
        Предварительная обработка новости
        :param info:
        :return:
        """
        my_str = info.replace('%', '%%')
        my_str = my_str.replace('\'', ' ')
        my_str = my_str.replace('\"', ' ')
        my_str = my_str.replace('\n', ' ')
        my_str = my_str.replace('\t', ' ')
        return my_str


class NewsFabric:
    """
    Общая фабрика новостей
    """
    PROVIDER_FINAM = 'Финам'

    @staticmethod
    def create_provider(provider_name):
        """
        Выбор провайдера новостей
        :param provider_name:
        :return:
        """
        if provider_name == NewsFabric.PROVIDER_FINAM:
            return FinamNewsProvider()
        return None


class Browser(metaclass=abc.ABCMeta):
    """
    Браузер
    """

    def __init__(self):
        self.browser = None
        self.connect_error = ''

    @abc.abstractmethod
    def connect(self):
        """
        Соединение с браузером
        :return:
        """

    @abc.abstractmethod
    def disconnect(self):
        """
        Завершение работы с браузером
        :return:
        """

    @abc.abstractmethod
    def get_html(self, url, show_message=False):
        """
        Возвращает html-строку по URL
        :param url:
        :param show_message:
        :return:
        """

    def is_connected(self):
        """
        Проверка соединения с браузером
        :return:
        """
        return self.browser and len(self.connect_error) == 0


class FireFoxBrowser(Browser):
    """
    Браузер FireFox
    """

    # def __init__(self):
    #     super().__init__()

    def connect(self):
        self.connect_error = ''
        options = Options()
        options.headless = True  # Не открывать окно браузера
        # options.add_argument('--headless')  # Не открывать окно браузера

        # Sets whether Firefox should accept SSL certificates which have expired,
        # signed by an unknown authority or are generally untrusted.
        # options.setAcceptUntrustedCertificates(True)

        # FirefoxOptions().setLegacy(true);
        # параметр marionette

        profile = webdriver.FirefoxProfile()
        profile.set_preference(
            "general.useragent.override",
            "Opera/9.80 (Android 2.2; Opera Mobi/-2118645896; U; pl) Presto/2.7.60 Version/10.5")

        profile.set_preference('browser.helperApps.alwaysAsk.force', False)  # 19042020
        profile.set_preference('browser.download.manager.showWhenStarting', False)  # 19042020
        # browser.download.folderList
        #   0 - Firefox will save all files downloaded via the browser on the user's desktop;
        #   1 - these downloads are stored in the Downloads folder;
        #   2 - custom location ('browser.download.dir')
        profile.set_preference('browser.download.folderList', 1)  # 19042020

        try:
            self.browser = webdriver.Firefox(
                executable_path=FIREFOX_EXECUTABLE_PATH,
                options=options,
                firefox_profile=profile
            )
            self.browser.implicitly_wait(20)  # seconds

        except WebDriverException as err:
            self.connect_error = err
            return
        except Exception as err:
            self.connect_error = err
            return

    def disconnect(self):
        if self.browser:
            self.browser.quit()

    def get_html(self, url, show_message=False):
        result = {'html': '', 'status_code': None, 'error': ''}

        page = requests.get(url)
        result['status_code'] = page.status_code

        if show_message:
            # print('================================================')
            print(url)
            # print(f'Status Code={page.status_code}')

        if page.status_code == 200:
            try:
                self.browser.get(url)
            except WebDriverException as err:
                result['error'] = f'Ошибка открытия ссылки (WebDriverException)\n{str(err)}'
            except TimeoutException as err:
                result['error'] = f'Ошибка открытия ссылки (TimeoutException)\n{str(err)}'
            except Exception as err:
                result['error'] = f'Ошибка открытия ссылки (Other)\n{str(err)}'

        if not result['error']:
            result['html'] = self.browser.page_source

        return result


class GrabBrowser(Browser):
    """
    Браузер Grab
    """

    # def __init__(self):
    #     super().__init__()

    def connect(self):
        self.connect_error = ''
        try:
            self.browser = Grab()
        except Exception as err:
            self.connect_error = err
            return

    def disconnect(self):
        if self.browser:
            self.browser = None

    def get_html(self, url, show_message=False):
        result = {'html': '', 'status_code': None, 'error': ''}
        # g.response.code
        # g.response.error_code
        # g.response.error_msg
        # g.doc.body

        self.browser.go(url)
        result['status_code'] = self.browser.response.code
        result['error'] = self.browser.response.error_msg

        if show_message:
            # print('================================================')
            print(url)
            # print(f'Status Code={page.status_code}')

        if not result['error']:
            result['html'] = self.browser.doc.body

        return result


class BrowserFabric:
    """
    Фабрика браузеров
    """
    BROWSER_FIREFOX = 'FireFox'
    BROWSER_GRAB = 'Grab'

    @staticmethod
    def create_browser(browser_name):
        """
        Создаем объект браузера
        :param browser_name:
        :return:
        """
        if browser_name == BrowserFabric.BROWSER_FIREFOX:
            return FireFoxBrowser()
        elif browser_name == BrowserFabric.BROWSER_GRAB:
            return GrabBrowser()

        return None


def beg_date_str(date_date):
    """
    Начало дня
    :param date_date:
    :return: date
    """
    return date_date.combine(date_date.date(), date_date.min.time())


def end_date_str(date_date):
    """
    Конец дня
    :param date_date:
    :return: date
    """
    return date_date.combine(date_date.date(), date_date.max.time())


def exec_sql(my_logger, cur, sql, *args, **kwargs):
    """
    Выполнить запрос SQL
    :param my_logger:
    :param cur:
    :param sql:
    :param args:
    :param kwargs:
    :return:
    """
    try:
        cur.execute(sql, *args, **kwargs)
    except Exception as err:
        # my_logger.exception()
        my_logger.exception(f'SQL: {sql}\nError: {err}')


if __name__ == '__main__':
    # news_provider = NewsFabric.create_provider('Финам')
    # news_provider.collect_news('30.03.2020')
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--date', type=str,
        required=False, help='Date to proceed (format dd.mm.yyyy)'
    )
    args = parser.parse_args()
    if args.date:
        news_provider = NewsFabric.create_provider('Финам')
        news_provider.collect_news(args.date)
