<h1>Finance News Parser</h1>

Файл зависимостей для разработчика: <b>requirements_dev.txt</b>

<br>
<p>Файл настроек подключения к MySQL <b>mysql.cnf</b>:</p> 
<p># mysql.cnf</p>
<p>[client]</p>
<p>host = 127.0.0.1</p>
<p>database = finnews</p>
<p>user = ***</p>
<p>password = ***</p>
<p>default-character-set = utf8</p>

<br>
<p>Файл с логинами/паролями <b>news_parser/my_settings.py</b>:</p>

SECRET_KEY = ''

EMAIL_HOST_USER = ''

EMAIL_HOST_PASSWORD = ''

EMAIL_PORT = 587

EMAIL_USE_TLS = True

<br>
<p>Файл с настройками Production <b>news_parser/production_settings.py</b>:</p>
ALLOWED_HOSTS = ['magv.pythonanywhere.com', ]

DOMAIN_NAME = 'https://magv.pythonanywhere.com:443'

Ограничения по SMTP:

https://help.pythonanywhere.com/pages/SMTPForFreeUsers/

Первоначальное заполнение сведениями о сайтах:

python manage.py init_sites


<b>Загрузка стоп-слов:</b>

import nltk

nltk.download('stopwords')

<b>Обновить русский морфологический словарь:</b>

pip install -U pymorphy2-dicts-ru

<h2>Установка geckodriver под Ubuntu</h2>
<li>Заходим на сайт https://github.com/mozilla/geckodriver/releases/, проверяем ссылку на последнюю версию архива</li>
<li>Скачиваем архив:
wget https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz
</li>
<li>
Вытаскиваем файл из архива: 
tar -xvzf geckodriver*
</li>
<li>
Даем нужные права драйверу: 
sudo chmod +x geckodriver
</li>
<li>
Отправляем драйвер в папку где его будет искать Selenium: 
sudo mv geckodriver /usr/local/bin/
</li>