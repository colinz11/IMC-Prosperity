from datamodel import *
import json
from typing import Any
import statistics as s
from collections import deque


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

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        results = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            if product == 'DIVING_GEAR':
                order_depth: OrderDepth = state.order_depths[product]

                orders: list[Order] = []

                if 'DOLPHIN_SIGHTINGS' in state.observations:
                    sight_number = state.observations['DOLPHIN_SIGHTINGS']
                else:
                    sight_number = 0

                
                self.update(sight_number)

                if state.timestamp < 200:
                    break

                average = s.mean(self.sightings)
                sd = s.stdev(self.sightings)
              
                if sd == 0:
                    sd = 1
                zscore = (sight_number - average)/sd

                limit_position = 50

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = limit_position - current_position
                can_sell = limit_position - (-1 * current_position)


                worst_ask = max(order_depth.sell_orders.keys())
                worst_bid = min(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2
                

                ema_12 = self.ema12.next(mid_price)
                ema_26 = self.ema26.next(mid_price)
                macd = ema_12-ema_26
                signal_line = self.ema9.next(macd)


                if macd > 0 and macd > signal_line:
                    self.signal += 1
                elif macd < 0 and macd < signal_line:
                    self.signal -= 1
                else:
                    self.signal = 0

                

                if self.enter_time != 0 and state.timestamp > self.enter_time + 26000:
                    
                    if self.position == 1 and self.signal < -20:
                        orders.append(Order(product, worst_bid, -current_position)) #short everything
                        print(f"Selling {current_position} units at ${worst_bid}")
                        print(str(state.timestamp))
                        self.enter_time = 0
                        self.position = 0
                    elif self.position == -1 and self.signal > 20:
                        
                        orders.append(Order(product, worst_ask, -current_position)) # buy everything
                        print(f"Buying {current_position} units at ${worst_ask}")
                        print(str(state.timestamp))
                        self.enter_time = 0
                        self.position = 0
            
                if zscore > 3 and (self.sightings[-1] - self.sightings[-2] > 1):
                    orders.append(Order(product, best_ask, can_buy)) # buy everything
                    self.enter_time = state.timestamp
                    self.position = 1
                    print(f"ZBuying {can_buy} units at ${worst_ask}")
                    print(str(state.timestamp))
                elif zscore < -3 and (self.sightings[-2] - self.sightings[-1] > 1):
                    
                    orders.append(Order(product, best_bid, -can_sell)) #short everything
                    self.enter_time = state.timestamp
                    self.position = -1
                    print(f"ZSelling {can_sell} units at ${worst_bid}")
                    print(str(state.timestamp))
                results[product] = orders

        #logger.flush(state, results)
        return results
