from datamodel import *

class Trader:
    def __init__(self) -> None:
        self.sell = 0
        self.buy = 0
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result = {}
        orders: list[Order] = []
        product = 'BANANAS'

        position = 0 
        if product in state.position.keys():
            position = state.position[product]
           
        max_sell = -abs(position-20)
        max_buy = abs(position-20)

        best_ask = min(state.order_depths[product].sell_orders.keys()) 
        best_bid = max(state.order_depths[product].buy_orders.keys()) 
        mid_price = (best_ask + best_bid) / 2
        print('mid_pirce: ' + str(mid_price))


        orders.append(Order(product, mid_price + 2, max_sell))
        orders.append(Order(product, mid_price - 2, max_buy))
    

        
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