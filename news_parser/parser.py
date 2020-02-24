import requests
import abc

from bs4 import BeautifulSoup
from collections import namedtuple

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

SiteInfo = namedtuple('SiteInfo', 'name ref descr')
FIREFOX_EXECUTABLE_PATH = r'C:\Program Files\Geckodriver\geckodriver.exe'


class NewsProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def collect_news(self, news_date):
        """
        Собрать новости с сайта за выбранную дату и сохранить их в базе.
        :param news_date:
        :return:
        """
        pass

    @abc.abstractmethod
    def get_site(self, site_name):
        """
        Возвращает ссылку на сайт в базе, если ее нет, то создает ее.
        :return:
        """
        pass


class FinamNewsProvider(NewsProvider):
    site_info = SiteInfo(
        name='Финам',
        ref='https://www.finam.ru/analysis/united/',
        descr='Объединенная лента финансовых новостей и событий'
    )

    def __init__(self):
        super().__init__()
        self.ref = 'https://www.finam.ru/analysis/united/'  # TODO: читать из базы

    def collect_news(self, news_date):
        """

        :param news_date: дата в формате '14.02.2020'
        :return:
        """
        browser = BrowserFabric.create_browser('FireFox')
        browser.connect()
        if not browser.is_connected():
            browser.disconnect()
            return

        # url = "https://www.finam.ru/analysis/united/rqdate0E027E4"
        maim_url = str(self.ref)
        if maim_url[-1] != '/':
            maim_url += '/'
        maim_url += format(self.date_ref(news_date))

        page_num = 0

        while True:
            page_num += 1

            if page_num == 1:
                url = maim_url
            else:
                url = maim_url + '/?page=' + str(page_num)

            read_page = browser.get_html(url, show_message=True)

            if read_page['error']:
                break

            html_doc = read_page['html']

            bs_obj = BeautifulSoup(html_doc, features="html.parser")

            lines_cnt = 0
            for obj in bs_obj.findAll("div", class_="ln"):
                lines_cnt += 1
                for link in obj.find_all(lambda tag: tag.name == 'a' and tag.get('class') != ['section']):
                    print('---')
                    print(obj.find("span", class_="date").text)
                    print(obj.p.text)
                    print(f'{link}')

            if lines_cnt == 0:
                break

    def get_site(self):
        pass

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
            print('================================================')
            print(url)
            print(f'Status Code={page.status_code}')

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
