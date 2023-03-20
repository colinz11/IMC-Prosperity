from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:


    def rolling(self, days) -> int:
        pass

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """

        # Initialize the method output dict as an empty dict
        result = {}

        # Iterate over all the keys (the available products) contained in the order dephts
        for product in state.order_depths.keys():
            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':

                pass
            elif product == 'BANANAS':
                pass

        # Return the dict of orders        
        return result