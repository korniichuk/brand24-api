#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# Version 0.1a3

import os
import time
from urlparse import urljoin, urlparse

from bs4 import BeautifulSoup
from fbi import getpassword
from requestium import Session

username = 'info@korniichuk.com'
passwd = getpassword('~/.key/brand24.enc')
sid = '250201232'

driver = '/usr/lib/chromium-browser/chromedriver'
s = Session(webdriver_path=driver,
            browser='chrome',
            default_timeout=15,
            webdriver_options={'arguments': ['headless']})

def download_xlsx(s, username, passwd, sid, download_path=None):
    """Export data from www.brand24.com website as xlsx file (Excel) to
       download path and return session.
    Input:
        s -- Requestium session (required |
             type: requestium.requestium.Session);
        username -- username on www.brand24.com (required | type: str);
        passwd -- password for username on www.brand24.com (required |
                  type: str);
        sid -- sid on www.brand24.com (required | type: str);
        download_path -- download path (not required | type: str).
    Output:
        s -- Requestium session (type: requestium.requestium.Session).
    """

    s = login(s, username, passwd)
    s.driver.command_executor._commands['send_command'] = ('POST',
            '/session/$sessionId/chromium/send_command')
    if download_path == None:
        download_path = os.getcwd()
    params = {'cmd': 'Page.setDownloadBehavior',
              'params': {'behavior': 'allow', 'downloadPath': download_path}}
    s.driver.execute('send_command', params)
    url = 'https://app.brand24.com/panel/results/?sid=%s' % sid
    s.driver.get(url)
    s.driver.ensure_element_by_id('results_download').click()
    return s

def get_top_10_mentions(s, username, passwd, sid):

    result = []

    s = login(s, username, passwd)
    url = 'https://app.brand24.com/panel/analysis/?sid=%s' % sid
    s.driver.get(url)
    time.sleep(5)
    soap = BeautifulSoup(s.driver.page_source, 'lxml')
    class_ = 'mention entry-from-most-popular-authors'
    divs = soap.find_all('div', class_=class_)
    for div in divs:
         result.append(parser(div))
    return result

def get_top_mention(s, username, passwd, sid):

    result = {}

    s = login(s, username, passwd)
    url = 'https://app.brand24.com/panel/analysis/?sid=%s' % sid
    s.driver.get(url)
    time.sleep(5)
    soap = BeautifulSoup(s.driver.page_source, 'lxml')
    # Parse 'text'
    class_ = 'mention most-interactive-entry-from-social-media'
    dev = soap.find('div', class_=class_)
    result = parser(dev)
    return result

def login(s, username, passwd):
    """Login to www.brand24.com with username/passwd pair and return session.
    Input:
        s -- Requestium session (required |
             type: requestium.requestium.Session);
        username -- username on www.brand24.com (required | type: str);
        passwd -- password for username on www.brand24.com (required |
                  type: str).
    Output:
        s -- Requestium session (type: requestium.requestium.Session).
    """

    url = 'https://app.brand24.com/user/login/'
    s.driver.get(url)
    s.driver.ensure_element_by_name('login').send_keys(username)
    s.driver.ensure_element_by_name('password').send_keys(passwd)
    s.driver.ensure_element_by_id('login_button').click()
    time.sleep(5)
    return s

def parser(soap):

    domain = 'https://app.brand24.com'
    result = {}

    # Parse 'text'
    text = soap.find('div', class_='mention_text').text
    result['text'] = text
    # Parse 'title'
    title = soap.find('div', class_='mention_title').a.text
    result['title'] = title
    # Parse 'avatar'
    avatar = soap.find('div', class_='mention_avatar').a.img['src']
    if not avatar.startswith('http'):
        avatar = urljoin(domain, avatar)
    result['avatar'] = avatar
    # Parse 'source'
    source = soap.find('div', class_='mention_meta') \
                 .find('span', class_='mention_source').text
    result['source'] = source
    # Parse 'url' and 'id'
    path = soap.find('div', class_='mention_meta') \
               .find('span', class_='mention_source').a['href']
    url = urljoin(domain, path)
    result['url'] = url
    id_ = urlparse(path).query.split('&')[0].replace('id=', '').strip()
    result['id'] = id_
    # Parse 'date' and 'time'
    d, t = soap.find('div', class_='mention_meta') \
               .find('span', class_='mention_date').text.split()
    result['date'] = d
    result['time'] = t
    # Parse 'influencer_score'
    spans = soap.find('div', class_='mention_meta').find_all('span')
    for span in spans:
        if 'Influencer Score:' in span.text:
            influencer_score = span.text.split()[-1].replace('/10', '')
            break
    result['influencer_score'] = influencer_score
    return result

# Example. Get top 10 mentions by influencer score from www.brand24.com website
# as Python dict
#mentions = get_top_10_mentions(s, username, passwd, sid)

# Example. Get top mention from www.brand24.com website as Python dict
#mention = get_top_mention(s, username, passwd, sid)

# Example. Export data from www.brand24.com website as xlsx file (Excel) to
# current directory
#download_xlsx(s, username, passwd, sid)

# Example. Export data from www.brand24.com website as xlsx file (Excel) to
# '/tmp' directory
#download_xlsx(s, username, passwd, sid, download_path='/tmp')
