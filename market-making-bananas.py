from datamodel import *
import math
import json
from datamodel import Order, ProsperityEncoder, TradingState, Symbol
from typing import Any

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
    def __init__(self) -> None:
        self.sell = 0
        self.buy = 0
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        orders: list[Order] = []
        product = 'BANANAS'

        position = 0 
        if product in state.position.keys():
            position = state.position[product]
           
        max_sell = -abs(position-20)
        max_buy = abs(position-20)

        best_ask = min(state.order_depths[product].sell_orders.keys()) 
        best_bid = max(state.order_depths[product].buy_orders.keys()) 
        mid_price = (best_ask + best_bid) / 2
        print('mid_pirce: ' + str(mid_price))


        orders.append(Order(product, mid_price + 2, max_sell))
        orders.append(Order(product, mid_price - 2, max_buy))
    

        
        result[product] = orders
        logger.flush(state, result)
        return result