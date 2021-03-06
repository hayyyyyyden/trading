import uuid


class Event(object):
  """
  Event is base class providing an interface for all subsequent
  (inherited) events, that will trigger further events in the
  trading infrastructure.
  """
  pass


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self):
        """
        Initialises the MarketEvent.
        """
        self.type = 'MARKET'


class ActionEvent(Event):
    def __init__(self, symbol, action_type):
        """
        Initialises the ActionEvent.

        Parameters:
        action_type - 'CLOSE_ALL' close all unfilled and open orders. Usually used before the end of
                       each day or weekend to avoid risk or overnight fee.
        """
        self.type = 'ACTION'
        self.symbol = symbol
        self.action_type = action_type


class SignalEvent(Event):
    """
    Handles the event of sending a Signal from a Strategy object.
    This is received by a Portfolio object and acted upon.
    """

    def __init__(self, symbol, datetime, signal_type, order_type='MKT',
                limit_price=None, stop_loss=None, profit_target=None,
                stop_price=None, quantity=10000, strategy_id=1):
        """
        Initialises the SignalEvent.

        Parameters:
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - 'LONG' or 'SHORT' or 'EXIT'.
        """

        self.type = 'SIGNAL'
        self.strategy_id = strategy_id
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.quantity = quantity
        self.stop_loss = stop_loss
        self.profit_target = profit_target
        self.limit_price = limit_price  # muse be set when order_type is LMT
        self.stop_price = stop_price # must be set when order_type is STP
        self.order_type = order_type



class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """

    def __init__(self, signal, quantity, direction):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        Parameters:
        signal - The signal to generate the order.
        order_type - 'MKT' or 'LMT' or 'STP' for Market or Limit or Stop.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """

        self.type = 'ORDER'
        self.order_id = uuid.uuid4()
        self.direction = direction
        self.quantity = quantity
        self.symbol = signal.symbol
        self.order_type = signal.order_type
        self.stop_loss = signal.stop_loss
        self.profit_target = signal.profit_target
        self.limit_price = signal.limit_price  # muse be set when order_type is LMT
        self.stop_price = signal.stop_price # must be set when order_type is STP
        self.entry_price = None
        self.exit_price = None
        self.entry_time = None
        self.exit_time = None
        self.profit = None

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" % \
            (self.symbol, self.order_type, self.quantity, self.direction))


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.
    """

    def __init__(self, order, timeindex, price, symbol, exchange, quantity,
                 direction, commission=None):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timeindex - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        commission - An optional commission sent from IB.
        """

        self.type = 'FILL'
        self.fill_id = uuid.uuid4()
        self.order = order
        self.timeindex = timeindex
        self.price = price
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction

        # Calculate commission
        if commission is None:
            self.commission = self.calculate_commission()
        else:
            self.commission = commission

    def calculate_commission(self):
        """
        Calculates the fees of trading. Zero for now.
        """
        return 0
