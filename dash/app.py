#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.1a2

import re

import dash
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import iso3166
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

df = pd.read_pickle('brand24.pkl')

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
        label='sentiment analysis',
        id = 'sentiment')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H3('Brand Monitoring', style={'textAlign': 'center'}),
    html.Div(children=[
        location(df),
        sentiment(df),
        language(df)
    ], style={'columnCount': 1}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
