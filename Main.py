from GetData import Position
from ModelTrade import BUY,SELL,ClosePosition

def Start():
    symbol = 'EURUSD_i'
    Magic_Number = 5       
    position = Position()
    print('Going For %s' %position )
    # ClosePosition(Magic_Number, position)
    BUY(symbol, Magic_Number) if position == 'BUY'else SELL(symbol, Magic_Number)
        

        
