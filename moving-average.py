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
    
    def __init__(self) -> None:
        self.ma20 = MovingAverage(20)
        self.ma50 = MovingAverage(50)
        self.sell = 0
        self.buy = 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        results = {}

       
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
                best_ask = min(state.order_depths[product].sell_orders.keys()) 
                best_bid = max(state.order_depths[product].buy_orders.keys()) 
                mid_price = (best_ask + best_bid) / 2
                print('mid price ' + str(mid_price))
                ma_20 = self.ma20.next(mid_price)
                ma_50 = self.ma50.next(mid_price)
                
              
                if ma_20 > ma_50: #we buy
                    if len(order_depth.sell_orders) > 0:
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = order_depth.sell_orders[best_ask]
                        print("BUY", str(-best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_volume))
                    
                if ma_20 < ma_50: #we sell
                    if len(order_depth.buy_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = order_depth.buy_orders[best_bid]
                        print("SELL", str(best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                results[product] = orders

                print(state.own_trades)
                print(state.position)
                if product in state.own_trades.keys():
                    for trade in state.own_trades[product]:
                        if trade.timestamp == state.timestamp - 100:
                            if trade.buyer == 'SUBMISSION':
                                self.buy += trade.price*trade.quantity
                            else:
                                self.sell += trade.price*trade.quantity
                print(self.sell - self.buy)
        return results
    
    def get_mid_price(self, state, product):
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
       
        if (total_ask_qty + total_bid_qty) == 0:
            return 0
        return (total_ask_price + total_bid_price) / (total_ask_qty + total_bid_qty)
        
    
  
        





