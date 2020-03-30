import schedule
import time
import datetime

from news_parser.parser import NewsFabric
from news_parser.filtering import filtering
from news_parser.sorting import sorting
from news_parser.sending import sending


def job_news(date_date):
    parsing_finished = False
    filtering_finished = False
    sorting_finished = False
    sending_finished = False

    try:
        news_provider = NewsFabric.create_provider('Финам')
        news_provider.collect_news(date_date)
        parsing_finished = True
    except Exception as err:
        pass

    if parsing_finished:
        try:
            filtering(date_date)
            filtering_finished = True
        except Exception as err:
            pass

    if filtering_finished:
        try:
            sorting(date_date)
            sorting_finished = True
        except Exception as err:
            pass

    if sorting_finished:
        try:
            sending(date_date)
            sorting_finished = True
        except Exception as err:
            pass


if __name__ == '__main__':
    today = datetime.datetime.today()
    start_time = "22:00"
    schedule.every().monday.at().do(job_news, today)
    schedule.every().tuesday.at(start_time).do(job_news, today)
    schedule.every().wednesday.at(start_time).do(job_news, today)
    schedule.every().thursday.at(start_time).do(job_news, today)
    schedule.every().friday.at(start_time).do(job_news, today)

    while True:
        schedule.run_pending()
        time.sleep(1)
