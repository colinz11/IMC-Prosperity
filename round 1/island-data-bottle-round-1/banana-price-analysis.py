import math
from collections import deque

import pandas as pd
import numpy as np
from math import sqrt


class RollingStatistic:
    def __init__(self, window_size, average, variance):
        self.N = window_size
        self.average = average
        self.variance = variance
        self.stddev = sqrt(variance)
        self.data = deque([])

    def update(self, new):
        data = self.data
        old = 0
        if len(data) >= self.N:
            old = data.popleft()
        data.append(new)

        oldavg = self.average
        newavg = oldavg + (new - old)/self.N
        self.average = newavg
        self.variance += (new-old)*(new-newavg+old-oldavg)/(self.N-1)
        self.stddev = sqrt(self.variance)
        if len(data) < self.N:
            return 0
        return self.stddev

def read_market_data(fileName):
    df = pd.read_csv(fileName).fillna("")
    cols = df.columns.tolist()[0].split(';')
    fin = pd.DataFrame(df.iloc[:, 0].apply(lambda x: x.split(';')).values.tolist(), columns=cols)
    to_float_cols = ['day', 'timestamp', 'bid_price_1', 'bid_volume_1', 'bid_price_2', 'bid_volume_2', 'bid_price_3',
                     'bid_volume_3', 'ask_price_1', 'ask_volume_1', 'ask_price_2', 'ask_volume_2', 'ask_price_3',
                     'ask_volume_3', 'mid_price', 'profit_and_loss']
    fin[to_float_cols] = fin[to_float_cols].applymap(lambda x: float(x) if x != '' else '')
    return fin


def main():
    fileName = "prices_round_1_day_0.csv"
    product = "PEARLS"

    df = read_market_data(fileName)
    # print(df['product'])
    df.drop(df.loc[df['product'] == product].index, inplace=True)

    totalSum = 0
    changeSum = 0
    varianceSum = 0

    for i in range(len(df.index) - 1):
        totalSum += df.iloc[i]['mid_price']

    mid_price_average = totalSum/len(df.index)
    print(mid_price_average)

    for i in range(len(df.index) - 1):
        varianceSum += (df.iloc[i]['mid_price'] - mid_price_average)**2

    variance = varianceSum/(len(df.index) - 1)
    stddev = variance**(1/2)
    print(stddev)

    for i in range(len(df.index) - 1):
        changeSum += df.iloc[i + 1]['mid_price'] - df.iloc[i]['mid_price']

    net_average = changeSum / len(df.index)
    print(net_average)


main()
