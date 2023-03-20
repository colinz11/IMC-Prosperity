from datamodel import *
from typing import *
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
            return self.windowSum / len(data)

            

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
    

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        results = {}

        window_size = 10

        moving_average = MovingAverage(window_size)

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                
                mid_price = self.get_mid_price(state, product)
                ma = moving_average.next(mid_price)




        return results
    
    def get_mid_price(state, product):
        order_depth: OrderDepth = state.order_depths[product]

        total_ask_qty = 0
        total_ask_price = 0

        for ask_price in order_depth.sell_orders.keys():
            ask_qty = order_depth.sell_orders[ask_price]
            total_ask_qty += ask_qty
            total_ask_price += ask_price * ask_qty    

        total_bid_qty = 0
        total_bid_price = 0

        for bid_price in order_depth.buy_orders.keys():
            bid_qty = order_depth.buy_orders[bid_price]
            total_bid_qty += bid_qty
            total_bid_price += bid_price * bid_qty
       
        return (total_ask_price + total_bid_price) / (total_ask_qty + total_bid_qty)
        
    
  
        





