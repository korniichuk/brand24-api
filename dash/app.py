#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.1a8

import re
from collections import Counter

import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import iso3166
import pandas as pd
import plotly.graph_objs as go
from sklearn import preprocessing

df = pd.read_pickle('brand24.pkl')

def hashtags(df):

    result = []
    for i, v in enumerate(df.text[df.text.notna()]):
        hashtags = re.findall(r'\B#\w*[a-zA-Z]+\w*', v)
        hashtags = list(set(hashtags))
        result.extend(hashtags)
    tmp = pd.DataFrame.from_dict(Counter(result), orient='index').reset_index()
    tmp = tmp.rename(columns={'index':'hashtag', 0:'mentions'})
    tmp = tmp.sort_values('mentions', ascending=False)
    data = [go.Table(
        header = dict(
            values = ['hashtag', 'mentions'],
            fill = dict(color='#00a0d6'),
            font = dict(color='white'),
            line = dict(color='white'),
            align = ['left'] * 5),
        cells=dict(values = [tmp.hashtag, tmp.mentions],
            fill = dict(color='white'),
            font = dict(color='#1e1e1e'),
            line = dict(color='white'),
            align = ['left'] * 5))]
    layout = dict(
        title = '# of mentions by hashtag')
    return dcc.Graph(
        figure=go.Figure(data=data, layout=layout), id='hashtags')

def language(df):

    langs = df.language[df.language.notna()].unique()
    result = []
    for i, lang in enumerate(langs):
        is_lang = df.language == lang
        mentions = df.language[is_lang].count()
        result.append({'language': lang, 'mentions': mentions})
    tmp = pd.DataFrame(result).sort_values('mentions', ascending=False)
    data = [go.Table(
        header = dict(
            values = ['language', 'mentions'],
            fill = dict(color='#00a0d6'),
            font = dict(color='white'),
            line = dict(color='white'),
            align = ['left'] * 5),
        cells=dict(values = [tmp.language, tmp.mentions],
            fill = dict(color='white'),
            font = dict(color='#1e1e1e'),
            line = dict(color='white'),
            align = ['left'] * 5))]
    layout = dict(
        title = '# of mentions by language')
    return dcc.Graph(
        figure=go.Figure(data=data, layout=layout), id='language')

def location(df):

    result = []
    for i, country in enumerate(iso3166.countries):
        is_code = df.country == country.alpha2
        num = df.country[is_code].count()
        result.append({'country': country.name, 'code': country.alpha2,
                       'mentions': num})
    tmp =  pd.DataFrame(result)
    data = [dict(
        type = 'choropleth',
        locations = tmp.country,
        locationmode = 'country names',
        z = tmp.mentions,
        colorscale = [[0, 'white'], [1, '#00a0d6']],
        reversescale = False,
        marker = dict(
            line = dict(
                color = '#757575',
                width = 0.5)),
        colorbar = dict(
            title = '',
            thickness = 15,
            len = 0.872,
            outlinewidth = 0,
            tickfont = dict(
                color = '#1e1e1e')),
        hoverlabel = dict(
            bgcolor = '#00a0d6',
            bordercolor = 'white',
            font = dict(
                color = 'white')))]
    layout = dict(
        title = '# of mentions by country',
        geo = dict(
            showframe = False,
            showcoastlines = False,
            projection = dict(
                type = 'miller')))
    return dcc.Graph(
        figure=go.Figure(data=data, layout=layout), id='location')

def mentions(df):

    # Normalize
    tmp = df.fillna(0)
    columns = ['reach', 'followers',  'shares', 'likes', 'dislikes', 'comments']
    x = tmp[columns].values # returns a numpy array
    min_max_scaler = preprocessing.MinMaxScaler()
    x_scaled = min_max_scaler.fit_transform(x)
    tmp[columns] = pd.DataFrame(x_scaled)

    # Calcl impact score of mentions
    tmp['impact'] = (tmp.reach + tmp.followers) * 0.3 + \
                    tmp.sentiment.abs() * 0.24 + tmp.shares * 0.1 + \
                    (tmp.likes + tmp.dislikes + tmp.comments) * 0.02

    tmp = tmp.sort_values('impact', ascending=False).head(10)
    data = [go.Table(
        header = dict(
            values = ['title', 'text', 'source', 'date'],
            fill = dict(color='#00a0d6'),
            font = dict(color='white'),
            line = dict(color='white'),
            align = ['left'] * 5),
        cells=dict(values = [tmp.title, tmp.text, tmp.source, tmp.date],
            fill = dict(color='white'),
            font = dict(color='#1e1e1e'),
            line = dict(color='white'),
            align = ['left'] * 5))]
    layout = dict(
        title = 'top 10 mentions')
    return dcc.Graph(
        figure=go.Figure(data=data, layout=layout), id='mentions')

def sentiment(df):

    value = df.sentiment[df.sentiment != 0].mean()
    value = round(value, 1)
    value = float("%.1f" % value)
    return daq.Gauge(
        min=-1,
        max=1,
        value=value,
        showCurrentValue=True,
        scale={'start': -1, 'interval': 0.5, 'labelInterval': 0.5},
        color='#00a0d6',
        label=' ',
        size = 200,
        id='sentiment')

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H3('Brand Monitoring', style={'textAlign': 'center'}, id='header'),
    html.Div([
        html.Div([
            location(df),
            language(df),
        ], style={'columnCount': 2, 'width': '66.7%', 'float': 'left'}),
        html.Div([
            html.Br(style={'lineHeight': '200%'}),
            html.Div('sentiment analysis',
                     style={'textAlign': 'center', 'fontSize': '17px'}),
            html.Br(style={'lineHeight': '350%'}),
            sentiment(df)
        ], style={'width': '33.3%', 'float': 'left'})
    ]),
    html.Div([
        html.Div([
            mentions(df)
        ], style={'width': '66.7%', 'float': 'left'}),
        html.Div([
            hashtags(df)
        ], style={'width': '33.3%', 'float': 'left'}),
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)
