from datamodel import *
from typing import *
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
        
class Trader:
    
    def __init__(self) -> None:
        self.ema12 = ExponentialMovingAverage(12)
        self.ema26 = ExponentialMovingAverage(26)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        results = {}
       
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_ask = min(order_depth.sell_orders.keys()) 
                best_bid = max(order_depth.buy_orders.keys()) 
                mid_price = (best_ask + best_bid) / 2
                
                ema_12 = self.ema12.next(mid_price)
                ema_26 = self.ema26.next(mid_price)
               

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 20 - current_position
                can_sell = 20 - (-1 * current_position)

              
                
                orders.append(Order(product, mid_price - 1, can_buy)) 
                orders.append(Order(product, mid_price + 1, -can_sell))   
                    

                results[product] = orders

        logger.flush(state, results)
        return results
    
  
        
    
  
        





