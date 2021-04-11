from pyti.smoothed_moving_average import smoothed_moving_average as sma
from pyti.bollinger_bands import lower_bollinger_band as lbb
from pyti.bollinger_bands import upper_bollinger_band as ubb
from pyti.bollinger_bands import middle_bollinger_band as mbb

class Indicators:
    INDICATOR_DICT = {
        'Smooth_moving_average': sma,
        'Low_boll': lbb,
        'Up_boll': ubb,
        'Mid_boll': mbb
    }

    @staticmethod
    def AddIndicator(df, indicator_name, col_name, args):
        try:
            df[col_name] = Indicators.INDICATOR_DICT[indicator_name](df['Close'].tolist(), args)
        except Exception as E:
            print('[X] Exception raised on adding indicator -- '+ col_name)
            print(E)