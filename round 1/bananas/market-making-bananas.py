from datamodel import *
import json
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

        for product in state.order_depths.keys():
            if product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

               

                


                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 20 - current_position
                can_sell = 20 - (-1 * current_position)

                still_buying = True
                still_selling = True


                best_ask = min(order_depth.sell_orders.keys()) 
                best_bid = max(order_depth.buy_orders.keys()) 
                mid_price = (best_ask + best_bid) / 2

                buy_price = mid_price - 3

                sell_price = mid_price + 3
                
                while still_buying:
                    if len(order_depth.sell_orders) > 0:
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = abs(order_depth.sell_orders[best_ask])

                        if can_buy <= 0:
                            still_buying = False
                        elif best_ask < buy_price:
                            quantity = min(can_buy, best_ask_volume)

                           
                            orders.append(Order(product, best_ask, quantity))

                            order_depth.sell_orders.pop(best_ask)
                            can_buy -= quantity
                        elif best_ask == buy_price:
                            if can_buy > 20:
                                quantity = min(can_buy - 20, best_ask_volume)
                                
                                orders.append(Order(product, best_ask, quantity))

                                order_depth.sell_orders.pop(best_ask)
                                can_buy -= quantity
                            else:
                                still_buying = False
                        else:   
                            still_buying = False

                    else:
                        still_buying = False


                while still_selling:
                    if len(order_depth.buy_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = abs(order_depth.buy_orders[best_bid])
                        if can_sell <= 0:
                            still_selling = False
                        elif best_bid > sell_price:
                            quantity = min(can_sell, best_bid_volume)
                            orders.append(Order(product, best_bid, -quantity))
                            order_depth.buy_orders.pop(best_bid)
                            can_sell -= quantity

                        elif best_bid == sell_price:
                            if can_sell > 20:
                                quantity = min(can_sell - 20, best_bid_volume)

                                orders.append(Order(product, best_bid, -quantity))

                                order_depth.buy_orders.pop(best_bid)
                                can_sell -= quantity
                            else:
                                still_selling = False
                        else:
                            still_selling = False
                    else:
                        still_selling = False
                result[product] = orders
        logger.flush(state, result)
        return result