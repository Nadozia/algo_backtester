import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from Backtest import backtester
from Strategies import boll_mid_ma_buy, boll_mid_ma_sell


tester = backtester(symbol='QQQ', period='d', initial_balance=2000, buy_strategy=boll_mid_ma_buy, sell_strategy=boll_mid_ma_sell)
tester.backtest()
fig = tester.trades_plot(buy_signal=tester.buy_signal, sell_signal=tester.sell_signal, plot_title='Backtest_Report')

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure = fig)
])

app.run_server(debug=True)