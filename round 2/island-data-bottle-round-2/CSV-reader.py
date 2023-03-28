import pandas as pd
import numpy as np
import plotly.graph_objs as go


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


def main():
    fileName = "../../round 4/island-data-bottle-round-4/prices_round_2_day_-1.csv"
    product = "PINA_COLADAS"

    df_both = read_market_data(fileName)
    df_single = split_data_by_product(df_both)
    df = df_single[product]
    df.to_csv('pc_prices.csv')

#    fig = go.Figure()
#    fig.add_trace(go.Scatter(name="profit & loss", x=df["timestamp"], y=df["profit_and_loss"]))
    # fig.add_trace(go.Scatter(name="best ask", x=df["timestamp"], y=df["ask_price_1"]))

#    fig.show()


main()
