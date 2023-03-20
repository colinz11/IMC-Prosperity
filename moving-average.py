import numpy as np
import pandas as pd

from datamodel import TradingState, Listing, OrderDepth, Order

from collections import deque


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

        ma = MovingAverage(window_size)

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                if len(order_depth.sell_orders) > 0:



        return results
    
  
        





