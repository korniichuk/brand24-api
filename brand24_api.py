#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.1a22

import os
import time
from configparser import RawConfigParser
from os import getcwd, walk
from urllib.parse import urljoin, urlparse

import matplotlib.pyplot as plt
import pandas as pd
import plotly
from bs4 import BeautifulSoup
from iso3166 import countries
from requestium import Session
from wordcloud import WordCloud, STOPWORDS

from comprehend import get_language

username = 'name.surname@example.com'
passwd = 'password'
sid = '285903724'

driver = '/usr/lib/chromium-browser/chromedriver'
s = Session(webdriver_path=driver,
            browser='chrome',
            default_timeout=15,
            webdriver_options={'arguments': ['headless', 'no-sandbox']})

def clean(df):

    # Rename column names
    df = df.rename(columns={
        'ID': 'id', 'Date': 'date', 'Hrs': 'time', 'Title': 'title',
        'Content': 'text', 'Author' : 'author', 'Source': 'url',
        'Domain': 'source', 'Category': 'category', 'Country': 'country',
        'Sentiment': 'sentiment', 'Followers Count': 'followers',
        'Social Media Reach': 'reach', 'Likes': 'likes', 'Dislikes': 'dislikes',
        'Shares': 'shares', 'Comments': 'comments'})
    # Remove columns with NaN values
    df = df.dropna(axis=1, how="all")
    # Remove rows with NaN values
    df = df.dropna(axis=0, how="all")
    # Remove 'trial' row
    text = 'This is a trial version. Upgrade to access full data and reports.'
    df = df[df.id != text]
    # Select important columns
    full_columns_list = [
            'title', 'text', 'source', 'country', 'sentiment', 'followers',
            'reach', 'likes', 'dislikes', 'shares', 'comments']
    columns_list = []
    for column in full_columns_list:
        if column in df.columns:
            columns_list.append(column)
    df = df[columns_list]
    return df

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

    s.driver.command_executor._commands['send_command'] = ('POST',
            '/session/$sessionId/chromium/send_command')
    if download_path == None:
        download_path = os.getcwd()
    params = {'cmd': 'Page.setDownloadBehavior',
              'params': {'behavior': 'allow', 'downloadPath': download_path}}
    s.driver.execute('send_command', params)
    url = 'https://app.brand24.com/panel/results/?sid=%s' % sid
    if not s.driver.current_url.startswith(url):
        s.driver.get(url)
    s.driver.ensure_element_by_id('results_download').click()
    return s

def find_excel(keyword, dir_abs_path='.'):

    results = []

    if dir_abs_path == '.':
        dir_abs_path = getcwd()
    for (dirpath, dirnames, filenames) in walk(dir_abs_path):
        for filename in filenames:
            if filename.startswith(keyword):
                results.append(filename)
    result = sorted(results)[-1]
    return result

def get_top_10_hashtags(s, username, passwd, sid, mode='default',
                        output='hashtags.html'):

    result = []

    url = 'https://app.brand24.com/panel/analysis/?sid=%s' % sid
    if not s.driver.current_url.startswith(url):
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
    # Plot.ly
    if mode == 'jupyter':
        # Jupyter
        plotly.offline.init_notebook_mode(connected=True)
    df =  pd.DataFrame(result)
    columns = ['hashtag', 'mentions']
    trace = plotly.graph_objs.Table(
        header = dict(values = columns,
                   font = dict(color='white'),
                   fill = dict(color='#00a0d6'),
                   line = dict(color='white'),
                   align = ['left'] * 5),
        cells=dict(values = [df.hashtag, df.mentions],
                   font = dict(color='#1e1e1e'),
                   fill = dict(color='white'),
                   line = dict(color='white'),
                   align = ['left'] * 5))
    data = [trace]
    plotly.offline.plot(data, validate=False, filename=output)
    if mode == 'jupyter':
        # Jupyter
        plotly.offline.iplot(data, validate=False)
    return output

def get_top_10_mentions(s, username, passwd, sid, mode='default',
                        output='mentions.html'):

    result = []

    url = 'https://app.brand24.com/panel/analysis/?sid=%s' % sid
    if not s.driver.current_url.startswith(url):
        s.driver.get(url)
        time.sleep(5)
    soap = BeautifulSoup(s.driver.page_source, 'lxml')
    class_ = 'mention entry-from-most-popular-authors'
    divs = soap.find_all('div', class_=class_)
    for div in divs:
         result.append(parser(div))
    # Plot.ly
    if mode == 'jupyter':
        # Jupyter
        plotly.offline.init_notebook_mode(connected=True)
    df =  pd.DataFrame(result)
    columns = ['title', 'text', 'source', 'date', 'time']
    trace = plotly.graph_objs.Table(
        header = dict(values = columns,
                   font = dict(color='white'),
                   fill = dict(color='#00a0d6'),
                   line = dict(color='white'),
                   align = ['left'] * 5),
        cells=dict(values = [df.title, df.text, df.source, df.date, df.time],
                   font = dict(color='#1e1e1e'),
                   fill = dict(color='white'),
                   line = dict(color='white'),
                   align = ['left'] * 5))
    data = [trace]
    plotly.offline.plot(data, validate=False, filename=output)
    if mode == 'jupyter':
        # Jupyter
        plotly.offline.iplot(data, validate=False)
    return output

def get_top_mention(s, username, passwd, sid):

    result = {}

    url = 'https://app.brand24.com/panel/analysis/?sid=%s' % sid
    if not s.driver.current_url.startswith(url):
        s.driver.get(url)
        time.sleep(5)
    soap = BeautifulSoup(s.driver.page_source, 'lxml')
    class_ = 'mention most-interactive-entry-from-social-media'
    dev = soap.find('div', class_=class_)
    result = parser(dev)
    return result

def language(df, mode='default', output='language.html'):

    def detector(value):
        lang = get_language(value, language_codes)
        return lang

    language_codes = RawConfigParser()
    language_codes.read('language_codes.cfg')
    df['language'] = df.text.map(detector)
    langs = df.language[df.language.notna()].unique()
    result = []
    for i, lang in enumerate(langs):
        is_lang = df.language == lang
        mentions = df.language[is_lang].count()
        result.append({'language': lang, 'mentions': mentions})
    tmp =  pd.DataFrame(result).sort_values('mentions', ascending=False)
    # Plot.ly
    if mode == 'jupyter':
        # Jupyter
        plotly.offline.init_notebook_mode(connected=True)
    columns = ['language', 'mentions']
    trace = plotly.graph_objs.Table(
        header = dict(values = columns,
                   font = dict(color='white'),
                   fill = dict(color='#00a0d6'),
                   line = dict(color='white'),
                   align = ['left'] * 5),
        cells=dict(values = [tmp.language, tmp.mentions],
                   font = dict(color='#1e1e1e'),
                   fill = dict(color='white'),
                   line = dict(color='white'),
                   align = ['left'] * 5))
    data = [trace]
    plotly.offline.plot(data, validate=False, filename=output)
    if mode == 'jupyter':
        # Jupyter
        plotly.offline.iplot(data, validate=False)
    return output

def location(df, mode='default', output='location.html'):

    if mode == 'jupyter':
        # Jupyter
        plotly.offline.init_notebook_mode(connected=True)

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
            title = ''))]
    layout = dict(
        title = '# of mentions by country',
        geo = dict(
            showframe = False,
            showcoastlines = False,
            projection = dict(
                type = 'Miller')))
    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, validate=False, filename=output)
    if mode == 'jupyter':
        # Jupyter
        plotly.offline.iplot(fig, validate=False)
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
    if not s.driver.current_url.startswith(url):
        s.driver.get(url)
    s.driver.ensure_element_by_name('login').send_keys(username)
    s.driver.ensure_element_by_name('password').send_keys(passwd)
    s.driver.ensure_element_by_id('login_button').click()
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

# Example. Get top 10 hashtags from www.brand24.com website as Python list and
# create Plot.ly table
#hashtags = get_top_10_hashtags(s, username, passwd, sid)

# Example. Get top 10 mentions by influencer score from www.brand24.com website
# as Python dict and create Plot.ly table
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
