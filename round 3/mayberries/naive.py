import json
from typing import Any
from datamodel import *
import statistics as s
import math


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


class Trader:
    

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        sell_timestamp = 350000
        buy_timestamp = 500000
        results = {}
        orders: list[Order] = []  
        for product in state.order_depths.keys():
            
            if product == 'BERRIES':
                    order_depth: OrderDepth = state.order_depths[product]
                    orders: list[Order] = []

                    if product in state.position.keys():
                        current_position = state.position[product]
                    else:
                        current_position = 0

                    can_buy = 250 - current_position
                    can_sell = 250 - (-1 * current_position)

                    worst_ask = max(order_depth.sell_orders.keys())
                    worst_bid = min(order_depth.buy_orders.keys())
                    best_ask = min(order_depth.sell_orders.keys())
                    best_bid = max(order_depth.buy_orders.keys())
                    mid_price = (best_ask + best_bid) / 2

                    sell_price = best_ask - 1
                    bid_price = best_bid + 1 

                    if sell_price < bid_price:
                        sell_price = mid_price
                        bid_price = mid_price

                    orders.append(Order(product, sell_price, -can_sell))
                    orders.append(Order(product, bid_price, can_buy))

                    results[product] = orders
        logger.flush(state, results)
        return results