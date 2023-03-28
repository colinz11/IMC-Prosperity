from datamodel import *
import json
from typing import Any
import statistics as s
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

        for product in state.order_depths.keys():
            if product == 'BAGUETTE':
                baguette_order_depth: OrderDepth = state.order_depths[product]
                baguette_best_ask = min(
                    baguette_order_depth.sell_orders.keys())
                # baguette_worst_ask = max(
                #     baguette_order_depth.sell_orders.keys())
                baguette_best_bid = max(baguette_order_depth.buy_orders.keys())
                # baguette_worst_bid = min(
                #     baguette_order_depth.buy_orders.keys())
                baguette_mid_price = (
                    baguette_best_ask + baguette_best_bid) / 2

                if product in state.position.keys():
                    baguette_position = state.position[product]
                else:
                    baguette_position = 0

                baguette_buy = 140 - baguette_position
                baguette_sell = 140 - (-1 * baguette_position)

            if product == 'DIP':
                dip_order_depth: OrderDepth = state.order_depths[product]
                dip_best_ask = min(dip_order_depth.sell_orders.keys())
                # dip_worst_ask = max(dip_order_depth.sell_orders.keys())
                dip_best_bid = max(dip_order_depth.buy_orders.keys())
                # dip_worst_bid = min(dip_order_depth.buy_orders.keys())
                dip_mid_price = (dip_best_ask + dip_best_bid) / 2

                if product in state.position.keys():
                    dip_position = state.position[product]
                else:
                    dip_position = 0

                dip_buy = 280 - dip_position
                dip_sell = 280 - (-1 * dip_position)

            if product == 'UKULELE':
                ukulele_order_depth: OrderDepth = state.order_depths[product]
                ukulele_best_ask = min(ukulele_order_depth.sell_orders.keys())
                # ukelele_worst_ask = max(ukulele_order_depth.sell_orders.keys())
                ukulele_best_bid = max(ukulele_order_depth.buy_orders.keys())
                # ukelele_worst_bid = min(ukulele_order_depth.buy_orders.keys())
                ukulele_mid_price = (ukulele_best_ask + ukulele_best_bid) / 2

                if product in state.position.keys():
                    ukulele_position = state.position[product]
                else:
                    ukulele_position = 0

                ukulele_buy = 70 - ukulele_position
                ukulele_sell = 70 - (-1 * ukulele_position)

            if product == 'PICNIC_BASKET':
                picnic_basket_order_depth: OrderDepth = state.order_depths[product]
                picnic_basket_best_ask = min(
                    picnic_basket_order_depth.sell_orders.keys())
                # picnic_basket_worst_ask = min(
                #     picnic_basket_order_depth.sell_orders.keys())
                picnic_basket_best_bid = max(
                    picnic_basket_order_depth.buy_orders.keys())
                # picnic_basket_worst_bid = min(
                #     picnic_basket_order_depth.buy_orders.keys())
                picnic_basket_mid_price = (
                    picnic_basket_best_ask + picnic_basket_best_bid) / 2

                if product in state.position.keys():
                    picnic_basket_position = state.position[product]
                else:
                    picnic_basket_position = 0

                picnic_basket_buy = 70 - picnic_basket_position
                picnic_basket_sell = 70 - (-1 * picnic_basket_position)

        ratio = picnic_basket_mid_price / \
            (2 * baguette_mid_price + 4*dip_mid_price + ukulele_mid_price)

        self.ratios.append(ratio)

        zscores = self.zscore(self.ratios)

        if zscores < -1:  # sell short first
            orders_baguette.append(
                Order('BAGUETTE', baguette_mid_price + 0.5, baguette_buy))
            orders_dip.append(Order('DIP', dip_mid_price+0.5, dip_buy))
            orders_ukulele.append(
                Order('UKULELE', ukulele_mid_price+0.5, ukulele_buy))
            orders_picnic_basket.append(
                Order('PICNIC_BASKET', picnic_basket_mid_price + 0.5, picnic_basket_buy))
        elif zscores > 1:  # buy long
            orders_baguette.append(
                Order('BAGUETTE', baguette_mid_price - 0.5, -baguette_sell))
            orders_dip.append(Order('DIP', dip_mid_price-0.5, -dip_sell))
            orders_ukulele.append(
                Order('UKULELE', ukulele_mid_price-0.5, -ukulele_sell))
            orders_picnic_basket.append(
                Order('PICNIC_BASKET', picnic_basket_mid_price - 0.5, -picnic_basket_sell))
        # elif abs(zscores) < 0.75:  # clear position
        #     #     if baguette_position > 0:
        #     #         orders_baguette.append(Order('BAGUETTE', baguette_mid_price-0.5, -baguette_position))
        #     #     elif baguette_position < 0:
        #     #         orders_baguette.append(Order('BAGUETTE', baguette_mid_price+0.5, -baguette_position))

        #     #     if dip_position > 0:
        #     #         orders_dip.append(Order('DIP', dip_mid_price-0.5, -dip_position))
        #     #     elif dip_position < 0:
        #     #         orders_dip.append(Order('DIP', dip_mid_price+0.5, -dip_position))

        #     #     if ukulele_position > 0:
        #     #         orders_ukulele.append(Order('UKULELE', ukulele_mid_price-0.5, -ukulele_position))
        #     #     elif ukulele_position < 0:
        #     #         orders_ukulele.append(Order('UKULELE', ukulele_mid_price+0.5, -ukulele_position))

        #     if picnic_basket_position > 0:
        #         orders_picnic_basket.append(
        #             Order('PICNIC_BASKET', picnic_basket_mid_price - 0.5, -picnic_basket_position))
        #     elif picnic_basket_position < 0:
        #         orders_picnic_basket.append(
        #             Order('PICNIC_BASKET', picnic_basket_mid_price+0.5, -picnic_basket_position))
        # print("AFTER")
        # print(state.position)

        result['BAGUETTE'] = orders_baguette
        result['DIP'] = orders_dip
        result['UKULELE'] = orders_ukulele
        result['PICNIC_BASKET'] = orders_picnic_basket

        # logger.flush(state, result)

        return result
