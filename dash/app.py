#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Version 0.1a1

import dash
import dash_core_components as dcc
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
            font = dict(color='white'),
            fill = dict(color='#00a0d6'),
            line = dict(color='white'),
            align = ['left'] * 5),
        cells=dict(values = [tmp.language, tmp.mentions],
            font = dict(color='#1e1e1e'),
            fill = dict(color='white'),
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
                type = 'miller')))
    return dcc.Graph(
        figure=go.Figure(data=data, layout=layout), id='location')

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H3('Brand Monitoring', style={'textAlign': 'center'}),
    html.Div(children=[
        location(df),
        language(df)
    ], style={'columnCount': 2}
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
