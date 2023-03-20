from datamodel import *
import math
class Trader:
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        orders: list[Order] = []
        product = 'PEARLS'
        if product in state.position.keys():
            max_sell = -abs(-state.position[product]-20)
            max_buy = abs(state.position[product]-20)
        else:
            max_sell = -20
            max_buy = 20
        orders.append(Order(product, 10001 , max_sell))
        orders.append(Order(product, 9999 , max_buy))
        result[product] = orders
        print(state.own_trades)
        print(state.position)
        return result