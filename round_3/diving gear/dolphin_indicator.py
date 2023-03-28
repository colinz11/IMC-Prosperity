import json
from typing import Any
from datamodel import *
import statistics as s
import math
from collections import deque


class ExponentialMovingAverage:
        def __init__(self, size, smoothing=2):
            """
            Initialize your data structure here.
            :type size: int
            """
            self.windowSize = size
            self.windowSum = 0
            self.data = deque([])
            self.smoothing = smoothing
            self.ema = 0

        def next(self, val):
            """
            :type val: int
            :rtype: float
            """
            data = self.data

            if len(data) == self.windowSize:
                self.ema = self.windowSum/self.windowSize
            if len(data) > self.windowSize:
                self.ema = (val * (self.smoothing / (1 + self.windowSize))) + self.ema * (1 - (self.smoothing / (1 + self.windowSize)))
                return self.ema
            self.windowSum += val
            data.append(val)
            return 0

class Trader:

    def __init__(self) -> None:
        self.ema9 = ExponentialMovingAverage(9)
        self.ema12 = ExponentialMovingAverage(12)
        self.ema26 = ExponentialMovingAverage(26)
        self.signal = 0
        self.prev_dolphins = 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        results = {}

        for product in state.order_depths.keys():
            if state.timestamp < 2600:
                break

            if product == 'DIVING_GEAR':
                orders: list[Order] = []

                order_depth: OrderDepth = state.order_depths[product]

                best_ask = min(order_depth.sell_orders.keys()) 
                best_bid = max(order_depth.buy_orders.keys()) 
                mid_price = (best_ask + best_bid) / 2

                ema_12 = self.ema12.next(mid_price)
                ema_26 = self.ema26.next(mid_price)
                macd = ema_12-ema_26
                signal_line = self.ema9.next(macd)

                position_limit = 50

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                max_buy = position_limit - current_position
                max_sell = position_limit + current_position

                #print(macd)
                #print(signal_line)
                #print(self.signal)


                if macd > 0 and macd > signal_line:
                    self.signal = 1
                elif macd < 0 and macd < signal_line:
                    self.signal = -1
                else:
                    self.signal = 0
                #print(state)
                num_dolphins = state.observations['DOLPHIN_SIGHTINGS']
                if self.prev_dolphins == 0:
                    dolphin_delta = 0
                else:
                    dolphin_delta = num_dolphins - self.prev_dolphins
                self.prev_dolphins = num_dolphins

                if dolphin_delta > 1: #buy
                    orders.append(Order(product, mid_price + 1, max_buy)) 
                elif dolphin_delta < 1: #sell
                    orders.append(Order(product, mid_price - 1, -max_sell))
            
                results[product] = orders
                print(current_position)
        #logger.flush(state, results)
        return results