from typing import *
from collections import deque
from datamodel import *

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
        self.ema9 = ExponentialMovingAverage(9)
        self.ema12 = ExponentialMovingAverage(12)
        self.ema26 = ExponentialMovingAverage(26)
        self.signal = 0
    

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

                print(self.signal)

                position_limit = 50

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                max_buy = position_limit - current_position
                max_sell = position_limit + current_position

                if macd > 0 and macd > signal_line:
                    self.signal += 1
                elif macd < 0 and macd < signal_line:
                    self.signal -= 1
                else:
                    self.signal = 0


                if self.signal > 20: #buy at mid_price + 1, slightly more expensive, so order fills
                    orders.append(Order(product, best_ask, max_buy)) 
                elif self.signal < -20: #sell at mid_price -1
                    orders.append(Order(product, best_bid, -max_sell))
                    
                
                results[product] = orders
        logger.flush(state, results)
        return results