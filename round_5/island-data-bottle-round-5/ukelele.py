from datamodel import *
import json
from typing import Any
import statistics as s
from collections import deque


# class Logger:
#     def __init__(self) -> None:
#         self.logs = ""
#
#     def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
#         self.logs += sep.join(map(str, objects)) + end
#
#     def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
#         print(json.dumps({
#             "state": state,
#             "orders": orders,
#             "logs": self.logs,
#         }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))
#
#         self.logs = ""
#
#
# logger = Logger()


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
            self.ema = self.windowSum / self.windowSize
        if len(data) > self.windowSize:
            self.ema = (val * (self.smoothing / (1 + self.windowSize))) + self.ema * (
                1 - (self.smoothing / (1 + self.windowSize)))
            return self.ema
        self.windowSum += val
        data.append(val)
        return 0


class Trader:

    def __init__(self) -> None:
        self.ratios = []
        self.ratios_picnic = []
        self.sightings = []
        self.enter_time = 0
        self.ema9 = ExponentialMovingAverage(9)
        self.ema12 = ExponentialMovingAverage(12)
        self.ema26 = ExponentialMovingAverage(26)
        self.signal = 0
        self.position = 0

    def update(self, count):
        self.sightings.append(count)
        if len(self.sightings) > 15:
            self.sightings.pop(0)

    def zscore(self, series):
        if len(series) < 10:
            return 0

        return (series[-1] - s.mean(series)) / s.stdev(series)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        orders_ukulele: list[Order] = []
        keep_buying = False
        keep_selling = False

        for product in state.order_depths.keys():
            if product == "UKULELE":
                ukelele_trades = state.market_trades.get("UKULELE", [])

                ukulele_order_depth: OrderDepth = state.order_depths[product]
                ukulele_best_ask = min(ukulele_order_depth.sell_orders.keys())
                # ukelele_worst_ask = max(ukulele_order_depth.sell_orders.keys())
                ukulele_best_bid = max(ukulele_order_depth.buy_orders.keys())
                # ukelele_worst_bid = min(ukulele_order_depth.buy_orders.keys())
                ukulele_mid_price = (ukulele_best_ask + ukulele_best_bid) / 2

                if product in state.position.keys():
                    ukulele_position = state.position[product]
                else:
                    ukulele_position = 0

                ukulele_buy = 70 - ukulele_position
                ukulele_sell = 70 - (-1 * ukulele_position)

                # print(len(ukelele_trades))

                for trade in ukelele_trades:
                    if trade.timestamp == state.timestamp - 100:
                        if trade.buyer == "Olivia":
                            # print("OLIVIA BUY")
                            # # print(state.timestamp)
                            # print("OLIVIA BUY PRICE: " + str(trade.price))
                            # print("UKELELE MID PRICE: " +
                            #       str(ukulele_mid_price))
                            keep_buying = True
                            keep_selling = False
                        if trade.seller == "Olivia":
                            # print(state.timestamp)
                            # print("OLIVIA SELL")
                            # print("OLIVIA SELL PRICE: " + str(trade.price))
                            # print("UKELELE MID PRICE: " +
                            #       str(ukulele_mid_price))
                            # orders_ukulele.append(
                            #     Order("UKULELE", ukulele_mid_price-1, -ukulele_sell))
                            keep_selling = True
                            keep_buying = False

        if keep_buying:
            orders_ukulele.append(
                Order("UKULELE", ukulele_mid_price + 1, ukulele_buy))

        if keep_selling:
            orders_ukulele.append(
                Order("UKULELE", ukulele_mid_price - 1, -ukulele_sell))

        result['UKULELE'] = orders_ukulele
        #logger.flush(state, result)
        return result
