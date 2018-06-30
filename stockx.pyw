from tkinter import Checkbutton, IntVar, Menu, Spinbox, StringVar, Text, Tk, Toplevel, messagebox, ttk
import csv, datetime, forecaster, quandl, reset_files, sqlite3, urllib.request, zipfile, meganalysis, pandas
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.animation as animation
from matplotlib.finance import candlestick2_ohlc
from matplotlib.widgets import Slider
quandl.ApiConfig.api_key = "yiSaMst67pW9Xesg9Zgy"

reset_files.vanish()

conn = sqlite3.connect('stockx.db')
c = conn.cursor()

stock_symbols = c.execute("SELECT nse_code FROM codes WHERE name NOT like '%index%' AND date LIKE '2018-6-2%' ORDER BY nse_code ASC")
stock_symbols = c.fetchall()
stock_symbols = ['[Select a Stock]'] + stock_symbols

index_symbols = c.execute("SELECT nse_code FROM codes WHERE name like '%index%' AND date LIKE '2018-6-2%' ORDER BY nse_code ASC")
index_symbols = c.fetchall()
index_symbols = ['[Select an Index]'] + index_symbols

stock_names = c.execute("SELECT name FROM codes WHERE date LIKE '2018-6-2%' ORDER BY name ASC")
stock_names = c.fetchall()
stock_names = ['[Select a Company]'] + stock_names

stockrow = []

class StockXApp(Tk):  # 3
    def __init__(self):  # 4
        Tk.__init__(self)
        self.title('StockX: Intelligent Analysis & Forecasting')
        self.state('zoomed')
        self.iconbitmap('C:\\Users\\Whistler.81\\Desktop\\StockX\\icon.ico')
        self.option_add('*tearOff', False)
        self.menubar = Menu(self)
        self.config(menu=self.menubar)
        self.file = Menu(self.menubar)
        self.help_ = Menu(self.menubar)
        self.screener = Menu(self.file)
        self.file.add_cascade(menu = self.screener, label = 'Stock Screener')
        self.screener.add_command(label = 'Basic', command=lambda: self.show_frame(Basic))
        self.screener.add_command(label = 'Advanced', command=lambda: self.show_frame(Advanced))
        self.menubar.add_cascade(menu=self.file, label='Application')
        self.menubar.add_cascade(menu=self.help_, label='Help')
        self.file.add_command(label='Technical Study', command=lambda: self.show_frame(Analysis))
        self.file.add_command(label='Forecast Screen', command=lambda: self.show_frame(Forecast))
        self.file.add_command(label='Exit', command=lambda: self.destroy())
        self.help_.add_command(label='Data fetcher', command=lambda: self.show_window(DataFetcher))
        
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}
        for F in (Basic, Analysis, Advanced, Forecast):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky="nsew")
        self.show_frame(Basic)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        frame.checkglobal()
    
    def show_window(self, this1):
        window = this1(self)
        window.title('StockX | Data Downloader')
        window.wm_resizable(height = False, width = False)

class Basic(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.f1 = ttk.Frame(self) # frame 1 holds the screener
        self.f1.pack(side = 'top')
        self.l0 = ttk.Label(self.f1, text = 'Select Stock By')
        self.l0.grid(row = 0, column = 0)
        self.choice = IntVar()
        self.r1 = ttk.Radiobutton(self.f1, text = 'NSE Symbol', variable = self.choice, value = 0, command = self.saywhat)
        self.r1.grid(row = 0, column = 1)
        self.r2 = ttk.Radiobutton(self.f1, text = 'Company Name', variable = self.choice, value = 1, command = self.saywhat)
        self.r2.grid(row = 0, column = 2)
        self.c1 = ttk.Combobox(self.f1)
        self.c1.grid(row = 0, column = 3)
        self.b1 = ttk.Button(self.f1, text = 'Submit', command = self.runscreener)
        self.b1.grid(row = 0, column = 4)
        self.b2 = ttk.Button(self.f1, text = 'Clear', command = reset_files.vanish)
        self.b2.grid(row = 0, column = 5)
        self.f2 = ttk.Frame(self)
        self.f2.pack(side = 'top')
        # date
        self.l4 = ttk.Label(self.f2, text = 'Date')
        self.l4.grid(row = 0, column = 0)
        self.l5 = ttk.Label(self.f2)
        self.l5.grid(row = 1, column = 0)
        # name
        self.l6 = ttk.Label(self.f2, text = 'Company')
        self.l6.grid(row = 0, column = 1)
        self.l7 = ttk.Label(self.f2)
        self.l7.grid(row = 1, column = 1)
        #symbol
        self.l8 = ttk.Label(self.f2, text = 'Symbol')
        self.l8.grid(row = 0, column = 2)
        self.l9 = ttk.Label(self.f2)
        self.l9.grid(row = 1, column = 2)
        # 52 week high
        self.l10 = ttk.Label(self.f2, text = '52 Week High')
        self.l10.grid(row = 0, column = 3)
        self.l11 = ttk.Label(self.f2)
        self.l11.grid(row = 1, column = 3)
        # 52 week low
        self.l12 = ttk.Label(self.f2, text = '52 week Low')
        self.l12.grid(row = 0, column = 4)
        self.l13 = ttk.Label(self.f2)
        self.l13.grid(row = 1, column = 4)
        # Max high
        self.l14 = ttk.Label(self.f2, text = 'Max High')
        self.l14.grid(row = 0, column = 5)
        self.l15 = ttk.Label(self.f2)
        self.l15.grid(row = 1, column = 5)
        # Max low
        self.l16 = ttk.Label(self.f2, text = 'Max Low')
        self.l16.grid(row = 0, column = 6)
        self.l17 = ttk.Label(self.f2)
        self.l17.grid(row = 1, column = 6)
        # CAGR
        self.l18 = ttk.Label(self.f2, text = 'CAGR')
        self.l18.grid(row = 0, column = 7)
        self.l19 = ttk.Label(self.f2)
        self.l19.grid(row = 1, column = 7)
        # Open
        self.l20 = ttk.Label(self.f2, text = 'Open')
        self.l20.grid(row = 0, column = 8)
        self.l21 = ttk.Label(self.f2)
        self.l21.grid(row = 1, column = 8)
        # High
        self.l22 = ttk.Label(self.f2, text = 'High')
        self.l22.grid(row = 0, column = 9)
        self.l23 = ttk.Label(self.f2)
        self.l23.grid(row = 1, column = 9)
        # Low
        self.l24 = ttk.Label(self.f2, text = 'Low')
        self.l24.grid(row = 0, column = 10)
        self.l25 = ttk.Label(self.f2)
        self.l25.grid(row = 1, column = 10)
        # price
        self.l26 = ttk.Label(self.f2, text = 'Price')
        self.l26.grid(row = 0, column = 11)
        self.l27 = ttk.Label(self.f2)
        self.l27.grid(row = 1, column = 11)
        # change
        self.l28 = ttk.Label(self.f2, text = 'Change')
        self.l28.grid(row = 0, column = 12)
        self.l29 = ttk.Label(self.f2)
        self.l29.grid(row = 1, column = 12)
        # chart controls
        self.f3 = ttk.Frame(self)
        self.f3.pack(side = 'top')
        self.abutton = ttk.Button(self.f3, text = 'Analyse Stock', command = self.go_ta)
        self.bbutton = ttk.Button(self.f3, text = 'Forecast Stock', command = self.go_fc)
        self.abutton.grid(row = 0, column = 0)
        self.bbutton.grid(row = 0, column = 1)
        # chart
        self.f = Figure(figsize=(14,6))
        self.f.suptitle('Chart')
        self.b = self.f.add_subplot(111)
        self.f.subplots_adjust(left=0.06, right=0.96, top=0.95, bottom=0.19)
        self.canvas = FigureCanvasTkAgg(self.f, self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True)
        self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side='bottom', fill='both', expand=True)
        self.ani_b = animation.FuncAnimation(self.f, self.animate, interval=500)
        # number of rows selector for the graph
        self.f4 = ttk.Frame(self)
        self.f4.pack(side = 'top')
        self.b2 = ttk.Button(self.f4, text = '1 Week', command = lambda: self.drawgraph(code = stockrow[0][3], rc = 5))
        self.b3 = ttk.Button(self.f4, text = '2 Week', command = lambda: self.drawgraph(code = stockrow[0][3], rc = 10))
        self.b4 = ttk.Button(self.f4, text = '1 Month', command = lambda: self.drawgraph(code = stockrow[0][3], rc = 20))
        self.b5 = ttk.Button(self.f4, text = '3 Months', command = lambda: self.drawgraph(code = stockrow[0][3], rc = 40))
        self.b6 = ttk.Button(self.f4, text = '1 Year', command = lambda: self.drawgraph(code = stockrow[0][3], rc = 100))
        #self.b7 = ttk.Button(self.f4, text = 'All Time', command = lambda: self.drawgraph(code = stockrow[0][3], rc = 999999999))
        self.b2.grid(row = 0, column = 0)
        self.b3.grid(row = 0, column = 1)
        self.b4.grid(row = 0, column = 2)
        self.b5.grid(row = 0, column = 3)
        self.b6.grid(row = 0, column = 4)
        #self.b7.grid(row = 0, column = 5)

    def go_ta(self):
        if(len(stockrow) == 0):
            messagebox.showinfo('No Stock Selected', 'Please select a stock to forecast or analyse.')
        elif(len(stockrow) != 0):
            app.show_frame(Analysis)
        else:
            messagebox.showerror('Unknown Error', 'Unknown error found at line StockX.pyw/210')

    def go_fc(self):
        if(len(stockrow) == 0):# if less than 1 stock selected forecast & analysis no go
            messagebox.showinfo('No Stock Selected', 'Please select a stock to forecast or analyse.')
        elif(len(stockrow) != 0):# if more than 1 stock selected forecast is a go & analysis no go
            app.show_frame(Forecast)
        else:
            messagebox.showerror('Unknown Error', 'Unknown error found at line StockX.pyw/210')

    def saywhat(self):
        if(self.choice.get() == 0):
            self.c1.config(values = stock_symbols)
            self.c1.current(0)
        elif(self.choice.get() == 1):
            self.c1.config(values = stock_names)
            self.c1.current(0)      
        else:
            messagebox.showerror('Unknown Error', 'Neither a stock nor a company name was selected.')
    
    def runscreener(self):
        global stockrow#, df
        c.execute("SELECT * FROM codes WHERE nse_code = ? OR name  = ? AND date LIKE '2018-6-2%'", (self.c1.get(), self.c1.get()[1:-1])) # use SQL OR here
        stockrow = c.fetchall()
        
        self.l5.config(text = stockrow[0][0])# date
        self.l7.config(text = stockrow[0][1])# name
        self.l9.config(text = stockrow[0][3])# symbol
        self.l11.config(text = stockrow[0][7])# 52 week high
        self.l13.config(text = stockrow[0][8])# 52 week low
        self.l15.config(text = stockrow[0][5])# Max high
        self.l17.config(text = stockrow[0][6])# Max low
        self.l19.config(text = stockrow[0][9])# CAGR
        self.l21.config(text = stockrow[0][12])# Open
        self.l23.config(text = stockrow[0][13])# High
        self.l25.config(text = stockrow[0][14])# Low
        self.l27.config(text = stockrow[0][15])# Close
        self.l29.config(text = stockrow[0][10])# Change
        self.f.suptitle(stockrow[0][1])
        self.drawgraph(code = stockrow[0][3])

    def drawgraph(self, code = '', rc = 10):
        self.p1 = open('b_s_p.txt', 'w')
        self.p2 = open('b_s_d.txt', 'w')
        self.f = open('csv\\' + code + '.csv', 'r')
        self.c = csv.reader(self.f)
        self.lines = [self.row for self.row in self.c]
        for self.line in self.lines[-rc:]:
            self.p1.write(str(self.line[4]))
            self.p1.write('\n')
            self.p2.write(str(self.line[0]))
            self.p2.write('\n')
        self.p1.close()
        self.p2.close()
    
    def animate(self, i):
        self.p1 = open('b_s_p.txt','r').read()
        self.p2 = open('b_s_d.txt', 'r').read()
        self.d1 = self.p1.split('\n')
        self.d2 = self.p2.split('\n')
        self.xlist = []
        self.ylist = []
        for eachLine in self.d1:
            if len(eachLine) > 1:
                self.xlist.append(eachLine)
        for eachLine in self.d2:
            if len(eachLine) > 1:            
                self.ylist.append(eachLine)
        self.b.clear()
        self.b.set_xlabel('Dates')
        self.b.set_ylabel('Prices (₹)')
        self.b.plot(self.ylist, self.xlist)
        # self.b.yaxis.set_major_locator(mticker.MaxNLocator(6))
        # self.g.autofmt_xdate(rotation = 30, ha = 'right', which = 'both')
    
    def checkglobal(self):
        pass
        
class Advanced(ttk.Frame):
    
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        # frame for the controls
        self.f1 = ttk.Frame(self)
        self.f1.pack(fill = 'both', side = 'left')
        # frame for the result display area
        self.f2 = ttk.Frame(self)
        self.f2.pack(fill = 'both', expand = True, side = 'left')
        self.header = ttk.Frame(self.f2)
        self.header.pack(side = 'top')
        self.date = ttk.Label(self.header, text = 'Date')
        self.date.pack(side = 'left', padx = 5, pady = 2)
        self.name = ttk.Label(self.header, text = 'Name')
        self.name.pack(side = 'left', padx = 5, pady = 2)
        self.symbol = ttk.Label(self.header, text = 'Symbol')
        self.symbol.pack(side = 'left', padx = 5, pady = 2)
        self.price = ttk.Label(self.header, text = 'Last Traded Price')
        self.price.pack(side = 'left', padx = 5, pady = 2)
        self.result = ttk.Frame(self.f2)
        self.result.pack(side = 'top', padx = 2, pady = 2)
        self.output = Text(self.result, width = 100, height =40)
        self.output.pack()

        # parameters add to frame 1
        self.lf1 = ttk.Labelframe(self.f1, text = 'Price Range : ', labelanchor = 'n') # 1st Labelframe
        self.lf1.pack()#grid(row = 0, column = 0, sticky = 'nsew')
        self.lf1l = ttk.Label(self.lf1, text = 'Lower Limit', background = 'gray80', justify = 'center')
        self.lf1l.pack(side = 'left')#grid(row = 0 , column = 0, sticky ='nsew')
        self.lf1u = ttk.Label(self.lf1, text = 'Upper Limit', background = 'gray80', justify = 'center')
        self.lf1u.pack(side = 'right')#grid(row = 0 , column = 1, sticky ='nsew')
        self.s1 = Spinbox(self.lf1, format='%10.3f', from_ = 0, to = 100000, justify = 'center', background = 'gray80')# 1 price LB
        self.s2 = Spinbox(self.lf1, format='%10.3f', from_ = 0, to = 100000, justify = 'center', background = 'gray80')# 2 price UB
        self.s1.pack(side = 'left')#grid(row = 1, column = 0, sticky ='nsew')
        self.s2.pack(side = 'right')#grid(row = 1, column = 1, sticky ='nsew')
        
        self.lf2 = ttk.Labelframe(self.f1, text ='Change Percentage Range', labelanchor = 'n') # 2nd Labelframe
        self.lf2.pack()#grid(row = 1, column = 0, sticky = 'nsew')
        self.lf2l = ttk.Label(self.lf2, text = 'Lower Limit', background = 'gray80')
        self.lf2l.pack(side = 'left')#grid(row = 0, column = 0, sticky ='nsew')
        self.lf2u = ttk.Label(self.lf2, text = 'Upper Limit', background = 'gray80')
        self.lf2u.pack(side = 'right')#grid(row = 0, column = 1, sticky ='nsew')
        self.s3 = Spinbox(self.lf2, format='%10.3f', from_ = -100, to = 100, justify = 'center', background = 'gray80')# 3 change % LB
        self.s4 = Spinbox(self.lf2, format='%10.3f', from_ = -100, to = 100, justify = 'center', background = 'gray80')#4 change % UB
        self.s3.pack(side = 'left')#grid(row = 1, column = 0, sticky ='nsew')
        self.s4.pack(side = 'right')#grid(row = 1, column = 1, sticky = 'nsew')
        
        self.lf3 = ttk.Labelframe(self.f1, text = 'Compound Annual Growth Rate', labelanchor = 'n') # 3rd LabelFrame
        self.lf3.pack()#grid(row = 2 , column = 0, sticky = 'nsew')
        self.lf3l = ttk.Label(self.lf3, text = 'Lower Limit', background = 'gray80')
        self.lf3l.pack(side = 'left')#grid(row = 0, column = 0, sticky ='nsew')
        self.lf3u = ttk.Label(self.lf3, text = 'Upper Limit', background = 'gray80')
        self.lf3u.pack(side = 'right')#grid(row = 0, column = 1, sticky ='nsew')
        self.s5 = Spinbox(self.lf3, format='%10.3f', from_ = -100, to = 100, justify = 'center', background = 'gray80')# 5 CARG LB
        self.s6 = Spinbox(self.lf3, format='%10.3f', from_ = -100, to = 100, justify = 'center', background = 'gray80')# 6 CAGR UB
        self.s5.pack(side = 'left')#grid(row = 1, column = 0, sticky = 'nsew')
        self.s6.pack(side = 'right')#grid(row = 1, column = 1, sticky = 'nsew')
        
        self.lf4 = ttk.Labelframe(self.f1, text = 'Volatility Range', labelanchor = 'n') # 4th LabelFrame
        self.lf4.pack()#grid(row = 3 , column = 0, sticky = 'nsew')
        self.lf4l = ttk.Label(self.lf4, text = 'Lower Limit', background = 'gray80')
        self.lf4l.pack(side = 'left')#grid(row = 0, column = 0, sticky ='nsew')
        self.lf4u = ttk.Label(self.lf4, text = 'Upper Limit', background = 'gray80')
        self.lf4u.pack(side = 'right')#grid(row = 0, column = 1, sticky ='nsew')
        self.s7 = Spinbox(self.lf4, format='%10.3f', from_ = 0, to = 100, justify = 'center', background = 'gray80')# 5 CARG LB
        self.s8 = Spinbox(self.lf4, format='%10.3f', from_ = 0, to = 100, justify = 'center', background = 'gray80')# 6 CAGR UB
        self.s7.pack(side = 'left')#grid(row = 1, column = 0, sticky = 'nsew')
        self.s8.pack(side = 'right')#grid(row = 1, column = 1, sticky = 'nsew')
        
        self.lf5 = ttk.Labelframe(self.f1, text = 'Stocks Trading Within', labelanchor = 'n') # 5th LabelFrame 
        self.lf5.pack(fill = 'both')#grid(row = 4, column = 0, sticky = 'nsew')
        self.l5 = ttk.Label(self.lf5, text = '%\ below its 1 Year High', background = 'gray80')
        self.l5.pack(fill = 'both')#grid(row = 0 , column = 0, columnspan = 2, sticky = 'nsew')
        self.s9 = Spinbox(self.lf5, format='%10.3f', from_ = 0, to = 100, justify = 'center', background = 'gray80')# 9 % below 52 week High
        self.s9.pack(fill = 'both')#grid(row = 1, column = 0, columnspan = 2, sticky = 'nsew')
        
        self.l6 = ttk.Label(self.lf5, text = '%\ above its 1 Year Low ', background = 'gray80')
        self.l6.pack(fill = 'both')#grid(row = 2 , column = 0, columnspan = 2, sticky = 'nsew')
        self.s10 = Spinbox(self.lf5, format='%10.3f', from_ = 0, to = 100, justify = 'center', background = 'gray80')# 10 % above its 52 week Low
        self.s10.pack(fill = 'both')#grid(row = 3, column = 0, columnspan = 2, sticky = 'nsew')
        
        self.l9 = ttk.Label(self.lf5, text = '%\ below its Max High', background = 'gray80')
        self.l9.pack(fill = 'both')#grid(row = 4 , column = 0, columnspan = 2, sticky = 'nsew')
        self.s11 = Spinbox(self.lf5, format='%10.3f', from_ = 0, to = 100, justify = 'center', background = 'gray80')# 11 % below its max high price
        self.s11.pack(fill = 'both')#grid(row = 5, column = 0, columnspan = 2, sticky = 'nsew')
        
        self.l11 = ttk.Label(self.lf5, text = '%\ above its Max Low', background = 'gray80')
        self.l11.pack(fill = 'both')#grid(row = 6 , column = 0, columnspan = 2, sticky = 'nsew')
        self.s12 = Spinbox(self.lf5, format='%10.3f', from_ = 0, to = 100, justify = 'center', background = 'gray80')# 12 % above its max low price
        self.s12.pack(fill = 'both')#grid(row = 7, column = 0, columnspan = 2, sticky = 'nsew')
        
        self.b1 = ttk.Button(self.lf5, text = 'Reset', command = self.cleanslate)
        self.b2 = ttk.Button(self.lf5, text = 'Submit', command = self.getparams)
        self.b1.pack(side = 'left',fill = 'both', expand = True)#grid(row = 8, column = 0, sticky = 'nsew')
        self.b2.pack(side = 'right', fill = 'both', expand = True)#grid(row = 8, column = 1, sticky = 'nsew')

        self.lf6 = ttk.Labelframe(self.f1, text = 'Select Forecast or Analyse', labelanchor = 'n') # 6th LabelFrame
        self.lf6.pack(fill = 'both')#grid(row = 5, column = 0, sticky = 'nsew')

        self.l13 = ttk.Label(self.lf6, text = 'Select Stock', background = 'grey80')
        self.l13.pack(fill = 'both')#grid(row = 0, column = 0, columnspan = 2, sticky = 'nsew')
        self.c1 = ttk.Combobox(self.lf6)
        self.c1.pack(fill = 'both')#grid(row = 1, column = 0, columnspan = 2, sticky = 'nsew')
        self.b3 = ttk.Button(self.lf6, text = 'Analyse', command = self.go_ta)
        self.b4 = ttk.Button(self.lf6, text = 'Forecast', command = self.go_fc)
        self.b3.pack(side = 'left', expand = True, fill = 'both')#grid(row = 2, column = 0, sticky = 'nsew')
        self.b4.pack(side = 'right', expand = True, fill = 'both')#grid(row = 2, column = 1, sticky = 'nsew')

    def cleanslate(self):
        self.output.delete('1.0', 'end')
        
    def getparams(self):
        global stockrow#, df
        self.masterlist = set()
        # fetch stocks within price range
        c.execute("SELECT nse_code FROM codes WHERE close BETWEEN ? AND ? AND date LIKE '2018-6-2%'",(self.s1.get(), self.s2.get()))
        data232 = c.fetchall()
        for row in data232:
            self.masterlist.add(row[0])
        # fetch stocks within change % range
        c.execute("SELECT nse_code FROM codes WHERE change BETWEEN ? AND ? AND date LIKE '2018-6-2%'",(self.s3.get(), self.s4.get()))
        data232 = c.fetchall()
        for row in data232:
            self.masterlist.intersection(row[0])
        # fetch stocks within CAGR range
        c.execute("SELECT nse_code FROM codes WHERE cagr BETWEEN ? AND ? AND date LIKE '2018-6-2%'",(self.s5.get(), self.s6.get()))
        data232 = c.fetchall()
        for row in data232:
            self.masterlist.intersection(row[0])
        # fetch stocks within volatility range
        c.execute("SELECT nse_code FROM codes WHERE volatility BETWEEN ? AND ? AND date LIKE '2018-6-2%'",(self.s7.get(), self.s8.get()))
        data232 = c.fetchall()
        for row in data232:
            self.masterlist.intersection(row[0])
        # last 4 queries ignored dont tell anyone
        self.masterlist = list(self.masterlist)# converting set to list
        self.c1.config(values = self.masterlist)
        for i in range (1, len(self.masterlist)+1) :

            c.execute("SELECT * from codes WHERE nse_code = ? AND date like '2018-6-2%' ORDER BY close ASC", (self.masterlist[i],))
            stockrow = c.fetchall()

            self.output.insert(str(i)+'.0', stockrow[0][0])
            self.output.insert(str(i)+'.0', '\t')
            self.output.insert(str(i)+'.0', stockrow[0][1])
            self.output.insert(str(i)+'.0', '\t')
            self.output.insert(str(i)+'.0', stockrow[0][3])
            self.output.insert(str(i)+'.0', '\t')
            self.output.insert(str(i)+'.0', stockrow[0][16])
            #self.output.insert(str(i)+'.0', '\t')
            self.output.insert('end', '\n\n')
            # elist.append(stockrow[0][0])
            # elist.append(stockrow[0][1])
            # elist.append(stockrow[0][3])
            # elist.append(stockrow[0][16])

            # for j in range(0, len(elist)):


                # self.l55 = ttk.Label(self.result, text = elist[j])
                # self.l55.grid(row = i, column = j, padx = 2, pady = 2, sticky = 'nsew')
    
    def checkglobal(self):
        pass
    
    def go_ta(self):
        global stockrow
        if self.c1.get() == '' :
            messagebox.showinfo('No Stock Selected', 'Please select a stock to forecast or analyse.')
        elif(self.c1.get != ''):
            c.execute("SELECT * from codes WHERE nse_code = ? AND date like '2018-6-2%' ORDER BY close ASC", (self.c1.get(),))
            stockrow = c.fetchall()
            app.show_frame(Analysis)
        else:
            messagebox.showerror('Unknown Error', 'Unknown error found at line StockX.pyw/210')

    def go_fc(self):
        global stockrow
        if(self.c1.get() == ''):# if less than 1 stock selected forecast & analysis no go
            messagebox.showinfo('No Stock Selected', 'Please select a stock to forecast or analyse.')
        elif(self.c1.get != ''):# if more than 1 stock selected forecast is a go & analysis no go
            c.execute("SELECT * from codes WHERE nse_code = ? AND date like '2018-6-2%' ORDER BY close ASC", (self.c1.get(),))
            stockrow = c.fetchall()

            app.show_frame(Forecast)
        else:
            messagebox.showerror('Unknown Error', 'Unknown error found at line StockX.pyw/210')

class Analysis(ttk.Frame):
    
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        #self.okayCommand = self.register(self.entryvalidate)
        
        self.f1 = ttk.Frame(self)
        self.f1.grid(row = 0, column = 0)#pack(side ='top')
        
        self.f2 = ttk.Frame(self) # this frame for controls
        self.f2.grid(row = 1, column = 0)
        
        self.f3 = ttk.Frame(self)
        self.f3.grid(row = 2, column = 0)
        
        self.l1 = ttk.Label(self.f1, text = 'Company', background = 'grey80')
        self.l2 = ttk.Label(self.f1, text = 'Symbol', background = 'grey80')
        self.l3 = ttk.Label(self.f1, text = 'Open', background = 'grey80')
        self.l4 = ttk.Label(self.f1, text = 'High', background = 'grey80')
        self.l5 = ttk.Label(self.f1, text = 'Low', background = 'grey80')
        self.l6 = ttk.Label(self.f1, text = 'Close', background = 'grey80')
        self.l7 = ttk.Label(self.f1, text = 'Change', background = 'grey80')
        self.l8 = ttk.Label(self.f1, text = 'Date', background = 'grey80')
        self.l1.grid(row = 0, column = 0, ipadx = 2, ipady = 2, sticky = 'ew')
        self.l2.grid(row = 0, column = 1, ipadx = 2, ipady = 2, sticky = 'ew')
        self.l3.grid(row = 0, column = 2, ipadx = 2, ipady = 2, sticky = 'ew')
        self.l4.grid(row = 0, column = 3, ipadx = 2, ipady = 2, sticky = 'ew')
        self.l5.grid(row = 0, column = 4, ipadx = 2, ipady = 2, sticky = 'ew')
        self.l6.grid(row = 0, column = 5, ipadx = 2, ipady = 2, sticky = 'ew')
        self.l7.grid(row = 0, column = 6, ipadx = 2, ipady = 2, sticky = 'ew')
        self.l8.grid(row = 0, column = 7, ipadx = 2, ipady = 2, sticky = 'ew')
        # frame 2 controls Line/Candlestick, TA, Parameters

        self.graph = IntVar()
        self.r1 = ttk.Radiobutton(self.f1, text = 'Line Graph', value = 0, variable = self.graph)
        self.r2 = ttk.Radiobutton(self.f1, text = 'Candlestick', value = 1, variable = self.graph)
        self.r1.grid(row = 0, column = 8, ipadx = 2, ipady = 2, sticky = 'ew')
        self.r2.grid(row = 0, column = 9, ipadx = 2, ipady = 2, sticky = 'ew')
        
        self.indicator = StringVar()
        self.var = StringVar()
        #self.var.set() # default value
        self.op = ttk.OptionMenu(self.f1, self.var, "Select an Indicator", "Parabolic SAR", "Stochastic", "Average True Range", "Simple Moving Average", "Relative Strength Index", "MACD" , "Bollinger Bands", command = lambda x: self.displayaprams(self.var.get()))
        self.op.grid(row = 0, column = 10, ipadx = 2, ipady = 2, sticky = 'ew')

        self.f = Figure(figsize = (14,7))
        self.x, self.y = self.f.subplots(2,1, gridspec_kw = {'height_ratios' : [3,1]}, sharex= True)
        self.f.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15)
        self.canvas = FigureCanvasTkAgg(self.f, self.f3)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(row = 0, column = 0, columnspan = 11)
        # self.a_main = animation.FuncAnimation(self.f, self.animate_main, interval=500)
        self.a_line = animation.FuncAnimation(self.f, self.animate_line, interval=500)

    def displayaprams(self, ind):

        if ind == 'Parabolic SAR':
            #add two entry fields
            self.f2.destroy()
            self.f2 = ttk.Frame(self)
            self.f2.grid(row = 1, column = 0, ipadx = 2, ipady = 2)
            self.l10 = ttk.Label(self.f2, text = 'Enter Acceleration (default 0.02)')
            self.l10.grid(row = 0, column = 1, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e10 = ttk.Entry(self.f2)
            self.e10.grid(row = 0, column = 2, ipadx = 2, ipady = 2, sticky = 'ew')
            
            self.l11 = ttk.Label(self.f2, text = 'Enter Maximum (default 0.2)')
            self.l11.grid(row = 0, column = 3, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e11 = ttk.Entry(self.f2)
            self.e11.grid(row = 0, column = 4, ipadx = 2, ipady = 2, sticky = 'ew')
            self.b01 = ttk.Button(self.f2, text = 'Display Graph', command = self.runanalysis)
            self.b01.grid(row = 0, column = 5, ipadx = 2, ipady = 2, sticky = 'ew')

        elif ind == 'Stochastic':
            #add two entry fields
            self.f2.destroy()
            self.f2 = ttk.Frame(self)
            self.f2.grid(row = 1, column = 0, ipadx = 2, ipady = 2)
            self.l10 = ttk.Label(self.f2, text = 'fastk_period (default 14)')
            self.l10.grid(row = 1, column = 1, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e10 = ttk.Entry(self.f2)
            self.e10.grid(row = 1, column = 2, ipadx = 2, ipady = 2, sticky = 'ew')

            self.l11 = ttk.Label(self.f2, text = 'slowk_period (default 3)')
            self.l11.grid(row = 1, column = 3, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e11 = ttk.Entry(self.f2)
            self.e11.grid(row = 1, column = 4, ipadx = 2, ipady = 2, sticky = 'ew')
            
            self.l12 = ttk.Label(self.f2, text = 'slowd_period (default 3)')
            self.l12.grid(row = 1, column = 5, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e11 = ttk.Entry(self.f2)
            self.e11.grid(row = 1, column = 6, ipadx = 2, ipady = 2, sticky = 'ew')
            
            self.b01 = ttk.Button(self.f2, text = 'Display Graph', command = self.runanalysis)
            self.b01.grid(row = 1, column = 7, ipadx = 2, ipady = 2, sticky = 'ew')

        elif ind == 'Average True Range' or ind == 'Simple Moving Average' or ind == 'Relative Strength Index' or ind == 'Bollinger Bands':
            #add two entry fields
            self.f2.destroy()
            self.f2 = ttk.Frame(self)   
            self.f2.grid(row = 1, column = 0, ipadx = 2, ipady = 2)
            self.l10 = ttk.Label(self.f2, text = 't_period (default 14)')
            self.l10.grid(row = 1, column = 1, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e10 = ttk.Entry(self.f2)
            self.e10.grid(row = 1, column = 2, ipadx = 2, ipady = 2, sticky = 'ew')
            
            self.b01 = ttk.Button(self.f2, text = 'Display Graph', command = self.runanalysis)
            self.b01.grid(row = 1, column = 3, ipadx = 2, ipady = 2, sticky = 'ew')
        
        elif ind == 'Simple Moving Average':
            #add two entry fields
            self.f2.destroy()
            self.f2 = ttk.Frame(self)
            self.f2.grid(row = 1, column = 0, ipadx = 2, ipady = 2)
            self.l10 = ttk.Label(self.f2, text = 't_period (default 14)')
            self.l10.grid(row = 1, column = 1, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e10 = ttk.Entry(self.f2)
            self.e10.grid(row = 1, column = 2, ipadx = 2, ipady = 2, sticky = 'ew')
            
            self.b01 = ttk.Button(self.f2, text = 'Display Graph', command = self.runanalysis)
            self.b01.grid(row = 1, column = 3, ipadx = 2, ipady = 2, sticky = 'ew')
        
        elif ind == 'MACD':
            self.f2.destroy()
            self.f2 = ttk.Frame(self)
            self.f2.grid(row = 1, column = 0, ipadx = 2, ipady = 2)
            #add two entry fields
            self.l10 = ttk.Label(self.f2, text = 'fastperiod (default 14)')
            self.l10.grid(row = 1, column = 1, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e10 = ttk.Entry(self.f2)
            self.e10.grid(row = 1, column = 2, ipadx = 2, ipady = 2, sticky = 'ew')

            self.l11 = ttk.Label(self.f2, text = 'slowperiod (default 26)')
            self.l11.grid(row = 1, column = 3, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e11 = ttk.Entry(self.f2)
            self.e11.grid(row = 1, column = 4, ipadx = 2, ipady = 2, sticky = 'ew')
            
            self.l12 = ttk.Label(self.f2, text = 'signalperiod (default 9)')
            self.l12.grid(row = 1, column = 5, ipadx = 2, ipady = 2, sticky = 'ew')
            self.e11 = ttk.Entry(self.f2)
            self.e11.grid(row = 1, column = 6, ipadx = 2, ipady = 2, sticky = 'ew')
            
            self.b01 = ttk.Button(self.f2, text = 'Display Graph', command = self.runanalysis)
            self.b01.grid(row = 1, column = 7, ipadx = 2, ipady = 2, sticky = 'ew')
                
    def runanalysis(self ,rc = 10): # this is the main function
        if self.graph.get() == 0:
            meganalysis.line(rows = 10)# writes series to text file
            

    def checkglobal(self):
        if len(stockrow) == 0:
            pass
        else:
            self.l1.config(text = stockrow[0][1])
            self.l2.config(text = stockrow[0][3])
            self.l3.config(text = stockrow[0][13])
            self.l4.config(text = stockrow[0][14])
            self.l5.config(text = stockrow[0][15])
            self.l6.config(text = stockrow[0][16])
            self.l7.config(text = stockrow[0][11])
            self.l8.config(text = stockrow[0][0])

            meganalysis.megacrunch(stock = stockrow[0][3])
    
    def animate_line(self, i):
        self.x.clear()
        df = pandas.read_csv('linegraph.csv')
        self.x.set_xlabel('Dates')
        self.x.set_ylabel('Prices (₹)')
        self.x.plot_date(df['Date'].values, df['Close'].values, xdate = True, linestyle='solid', marker='None' )


class Forecast(ttk.Frame):
    
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        self.fl = ttk.Frame(self) # controls panel
        self.fl.pack(side = 'left', anchor = 'n')

        self.fr = ttk.Frame(self) # display area container
        self.fr.pack(side = 'right', fill = 'both', expand = True)
        self.ft = ttk.Frame(self.fr)
        self.fb = ttk.Frame(self.fr)
        self.ft.pack(side = 'top')
        self.fb.pack(side = 'right', fill = 'both', expand = True)

        self.l01 = ttk.Label(self.fl, text='Select a Stock', background='skyblue')
        self.l01.pack(anchor='n', fill='both')
        self.combo1 = ttk.Combobox(self.fl, values=stock_symbols)  # select a stock      1
        self.combo1.pack(fill='both')
        self.combo1.current(0)
        self.l02 = ttk.Label(self.fl, text='Days to Forecast', background='skyblue')
        self.l02.pack(anchor='n', fill='both')
        self.spinb1 = Spinbox(self.fl, from_=1, to=7)  # select days to forecast      2
        self.spinb1.pack(fill='both')
        self.lf1 = ttk.LabelFrame(self.fl, text='Select Features', labelanchor='n')
        self.lf1.pack(fill='both')
        self.l553 = ttk.Label(self.lf1, text='Select an Index', background='skyblue')
        self.l553.pack(fill='both')
        self.combo2 = ttk.Combobox(self.lf1, values=index_symbols)  # select an index    3
        self.combo2.pack(fill='both')
        self.combo2.current(0)
        self.l554 = ttk.Label(self.lf1, text='Technical Indicators', background='skyblue')
        self.l554.pack(fill='both')
        self.sar = IntVar()
        self.check1 = Checkbutton(self.lf1, text='Parabolic SAR', onvalue=1, offvalue=0, variable=self.sar)  # 10#1
        self.check1.pack(fill='both')
        self.so = IntVar()
        self.check2 = Checkbutton(self.lf1, text='Stochastic Oscillator', onvalue=1, offvalue=0, variable=self.so)  # 102
        self.check2.pack(fill='both')
        self.rsi = IntVar()
        self.check3 = Checkbutton(self.lf1, text='Relative Strength Index', onvalue=1, offvalue=0, variable=self.rsi)  # 93
        self.check3.pack(fill='both')
        self.atr = IntVar()
        self.check4 = Checkbutton(self.lf1, text='Average True Range', onvalue=1, offvalue=0, variable=self.atr)  # 114
        self.check4.pack(fill='both')
        self.sma = IntVar()
        self.check5 = Checkbutton(self.lf1, text='Simple Moving Average', onvalue=1, offvalue=0, variable=self.sma)  # 65
        self.check5.pack(fill='both')
        self.macd = IntVar()
        self.check6 = Checkbutton(self.lf1, text='MACD', onvalue=1, offvalue=0, variable=self.macd)  # 106
        self.check6.pack(fill='both')
        self.l556 = ttk.Label(self.lf1, text='Select Column to Forecast', background='skyblue')
        self.l556.pack(fill='both')
        self.combo3 = ttk.Combobox(self.lf1, values=['Close', 'High', 'Low', 'Open'])
        self.combo3.pack(fill='both')
        self.combo3.current(0)
        self.button = ttk.Button(self.lf1, text='Forecast', command=self.forecast)  ##calls forecast function
        self.button.pack(fill='both')
        self.button = ttk.Button(self.lf1, text='Clear Selections', command=self.setzero)
        self.button.pack(fill='both')
        self.l556 = ttk.Label(self.fl, text='CONSOLE', background='skyblue')
        self.l556.pack(fill='both')
        self.output = Text(self.fl, width = 25, height = 16, wrap='word')
        self.output.pack(fill='both')

        self.f = Figure()# figsize=(5,5)
        self.a = self.f.add_subplot(111)
        self.f.subplots_adjust(left=0.1, right=0.95, top=0.95, bottom=0.15)
        self.canvas = FigureCanvasTkAgg(self.f, self.fb) # self.f
        self.canvas.show()
        self.canvas._tkcanvas.pack(side='bottom', fill='both', expand=True)
        self.ani_a = animation.FuncAnimation(self.f, self.animate, interval=500)
        # self.canvas.get_tk_widget().pack(side='top', fill='both', expand=True)
        # self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.ft)
        # self.toolbar.update()

    # forecast function start
    def forecast(self):  # forecast fetches all the inputs and sends it to the forecast module for regression
        self.result, self.name = forecaster.forecast(self.combo1.get().upper(), self.spinb1.get(), self.combo2.get(), self.sar.get(), self.so.get(), self.rsi.get(),self.atr.get(), self.sma.get(), self.macd.get(), self.combo3.get())

        self.output.insert('end', 'Stock Selected')
        self.output.insert('end', '\n')
        self.output.insert('end', self.name + '\n')
        self.output.insert('end', '\n')
        for row in self.result:
            self.output.insert('end', row)
            self.output.insert('end', '\n')

    # forecast function end
    def setzero(self):
        self.combo1.current(0)
        self.spinb1.selection_clear()
        self.combo2.current(0)
        self.sar.set(0)
        self.so.set(0)
        self.rsi.set(0)
        self.atr.set(0)
        self.sma.set(0)
        self.macd.set(0)
        self.combo3.current(0)
        self.check1.deselect()
        self.check2.deselect()
        self.check3.deselect()
        self.check4.deselect()
        self.check5.deselect()
        self.check6.deselect()
    
    def animate(self, i):
        self.p1 = open("f_p.txt","r").read()
        self.p2 = open("f_d.txt","r").read()
        self.d1 = self.p1.split('\n')
        self.d2 = self.p2.split('\n')
        self.xList = []
        self.yList = []
        for eachLine in self.d1:
            if len(eachLine) > 1:
                self.xList.append(eachLine)
        for eachLine in self.d2:
            if len(eachLine) > 1:            
                self.yList.append(eachLine)
        self.a.clear()
        self.a.plot(self.yList, self.xList)

        self.a.set_xlabel('Dates')
        self.a.set_ylabel('Prices (₹)')
    
    def checkglobal(self):

        if len(stockrow) != 0:
            self.combo1.set(stockrow[0][3])
            self.output.insert('end','Stock Selected from Screener.\n')
            self.output.insert('end',stockrow[0][2])
            self.output.insert('end','\n.')

class DataFetcher(Toplevel):

    def __init__(self, parent):
        Toplevel.__init__(self, parent)
        self.count = 0
        self.done = 0
        self.left = self.count
        self.la1 = ttk.Label(self, text = 'Database Creator')
        self.la1.grid(row = 0, column = 0, columnspan = 2, sticky = 'nsew')
        self.la2 = ttk.Label(self, text = 'Download Quandl dataframes to CSV.')
        self.la2.grid(row = 1, column = 0, sticky = 'nsew', columnspan = 2)
        self.info1 = ttk.Label(self, text = 'Total Datasets : ')
        self.info1.grid(row = 2, column = 0, sticky = 'nsew')
        self.infoa = ttk.Label(self)
        self.infoa.grid(row = 2, column = 1, sticky = 'nsew')
        self.info2 = ttk.Label(self, text = 'Total Done : ')
        self.info2.grid(row = 3, column = 0, sticky = 'nsew')
        self.infob = ttk.Label(self, text = '0')
        self.infob.grid(row = 3, column = 1, sticky = 'nsew')
        self.info3 = ttk.Label(self, text = 'Total Remaining : ')
        self.info3.grid(row = 4, column = 0, sticky = 'nsew')
        self.infoc = ttk.Label(self, text = '0')
        self.infoc.grid(row = 4, column = 1, sticky = 'nsew')
        self.info4 = ttk.Label(self, text = 'Percentage : ')
        self.info4.grid(row = 5, column = 0, sticky = 'nsew')
        self.infod = ttk.Label(self, text = '0')
        self.infod.grid(row = 5, column = 1, sticky = 'nsew')
        self.pbar = ttk.Progressbar(self, mode = 'determinate', maximum = self.count)
        self.pbar.grid(row = 6, column = 0, columnspan = 2, sticky = 'nsew')
        self.b1 = ttk.Button(self, text = 'Quit', command = self.quitapp)
        self.b1.grid(row = 7, column = 0, sticky = 'nsew')
        self.b2 = ttk.Button(self, text = 'Start', command = self.fetchcsv)
        self.b2.grid(row = 7, column = 1, sticky = 'nsew')
        self.stime = datetime.datetime.now()
        self.url = r'https://www.quandl.com/api/v3/databases/NSE/codes?api_key=yiSaMst67pW9Xesg9Zgy'# url of the zip file
        c.execute('CREATE TABLE IF NOT EXISTS codes(date TEXT, name TEXT, quandl_code TEXT, nse_code TEXT, high_max REAL, low_max REAL, high_52 REAL, low_52 REAL, high_52_b REAL, low_52_a REAL, cagr REAL, change REAL, volatility REAL, open REAL, high REAL, low REAL, close REAL, volume INTEGER)')
        c.execute('DELETE FROM codes')# empty the codes table to insert new values for each stock
        print('Running Update Codes')
    
    def quitapp(self):
        c.close()
        conn.close()
        print('start time : ', self.stime)
        print('end time: ', datetime.datetime.now())
        raise SystemExit
    
    def fetchcsv(self):
        self.local_filename, self.headers = urllib.request.urlretrieve(self.url)# getting the zipfile
        self.zip_ref = zipfile.ZipFile(self.local_filename, 'r')
        self.file = open(self.zip_ref.extract(self.zip_ref.namelist()[0]), 'r')
        self.file = list(csv.reader(self.file, delimiter = ','))
        self.count = len(self.file)
        
        self.infoa.config(text = self.count)# display number of rows    WORKS TILL HERE
        for row in self.file:
            self.df = quandl.get(row[0])
            self.path = 'csv\\' + row[0][4:] + '.csv'
            self.df.to_csv(self.path, sep=',')
            self.df = self.df.fillna(value = 1)
            self.nse_code = row[0][4:] # 4
            self.quandl_code = row[0] # 3
            self.name = row[1] # 2
            self.open = float(self.df['Open'].tail(1).values)
            self.high = float(self.df['High'].tail(1).values)
            self.low = float(self.df['Low'].tail(1).values)
            self.close = float(self.df['Close'].tail(1).values)
            self.volume = float(self.df['Total Trade Quantity'].tail(1).values)
            self.date = str(self.df.index[-1].date().year) + '-' + str(self.df.index[-1].date().month) + '-' + str(self.df.index[-1].date().day)# 1
            self.high_max = self.df['High'].max() # 6
            self.low_max = self.df['Low'].min()
            self.dg = self.df.tail(248)#one year's data
            self.high_52 = self.dg['High'].max()# one years max high
            self.low_52 = self.dg['Low'].min()# one years max low
            self.cagr = round((self.dg['Close'].iloc[-1] / self.dg['Close'].iloc[0]) - 1,3)# one year CAGR
            self.change = round(((self.df['Close'].iloc[-1] - self.df['Close'].iloc[-2]) / self.df['Close'].iloc[-1]) * 100,3)# last change
            self.volatility = round(((self.df['High'].iloc[-1] - self.df['Low'].iloc[-1]) / self.df['Low'].iloc[-1]) * 100,3)#last day's volatility
            self.high_52_b = round(100 - ((self.close * 100)/self.high_52), 3)
            self.low_52_a = round(((self.close - self.low)* 100) / self.low, 3)
            self.done = self.done + 1
            self.left = self.left - 1
            self.infob.config(text = self.done)# display number of rows
            self.infoc.config(text = self.left)# display number of rows
            self.infod.config(text = int((self.done/self.count)*100))
            self.pbar.step()
            c.execute('INSERT INTO codes (date, name, quandl_code, nse_code, high_max, low_max, high_52, low_52, high_52_b, low_52_a, cagr, change, volatility, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (self.date, self.name, self.quandl_code, self.nse_code, self.high_max, self.low_max, self.high_52, self.low_52, self.high_52_b, self.low_52_a, self.cagr, self.change, self.volatility, self.open, self.high, self.low, self.close, self.volume))
            conn.commit()

app = StockXApp()
app.mainloop()
