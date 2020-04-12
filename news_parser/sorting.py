import datetime
import logging.config
import socket
from news_parser.parser import NewsProvider, beg_date_str, end_date_str, exec_sql
from argparse import ArgumentParser
from os import path

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
if socket.gethostname() == 'magv-hp':
    DEBUG = True
else:
    DEBUG = False

logging.config.fileConfig(path.join(BASE_DIR, 'news_parser', 'logging.conf'))
logger = logging.getLogger('sorting')


def sorting(date_date):
    logger.info('Connecting to the database...')
    con = NewsProvider.connect_db()
    cur = con.cursor()

    sql = f"SELECT topic.id, topic.name, topic.keywords " \
          f"FROM {NewsProvider.TOPIC_DBNAME} AS topic " \
          f"WHERE inactive = False AND (period_start is NULL OR period_start <= '{beg_date_str(date_date)}') " \
          f"    AND (period_end is NULL OR period_end >= '{beg_date_str(date_date)}');"
    # print(sql)
    # cur.execute(sql)
    exec_sql(logger, cur, sql)

    topics = cur.fetchall()
    topics_cnt = cur.rowcount
    logger.info(f'Date: {date_date}, Active topic: {topics_cnt}')
    # Перебираем все активные топики
    for topic in topics:
        # Предварительно очищаем ранее отобранные новости по текущему топику и выбранной дате
        sql = f"DELETE FROM {NewsProvider.TOPIC_NEWS_DBNAME} WHERE id > 0 AND topic_id={topic['id']} AND " \
              f"news_date >= '{beg_date_str(date_date)}' AND " \
              f"news_date <= '{end_date_str(date_date)}';"
        # print(sql)
        # cur.execute(sql)
        exec_sql(logger, cur, sql)
        con.commit()

        # print(f'{topic["id"]},{topic["name"]}')

        keywords = topic['keywords'].lower().split(',')

        # Сюда будем времено помещать подходящие новости со всех сайтов
        topic_news = []

        # Перебираем все сайты, привязанные к текущему топику
        sql = f"SELECT site_id " \
              f"FROM {NewsProvider.TOPIC_SITE_DBNAME} " \
              f"WHERE topic_id={topic['id']}; "
        # print(sql)
        # cur.execute(sql)
        exec_sql(logger, cur, sql)

        sites = cur.fetchall()
        sites_cnt = cur.rowcount
        logger.info(f'Topic ID {topic["id"]}, \'{topic["name"]}\', sites: {sites_cnt}')
        # Перебираем все сайты
        for site in sites:
            sql = f"SELECT news_date, id, info FROM {NewsProvider.NEWS_DBNAME} " \
                  f"WHERE site_id={site['site_id']} AND " \
                  f"news_date >= '{beg_date_str(date_date)}' AND " \
                  f"news_date <= '{end_date_str(date_date)}' AND " \
                  f"raw_converted = True;"
            # print(sql)
            # cur.execute(sql)
            exec_sql(logger, cur, sql)

            news = cur.fetchall()
            news_cnt = cur.rowcount
            for news_item in news:
                info_list = news_item['info'].split(',')
                for keyword in keywords:
                    if info_list.count(keyword.strip()) > 0:
                        topic_news.append(
                            {
                                'news_date': news_item['news_date'],
                                'news_id': news_item['id'],
                            }
                        )

        logger.info(f'\t{len(topic_news)} news items found on all sites')

        # Работаем с найденными новостями
        for item in topic_news:
            # print(item)
            sql = f"INSERT INTO {NewsProvider.TOPIC_NEWS_DBNAME} (news_id, news_date, topic_id, is_send) " \
                  f"VALUES ({item['news_id']}, '{item['news_date']}', {topic['id']}, False);"
            # cur.execute(sql)
            exec_sql(logger, cur, sql)
            con.commit()

    con.close()
    logger.info('Connection closed')
    return


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-d', '--date', type=str,
        required=False, help='Date to proceed (format dd.mm.yyyy)'
    )
    args = parser.parse_args()
    if args.date:
        sorting(datetime.datetime.strptime(args.date, "%d.%m.%Y"))
