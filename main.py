# region imports
from AlgorithmImports import *
# endregion

class AlertLightBrownOwl(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2022, 2, 12)
        self.set_end_date(2024, 8, 12)
        self.set_cash(100000)

        self.qqq = self.add_equity("QQQ", Resolution.HOUR).symbol

        self.entryTicket = None
        self.stopMarketTicket = None
        self.entryTime = datetime.min
        self.stopMarketOrderFillTime = datetime.min
        self.highestPrice = 0
        

    def on_data(self, data: Slice):
        if (self.time - self.stopMarketOrderFillTime).days < 30:
            return
        price = self.securities[self.qqq].price

        if not self.portfolio.invested and not self.transactions.get_open_orders(self.qqq):
            quantity = self.calculate_order_quantity(self.qqq, 0.9)
            self.entryTicket = self.limit_order(self.qqq, quantity, price, "Entry Order")
            self.entryTime = self.time
        
        if (self.time - self.entryTime).days > 1 and self.entryTicket.status != OrderStatus.FILLED:
            self.entryTime = self.time
            updateFields = UpdateOrderFields()
            updateFields.limit_price = price
            self.entryTicket.Update(updateFields)

        if self.stopMarketTicket is not None and self.Portfolio.Invested:
            if price > self.highestPrice:
                self.highestPrice = price
                updateFields = UpdateOrderFields()
                updateFields.stop_price = price * 0.95
                self.stopMarketTicket.Update(updateFields)

    def on_order_event(self, order_event):
        if order_event.status != OrderStatus.FILLED:
            return

        if self.entryTicket is not None and self.entryTicket.order_id == order_event.order_id:
            self.stopMarketTicket = self.stop_market_order(self.qqq, -self.entryTicket.quantity, 0.95*self.entryTicket.average_fill_price)

        if self.stopMarketTicket is not None and self.stopMarketTicket.order_id == order_event.order_id:
            self.stopMarketOrderFillTime = self.time
            self.highestPrice = 0
