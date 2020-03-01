import requests
import abc
import pymysql
import pymysql.cursors
import datetime

from os import path

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

FIREFOX_EXECUTABLE_PATH = r'C:\Program Files\Geckodriver\geckodriver.exe'
BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))


class NewsProvider(metaclass=abc.ABCMeta):
    site_ref = ''
    site_id = None
    SITE_DBNAME = 'mainapp_site'
    NEWS_DBNAME = 'mainapp_news'

    def __init__(self):
        self.site_name = ''

    @abc.abstractmethod
    def collect_news(self, news_date):
        """
        Собрать новости с сайта за выбранную дату и сохранить их в базе.
        :param news_date:
        :return:
        """
        pass

    def get_site_info(self):
        """
        Возвращает ссылку на сайт в базе.
        :return:
        """
        if self.site_ref:
            return

        con = NewsProvider.connect_db()
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {self.SITE_DBNAME} WHERE name=%s", self.site_name)

        site = cur.fetchone()
        if len(site) > 0:
            self.site_ref = site['ref']
            self.site_id = site['id']

        con.close()

    @staticmethod
    def connect_db():
        mysql_config = {}
        with open(path.join(BASE_DIR, 'mysql.cnf'), 'r') as file:
            lines = file.read().splitlines()
            for line in lines:
                pair = line.split('=')
                if len(pair) == 2:
                    mysql_config[pair[0].strip()] = pair[1].strip()
        return pymysql.connect(
            mysql_config['host'],
            mysql_config['user'],
            mysql_config['password'],
            mysql_config['database'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )


class FinamNewsProvider(NewsProvider):

    def __init__(self):
        super().__init__()
        self.site_name = 'Финам'
        self.get_site_info()

    def collect_news(self, news_date):
        """

        :param news_date: дата в формате '14.02.2020' или datetime
        :return:
        """
        browser = BrowserFabric.create_browser('FireFox')
        browser.connect()
        if not browser.is_connected():
            browser.disconnect()
            return

        if type(news_date) is str:
            date_str = news_date
            date_date = datetime.datetime.strptime(news_date, "%d.%m.%Y")
        elif type(news_date) is datetime.datetime:
            date_str = news_date.strftime("%d.%m.%Y")
            date_date = news_date

            # url = "https://www.finam.ru/analysis/united/rqdate0E027E4"
        maim_url = str(self.site_ref)
        if maim_url[-1] != '/':
            maim_url += '/'
        maim_url += format(self.date_ref(date_str))

        page_num = 0
        news = []

        while True:
            page_num += 1

            if page_num == 1:
                url = maim_url
            else:
                url = maim_url + '/?page=' + str(page_num)
            # print(f'URL={url}')
            read_page = browser.get_html(url, show_message=True)

            if read_page['error']:
                break

            html_doc = read_page['html']

            bs_obj = BeautifulSoup(html_doc, features="html.parser")

            lines_cnt = 0
            for obj in bs_obj.findAll("div", class_="ln"):
                lines_cnt += 1
                for link in obj.find_all(lambda tag: tag.name == 'a' and tag.get('class') != ['section']):
                    date_s = obj.find("span", class_="date").text
                    if not date_s:
                        date_s = '00:00'
                    link_text = ''
                    try:
                        link_text = link.attrs['href']
                    except:
                        pass
                    finally:
                        pass
                    if link_text:
                        brief_info = str(obj.p.text).strip()
                        if brief_info:
                            news.append(
                                {
                                    'news_date': datetime.datetime.strptime(date_str + ' ' + date_s, '%d.%m.%Y %H:%M'),
                                    'ref': f'https://www.finam.ru{link_text}',
                                    'brief_info': brief_info,
                                    'info': ''
                                }
                            )

            if lines_cnt == 0:
                break

        # Запись новостей в базу

        if self.site_id is not None:
            # print(news)
            con = NewsProvider.connect_db()
            cur = con.cursor()

            sql = f"DELETE FROM {self.NEWS_DBNAME} WHERE id > 0 AND site_id={self.site_id} AND " \
                  f"news_date >= '{date_date.combine(date_date.date(), date_date.min.time())}' AND " \
                  f"news_date <= '{date_date.combine(date_date.date(), date_date.max.time())}';"
            # print(sql)
            cur.execute(sql)

            check_ref = []
            for one_news in news:
                if not one_news['ref'] in check_ref:
                    sql = f"INSERT INTO {self.NEWS_DBNAME} (site_id, news_date, ref, brief_info, info) " \
                          f"VALUES ({self.site_id}, '{one_news['news_date']}', " \
                          f"'{one_news['ref']}', '{one_news['brief_info']}', '{one_news['info']}');"
                    # print(sql)
                    cur.execute(sql)
                    check_ref.append(one_news['ref'])

            con.commit()
            con.close()

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


class NewsFabric:
    PROVIDER_FINAM = 'Финам'

    @staticmethod
    def create_provider(provider_name):
        if provider_name == __class__.PROVIDER_FINAM:
            return FinamNewsProvider()
        else:
            return None


class Browser(metaclass=abc.ABCMeta):

    def __init__(self):
        self.browser = None
        self.connect_error = ''

    @abc.abstractmethod
    def connect(self):
        pass

    @abc.abstractmethod
    def disconnect(self):
        pass

    @abc.abstractmethod
    def get_html(self, url, show_message=False):
        pass

    def is_connected(self):
        return self.browser and len(self.connect_error) == 0


class FireFoxBrowser(Browser):

    def __init__(self):
        super().__init__()

    def connect(self):
        self.connect_error = ''
        options = Options()
        options.headless = True  # Не открывать окно браузера
        # options.add_argument('--headless')  # Не открывать окно браузера

        # Sets whether Firefox should accept SSL certificates which have expired, signed by an unknown authority or
        # are generally untrusted.
        # options.setAcceptUntrustedCertificates(True)

        # FirefoxOptions().setLegacy(true);
        # параметр marionette

        profile = webdriver.FirefoxProfile()
        profile.set_preference(
            "general.useragent.override",
            "Opera/9.80 (Android 2.2; Opera Mobi/-2118645896; U; pl) Presto/2.7.60 Version/10.5"
        )

        try:
            self.browser = webdriver.Firefox(
                executable_path=FIREFOX_EXECUTABLE_PATH,
                options=options,
                firefox_profile=profile
            )
        except WebDriverException as err:
            self.connect_error = err.msg
            return
        except Exception as err:
            self.connect_error = err.msg
            return

        # browser.implicitly_wait(10)  # seconds

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


class BrowserFabric:
    BROWSER_FIREFOX = 'FireFox'

    @staticmethod
    def create_browser(browser_name):
        if browser_name == __class__.BROWSER_FIREFOX:
            return FireFoxBrowser()
        else:
            return None


if __name__ == '__main__':
    news_provider = NewsFabric.create_provider('Финам')
    news_provider.collect_news('14.02.2020')
