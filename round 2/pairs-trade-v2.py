import json
from typing import Any
from datamodel import *
import numpy as np


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


class ZScore:
    def __init__(self) -> None:
        self.prices = []
        self.zscores = []

    def next(self, price):
        self.prices.append(price)
        sd = np.std(self.prices)
        mean = np.mean(self.prices)

        for i in range(len(self.prices)):
            self.zscores.append((self.prices[i] - mean) / sd)

        return self.zscores


class Trader:

    def __init__(self) -> None:
        self.zscore = ZScore()

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        orders: list[Order] = []
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            if product == 'COCONUTS':
                coco_order_depth: OrderDepth = state.order_depths[product]
                coco_best_ask = min(coco_order_depth.sell_orders.keys())
                coco_best_bid = max(coco_order_depth.buy_orders.keys())
                coco_mid_price = (coco_best_ask + coco_best_bid) / 2

                if product in state.position.keys():
                    coco_position = state.position[product]
                else:
                    coco_position = 0

                coco_buy = 600 - coco_position
                coco_sell = 600 - (-1 * coco_position)

            if product == 'PINA_COLADAS':
                pc_order_depth: OrderDepth = state.order_depths[product]
                pc_best_ask = min(pc_order_depth.sell_orders.keys())
                pc_best_bid = max(pc_order_depth.buy_orders.keys())
                pc_mid_price = (pc_best_ask + pc_best_bid) / 2

                if product in state.position.keys():
                    pc_position = state.position[product]
                else:
                    pc_position = 0

                pc_buy = 300 - pc_position
                pc_sell = 300 - (-1 * pc_position)

        ratio = coco_mid_price / pc_mid_price
        zscores = self.zscore.next(ratio)

        sd_zscores = np.std(zscores)
        mean_zscores = np.mean(zscores)
        up_limit = mean_zscores + sd_zscores
        lower_limit = mean_zscores - sd_zscores

        print('Ratio: ' + str(ratio))
        print('Mean zscores: ' + str(mean_zscores))
        print('SD zscores: ' + str(sd_zscores))
        print('Z score: ' + str(zscores[-1]))

        if zscores[-1] > up_limit:  # short first
            orders.append(Order('COCONUTS', coco_mid_price, -coco_sell))
            orders.append(Order('PINA_COLADAS', pc_mid_price, pc_buy))
        elif zscores[-1] < lower_limit:  # long first
            orders.append(Order('COCONUTS', coco_mid_price, coco_buy))
            orders.append(Order('PINA_COLADAS', pc_mid_price, -pc_sell))
        result[product] = orders

        logger.flush(state, result)
        return result
