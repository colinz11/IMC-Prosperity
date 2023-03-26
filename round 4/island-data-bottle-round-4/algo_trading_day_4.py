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

class ExponentialMovingAverage:
        def __init__(self, size, smoothing=2):
            """
            Initialize your data structure here.
            :type size: int
            """
            self.windowSize = size
            self.windowSum = 0
            self.data = deque([])
            self.smoothing = smoothing
            self.ema = 0

        def next(self, val):
            """
            :type val: int
            :rtype: float
            """
            data = self.data

            if len(data) == self.windowSize:
                self.ema = self.windowSum/self.windowSize
            if len(data) > self.windowSize:
                self.ema = (val * (self.smoothing / (1 + self.windowSize))) + self.ema * (1 - (self.smoothing / (1 + self.windowSize)))
                return self.ema
            self.windowSum += val
            data.append(val)
            return 0


class Trader:

    def __init__(self) -> None:
        self.ratios = []
        self.sightings = []
        self.enter_time = 0
        self.ema9 = ExponentialMovingAverage(9)
        self.ema12 = ExponentialMovingAverage(12)
        self.ema26 = ExponentialMovingAverage(26)
        self.signal = 0
        self.position = 0

    def update(self, count):
        self.sightings.append(count)
        if len(self.sightings) > 15:
            self.sightings.pop(0)

    def zscore(self, series):
        if len(series) < 10:
            return 0

        return (series[-1] - s.mean(series)) / s.stdev(series)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        orders_coco: list[Order] = []
        orders_pc: list[Order] = []
     


        for product in state.order_depths.keys():

            if product == 'BERRIES':
                sell_timestamp = 350000
                buy_timestamp = 500000
                close = 700000
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 250 - current_position
                can_sell = 250 - (-1 * current_position)

                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

                sell_price = best_ask - 1
                bid_price = best_bid + 1

                if sell_price < bid_price:
                    sell_price = mid_price
                    bid_price = mid_price
                
                if state.timestamp >= sell_timestamp and state.timestamp < buy_timestamp: #buy
                    orders.append(Order(product, best_ask, can_buy))
                elif state.timestamp >= buy_timestamp and state.timestamp < close: #sell
                    orders.append(Order(product, best_bid, -can_sell))
                elif state.timestamp == close: #buy
                    orders.append(Order(product, best_ask, current_position))
                else: #market make
                    orders.append(Order(product, sell_price, -can_sell))
                    orders.append(Order(product, bid_price, can_buy))
                result[product] = orders

            if product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = 20 - current_position
                can_sell = 20 - (-1 * current_position)

                worst_ask = max(order_depth.sell_orders.keys())
                worst_bid = min(order_depth.buy_orders.keys())
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

                sell_price = worst_ask - 1 - (current_position / 20)
                bid_price = worst_bid + 1 - (current_position / 20)

                if sell_price < bid_price:
                    sell_price = mid_price
                    bid_price = mid_price

                orders.append(Order(product, sell_price, -can_sell))
                orders.append(Order(product, bid_price, can_buy))

                result[product] = orders

            if product == 'PEARLS':

                    # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                    order_depth: OrderDepth = state.order_depths[product]

                    # Initialize the list of Orders to be sent as an empty list
                    orders: list[Order] = []

                    acceptable_price = 10000

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

                    while still_buying:
                        if len(order_depth.sell_orders) > 0:
                            best_ask = min(order_depth.sell_orders.keys())
                            best_ask_volume = abs(order_depth.sell_orders[best_ask])

                            if can_buy <= 0:
                                still_buying = False
                            elif best_ask < acceptable_price:
                                quantity = min(can_buy, best_ask_volume)
                                orders.append(Order(product, best_ask, quantity))

                                order_depth.sell_orders.pop(best_ask)
                                can_buy -= quantity
                            elif best_ask == acceptable_price:
                                if can_buy > 20:
                                    quantity = min(can_buy - 20, best_ask_volume)
                                    
                                    orders.append(Order(product, best_ask, quantity))

                                    order_depth.sell_orders.pop(best_ask)
                                    can_buy -= quantity
                                else:
                                    still_buying = False
                            else:
                                orders.append(Order(product, min(mid_price - 3, 9999), can_buy))
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
                                orders.append(Order(product, best_bid, -quantity))

                                order_depth.buy_orders.pop(best_bid)
                                can_sell -= quantity
                            elif best_bid == acceptable_price:
                                if can_sell > 20:
                                    quantity = min(can_sell - 20, best_bid_volume)
                                    orders.append(Order(product, best_bid, -quantity))

                                    order_depth.buy_orders.pop(best_bid)
                                    can_sell -= quantity
                                else:
                                    still_selling = False
                            else:
                                orders.append(Order(product, max(mid_price + 3, 10001), -can_sell))
                                still_selling = False
                        else:
                            still_selling = False

                    result[product] = orders

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
        self.ratios.append(ratio)

        zscores = self.zscore(self.ratios)
    

        if 1 < zscores < 3:  # short first
            orders_coco.append(Order('COCONUTS', coco_mid_price - 0.5, -coco_sell))
            orders_pc.append(Order('PINA_COLADAS', pc_mid_price + 0.5, pc_buy))
        elif -3 < zscores < -1:  # long first
            orders_coco.append(Order('COCONUTS', coco_mid_price + 0.5, coco_buy))
            orders_pc.append(Order('PINA_COLADAS', pc_mid_price - 0.5, -pc_sell))

        result['COCONUTS'] = orders_coco
        result['PINA_COLADAS'] = orders_pc

        #logger.flush(state, result)
        return result