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
        for product in state.order_depths.keys():

            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                acceptable_price = 10000

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 20 - current_position
                can_sell = 20 - (-1 * current_position)

                still_buying = True
                still_selling = True

                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

                while still_buying:
                    if len(order_depth.sell_orders) > 0:
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = abs(order_depth.sell_orders[best_ask])

                        if can_buy <= 0:
                            still_buying = False
                        elif best_ask < acceptable_price:
                            quantity = min(can_buy, best_ask_volume)
                            orders.append(Order(product, best_ask, quantity))

                            order_depth.sell_orders.pop(best_ask)
                            can_buy -= quantity
                        elif best_ask == acceptable_price:
                            if can_buy > 20:
                                quantity = min(can_buy - 20, best_ask_volume)

                                orders.append(Order(product, best_ask, quantity))

                                order_depth.sell_orders.pop(best_ask)
                                can_buy -= quantity
                            else:
                                still_buying = False
                        else:
                            orders.append(Order(product, min(mid_price - 3, 9999), can_buy))
                            still_buying = False

                    else:
                        still_buying = False

                while still_selling:
                    if len(order_depth.buy_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = abs(order_depth.buy_orders[best_bid])
                        if can_sell <= 0:
                            still_selling = False
                        elif best_bid > acceptable_price:
                            quantity = min(can_sell, best_bid_volume)
                            orders.append(Order(product, best_bid, -quantity))

                            order_depth.buy_orders.pop(best_bid)
                            can_sell -= quantity
                        elif best_bid == acceptable_price:
                            if can_sell > 20:
                                quantity = min(can_sell - 20, best_bid_volume)
                                orders.append(Order(product, best_bid, -quantity))

                                order_depth.buy_orders.pop(best_bid)
                                can_sell -= quantity
                            else:
                                still_selling = False
                        else:
                            orders.append(Order(product, max(mid_price + 3, 10001), -can_sell))
                            still_selling = False
                    else:
                        still_selling = False

                result[product] = orders

        # logger.flush(state, result)
        return result