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
        self.keep_buying_ukuleles = False
        self.keep_selling_ukuleles = False
        self.keep_buying_berries = False
        self.keep_selling_berries = False

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
        orders_berries: list[Order] = []

        for product in state.order_depths.keys():
            if product == "UKULELE":
                ukulele_order_depth: OrderDepth = state.order_depths[product]
                ukulele_best_ask = min(ukulele_order_depth.sell_orders.keys())
                ukulele_best_bid = max(ukulele_order_depth.buy_orders.keys())
                ukulele_mid_price = (ukulele_best_ask + ukulele_best_bid) / 2

                if product in state.position.keys():
                    ukulele_position = state.position[product]
                else:
                    ukulele_position = 0

                ukulele_buy = 70 - ukulele_position
                ukulele_sell = 70 - (-1 * ukulele_position)

                ukelele_trades = state.market_trades.get("UKULELE", [])

                for trade in ukelele_trades:
                    if trade.timestamp == state.timestamp - 100:
                        if trade.buyer == "Olivia":
                            # print("OLIVIA BUY")
                            # # print(state.timestamp)
                            # print("OLIVIA BUY PRICE: " + str(trade.price))
                            # print("UKELELE MID PRICE: " +
                            #       str(ukulele_mid_price))
                            self.keep_buying_ukuleles = True
                            self.keep_selling_ukuleles = False
                        if trade.seller == "Olivia":
                            # print(state.timestamp)
                            # print("OLIVIA SELL")
                            # print("OLIVIA SELL PRICE: " + str(trade.price))
                            # print("UKELELE MID PRICE: " +
                            #       str(ukulele_mid_price))
                            # orders_ukulele.append(
                            #     Order("UKULELE", ukulele_mid_price-1, -ukulele_sell))
                            self.keep_selling_ukuleles = True
                            self.keep_buying_ukuleles = False

            if product == "BERRIES":
                sell_timestamp = 350000
                buy_timestamp = 500000
                close = 700000
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                berries_buy = 250 - current_position
                berries_sell = 250 - (-1 * current_position)

                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                berries_mid_price = (best_ask + best_bid) / 2

                sell_price = best_ask - 1
                bid_price = best_bid + 1

                if sell_price < bid_price:
                    sell_price = berries_mid_price
                    bid_price = berries_mid_price

                berries_trades = state.market_trades.get("BERRIES", [])

                for trade in berries_trades:
                    if trade.timestamp == state.timestamp - 100:
                        if trade.buyer == "Olivia":
                            self.keep_buying_berries = True
                            self.keep_selling_berries = False
                        if trade.seller == "Olivia":
                            self.keep_selling_berries = True
                            self.keep_buying_berries = False

                if self.keep_buying_berries is False and self.keep_selling_berries is False:
                    if state.timestamp >= sell_timestamp and state.timestamp < buy_timestamp:  # buy
                        orders_berries.append(
                            Order(product, best_ask, berries_buy))
                    elif state.timestamp >= buy_timestamp and state.timestamp < close:  # sell
                        orders_berries.append(
                            Order(product, best_bid, -berries_sell))
                    elif state.timestamp == close:  # buy
                        orders_berries.append(
                            Order(product, best_ask, current_position))
                    else:  # market make
                        orders_berries.append(
                            Order(product, sell_price, -berries_sell))
                        orders_berries.append(
                            Order(product, bid_price, berries_buy))

        if self.keep_buying_ukuleles:
            orders_ukulele.append(
                Order("UKULELE", ukulele_mid_price + 1, ukulele_buy))

        if self.keep_selling_ukuleles:
            orders_ukulele.append(
                Order("UKULELE", ukulele_mid_price - 1, -ukulele_sell))

        if self.keep_buying_berries:
            orders_berries.append(
                Order("BERRIES", berries_mid_price+1, berries_buy))
        if self.keep_selling_berries:
            orders_berries.append(
                Order("BERRIES", berries_mid_price-1, -berries_sell))

        # result['UKULELE'] = orders_ukulele
        result["BERRIES"] = orders_berries

        # logger.flush(state, result)
        return result
