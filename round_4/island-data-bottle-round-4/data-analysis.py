import math
from collections import deque

import pandas as pd
import statsmodels.api as stat
import statsmodels.tsa.stattools as ts
import matplotlib.pyplot as plt
from statsmodels.graphics.regressionplots import abline_plot
import seaborn as sns
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


def stationarity_test(X, cutoff=0.05):
    # H_0 in adfuller is unit root exists (non-stationary)
    # We must observe significant p-value to convince ourselves that the series is stationary
    pvalue = ts.adfuller(X)[1]
    if pvalue < cutoff:
        print('p-value = ' + str(pvalue) + ' The series ' + X.name +' is likely stationary.')
    else:
        print('p-value = ' + str(pvalue) + ' The series ' + X.name +' is likely non-stationary.')


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
    fileName = "prices_round_4_day_1.csv"

    df = read_market_data(fileName)
    df.drop(df.loc[df['product'] == "BANANAS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "PEARLS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "COCONUTS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "PINA_COLADAS"].index, inplace=True)
    df.drop(df.loc[df['product'] == "BERRIES"].index, inplace=True)
    df.drop(df.loc[df['product'] == "DIVING_GEAR"].index, inplace=True)
    df.drop(df.loc[df['product'] == "DOLPHIN_SIGHTINGS"].index, inplace=True)


    print(df)
    # df_ds.drop(df_ds.loc[df_ds['product'] != "DOLPHIN_SIGHTINGS"].index, inplace=True)
    #
    # df_dg = df_dg.replace('', 0)
    # df_ds = df_ds.replace('', 0)

    # for i in range(len(df_coco.index)):
    #     print(10 * (1.9 * math.log(df_coco.iloc[i]['mid_price']) - math.log(df_pc.iloc[i]['mid_price'])))

    # df_dg.rename(columns={'mid_price': 'dg_price'}, inplace=True)
    # df_ds.rename(columns={'mid_price': 'ds_count'}, inplace=True)
    # dg_price = df_dg['dg_price']
    # ds_count = df_ds['ds_count']
    #
    # df['dg_price'] = list(dg_price)
    #
    # df['ds_count'] = list(ds_count)
    #
    # #print(df)
    #
    # results = stat.OLS(df['dg_price'], df['ds_count']).fit()
    #
    # df.plot(x='ds_count', y='dg_price', kind='scatter')
    # plt.show()
    #
    # print(results.summary())

    #abline_plot(model_results=results.fit(), ax=ax)

    #print(results.summary())

    #print(results.rvalue**2)


main()
