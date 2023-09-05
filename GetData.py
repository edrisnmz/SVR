import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import ta
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error as mse
def Data():
    pd.set_option('display.max_columns', 500)
    pd.set_option('display.width', 1500)
    if not mt5.initialize():
        print("initialize() failed, error code =",mt5.last_error())    
    symbol = 'EURUSD_i'
    # rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15,0,12*24*100)
    # rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15,0,12*24*150)
    # rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15,0,12*24*300)
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4,0,4*24*300)
    point = mt5.symbol_info(symbol).point
    mt5.shutdown()
    rates_frame = pd.DataFrame(rates)
    rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
    rates_frame.set_index('time', inplace=True) 
    data = rates_frame
    data['EMA'] = ta.trend.ema_indicator(data['close'], 14)
    data['RSI'] = ta.momentum.rsi(data['close'],14)
    data['SMA'] = ta.trend.sma_indicator(data.close)
    data['WMA'] = ta.trend.wma_indicator(data.close) 
    data['A'] = ta.trend.IchimokuIndicator(data.high,data.low).ichimoku_a() 
    data['B'] = ta.trend.IchimokuIndicator(data.high,data.low).ichimoku_b()
    data['base'] = ta.trend.IchimokuIndicator(data.high,data.low).ichimoku_base_line()
    data['rsi2'] = ta.trend.IchimokuIndicator(data.high,data.low).ichimoku_conversion_line() 
    data['atr'] =ta.volatility.average_true_range(data.high,data.low,data.close,14)
    data['cmf'] =ta.volume.money_flow_index(data.high,data.low,data.close,data.tick_volume,14)
    data.dropna(inplace=True)
    data.drop(columns=['real_volume', 'spread', 'tick_volume'], inplace=True)
    return data

def Train():
    data = Data()
    Tick = data.iloc[-5:]
    data = data.iloc[:-5]
    X_List = ['open',
            'high',
            'low',
            'EMA',
            'RSI',
            'SMA',
            'WMA',
            'A',
            'B',
            'base',
            'rsi2',
            'atr',
            'cmf']
    X = data[X_List]
    y = data.close
    #-------------------------------------
    scr_x = MinMaxScaler(feature_range=(0, 1))
    scr_y= MinMaxScaler(feature_range=(0, 1))
    y = np.array(y)
    y = y.reshape(-1,1)
    y = scr_y.fit_transform(y)
    y = pd.DataFrame(y,columns=['close'])
    # Y Ticker
    y_Tick = np.array(Tick.close)
    y_Tick = y_Tick.reshape(-1,1)
    y_Tick = scr_y.fit_transform(y_Tick)
    y_Tick = pd.DataFrame(y_Tick,columns=['close'])
    #--------------------------------------
    X = np.array(X)
    X = scr_x.fit_transform(X)  
    X_Tick = np.array(Tick[X_List])
    X_Tick = scr_x.fit_transform(X_Tick)
    #--------------------------------------
    svr = SVR(kernel='rbf',gamma='auto')
    svr.fit(X,y)
    predicted = svr.predict(X_Tick)
    print('Error coefficient:', mse(y_Tick,predicted) *100)
    # Inverse Data
    predicted =  predicted.reshape(-1,1)
    predicted =scr_y.inverse_transform(predicted)
    y_Tick = scr_y.inverse_transform(y_Tick)
    predicted =  predicted.reshape(-1)
    return predicted

def Position():
    predicted = Train()
    return 'SELL 'if predicted[3] > predicted[4] else 'BUY'
