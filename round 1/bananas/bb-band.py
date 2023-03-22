from datamodel import *
from typing import *
from collections import deque
from math import sqrt

class Logger:
    def __init__(self) -> None:
        self.logs = ""

    def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
        self.logs += sep.join(map(str, objects)) + end

    def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
        print(json.dumps({
            "state": state,
            "orders": orders,
            "logs": self.logs,
        }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))

        self.logs = ""

logger = Logger()

class MovingAverage:
        def __init__(self, size):
            """
            Initialize your data structure here.
            :type size: int
            """
            self.windowSize = size
            self.windowSum = 0.0
            self.data = deque([])

        def next(self, val):
            """
            :type val: int
            :rtype: float
            """
            self.windowSum += val
            data = self.data

            leftTop = 0
            if len(data) >= self.windowSize:
                leftTop = data.popleft()
            data.append(val)

            self.windowSum -= leftTop
            if len(data) < self.windowSize:
                return self.windowSum / len(data)
            return self.windowSum / self.windowSize


class RollingStatistic():
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

class Trader:
    
    def __init__(self) -> None:
        self.rs = RollingStatistic(20, 0, 0 )
        self.ma20 = MovingAverage(20)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        results = {}
       
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            if product == 'BANANAS':

                
                order_depth: OrderDepth = state.order_depths[product]

                
                orders: list[Order] = []
                best_ask = min(order_depth.sell_orders.keys()) 
                best_bid = max(order_depth.buy_orders.keys()) 
                mid_price = (best_ask + best_bid) / 2


                ma = self.ma20.next(mid_price) 
                sd = self.rs.update(mid_price)

                upbb = ma + 2*sd
                lbb = ma - 2*sd 

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 20 - current_position
                can_sell = 20 - (-1 * current_position)

                if state.timestamp >= 2000:
                    if mid_price > upbb:
                        if len(order_depth.buy_orders) > 0:
                            best_bid = max(order_depth.buy_orders.keys())
                            best_bid_volume = abs(order_depth.buy_orders[best_bid])
                            quantity = min(can_sell, best_bid_volume)

                            print("SELL", str(quantity) + "x", best_bid)
                            orders.append(Order(product, best_bid, -quantity))
                    if mid_price < lbb:
                        if len(order_depth.sell_orders) > 0:
                            best_ask = min(order_depth.sell_orders.keys())
                            best_ask_volume = abs(order_depth.sell_orders[best_ask])

                            quantity = min(can_buy, best_ask_volume)

                            print("BUY", str(-quantity) + "x", best_ask)
                            orders.append(Order(product, best_ask, quantity))

                results[product] = orders

        logger.flush(state, results)
        return results