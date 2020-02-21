#!/usr/bin/env python3

# feed2email.py
# (c) Aleksander Alekseev 2016
# http://eax.me/

import feedparser

from contextlib import contextmanager
import re

processed_urls_fname = "processed-urls.txt"
feed_list_fname = "feed-list.txt"
# change to True before first run or you will receive A LOT of emails
# then change back to False
fake_send = False
sleep_time = 60 * 5  # seconds
net_timeout = 10  # seconds


# FUNCS



def file_to_list(fname):
    rslt = []
    with open(fname, "r") as f:
        rslt = [x for x in f.read().split("\n") if x.strip() != ""]
    return rslt


# MAIN


feed_list = ['https://www.finam.ru/analysis/nslent/rsspoint']
# filter comments
feed_list = [x for x in feed_list if not re.match("(?i)\s*#", x)]
keep_urls = 100 * len(feed_list)
processed_urls = []


print("Processing {} feeds...".format(len(feed_list)))

for feed in feed_list:
    print(feed)
    f = feedparser.parse(feed)

    feed_title = f['feed'].get('title', '(NO TITLE)')
    feed_link = f['feed'].get('link', '(NO LINK)')

    for entry in f['entries']:
        if entry['link'] in processed_urls:
            continue

        subject = "{title} | {feed_title} ({feed_link})".format(
            title=entry.get('title', '(NO TITLE'),
            feed_title=feed_title,
            feed_link=feed_link
        )
        print(subject)
        summary = entry.get('summary', '(NO SUMMARY)')
        body = "{summary}\n\n{link}\n\nSource feed: {feed}".format(
            summary=summary[:256],
            link=entry['link'],
            feed=feed
        )
        print(body)
        print("-------")

        processed_urls = [entry['link']] + processed_urls

with open(processed_urls_fname, "w") as urls_file:
    urls_file.write("\n".join(processed_urls[:keep_urls]))

