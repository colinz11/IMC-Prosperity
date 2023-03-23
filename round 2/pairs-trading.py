import json
from typing import Any
from datamodel import *
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
        self.ratios = []
   

    def zscore(self, series):
        if len(series) < 10:
            return 0

        return (series[-1] - s.mean(series)) / s.stdev(series)

    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        result = {}
        orders_coco: list[Order] = []    
        orders_pc: list[Order] = []  
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

        ratio = coco_mid_price/pc_mid_price
        self.ratios.append(ratio)
        

        zscores = self.zscore(self.ratios)
        print(zscores)
      
        

        if zscores > 0.95: #short first
            orders_coco.append(Order('COCONUTS', coco_mid_price - 1, -coco_sell))
            orders_pc.append(Order('PINA_COLADAS', pc_mid_price + 1, pc_buy))
        elif zscores < -0.95: #long first
            orders_coco.append(Order('COCONUTS', coco_mid_price + 1, coco_buy))
            orders_pc.append(Order('PINA_COLADAS', pc_mid_price - 1, -pc_sell))
        
   
            
        result['COCONUTS'] = orders_coco
        result['PINA_COLADAS'] = orders_pc

        logger.flush(state, result)
        return result
