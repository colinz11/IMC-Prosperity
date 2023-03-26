import json
from typing import Any
from datamodel import *
import statistics as s
import math


class Trader:
    

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        
        results = {}
        orders: list[Order] = []  
        for product in state.order_depths.keys():
            
            if product == 'BERRIES':
                sell_timestamp = 350000
                buy_timestamp = 500000
                close = 700000
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 250 - current_position
                can_sell = 250 - (-1 * current_position)

                
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

                sell_price = best_ask - 1
                bid_price = best_bid + 1

                if sell_price < bid_price:
                    sell_price = mid_price
                    bid_price = mid_price
                
                if state.timestamp >= sell_timestamp and state.timestamp < buy_timestamp: #buy
                    orders.append(Order(product, best_ask, can_buy))
                elif state.timestamp >= buy_timestamp and state.timestamp < close: #sell
                    orders.append(Order(product, best_bid, -can_sell))
                elif state.timestamp == close: #buy
                    orders.append(Order(product, best_ask, current_position))
                else: #market make
                    orders.append(Order(product, sell_price, -can_sell))
                    orders.append(Order(product, bid_price, can_buy))
                results[product] = orders
        #logger.flush(state, results)
        return results