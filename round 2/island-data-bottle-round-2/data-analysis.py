import math
from collections import deque

import pandas as pd
import numpy as np
from math import sqrt


def read_market_data(fileName):
    df = pd.read_csv(fileName).fillna(0.0)
    cols = df.columns.tolist()[0].split(';')
    fin = pd.DataFrame(df.iloc[:, 0].apply(lambda x: x.split(';')).values.tolist(), columns=cols)
    to_float_cols = ['day', 'timestamp', 'bid_price_1', 'bid_volume_1', 'bid_price_2', 'bid_volume_2', 'bid_price_3',
                     'bid_volume_3', 'ask_price_1', 'ask_volume_1', 'ask_price_2', 'ask_volume_2', 'ask_price_3',
                     'ask_volume_3', 'mid_price', 'profit_and_loss']
    fin[to_float_cols] = fin[to_float_cols].applymap(lambda x: float(x) if x != '' else '')
    return fin


def get_average(b1, b2, b3):
    a1 = 1
    a2 = 1
    a3 = 1
    if b1 == 0:
        a1 = 0
    if b2 == 0:
        a2 = 0
    if b3 == 0:
        a3 = 0
    divisor = a1 + a2 + a3
    return (b1 + b2 + b3) / divisor


def main():
    fileName = "prices_round_2_day_-1.csv"
    product = "COCONUTS"

    df = read_market_data(fileName)
    # print(df['product'])
    df.drop(df.loc[df['product'] != product].index, inplace=True)
    df = df.replace('', 0)

    bidSum = 0
    askSum = 0

    for i in range(len(df.index)):
        bidSpread = get_average(float(df.iloc[i]['bid_price_1']), float(df.iloc[i]['bid_price_2']),
                                float(df.iloc[i]['bid_price_3'])) - float(df.iloc[i]['mid_price'])
        bidSum += bidSpread
    print(f"Average mid-bid minus mid-price {bidSum / len(df.index)}")

    for i in range(len(df.index)):
        askSpread = get_average(float(df.iloc[i]['ask_price_1']), float(df.iloc[i]['ask_price_2']),
                                float(df.iloc[i]['ask_price_3'])) - float(df.iloc[i]['mid_price'])
        askSum += askSpread
    print(f"Average mid-ask minus mid-price {askSum / len(df.index)}")


#    totalSum = 0
#    changeSum = 0
#    varianceSum = 0

#    for i in range(len(df.index) - 1):
#        totalSum += df.iloc[i]['mid_price']

#    mid_price_average = totalSum/len(df.index)
#    print(mid_price_average)

#    for i in range(len(df.index) - 1):
#       varianceSum += (df.iloc[i]['mid_price'] - mid_price_average)**2

#    variance = varianceSum/(len(df.index) - 1)
#    stddev = variance**(1/2)
#    print(stddev)

#    for i in range(len(df.index) - 1):
#        changeSum += df.iloc[i + 1]['mid_price'] - df.iloc[i]['mid_price']

#    net_average = changeSum / len(df.index)
#    print(net_average)


main()
