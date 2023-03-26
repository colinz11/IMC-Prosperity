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

    def update(self, price):
        self.sightings.append(price)
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

                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

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

                if zscore > 3 and (self.sightings[-1] - self.sightings[-2] > 1):
                    i = 0 # buy diving_gear
                elif zscore < -3 and (self.sightings[-2] - self.sightings[-1] > 1):
                    i = 1 # sell diving gear


                # if state.timestamp >= 2000:
                #     if mid_price > upbb:
                #         if len(order_depth.buy_orders) > 0:
                #             orders.append(Order(product, upbb, -can_sell))
                #     if mid_price < lbb:
                #         if len(order_depth.sell_orders) > 0:
                #             orders.append(Order(product, lbb, can_buy))
                #
                # results[product] = orders

        logger.flush(state, result)
        return result
