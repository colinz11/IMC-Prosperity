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
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 20 - current_position
                can_sell = 20 - (-1 * current_position)

                still_buying = True
                still_selling = True

                inventory_risk_aversion = 0.1
                order_book_liquidity = 1.5
                volatility = 2
                T = 1

                acceptable_price = mid_price - current_position * inventory_risk_aversion * volatility**2 * (T - state.timestamp/1000000)

                bid_ask_spread = 2/inventory_risk_aversion * math.log(1 + inventory_risk_aversion/order_book_liquidity)

                while still_buying:
                    if len(order_depth.sell_orders) > 0:
                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = abs(order_depth.sell_orders[best_ask])

                        if can_buy <= 0:
                            still_buying = False
                        elif best_ask < acceptable_price:
                            quantity = min(can_buy, best_ask_volume)

                            print("BUY", str(-quantity) + "x", best_ask)
                            orders.append(Order(product, best_ask, quantity))

                            order_depth.sell_orders.pop(best_ask)
                            can_buy -= quantity
                        elif best_ask == acceptable_price:
                            if can_buy > 20:
                                quantity = min(can_buy - 20, best_ask_volume)
                                print("BUY", str(-quantity) + "x", best_ask)
                                orders.append(Order(product, best_ask, quantity))

                                order_depth.sell_orders.pop(best_ask)
                                can_buy -= quantity
                            else:
                                still_buying = False
                        else:
                            orders.append(Order(product, acceptable_price-bid_ask_spread/2, can_buy))
                            still_buying = False

                    else:
                        still_buying = False

                while still_selling:
                    if len(order_depth.buy_orders) > 0:
                        best_bid = max(order_depth.buy_orders.keys())
                        best_bid_volume = abs(order_depth.buy_orders[best_bid])
                        if can_sell <= 0:
                            still_selling = False
                        elif best_bid > acceptable_price:
                            quantity = min(can_sell, best_bid_volume)

                            print("SELL", str(quantity) + "x", best_bid)
                            orders.append(Order(product, best_bid, -quantity))

                            order_depth.buy_orders.pop(best_bid)
                            can_sell -= quantity
                        elif best_bid == acceptable_price:
                            if can_sell > 20:
                                quantity = min(can_sell - 20, best_bid_volume)

                                print("SELL", str(quantity) + "x", best_bid)
                                orders.append(Order(product, best_bid, -quantity))

                                order_depth.buy_orders.pop(best_bid)
                                can_sell -= quantity
                            else:
                                still_selling = False
                        else:
                            orders.append(Order(product, acceptable_price + bid_ask_spread/2, -can_sell))
                            still_selling = False
                    else:
                        still_selling = False

                result[product] = orders

        logger.flush(state, result)
        return result