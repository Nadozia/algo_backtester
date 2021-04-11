from Scraper import scraper
from Indicators import Indicators
import pandas as pd
from Strategies import boll_mid_ma_buy, boll_mid_ma_sell, counting_high, boll_low_buy
import numpy as np

from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import math
import os
import webbrowser

class backtester:
    def __init__(self, symbol, period, initial_balance=1000, buy_strategy='', sell_strategy='', stop_loss=False):
        """ indicator: tuple (col_name, args) """
        self.symbol = symbol
        self.period = period
        self.cash = self.balance = self.initial_balance = initial_balance
        self.equity = 0
        self.position = 0
        self.buy_strategy = buy_strategy
        self.sell_strategy = sell_strategy
        self.df = scraper().getdata(self.symbol, self.period)
        self.buy_signal = []
        self.sell_signal = []
        self.stop_loss = stop_loss
        self.stop_loss_count = 0
        self.result_pair_df = pd.DataFrame(columns=['Time', 'Position', 'Buy_price', 'Sell_price','Gain/loss'])
        self.result_balance_df = pd.DataFrame(columns=['Time', 'Balance', 'Cash', 'Equity','Positions'])

    def backtest(self):
        df = self.df
        current_high = 0
        pair = []

        for i in range(df.shape[0]-1):
            
            if self.position == 0:
                buy_condition = self.buy_strategy(df, i)
                
                if buy_condition is not None:
                    buy_positions = math.floor(self.balance/buy_condition[1])
                    if buy_positions>0:
                    # buy the product and update balance df
                        self.buy_signal.append(buy_condition)
                        self.cash = self.cash-buy_condition[1]*buy_positions
                        self.position = buy_positions
                        self.equity = df['Close'][i]*buy_positions
                        current_high = counting_high(df, buy_condition[0], current_high)
                        pair.extend([df.index[i], buy_positions, buy_condition[1]])       
                                            
                else:
                    self.equity = df['Close'][i]*self.position
                                        
            else:
                current_high = counting_high(df, i, current_high)
                sell_condition = self.sell_strategy(df, i, current_high)
                # If stop_loss is applicable
                if self.stop_loss:
                    print('Stoploss')
                    last_buy_price = self.buy_signal[-1][1]
                    stop_loss_price = last_buy_price*(1-self.stop_loss)
                    if df['Close'][i] < stop_loss_price:
                        self.sell_signal.append((i, df['Close'][i]))
                        self.cash = self.cash + df['Close'][i]*self.position
                        self.equity = 0
                        self.position = 0
                        current_high = 0

                        #print('[*] Stop loss triggered on '+str(df.index[i])+' at price: '+ str(df['Close'][i]))
                        self.stop_loss_count +=1
                        continue
                elif sell_condition is not None:
                    self.sell_signal.append(sell_condition)

                    gnlPerShare = sell_condition[1]-pair[2]
                    pair.extend([sell_condition[1], gnlPerShare*self.position])
                    series = pd.Series(pair, index=self.result_pair_df.columns)
                    self.result_pair_df = self.result_pair_df.append(series, ignore_index=True)

                    pair = []
                    self.cash = self.cash + sell_condition[1]*self.position
                    self.equity = 0
                    self.position = 0
                    
                    #print('[-] Sell Signal detected on '+str(df.index[i])+' at price: '+ str(sell_condition[1]))
                    current_high = 0
                else:
                    self.equity = df['Close'][i]*self.position
            self.update_result_balance(df.index[i])
        self.result_balance_df['Daily_return'] = self.result_balance_df['Balance'].pct_change(1)
        sharpe_ratio = self.result_balance_df['Daily_return'].mean()/self.result_balance_df['Daily_return'].std()
        print(f"Report of {self.symbol}")
        print(f"Initial balance : {self.initial_balance}")
        print(f'Trades : {self.result_pair_df.shape[0]}')
        print(f"Win rate : {self.result_pair_df[self.result_pair_df['Gain/loss']>0].shape[0]/self.result_pair_df.shape[0]}")
        print(f"Max Gain : {self.result_pair_df['Gain/loss'].max()}")
        print(f"Max draw down : {self.result_pair_df['Gain/loss'].min()}")
        print(f"Sharpe ratio : {sharpe_ratio}")
        print(f"Sharpe ratio(252) : {sharpe_ratio*(252**0.5)}")
        print(f"Total Gain/Loss : {self.result_balance_df['Balance'].iloc[-1]-self.initial_balance}")
        print(f"Buy and hold return : {self.getStrongHoldReturn()}")
        
        trade_fig = self.trades_plot(buy_signal=self.buy_signal, sell_signal=self.sell_signal, plot_title='Trades')
        balance_fig = self.balance_plot()
        filename = 'graphs/'+self.symbol+'.html'
        self.render_html([trade_fig,balance_fig], filename)
        url = 'file://'+os.path.abspath(filename)
        webbrowser.open(url)
        self.result_balance_df.to_csv(f'Balance_csv/{self.symbol}_balance.csv', index=None)
        self.result_pair_df.to_csv(f'Pair_csv/{self.symbol}_pair.csv', index=None)
        #plt.plot(self.result_balance_df['Time'], self.result_balance_df['Balance'])
        #plt.title(f'{self.symbol}_result_balance')
        #plt.show()

    def update_result_balance(self, time):
        self.balance = self.cash+self.equity
        s = pd.Series([time, self.balance, self.cash, self.equity, self.position], index =self.result_balance_df.columns)
        self.result_balance_df = self.result_balance_df.append(s, ignore_index=True)

    def getStrongHoldReturn(self):
            initial_price = self.df['Close'][1]
            initial_position = math.floor(self.initial_balance/initial_price)
            lastest_price = self.df['Close'].iloc[-1]
            return (lastest_price-initial_price)*initial_position

    def trades_plot(self, buy_signal=False, sell_signal=False, plot_title:str=''):
        df = self.df

        candle = go.Candlestick(
            x = df.index,
            open = df['Open'],
            close = df['Close'],
            high = df['High'],
            low = df['Low'],
            name = 'Candlesticks'
        )

        data = [candle]
        #plot indicators
        if 'Low_boll' in df.columns:
            lb = go.Scatter(
                x = df.index,
                y = df['Low_boll'],
                name = 'Low_boll',
                line = dict(color=("rgba(100,0,100,60)"))
            )
            data.append(lb)

        if 'Up_boll' in df.columns:
            ub = go.Scatter(
                x = df.index,
                y = df['Up_boll'],
                name = 'Up_boll',
                line = dict(color=("rgba(250,100,100,60)"))
            )
            data.append(ub)

        if 'Mid_boll' in df.columns:
            mb = go.Scatter(
                x = df.index,
                y = df['Mid_boll'],
                name = 'Mid_boll',
                line = dict(color=("rgba(70,70,70,60)"))
            )
            data.append(mb)

        if 'Smooth_moving_average' in df.columns:
            sma = go.Scatter(
                x = df.index,
                y = df['Smooth_moving_average'],
                name = 'Smooth_moving_average',
                line = dict(color=("rgba(144,144,14,60)"))
            )
            data.append(sma)

        #plot signals
        if buy_signal:
            buys = go.Scatter(
                x = [df.index[item[0]] for item in buy_signal],
                y = [item[1] for item in buy_signal],
                name = 'Buy Signals',
                mode = 'markers',
                marker_size = 10
            )
            data.append(buys)

        if sell_signal:
            sells = go.Scatter(
                x = [df.index[item[0]] for item in sell_signal],
                y = [item[1] for item in sell_signal],
                name = 'Sell Signals',
                mode = 'markers',
                marker_size = 10
            )
            data.append(sells)


        layout = go.Layout(
            title = plot_title,
            xaxis = {
                'title': self.symbol,
                'rangeslider':{
                    'visible': True,
                },
                'type':'date'
            },
            yaxis={
                'fixedrange': False
            }
        )

        fig = go.Figure(data = data, layout=layout)
        return fig

    def balance_plot(self):
        df = self.result_balance_df
        balance = go.Scatter(
            x= df['Time'],
            y= df['Balance']
        )
        layout = go.Layout(title = 'Acount Balance Curve')
        fig = go.Figure(balance, layout=layout)
        return fig

    def render_html(self, figs, filepath):
        dashboard = open(filepath, 'w')
        dashboard.write("<html><head></head><body>" + "\n")
        for fig in figs:
            inner_html = fig.to_html().split('<body>')[1].split('</body>')[0]
            dashboard.write(inner_html)
        dashboard.write("</body></html>" + "\n")
        
def main():
    
    test_list = ['SPY']
    for item in test_list:
        tester = backtester(symbol=item, period='d', initial_balance=2000, buy_strategy=boll_low_buy, sell_strategy=boll_mid_ma_sell)
        tester.backtest() 
       
    
    

if __name__ =='__main__':
    main()