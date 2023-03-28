import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly.express as px
import matplotlib.pyplot as plt


def read_market_data(fileName):
    df = pd.read_csv(fileName).fillna("")
    cols = df.columns.tolist()[0].split(';')
    fin = pd.DataFrame(df.iloc[:, 0].apply(lambda x: x.split(';')).values.tolist(), columns=cols)
    to_float_cols = ['day', 'timestamp', 'bid_price_1', 'bid_volume_1', 'bid_price_2', 'bid_volume_2', 'bid_price_3',
                     'bid_volume_3', 'ask_price_1', 'ask_volume_1', 'ask_price_2', 'ask_volume_2', 'ask_price_3',
                     'ask_volume_3', 'mid_price', 'profit_and_loss']
    fin[to_float_cols] = fin[to_float_cols].applymap(lambda x: float(x) if x != '' else '')
    return fin


def split_data_by_product(df):
    markets = dict()
    products = df['product'].unique().tolist()
    for prod in products:
        markets[prod] = df[df['product'] == prod]
    return markets


def SMA(df):
    return df.rolling(window=15)['mid_price'].mean()


def BolBand(df):
    return df.rolling(window=15)['mid_price'].std()


def rescale(x):
    if x < 5000:
        return 20 * x + 37000
    else:
        return x


def graph_bolbands(df):
    df['MA'] = SMA(df)
    df['SD'] = BolBand(df)
    df['BOLU'] = df['MA'] + 3 * BolBand(df)
    df['BOLD'] = df['MA'] - 3 * BolBand(df)

    for i in range(len(df.index)):
        if (df.iloc[i]['mid_price'] > df.iloc[i]['BOLU']) and (
                df.iloc[i]['mid_price'] - df.iloc[i - 1]['mid_price'] > 1):
            print(f"{df.iloc[i]['timestamp']}, {(df.iloc[i]['mid_price'] - df.iloc[i]['MA']) / df.iloc[i]['SD']} std")
        elif (df.iloc[i]['mid_price'] < df.iloc[i]['BOLD']) and (
                df.iloc[i - 1]['mid_price'] - df.iloc[i]['mid_price'] > 1):
            print(f"{df.iloc[i]['timestamp']}, {(df.iloc[i]['mid_price'] - df.iloc[i]['MA']) / df.iloc[i]['SD']} std")
    df = df.dropna()

    fig = go.Figure()
    fig.add_trace(go.Scatter(name='mid_price', x=df['timestamp'], y=df['mid_price']))
    # fig.add_trace(go.Scatter(name='MA', x=df['timestamp'], y=df['MA']))
    fig.add_trace(go.Scatter(name='BOLD', x=df['timestamp'], y=df['BOLD']))
    fig.add_trace(go.Scatter(name='BOLU', x=df['timestamp'], y=df['BOLU']))
    fig.show()


def rescaled_graph(df):
    df['mid_price'] = df['mid_price'].map(rescale)
    fig = px.line(df, x='timestamp', y='mid_price', color='product', line_group='product', hover_name='product')
    fig.show()

def main():
    fileName = "prices_round_4_day_4.csv"

    df = read_market_data(fileName)
    df.drop(df.loc[df['product'] == "BANANAS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "PEARLS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "COCONUTS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "PINA_COLADAS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "BERRIES"].index, inplace=True)
    df.drop(df.loc[df['product'] == "DIVING_GEAR"].index, inplace=True)
    # df.drop(df.loc[df['product'] == "DOLPHIN_SIGHTINGS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "PICNIC_BASKET"].index, inplace=True)
    df.drop(df.loc[df['product'] == "DIP"].index, inplace=True)
    df.drop(df.loc[df['product'] == "BAGUETTE"].index, inplace=True)
    df.drop(df.loc[df['product'] == "UKULELE"].index, inplace=True)

    # Ouputs BolBands

    # graph_bolbands(df)

    # Superimposed both diving gear and dolphin sightings on each other

    rescaled_graph(df)

#
main()
