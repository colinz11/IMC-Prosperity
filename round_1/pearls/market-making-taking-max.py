from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

    def __init__(self) -> None:
        self.sell = 0
        self.buy = 0

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
            if product == 'PEARLS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!
                acceptable_price = 10000

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 20 - current_position
                can_sell = 20 - (-1 * current_position)

                still_buying = True
                still_selling = True

                while still_buying:

                    # If statement checks if there are any SELL orders in the PEARLS market
                    if len(order_depth.sell_orders) > 0:

                        # Sort all the available sell orders by their price,
                        # and select only the sell order with the lowest price

                        best_ask = min(order_depth.sell_orders.keys())
                        best_ask_volume = abs(order_depth.sell_orders[best_ask])

                        # Check if the lowest ask (sell order) is lower than the above defined fair value
                        if can_buy <= 0:
                            still_buying = False
                        elif best_ask < acceptable_price:
                            quantity = min(can_buy, best_ask_volume)

                            print("BUY", str(-quantity) + "x", best_ask)
                            orders.append(Order(product, best_ask, quantity))

                            order_depth.sell_orders.pop(best_ask)
                            can_buy -= quantity
                        else:
                            mid_price = (min(order_depth.sell_orders.keys()) +
                                         min(10000, max(order_depth.sell_orders.keys())))//2
                            orders.append(Order(product, mid_price, can_buy))
                            still_buying = False

                    else:
                        still_buying = False

                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium
                while still_selling:

                    if len(order_depth.buy_orders) != 0:
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
                        else:
                            mid_price = (max(order_depth.buy_orders.keys()) +
                                         max(10000, min(order_depth.buy_orders.keys()))) // 2
                            orders.append(Order(product, mid_price, -can_sell))
                            still_selling = False
                    else:
                        still_selling = False

                # Add all the above orders to the result dict
                result[product] = orders

                print(state.own_trades)
                print(state.position)
                if product in state.own_trades.keys():
                    for trade in state.own_trades[product]:
                        if trade.timestamp == state.timestamp - 100:
                            if trade.buyer == 'SUBMISSION':
                                self.buy += trade.price * trade.quantity
                            else:
                                self.sell += trade.price * trade.quantity
                print(self.sell - self.buy)

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result