from Indicators import Indicators

def boll_ma_buy1(df, i:int):
    indicators = [
        ('Low_boll', 14)
    ]

    # Adding indicator
    adding_indicators(df, indicators)

    if df['High'][i]>=df['Low_boll'][i] and df['Low'][i]<df['Low_boll'][i]:
        return i, df['Low_boll'][i]
    else:
        return None

def boll_low_buy(df, i:int):
    indicators = [
        ('Low_boll', 14)
    ]
    adding_indicators(df, indicators)

    if df['Close'][i-1]<df['Low_boll'][i-1] and df['High'][i]>=df['Low_boll'][i]>=df['Low'][i]:
        return i, df['Low_boll'][i]
    else:
        return None

def boll_mid_ma_buy(df, i:int):
    indicators = [
        ('Mid_boll', 14),
        ('Smooth_moving_average', 5)
    ]
    adding_indicators(df, indicators)

    if df['Smooth_moving_average'][i-1]<df['Mid_boll'][i-1] and df['Smooth_moving_average'][i]>df['Mid_boll'][i]:
        return i+1, df['Open'][i+1]
    else:
        return None

def boll_mid_ma_sell(df, i:int, *args):
    indicators = [
        ('Mid_boll', 14),
        ('Smooth_moving_average', 5)
    ]
    adding_indicators(df, indicators)

    if df['Smooth_moving_average'][i-1]>df['Mid_boll'][i-1] and df['Smooth_moving_average'][i]<df['Mid_boll'][i]:
        return i+1, df['Close'][i+1]
    else:
        return None

def trailing_sell(df, i, current_high):
    indicators = [
        ('Up_boll', 14),
    ]

    # Adding indicator
    adding_indicators(df, indicators)

    trailing = 0.8
    if df['Low'][i]< current_high*trailing:
        return i, current_high*trailing
    else:
        return None

def counting_high(df, i, current_high):
    if df['High'][i] > current_high:
        return df['High'][i]
    else:
        return current_high

def adding_indicators(df, indicators:list=[]):
    for indicator in indicators:
        if indicator[0] not in df.columns:
            Indicators.AddIndicator(df = df, indicator_name=indicator[0], col_name=indicator[0], args=indicator[1])
