import sqlite3, quandl, talib, pandas, numpy, date_today, datawriter
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
quandl.ApiConfig.api_key = 'yiSaMst67pW9Xesg9Zgy'
conn = sqlite3.connect('stockx.db')
cz = conn.cursor()

def forecast(s1, s2, s3, p1, p2, p3, p4, p5, p6, f7):

    features = ['Open', 'High', 'Low', 'Close']#holds the column names that when selected, will form the features for the prediction
    cz.execute("SELECT quandl_code FROM codes WHERE nse_code = ?", (s1,))
    df = quandl.get(cz.fetchall()[0][0])#this fetches the entire dataframe for the stock
    df = df[['Open', 'High', 'Low', 'Close', 'Total Trade Quantity']]##discarding irrelevant columns
    print('the first dataframe head\n',df.head(2))
    print('the first dataframe tail\n',df.tail(2))
    r, c  = df.shape#get the dimensions of the dataframe
    p = df.index#gets the index of the dataframe
    first_date = str(p[0].year) + '-' + str(p[0].month) + '-' + str(p[0].day)#gets the date from the fist row
    last_date = str(p[r-1].year) + '-' + str(p[r-1].month) + '-' + str(p[r-1].day)#gets the date from the most recent row
    if s3 != '[Select an Index]':
        cz.execute("SELECT quandl_code FROM codes WHERE nse_code = ?", (s3,))
        di = quandl.get(cz.fetchall()[0][0], start_date = first_date, end_date = last_date, column_index = 4)
        df['Index'] = di['Close']
        features.append('Index')
    index = pandas.date_range(first_date, last_date)#creates an array of dates from first date to last date
    dg = df.reindex(index, method='ffill')#(last observation carried forward), reindexes the entire dataframe
    forecast_column = f7#sets the forecast column as the close price
    forecast_out = 1#sets the number of days to shift the close price
    dg['Label'] = dg[forecast_column].shift(-forecast_out)
    ##compute the features
    if(p1 != 0):## adding parameter1 to the dataframe
        dg['sar'] = talib.SAR(dg['High'].values, dg['Low'].values, acceleration=0.02, maximum=0.2)
        features.append('sar')
    if(p2 != 0):
        dg['slowk'], dg['slowd'] = talib.STOCH(dg['High'].values, dg['Low'].values, dg['Close'].values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
        features.append('slowk')
        features.append('slowd')
    if(p3 != 0):
        dg['rsi'] = talib.RSI(dg['Close'].values, timeperiod=14)
        features.append('rsi')
    if(p5 != 0):
        dg['sma'] = talib.SMA(dg['Close'].values, timeperiod=14)
        features.append('sma')
    if(p6 !=0):
        dg['macd'], dg['macdsignal'], dg['macdhist'] = talib.MACD(dg['Close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        features.append('macd')
        features.append('macdsignal')
        features.append('macdhist')
    if(p4 != 0):
        dg['atr'] = talib.ATR(dg['High'].values, dg['Low'].values, dg['Close'].values, timeperiod=14)
        features.append('atr')
    ##here the dataframe is split into two, old data should have all but day rows, new data shuld have day rows
    df_old = dg.iloc[:dg.shape[0] - int(s2)]
    df_new = dg.iloc[dg.shape[0] - int(s2):]
    print('the old dataframe head\n',df_old.head(2))
    print('the old dataframe tail\n',df_old.tail(2))
    print('the new dataframe head\n',df_new.head(2))
    print('the new dataframe tail\n',df_new.tail(2))
    df_old.dropna(inplace = True)
    print('after DropNa()')
    print('the old dataframe head\n',df_old.head(2))
    print('the old dataframe tail\n',df_old.tail(2))
    print('the new dataframe head\n',df_new.head(2))
    print('the new dataframe tail\n',df_new.tail(2))
    X = numpy.array(df_old[features])##converting dataframe to ndarray
    y = numpy.array(df_old['Label'])
    df_new = numpy.array(df_new[features])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3)
    clf = LinearRegression()
    clf.fit(X_train, y_train)
    forecast_set = clf.predict(df_new)
    gendate = pandas.date_range(start = date_today.get_date(), periods = int(s2))
    datawriter.d2f(forecast_set, gendate.date)
    cz.execute("SELECT name FROM codes WHERE nse_code = ?", (s1,))
    name = cz.fetchall()[0][0]
    return(forecast_set, name)