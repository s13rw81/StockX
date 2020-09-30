import pandas, talib

df = pandas.DataFrame()

def megacrunch(stock = ''):
    global df
    df = pandas.read_csv('csv\\' + stock + '.csv')    
    df = df[[df.columns[0],df.columns[1],df.columns[2],df.columns[3], df.columns[5], df.columns[6]]]

    # Parabolic SAR
    df['sar'] = talib.SAR(df['High'].values, df['Low'].values, acceleration=0, maximum=0)
    # Stochastic
    df['slowk'], df['slowd'] = talib.STOCH(df['High'].values, df['Low'].values, df['Close'].values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    # Average True Range
    df['atr'] = talib.ATR(df['High'].values, df['Low'].values, df['Close'].values, timeperiod=14)
    # Simple Moving Average
    df['sma'] = talib.SMA(df['Close'].values, timeperiod=30)
    # Relative Strength Index
    df['rsi'] = talib.RSI(df['Close'].values, timeperiod=14)
    # MACD
    df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    # Bollinger Bands
    df['upperband'], df['middleband'], df['lowerband'] = talib.BBANDS(df['Close'].values, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)

def line(rows):
    global df
    dg = df.tail(rows)
    print('dg dataframe :', dg.tail(1))
    dg.to_csv('linegraph.csv', columns = ['Date', 'Close'], index = False)
    