from datamodel import *
import json
from typing import Any
import statistics as s
import math
from collections import deque


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
        self.ratios = []

    def zscore(self, series):
        if len(series) < 10:
            return 0

        return (series[-1] - s.mean(series)) / s.stdev(series)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}

        orders_baguette: list[Order] = []
        orders_dip: list[Order] = []
        orders_ukulele: list[Order] = []
        orders_picnic_basket: list[Order] = []
        batch_buy_size = 1000  # should be greater than any theoretical buy size
        batch_sell_size = 1000  # should be greater than any theoretical sell size

        for product in state.order_depths.keys():
            if product == 'BAGUETTE':
                baguette_order_depth: OrderDepth = state.order_depths[product]
                baguette_best_ask = min(baguette_order_depth.sell_orders.keys())
                baguette_best_bid = max(baguette_order_depth.buy_orders.keys())
                baguette_mid_price = (baguette_best_ask + baguette_best_bid) / 2

                if product in state.position.keys():
                    baguette_position = state.position[product]
                else:
                    baguette_position = 0

                max_baguette_buy = 150 - baguette_position
                max_baguette_sell = 150 - (-1 * baguette_position)

                if math.floor(max_baguette_buy / 2) < batch_buy_size:
                    batch_buy_size = math.floor(max_baguette_buy / 2)
                if math.floor(max_baguette_sell / 2) < batch_sell_size:
                    batch_sell_size = math.floor(max_baguette_sell / 2)

            if product == 'DIP':
                dip_order_depth: OrderDepth = state.order_depths[product]
                dip_best_ask = min(dip_order_depth.sell_orders.keys())
                dip_best_bid = max(dip_order_depth.buy_orders.keys())
                dip_mid_price = (dip_best_ask + dip_best_bid) / 2

                if product in state.position.keys():
                    dip_position = state.position[product]
                else:
                    dip_position = 0

                max_dip_buy = 300 - dip_position
                max_dip_sell = 300 - (-1 * dip_position)

                if math.floor(max_dip_buy / 4) < batch_buy_size:
                    batch_buy_size = math.floor(max_dip_buy / 4)
                if math.floor(max_dip_sell / 4) < batch_sell_size:
                    batch_sell_size = math.floor(max_dip_sell / 4)

            if product == 'UKULELE':
                ukulele_order_depth: OrderDepth = state.order_depths[product]
                ukulele_best_ask = min(ukulele_order_depth.sell_orders.keys())
                ukulele_best_bid = max(ukulele_order_depth.buy_orders.keys())
                ukulele_mid_price = (ukulele_best_ask + ukulele_best_bid) / 2

                if product in state.position.keys():
                    ukulele_position = state.position[product]
                else:
                    ukulele_position = 0

                max_ukulele_buy = 70 - ukulele_position
                max_ukulele_sell = 70 - (-1 * ukulele_position)

                if max_ukulele_buy < batch_buy_size:
                    batch_buy_size = max_ukulele_buy
                if max_ukulele_sell < batch_sell_size:
                    batch_sell_size = max_ukulele_sell

            if product == 'PICNIC_BASKET':
                picnic_basket_order_depth: OrderDepth = state.order_depths[product]
                picnic_basket_best_ask = min(picnic_basket_order_depth.sell_orders.keys())
                picnic_basket_best_bid = max(picnic_basket_order_depth.buy_orders.keys())
                picnic_basket_mid_price = (picnic_basket_best_ask + picnic_basket_best_bid) / 2

                if product in state.position.keys():
                    picnic_basket_position = state.position[product]
                else:
                    picnic_basket_position = 0

                max_picnic_basket_buy = 70 - picnic_basket_position
                max_picnic_basket_sell = 70 - (-1 * picnic_basket_position)

                if max_picnic_basket_buy < batch_buy_size:
                    batch_buy_size = max_picnic_basket_buy
                if max_picnic_basket_sell < batch_sell_size:
                    batch_sell_size = max_picnic_basket_sell

        ratio = picnic_basket_mid_price / (2 * baguette_mid_price + 4 * dip_mid_price + ukulele_mid_price)
        self.ratios.append(ratio)

        zscores = self.zscore(self.ratios)

        batch_size = min(batch_sell_size, batch_buy_size)

        if zscores < -1:  # sell short first
            orders_baguette.append(Order('BAGUETTE', baguette_mid_price - 0.5,  2 * -batch_size))
            orders_dip.append(Order('DIP', dip_mid_price - 0.5, 4 * -batch_size))
            orders_ukulele.append(Order('UKULELE', ukulele_mid_price - 0.5, -batch_size))
            orders_picnic_basket.append(Order('PICNIC_BASKET', picnic_basket_mid_price + 0.5, batch_size))
        elif zscores > 1:  # buy long
            orders_baguette.append(Order('BAGUETTE', baguette_mid_price + 0.5, 2 * batch_size))
            orders_dip.append(Order('DIP', dip_mid_price + 0.5, 4 * batch_size))
            orders_ukulele.append(Order('UKULELE', ukulele_mid_price + 0.5, batch_size))
            orders_picnic_basket.append(Order('PICNIC_BASKET', picnic_basket_mid_price - 0.5, -batch_size))

        result['BAGUETTE'] = orders_baguette
        result['DIP'] = orders_dip
        result['UKULELE'] = orders_ukulele
        result['PICNIC_BASKET'] = orders_picnic_basket

        return result

        logger.flush(state, result)
        return result
