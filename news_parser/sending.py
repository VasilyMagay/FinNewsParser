# https://selenium-python.com/smtplib-email-example

import datetime
import smtplib
import ssl

from news_parser.parser import NewsProvider, beg_date_str, end_date_str
from news_parser.my_settings import EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_HOST
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MESSAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>FinNews</title>
    <style>
        <%style%>
    </style>
</head>
<body>
<%main_text%>
<%table%>
</body>
</html>
"""

TABLE_START = """
<div class="divTable">
<div class="divTableBody">
"""

TABLE_ROW = """
<div class="divTableRow">
<div class="divTableCell"><%str_date%></div>
<div class="divTableCell"><a href='<%str_ref%>'><%str_info%></a></div>
</div>
"""

TABLE_END = """
</div>
</div>
"""

MESSAGE_STYLE = """
.divTable{
    display: table;
    width: 100%;
}
.divTableRow {
    display: table-row;
}
.divTableHeading {
    background-color: #EEE;
    display: table-header-group;
}
.divTableCell, .divTableHead {
    border: 1px solid #999999;
    display: table-cell;
    padding: 3px 10px;
}
.divTableHeading {
    background-color: #EEE;
    display: table-header-group;
    font-weight: bold;
}
.divTableFoot {
    background-color: #EEE;
    display: table-footer-group;
    font-weight: bold;
}
.divTableBody {
    display: table-row-group;
}
"""


def sending(date_date):
    con = NewsProvider.connect_db()
    cur = con.cursor()

    sql = f"SELECT DISTINCT topic.name, topic_id, users.username, users.email " \
          f"FROM {NewsProvider.TOPIC_NEWS_DBNAME} AS topic_news " \
          f"LEFT JOIN {NewsProvider.TOPIC_DBNAME} AS topic " \
          f"    ON topic_news.topic_id = topic.id " \
          f"LEFT JOIN {NewsProvider.USERS_DBNAME} AS users " \
          f"    ON topic.user_id = users.id " \
          f"WHERE topic_news.is_send = False AND " \
          f"    topic_news.news_date >= '{beg_date_str(date_date)}' AND " \
          f"    topic_news.news_date <= '{end_date_str(date_date)}';"
    # print(sql)
    cur.execute(sql)

    topics = cur.fetchall()
    topics_cnt = cur.rowcount
    # Перебираем топики с неотправленными новостями за выбранную дату.
    # Для каждого топика будет отдельное письмо.
    for topic in topics:
        # print(topic)
        sql = f"SELECT topic_news.id, topic_news.news_date, news.ref, news.brief_info " \
              f"FROM {NewsProvider.TOPIC_NEWS_DBNAME} AS topic_news " \
              f"LEFT JOIN {NewsProvider.NEWS_DBNAME} AS news " \
              f"    ON topic_news.news_id = news.id " \
              f"WHERE topic_news.topic_id = {topic['topic_id']} AND " \
              f"    topic_news.is_send = False AND " \
              f"    topic_news.news_date >= '{beg_date_str(date_date)}' AND " \
              f"    topic_news.news_date <= '{end_date_str(date_date)}';"
        # print(sql)
        cur.execute(sql)

        news = cur.fetchall()
        news_cnt = cur.rowcount
        if news_cnt > 0:
            if send_message(topic, news, date_date):
                for news_item in news:
                    send_date = datetime.datetime.today()
                    sql = f"UPDATE {NewsProvider.TOPIC_NEWS_DBNAME} " \
                          f"SET send_date = '{send_date}', is_send = True " \
                          f"WHERE id = {news_item['id']}"
                    # print(sql)
                    cur.execute(sql)
                    con.commit()

    con.close()
    return


def create_page(topic, news, date_date):
    main_text = f"FinNews: {topic['name']}, {date_date}"
    main_text = "<h2>" + main_text + "</h2>"

    table = TABLE_START
    for news_item in news:
        table_row = TABLE_ROW.replace('<%str_date%>', str(news_item['news_date'])). \
            replace('<%str_ref%>', news_item['ref']). \
            replace('<%str_info%>', news_item['brief_info'])
        table += table_row
    table += TABLE_END

    page = MESSAGE_TEMPLATE.replace('<%style%>', MESSAGE_STYLE). \
        replace('<%main_text%>', main_text). \
        replace('<%table%>', table)
    return page


def send_message(topic, news, date_date):
    sender_email = EMAIL_HOST_USER
    receiver_email = topic['email']

    message = MIMEMultipart("alternative")
    message["Subject"] = f"FinNews: {topic['name']}, {date_date}"
    message["From"] = sender_email
    message["To"] = receiver_email
    # message['Reply-To'] = sender_email
    # message['Return-Path'] = sender_email
    # message['X-Mailer'] = 'Python/'+(python_version())

    # Текстовая версия сообщения
    text = message["Subject"]

    # HTML версия сообщения
    html = create_page(topic, news, date_date)

    # Сделать их текстовыми\html объектами MIMEText
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Внести HTML\текстовые части сообщения MIMEMultipart
    # Почтовый клиент сначала попытается отрендерить последнюю часть
    message.attach(part1)
    message.attach(part2)

    # Создание безопасного подключения с сервером и отправка сообщения
    result = False
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(EMAIL_HOST, 465, context=context) as server:
            server.login(sender_email, EMAIL_HOST_PASSWORD)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
        result = True
    except Exception as err:
        pass
    return result


if __name__ == '__main__':
    sending(datetime.datetime.strptime('14.02.2020', "%d.%m.%Y"))
