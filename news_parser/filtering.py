import datetime
import pymorphy2
import re
import logging.config
from news_parser.parser import NewsProvider, beg_date_str, end_date_str, exec_sql
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from string import punctuation

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('filtering')

my_stopwords = stopwords.words('russian') + [a for a in punctuation]

# Экземпляры класса MorphAnalyzer обычно занимают порядка 15Мб оперативной памяти (т.к. загружают в память словари,
# данные для предсказателя и т.д.). Старайтесь создавать экземпляр MorphAnalyzer заранее и работать с этим
# единственным экземпляром в дальнейшем.
morph = pymorphy2.MorphAnalyzer()

pattern_rus = re.compile("[а-яёА-ЯЁ]+$")  # предполагаем, что русское слово - только из русских букв


def normal_noun(word):
    """
    Проверяет, что это существительное и возвращет его нормальную форму
    :param word:
    :return:
    """
    result = ''
    if pattern_rus.fullmatch(word):
        word_parse = morph.parse(word)
        for item in word_parse:
            if 'NOUN' in item.tag:
                result = item.normal_form
                break
    else:
        result = word
    return result


def convert_news(news):
    # Всё в нижний регистр
    text = news.lower()
    # Создаем объект класса с регулярным выражением
    regex_tok = RegexpTokenizer(r'\w+')
    # Получаем токены (слова)
    tokens = regex_tok.tokenize(text)
    # Оставляем только определеннные существительные
    tokens_no_sw = []
    for token in tokens:
        if token.isalpha() and len(token) > 2 and token not in my_stopwords:  # Убираем стоп-слова и цифры
            normal = normal_noun(token)
            if normal and normal not in tokens_no_sw:  # без повторов
                tokens_no_sw.append(normal)
    return tokens_no_sw


def raw_conversion(site_id, date_date):
    logger.info('Connecting to the database...')
    con = NewsProvider.connect_db()
    cur = con.cursor()

    sql = f"SELECT id, raw_info FROM {NewsProvider.NEWS_DBNAME} WHERE site_id={site_id} AND " \
          f"news_date >= '{beg_date_str(date_date)}' AND " \
          f"news_date <= '{end_date_str(date_date)}' AND " \
          f"raw_converted = False;"
    # print(sql)
    # cur.execute(sql)
    exec_sql(logger, cur, sql)

    rows = cur.fetchall()
    rows_cnt = cur.rowcount
    logger.info(f'Site ID {site_id}, Date {date_date}, Items to proceed: {rows_cnt}')
    for row in rows:
        compressed_news = convert_news(row['raw_info'])
        compressed_news_str = ','.join(compressed_news)
        sql = f"UPDATE {NewsProvider.NEWS_DBNAME} " \
              f"SET info = '{compressed_news_str}', raw_converted = True " \
              f"WHERE id = {row['id']}"
        # print(sql)
        # cur.execute(sql)
        exec_sql(logger, cur, sql)
        con.commit()
        # print(row['id'])
        # for item in compressed_news:
        #     print(f'{item}')

    con.close()
    logger.info('Connection closed')
    return


def filtering(date_date):
    logger.info('Connecting to the database...')
    con = NewsProvider.connect_db()
    cur = con.cursor()

    sql = f"SELECT id FROM {NewsProvider.SITE_DBNAME};"
    exec_sql(logger, cur, sql)

    rows = cur.fetchall()
    for row in rows:
        raw_conversion(row['id'], date_date)

    con.close()
    logger.info('Connection closed')


# if __name__ == '__main__':
#     raw_conversion(1, datetime.datetime.strptime('14.02.2020', "%d.%m.%Y"))
#     # print(f'Обработано записей: {l}')
