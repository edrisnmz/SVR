import MetaTrader5 as mt5


def ClosePosition(target_magic,trade_direction):
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
        return
    positions = mt5.positions_get()
    for position in positions:
        ticket = position.ticket
        symbol = position.symbol
        lot = position.volume
        price = position.price_current 
        magic_number = position.magic
        position_type = position.type        
        if magic_number == target_magic:
            if (trade_direction == "BUY" and position_type == 0) or \
            (trade_direction == "SELL" and position_type == 1):
                print("Position #{} has the same direction ({}) as the trade direction. Skipping...".format(ticket, trade_direction))
                continue
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "type": mt5.ORDER_TYPE_SELL if position_type == 0 else mt5.ORDER_TYPE_BUY,
                "position": ticket,
                "volume": lot,
                "price": price,
                "magic": magic_number,
            }

            result = mt5.order_send(request)
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                print("Closing position {} failed, retcode={}".format(ticket, result.retcode))
            else:
                print("Position #{} with magic number {} closed successfully".format(ticket, magic_number))
    else:
        print('No position for close ! continue...')

    mt5.shutdown()

def BUY(symbol,Magic_Number):
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())
             
    # prepare the buy request structure
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
            
    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol,True):
            print("symbol_select({}}) failed, exit",symbol)
            mt5.shutdown()
             
    positions = mt5.positions_get(symbol=symbol)
    magic_positions = [pos for pos in positions if pos.magic == Magic_Number]    
    if magic_positions:
        print("Active position exists. Skip...")
    else:
        print("No active position found. Opening a new position...")  
        lot = 0.1
        point = mt5.symbol_info(symbol).point
        spread = mt5.symbol_info(symbol).spread /1000000
        price = mt5.symbol_info_tick(symbol).ask
        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_BUY,
            "price": price,
            "sl": price - (300 * point) - spread,
            "tp": price + (300 * point) + spread,
            "deviation": deviation,
            "magic": Magic_Number,
            "comment": 'MLTRADER',
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result
        print("1. order_send(): by {} {} lots at {} with deviation={} points".format(symbol,lot,price,deviation));
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print("2. order_send failed, retcode={}".format(result.retcode))
            # request the result as a dictionary and display it element by element
            result_dict=result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field,result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field=="request":
                    traderequest_dict=result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
            print("shutdown() and quit")
            mt5.shutdown()
             
        print("opened position with POSITION_TICKET={}".format(result.order))

def SELL(symbol,Magic_Number):
    if not mt5.initialize():
        print("initialize() failed, error code =", mt5.last_error())
             
    # prepare the sell request structure
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print(symbol, "not found, can not call order_check()")
        mt5.shutdown()
             
    # if the symbol is unavailable in MarketWatch, add it
    if not symbol_info.visible:
        print(symbol, "is not visible, trying to switch on")
        if not mt5.symbol_select(symbol, True):
            print("symbol_select({}}) failed, exit", symbol)
            mt5.shutdown()
             
    positions = mt5.positions_get(symbol=symbol)
    magic_positions = [pos for pos in positions if pos.magic == Magic_Number]   
    if magic_positions:
        print("Active position exists. Skip...")
    else:
        print("No active position found. Opening a new position...")      
        lot = 0.1
        point = mt5.symbol_info(symbol).point
        spread = mt5.symbol_info(symbol).spread / 1000000
        price = mt5.symbol_info_tick(symbol).bid  # Use bid price for selling
        deviation = 20
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": mt5.ORDER_TYPE_SELL,
            "price": price,
            "sl": price + (300 * point) + spread,  # Adjust SL and TP for selling
            "tp": price - (300 * point) - spread,
            "deviation": deviation,
            "magic": Magic_Number,
            "comment": 'MLTRADER',
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        # send a trading request
        result = mt5.order_send(request)
        # check the execution result
        print(">> order_send(): by {} {} lots at {} with deviation={} points".format(symbol, lot, price, deviation))
        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(">> order_send failed, retcode={}".format(result.retcode))
            # request the result as a dictionary and display it element by element
            result_dict = result._asdict()
            for field in result_dict.keys():
                print("   {}={}".format(field, result_dict[field]))
                # if this is a trading request structure, display it element by element as well
                if field == "request":
                    traderequest_dict = result_dict[field]._asdict()
                    for tradereq_filed in traderequest_dict:
                        print("       traderequest: {}={}".format(tradereq_filed, traderequest_dict[tradereq_filed]))
            print("shutdown() and quit")
            mt5.shutdown()
             
        print("opened position with POSITION_TICKET={}".format(result.order))
