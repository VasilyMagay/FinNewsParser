<h1>Finance News Parser</h1>

<div>
    <p>Проект <b>Finance News Parser</b> предназначен для ежедневного сбора (парсинга) финансовых новостей с финансовых сайтов и их рассылке пользователям по подписке.</p>
    <p>Проект состоит из двух частей: административная часть, через которую пользователь может зарегистрироваться и настроить сбор новостей, и автоматические задания сбора, сортировки и рассылки новостей. Результаты парсинга сохраняются в базе данных.</p>
    <p>Можно указать ключевые слова, по которым сайт ежедневно будет присылать информационное письмо на электронную почту пользователя с ссылками на интересующую тему. Пользователь может самостоятельно зарегистрироваться на сайте через электронную почту.</p>
    <p>Сейчас в качестве источника информации доступна лента новостей с единственного финансового сайта – <a href="https://www.finam.ru/analysis/united/">https://www.finam.ru/analysis/united/</a></p>
</div>

<h2>Структура каталогов проекта</h2>

<p>Пути указаны относительно домашнего каталога пользователя (/home/user/).</p>
<pre>cron/</pre>
<pre>env/</pre>
<pre>FinNewsParser/</pre>
<pre>	authapp/</pre>
<pre>	event.log</pre>
<pre>	finnews.sock</pre>
<pre>	geckodriver.log</pre>
<pre>	mainapp/</pre>
<pre>	manage.py</pre>
<pre>	mysql.cnf</pre>
<pre>	news_parser/</pre>
<pre>	process.py</pre>
<pre>	README.md</pre>
<pre>	requirements.txt</pre>
<pre>	static/</pre>
<pre>logs/</pre>
<pre>static_content/</pre>

<h2>Дополнительные настройки при развертывании проекта в production</h2>
<ol>
<li>Файл mysql.cnf</li>
<li>Файл my_settings.py</li>
<li>Файл production_settings.py</li>
<li>Первоначальное заполнение</li>
<li>Загрузка стоп-слов</li>
<li>Обновление русского морфологического словаря</li>
<li>Установка geckodriver</li>
<li>Настройка регламентных заданий</li>
<li>Nginx</li>
<li>Gunicorn</li>
</ol>

<h2>Файл mysql.cnf</h2>
<p>Файл настроек подключения к MySQL <b>mysql.cnf</b>. Требуется указать host, user, password.</p> 
<div># mysql.cnf</div>
<div>[client]</div>
<div>host = 127.0.0.1</div>
<div>database = finnews</div>
<div>user = ***</div>
<div>password = ***</div>
<div>default-character-set = utf8</div>
<br>
<div>Дополнительно создать файл <b>/etc/my.cnf</b>, либо <b>/etc/mysql/my.cnf</b> с содержанием:</div>
<div>[mysqld]</div>
<div>default-storage-engine=innodb</div>

<h2>Файл my_settings.py</h2>
<p>Файл с логинами/паролями <b>news_parser/my_settings.py</b>:</p>
<div>SECRET_KEY = ''</div>
<div>EMAIL_HOST_USER = ''</div>
<div>EMAIL_HOST_PASSWORD = ''</div>
<div>EMAIL_PORT = 587</div>
<div>EMAIL_USE_TLS = True</div>

<h2>Файл production_settings.py</h2>
<p>Файл с настройками Production <b>news_parser/production_settings.py</b>:</p>
<div>ALLOWED_HOSTS = []</div>
<div>DOMAIN_NAME = ''</div>
<div>STATIC_ROOT = '/home/user/static_content/'</div>

<h2>Первоначальное заполнение</h2>
<p>Первоначальное заполнение базы данных сведениями о финансовых сайтах:</p>
<p style="margin-left: 50px;">python manage.py init_sites</p>

<h2>Загрузка стоп-слов</h2>
<p style="margin-left: 50px;">import nltk</p>
<p style="margin-left: 50px;">nltk.download('stopwords')</p>

<h2>Обновление русского морфологического словаря</h2>
<p style="margin-left: 50px;">pip install -U pymorphy2-dicts-ru</p>

<h2>Установка geckodriver под Ubuntu</h2>
<p>Заходим на сайт <a href='https://github.com/mozilla/geckodriver/releases/'>https://github.com/mozilla/geckodriver/releases/</a>, проверяем ссылку на последнюю версию архива установки.</p>
<div>Скачиваем архив:</div>
<pre>    wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz</pre>
<div>Вытаскиваем файл из архива:</div> 
<pre>    tar -xvzf geckodriver*</pre>
<div>Даем нужные права драйверу:</div>
<pre>    sudo chmod +x geckodriver</pre>
<div>Отправляем драйвер в папку, где его будет искать Selenium:</div> 
<pre>    sudo mv geckodriver /usr/local/bin/</pre>

<h2>Настройка регламентных заданий</h2>
<div>Создаем сценарий <b>finnewsProcess</b>:</div>
<pre>    mkdir ./cron</pre>
<pre>    sudo nano cron/finnewsProcess</pre>
<pre>    sudo chmod +x cron/finnewsProcess</pre>

<p>Содержимое сценария <b>finnewsProcess</b>:</p>
<div>#!/bin/bash</div>
<div>cd ~</div>
<div>source ./env/bin/activate</div>
<div>cd /home/user/FinNewsParser</div>
<div>python process.py</div>
<div>deactivate</div>
<br>
<div>Открыть таблицу с периодическими заданиями CRON:</div>
<pre>    crontab -e</pre>

<p>В конец файла дописываем две строки (запуск заданий ежедневно в 21:30 и 21:45):</p>
<pre>30 21 * * * root pkill firefox</pre>
<pre>45 21 * * * /home/user/cron/finnewsProcess</pre>

<h2>Nginx</h2>
<p>sudo nano /etc/nginx/sites-available/finnews.conf</p>

<pre>server {</pre>
<pre>    listen 149.154.70.150:80;</pre>
<pre></pre>
<pre>    location = /favicon.ico { access_log off; log_not_found off; }</pre>
<pre></pre>
<pre>    location /static/ {</pre>
<pre>        autoindex on;</pre>
<pre>        alias /home/user/static_content/;</pre>
<pre>    }</pre>
<pre></pre>
<pre>    location / {</pre>
<pre>        include proxy_params;</pre>
<pre>        proxy_pass http://unix:/home/user/FinNewsParser/finnews.sock;</pre>
<pre>    }</pre>
<pre>}</pre>
<pre></pre>
<p>Теперь мы можем включить файл, связав его с каталогом сайтов:</p>
<pre>    sudo ln -s /etc/nginx/sites-available/finnews.conf /etc/nginx/sites-enabled</pre>

<h2>Gunicorn</h2>
<p>Проверка работы веб-сервера:</p>
<pre>    gunicorn --bind 0.0.0.0:8001 news_parser.wsgi:application</pre>

<p>Конфигурация Gunicorn:</p>
<pre>    sudo nano /etc/systemd/system/gunicorn.service</pre>
<p>Вставьте следующие строки:</p>
<pre>[Unit]</pre>
<pre>Description=gunicorn daemon</pre>
<pre>After=network.target</pre>
<pre></pre>
<pre>[Service]</pre>
<pre>User=root</pre>
<pre>Group=www-data</pre>
<pre>WorkingDirectory=/home/user/FinNewsParser</pre>
<pre>ExecStart=/home/user/env/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/user/FinNewsParser/finnews.sock news_parser.wsgi:application</pre>
<pre></pre>
<pre>[Install]</pre>
<pre>WantedBy=multi-user.target</pre>

<p>Теперь можно запустить созданную службу Gunicorn и включить ее так, чтобы она запускалась при загрузке:</p>
<pre>    sudo systemctl start gunicorn</pre>
<pre>    sudo systemctl enable gunicorn</pre>

<p>Для начала необходимо проверить состояние процесса, чтобы узнать, удалось ли его запустить:</p>
<pre>    sudo systemctl status gunicorn</pre>

<p>Затем проверьте наличие файла finnews.sock в каталоге вашего проекта:</p>
<pre>    ls /home/user/FinNewsParser/finnews.sock</pre>

