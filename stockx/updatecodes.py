#simplified updatecodes
import zipfile, urllib.request, sqlite3, csv, pandas, quandl, datetime # operator
quandl.ApiConfig.api_key = 'yiSaMst67pW9Xesg9Zgy'

class UpdateCodes:
    def __init__(self):
        self.stime = datetime.datetime.now()
        self.url = r'https://www.quandl.com/api/v3/databases/NSE/codes?api_key=yiSaMst67pW9Xesg9Zgy'# url of the zip file
        self.conn = sqlite3.connect('stockx.db')# connect to database
        self.c = self.conn.cursor()# create a cursor
        self.c.execute('CREATE TABLE IF NOT EXISTS codes(date TEXT, name TEXT, quandl_code TEXT, nse_code TEXT, high_max REAL, low_max REAL, high_52 REAL, low_52 REAL, high_52_b REAL, low_52_a REAL, cagr REAL, change REAL, volatility REAL, open REAL, high REAL, low REAL, close REAL, volume INTEGER)')
        self.c.execute('DELETE FROM codes')# empty the codes table to insert new values for each stock
        self.fetchcsv()
        
    def fetchcsv(self):
        self.local_filename, self.headers = urllib.request.urlretrieve(self.url)# getting the zipfile
        self.zip_ref = zipfile.ZipFile(self.local_filename, 'r')
        self.csvfile = self.zip_ref.namelist()
        self.csvfile = self.csvfile[0]
        self.csvfile = self.zip_ref.extract(self.csvfile)# extracting the zipfile
        self.file = open(self.csvfile, 'r')
        self.file = csv.reader(self.file, delimiter = ',')
        self.fetchdf()
    
    def fetchdf(self):
        for self.row in self.file:
            try:
                self.df = quandl.get(self.row[0])
            except Exception as e:
                pass
                
            self.path = 'csv\\' + self.row[0][4:] + '.csv'
            self.df.to_csv(self.path, sep=',')
            self.df = self.df.fillna(value = 1)
            self.nse_code = self.row[0][4:] # 4
            self.quandl_code = self.row[0] # 3
            self.name = self.row[1] # 2
            self.open = self.df['Open'].tail(1).values
            self.high = self.df['High'].tail(1).values
            self.low = self.df['Low'].tail(1).values
            self.close = self.df['Close'].tail(1).values
            self.volume = self.df[self.df.columns[4]].tail(1).values
            self.calc()
            self.commitz()

    def calc(self):
        self.date = str(self.df.index[-1].date().year) + '-' + str(self.df.index[-1].date().month) + '-' + str(self.df.index[-1].date().day)# 1
        self.high_max = self.df['High'].max() # 6
        self.low_max = self.df['Low'].min()
        self.dg = self.df.tail(248)#one year's data
        self.high_52 = self.dg['High'].max()# one years max high
        self.low_52 = self.dg['Low'].min()# one years max low
        self.cagr = round((self.dg['Close'].iloc[-1] / self.dg['Close'].iloc[0]) - 1,3)# one year CAGR
        self.change = round(((self.df['Close'].iloc[-1] - self.df['Close'].iloc[-2]) / self.df['Close'].iloc[-1]) * 100,3)# last change
        self.volatility = round(((self.df['High'].iloc[-1] - self.df['Low'].iloc[-1]) / self.df['Low'].iloc[-1]) * 100,3)#last day's volatility
        self.high_52_b = 100 - ((self.close * 100)/self.high_52)
        self.low_52_a = ((self.close - self.low)* 100) / self.low
    
    def commitz(self):
        self.c.execute('INSERT INTO codes (date, name, quandl_code, nse_code, high_max, low_max, high_52, low_52, high_52_b, low_52_a, cagr, change, volatility, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (self.date, self.name, self.quandl_code, self.nse_code, self.high_max, self.low_max, self.high_52, self.low_52, self.high_52_b, self.low_52_a, self.cagr, self.change, self.volatility, self.open, self.high, self.low, self.close, self.volume))
        self.conn.commit()

    
    def finish(self):
        self.c.close()
        self.conn.close()
        print('start time : ', self.stime)
        print('end time: ', datetime.datetime.now())
        print('Total Download time : ', datetime.datetime.now() - self.stime)

obj = UpdateCodes()
obj.finish()
