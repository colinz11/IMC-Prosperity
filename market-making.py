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
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        orders: list[Order] = []
        product = 'PEARLS'
        if product in state.position.keys():
            max_sell = -abs(-state.position[product]-20)
            max_buy = abs(state.position[product]-20)
        else:
            max_sell = -20
            max_buy = 20
        orders.append(Order(product, 10001 , max_sell))
        orders.append(Order(product, 9999 , max_buy))
        result[product] = orders
        logger.flush(state, result)
        return result