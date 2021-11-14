
class Tick(object):

    def __init__(self,symbol,position):
        self.symbol = symbol
        self.position = position

        self.long_hedge_side = "BUY"
        self.long_hedge_filled = False
        self.long_hedge_order = None

        self.short_hedge_side = "SELL"
        self.short_hedge_filled = False
        self.short_hedge_order = None

