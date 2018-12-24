#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.1a9

import os
import time
from configparser import RawConfigParser
from urllib.parse import urljoin, urlparse

import matplotlib.pyplot as plt
import plotly
from bs4 import BeautifulSoup
from iso3166 import countries
from requestium import Session
from wordcloud import WordCloud, STOPWORDS

from comprehend import get_language

username = 'name.surname@example.com'
passwd = 'password'
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

def get_top_hashtags(s, username, passwd, sid):

    result = []

    s = login(s, username, passwd)
    url = 'https://app.brand24.com/panel/analysis/?sid=%s' % sid
    s.driver.get(url)
    time.sleep(5)
    soap = BeautifulSoup(s.driver.page_source, 'lxml')
    divs = soap.find('div', class_='trending-hashtags__column-box') \
               .find_all('div', class_='trending-hashtags-entry sources_entry')
    for div in divs:
        hashtag = div.a.text.strip()
        mentions = div.find('strong', class_="sources_entry-list-value") \
                      .text.strip()
        result.append({'hashtag': hashtag, 'mentions': mentions})
    return result

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
    class_ = 'mention most-interactive-entry-from-social-media'
    dev = soap.find('div', class_=class_)
    result = parser(dev)
    return result

def language_analysis(df):

    def detector(value):
        language = get_language(value, language_codes)
        return language

    result = {}

    language_codes = RawConfigParser()
    language_codes.read('language_codes.cfg')
    df['language'] = df.text.map(detector)
    languages = df.language[df.language.notna()].unique()
    total = df.language[df.language.notna()].count()
    result['total'] = total
    for language in languages:
        is_language = df.language == language
        num = df.language[is_language].count()
        result[language] = num
    return result

def location(df, output='location.html'):

    # Jupyter
    #plotly.offline.init_notebook_mode(connected=True)

    mentions = {}

    for i, country in enumerate(countries):
        is_code = df.country == country.alpha2
        num = df.country[is_code].count()
        mentions[i] = {'country': country.name, 'code': country.alpha2,
                       'mentions': num}
    out = pd.DataFrame(mentions).T[['country', 'code', 'mentions']] \
                                .sort_values('country')
    data = [dict(
        type = 'choropleth',
        locations = out.country,
        locationmode = 'country names',
        z = out.mentions,
        autocolorscale = True,
        reversescale = False,
        marker = dict(
            line = dict(
                color = 'rgb(128, 128, 128)',
                width = 0.5)),
        colorbar = dict(
            title = '# of<br>mentions'))]
    layout = dict(
        title = '# of mentions by country',
        geo = dict(
            showframe = False,
            showcoastlines = False,
            projection = dict(
                type = 'Miller')))
    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, validate=False, filename=output)
    # Jupyter
    #plotly.offline.iplot(fig, validate=False)
    return output

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

def sentiment_analysis(df):

    result = {}

    sentiments = (-1, 0, 1)
    total = df.sentiment[df.sentiment.isin(sentiments)].count()
    result['total'] = total
    is_negative = df.sentiment == -1
    num = df.sentiment[is_negative].count()
    result['negative'] = num
    is_neutral = df.sentiment == 0
    num = df.sentiment[is_neutral].count()
    result['neutral'] = num
    is_positive = df.sentiment == 1
    num = df.sentiment[is_positive].count()
    result['positive'] = num
    return result

def wordcloud(df, background_color='white', output='wordcloud.png'):

    text = ''

    # Prepare 'text' var
    for i, v in enumerate(df.text):
        if i != 0:
            text += ' '
        text += str(v)
    # Remove URLs and nicknames
    # TODO
    wordcloud = WordCloud(
        width = 3000,
        height = 2000,
        background_color = background_color,
        stopwords = STOPWORDS).generate(text)
    fig = plt.figure(
        figsize = (40, 30),
        facecolor = background_color,
        edgecolor = background_color)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    plt.savefig(output)
    return output

# Example. Export data from www.brand24.com website as xlsx file (Excel) to
# current directory
#download_xlsx(s, username, passwd, sid)

# Example. Export data from www.brand24.com website as xlsx file (Excel) to
# '/tmp' directory
#download_xlsx(s, username, passwd, sid, download_path='/tmp')

# Example. Get top hashtags from www.brand24.com website as Python list
#hashtags = get_top_hashtags(s, username, passwd, sid)

# Example. Get top 10 mentions by influencer score from www.brand24.com website
# as Python dict
#mentions = get_top_10_mentions(s, username, passwd, sid)

# Example. Get top mention from www.brand24.com website as Python dict
#mention = get_top_mention(s, username, passwd, sid)

# Example. Create choropleth map and save as location.html file
#location(df)

# Example. Create choropleth map and save as example.html file
#location(df, output='example.html')

# Example. Create wordcloud with default white background and save as
# wordcloud.png file
#wordcloud(df)

# Example. Create wordcloud with black background and save as
# example.png file
#wordcloud(df, background_color='black', output='example.png')
