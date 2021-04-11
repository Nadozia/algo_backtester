import pandas_datareader as web
import pandas as pd

class scraper:
    def getdata(self, symbol, period='d'):
        """ get data from yahoo """
        df = web.get_data_yahoo(symbol, interval=period)
        return df

def main():
    s = scraper()
    df = s.getdata('AAPL')
    print(df.head())

if __name__ =='__main__':
    main()