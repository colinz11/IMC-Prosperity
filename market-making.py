from datamodel import *
import math
class Trader:
    def __init__(self) -> None:
        self.sell = 0
        self.buy = 0
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
        if product in state.own_trades.keys():
            for trade in state.own_trades[product]:
                if trade.timestamp == state.timestamp - 100:
                    if trade.buyer == 'SUBMISSION':
                        self.buy += trade.price*trade.quantity
                    else:
                        self.sell += trade.price*trade.quantity
        print(self.sell - self.buy)
        return result