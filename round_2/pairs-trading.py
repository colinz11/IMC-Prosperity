import json
from typing import Any
from datamodel import *
import statistics as s
import math

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
        
        mean = s.mean(series)
        std = s.stdev(series)
        return (series[-1] - mean) / std

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        orders_coco: list[Order] = []    
        orders_pc: list[Order] = []  


        
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

        self.ratios.append(coco_mid_price/pc_mid_price)        
        
        if state.timestamp < 1000:
            return result


        signal = self.zscore(self.ratios)
        #print(zscores)

        if int(coco_mid_price) == coco_mid_price:
            coco_sell_price = coco_mid_price - 1
            coco_buy_price = coco_mid_price + 1
        else:
            coco_sell_price = math.floor(coco_mid_price)
            coco_sell_price = math.ceil(coco_mid_price)
        
        if int(pc_mid_price) == pc_mid_price:
            pc_sell_price = pc_mid_price - 1
            pc_buy_price = pc_mid_price + 1
        else:
            pc_sell_price = math.floor(pc_mid_price)
            pc_buy_price = math.ceil(pc_mid_price)
        

        if signal > 1.5: #short first
            orders_coco.append(Order('COCONUTS', coco_sell_price, -coco_sell))
            orders_pc.append(Order('PINA_COLADAS', pc_buy_price, pc_buy))
        elif signal < -1.5: #long first
            orders_coco.append(Order('COCONUTS', coco_buy_price, coco_buy))
            orders_pc.append(Order('PINA_COLADAS', pc_sell_price, -pc_sell))
        elif -0.5 < signal < 0.5: #close
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

        logger.flush(state, result)
        return result
