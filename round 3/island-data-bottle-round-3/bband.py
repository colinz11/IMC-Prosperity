from datamodel import *
import json
from typing import Any
import statistics as s


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
        self.sightings = []

    def update(self, count):
        self.sightings.append(count)
        if len(self.sightings) > 15:
            self.sightings.pop(0)

    def get_sma(self):
        return s.mean(self.sightings)

    def get_sd(self):
        return s.stdev(self.sightings)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        results = {}

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            if product == 'DIVING_GEAR':

                order_depth: OrderDepth = state.order_depths[product]

                orders: list[Order] = []

                sight_number = state.observations['DOLPHIN_SIGHTINGS']

                self.update(sight_number)

                average = self.get_sma()
                sd = self.get_sd()

                zscore = (sight_number - average)/sd

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 50 - current_position
                can_sell = 50 - (-1 * current_position)

                worst_ask = max(order_depth.sell_orders.keys())
                worst_bid = min(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

                bid_price = worst_ask
                sell_price = worst_bid

                if sell_price > bid_price:
                    sell_price = mid_price
                    bid_price = mid_price

                if zscore > 3 and (self.sightings[-1] - self.sightings[-2] > 1):
                    orders.append(Order(product, bid_price, can_buy)) # buy everything
                    print(f"Buying {can_buy} units at ${bid_price}")
                elif zscore < -3 and (self.sightings[-2] - self.sightings[-1] > 1):
                    orders.append(Order(product, sell_price, -can_sell)) #short everything
                    print(f"Selling {can_sell} units at ${sell_price}")
                results[product] = orders

        logger.flush(state, results)
        return results
