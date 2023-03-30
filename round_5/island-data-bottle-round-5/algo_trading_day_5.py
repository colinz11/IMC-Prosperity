from datamodel import *
import json
from typing import Any
import statistics as s
from collections import deque
import math


# class Logger:
#     def __init__(self) -> None:
#         self.logs = ""
#
#     def print(self, *objects: Any, sep: str = " ", end: str = "\n") -> None:
#         self.logs += sep.join(map(str, objects)) + end
#
#     def flush(self, state: TradingState, orders: dict[Symbol, list[Order]]) -> None:
#         print(json.dumps({
#             "state": state,
#             "orders": orders,
#             "logs": self.logs,
#         }, cls=ProsperityEncoder, separators=(",", ":"), sort_keys=True))
#
#         self.logs = ""
#
#
# logger = Logger()


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
            self.ema = self.windowSum / self.windowSize
        if len(data) > self.windowSize:
            self.ema = (val * (self.smoothing / (1 + self.windowSize))) + self.ema * (
                        1 - (self.smoothing / (1 + self.windowSize)))
            return self.ema
        self.windowSum += val
        data.append(val)
        return 0


class Trader:

    def __init__(self) -> None:
        self.ratios = []
        self.ratios_picnic = []
        self.sightings = []
        self.enter_time = 0
        self.ema9 = ExponentialMovingAverage(9)
        self.ema12 = ExponentialMovingAverage(12)
        self.ema26 = ExponentialMovingAverage(26)
        self.signal = 0
        self.position = 0
        self.coco_seen = False
        self.pina_seen = False
        self.bag_seen = False
        self.picnic_seen = False
        self.dip_seen = False
        self.uk_seen = False
        self.bag_seen = False
        self.keep_buying_ukuleles = False
        self.keep_selling_ukuleles = False
        self.keep_buying_berries = False
        self.keep_selling_berries = False

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
        orders_baguette: list[Order] = []
        orders_dip: list[Order] = []
        orders_picnic_basket: list[Order] = []
        orders_ukulele: list[Order] = []
        orders_berries: list[Order] = []



        for product in state.order_depths.keys():
            if product == 'DIVING_GEAR':
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []

                if 'DOLPHIN_SIGHTINGS' in state.observations:
                    sight_number = state.observations['DOLPHIN_SIGHTINGS']
                else:
                    sight_number = 0

                self.update(sight_number)

                if state.timestamp < 200:
                    break

                average = s.mean(self.sightings)
                sd = s.stdev(self.sightings)

                if sd == 0:
                    sd = 1
                zscore = (sight_number - average) / sd

                limit_position = 50

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                can_buy = limit_position - current_position
                can_sell = limit_position - (-1 * current_position)

                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                mid_price = (best_ask + best_bid) / 2

                ema_12 = self.ema12.next(mid_price)
                ema_26 = self.ema26.next(mid_price)
                macd = ema_12 - ema_26
                signal_line = self.ema9.next(macd)

                if macd > 0 and macd > signal_line:
                    self.signal += 1
                elif macd < 0 and macd < signal_line:
                    self.signal -= 1
                else:
                    self.signal = 0

                if self.enter_time != 0 and state.timestamp > self.enter_time + 26000:
                    if self.position == 1 and self.signal < -20:
                        orders.append(Order(product, best_bid, -current_position))  # sell to 0
                        self.enter_time = 0
                        self.position = 0
                    elif self.position == -1 and self.signal > 20:
                        orders.append(Order(product, best_ask, -current_position))  # buy to 0
                        self.enter_time = 0
                        self.position = 0

                if zscore > 3.2 and (self.sightings[-1] - self.sightings[-2] > 2):
                    orders.append(Order(product, best_ask, can_buy))  # buy everything
                    self.enter_time = state.timestamp
                    self.position = 1
                elif zscore < -3.2 and (self.sightings[-2] - self.sightings[-1] > 2):
                    orders.append(Order(product, best_bid, -can_sell))  # short everything
                    self.enter_time = state.timestamp
                    self.position = -1
                result[product] = orders

            if product == "BERRIES":
                sell_timestamp = 350000
                buy_timestamp = 500000
                close = 700000
                order_depth: OrderDepth = state.order_depths[product]

                if product in state.position.keys():
                    current_position = state.position[product]
                else:
                    current_position = 0

                berries_buy = 250 - current_position
                berries_sell = 250 - (-1 * current_position)

                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                berries_mid_price = (best_ask + best_bid) / 2

                sell_price = best_ask - 1
                bid_price = best_bid + 1

                if sell_price < bid_price:
                    sell_price = berries_mid_price
                    bid_price = berries_mid_price

                if "BERRIES" in state.market_trades:
                    for trade in state.market_trades["BERRIES"]:
                        if trade.timestamp == state.timestamp - 100:
                            if trade.buyer == "Olivia":
                                self.keep_buying_berries = True
                                self.keep_selling_berries = False
                            if trade.seller == "Olivia":
                                self.keep_selling_berries = True
                                self.keep_buying_berries = False

                if self.keep_buying_berries is False and self.keep_selling_berries is False:
                    if state.timestamp >= sell_timestamp and state.timestamp < buy_timestamp:  # buy
                        orders_berries.append(
                            Order(product, best_ask, berries_buy))
                    elif state.timestamp >= buy_timestamp and state.timestamp < close:  # sell
                        orders_berries.append(
                            Order(product, best_bid, -berries_sell))
                    elif state.timestamp == close:  # buy
                        orders_berries.append(
                            Order(product, best_ask, current_position))
                    else:  # market make
                        orders_berries.append(
                            Order(product, sell_price, -berries_sell))
                        orders_berries.append(
                            Order(product, bid_price, berries_buy))

            if product == 'BANANAS':
                sell_changed = False
                buy_changed = False
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

                if "BANANAS" in state.market_trades:
                    for trade in state.market_trades["BANANAS"]:
                        if trade.timestamp == state.timestamp - 100:
                            if trade.seller == "Olivia":
                                sell_price = trade.price
                                sell_changed = True
                            if trade.buyer == "Olivia":
                                bid_price = trade.price
                                buy_changed = True

                if not (sell_changed or buy_changed):
                    if sell_price < bid_price:
                        sell_price = mid_price
                        bid_price = mid_price

                if not buy_changed:
                    orders.append(Order(product, sell_price, -can_sell))
                if not sell_changed:
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
                self.coco_seen = True
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
                self.pina_seen = True
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

            if product == 'BAGUETTE':
                self.bag_seen = True
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
                self.dip_seen = True
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

            if product == "UKULELE":
                self.uk_seen = True
                ukulele_order_depth: OrderDepth = state.order_depths[product]
                ukulele_best_ask = min(ukulele_order_depth.sell_orders.keys())
                ukulele_best_bid = max(ukulele_order_depth.buy_orders.keys())
                ukulele_mid_price = (ukulele_best_ask + ukulele_best_bid) / 2

                if product in state.position.keys():
                    ukulele_position = state.position[product]
                else:
                    ukulele_position = 0

                ukulele_buy = 70 - ukulele_position
                ukulele_sell = 70 - (-1 * ukulele_position)

                if "UKULELE" in state.market_trades:
                    for trade in state.market_trades["UKULELE"]:
                        if trade.timestamp == state.timestamp - 100:
                            if trade.buyer == "Olivia":
                                # print("OLIVIA BUY")
                                # # print(state.timestamp)
                                # print("OLIVIA BUY PRICE: " + str(trade.price))
                                # print("UKELELE MID PRICE: " +
                                #       str(ukulele_mid_price))
                                self.keep_buying_ukuleles = True
                                self.keep_selling_ukuleles = False
                            if trade.seller == "Olivia":
                                # print(state.timestamp)
                                # print("OLIVIA SELL")
                                # print("OLIVIA SELL PRICE: " + str(trade.price))
                                # print("UKELELE MID PRICE: " +
                                #       str(ukulele_mid_price))
                                # orders_ukulele.append(
                                #     Order("UKULELE", ukulele_mid_price-1, -ukulele_sell))
                                self.keep_selling_ukuleles = True
                                self.keep_buying_ukuleles = False

            if product == 'PICNIC_BASKET':
                self.picnic_seen = True
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

        if self.keep_buying_ukuleles:
            orders_ukulele.append(
                Order("UKULELE", ukulele_mid_price + 1, ukulele_buy))

        if self.keep_selling_ukuleles:
            orders_ukulele.append(
                Order("UKULELE", ukulele_mid_price - 1, -ukulele_sell))

        result['UKULELE'] = orders_ukulele

        if self.keep_buying_berries:
            orders_berries.append(
                Order("BERRIES", berries_mid_price+1, berries_buy))
        if self.keep_selling_berries:
            orders_berries.append(
                Order("BERRIES", berries_mid_price-1, -berries_sell))
        result["BERRIES"] = orders_berries

        if self.coco_seen and self.pina_seen:
            self.ratios.append(coco_mid_price / pc_mid_price)

            if state.timestamp > 10000:

                signal = self.zscore(self.ratios)

                if int(coco_mid_price) == coco_mid_price:
                    coco_sell_price = coco_mid_price - 1
                    coco_buy_price = coco_mid_price + 1
                else:
                    coco_sell_price = math.floor(coco_mid_price)
                    coco_buy_price = math.ceil(coco_mid_price)

                if int(pc_mid_price) == pc_mid_price:
                    pc_sell_price = pc_mid_price - 1
                    pc_buy_price = pc_mid_price + 1
                else:
                    pc_sell_price = math.floor(pc_mid_price)
                    pc_buy_price = math.ceil(pc_mid_price)

                if signal > 1.68:  # short first
                    orders_coco.append(Order('COCONUTS', coco_sell_price, -coco_sell))
                    orders_pc.append(Order('PINA_COLADAS', pc_buy_price, pc_buy))
                elif signal < -1.68:  # long first
                    orders_coco.append(Order('COCONUTS', coco_buy_price, coco_buy))
                    orders_pc.append(Order('PINA_COLADAS', pc_sell_price, -pc_sell))
                elif -0.25 < signal < 0.25:  # close
                    if pc_position > 0:
                        orders_pc.append(Order('PINA_COLADAS', pc_sell_price, -pc_position))
                    elif pc_position < 0:
                        orders_pc.append(Order('PINA_COLADAS', pc_buy_price, pc_position))
                    if coco_position > 0:
                        orders_coco.append(Order('COCONUTS', coco_sell_price, -coco_position))
                    elif coco_position < 0:
                        orders_coco.append(Order('COCONUTS', coco_buy_price, coco_position))

                result['COCONUTS'] = orders_coco
                result['PINA_COLADAS'] = orders_pc

        if self.picnic_seen and self.dip_seen and self.uk_seen and self.bag_seen:
            picnic_ratio = picnic_basket_mid_price / \
                (2 * baguette_mid_price + 4*dip_mid_price + ukulele_mid_price)
            self.ratios_picnic.append(picnic_ratio)
            if state.timestamp > 10000:
                zscores_picnic = self.zscore(self.ratios_picnic)

                if zscores_picnic < -1:  # sell short first
                    orders_picnic_basket.append(
                        Order('PICNIC_BASKET', picnic_basket_mid_price + 0.5, picnic_basket_buy))
                elif zscores_picnic > 1:  # buy long
                    orders_picnic_basket.append(
                        Order('PICNIC_BASKET', picnic_basket_mid_price - 0.5, -picnic_basket_sell))

                result['PICNIC_BASKET'] = orders_picnic_basket

        # logger.flush(state, result)
        return result