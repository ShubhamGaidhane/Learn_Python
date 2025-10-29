
import yfinance as yf
import pandas as pd
import talib as ta
import numpy as np

def fetch_ohlc_data(ticker, start_date, end_date):
    """
    Fetches historical OHLC data for a stock.
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def detect_patterns(data):
    """
    Detects Doji, Hammer, and Engulfing patterns in the data.
    """
    open_prices = data['Open'].to_numpy().ravel()
    high_prices = data['High'].to_numpy().ravel()
    low_prices = data['Low'].to_numpy().ravel()
    close_prices = data['Close'].to_numpy().ravel()

    # Doji
    data['Doji'] = ta.CDLDOJI(open_prices, high_prices, low_prices, close_prices)

    # Hammer
    data['Hammer'] = ta.CDLHAMMER(open_prices, high_prices, low_prices, close_prices)

    # Engulfing (Bullish and Bearish)
    data['Engulfing'] = ta.CDLENGULFING(open_prices, high_prices, low_prices, close_prices)

    return data

def plot_chart_with_patterns(data, ticker):
    """
    Plots the candlestick chart with markers for detected patterns.
    """
    import mplfinance as mpf

    # Create a list of additional plots for the patterns
    addplots = []

    # Markers for Doji
    doji_markers = np.where(data['Doji'] != 0, data['Low'] * 0.98, np.nan)
    addplots.append(mpf.make_addplot(doji_markers, type='scatter', marker='o', markersize=50, color='purple'))

    # Markers for Hammer
    hammer_markers = np.where(data['Hammer'] != 0, data['Low'] * 0.98, np.nan)
    addplots.append(mpf.make_addplot(hammer_markers, type='scatter', marker='^', markersize=100, color='green'))

    # Markers for Engulfing
    bullish_engulfing = np.where(data['Engulfing'] == 100, data['Low'] * 0.98, np.nan)
    bearish_engulfing = np.where(data['Engulfing'] == -100, data['High'] * 1.02, np.nan)
    addplots.append(mpf.make_addplot(bullish_engulfing, type='scatter', marker='s', markersize=100, color='green'))
    addplots.append(mpf.make_addplot(bearish_engulfing, type='scatter', marker='s', markersize=100, color='red'))

    # Plot the chart
    mpf.plot(data, type='candle', style='yahoo',
             title=f'{ticker} Candlestick Chart with Patterns',
             ylabel='Price ($)',
             addplot=addplots,
             figsize=(15, 7))

if __name__ == '__main__':
    # Define the stock and date range
    ticker = 'AAPL'
    start_date = '2024-01-01'
    end_date = '2024-07-01'

    # Fetch the data
    data = fetch_ohlc_data(ticker, start_date, end_date)

    # If yfinance returns a multi-level column index, flatten it
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Detect the patterns
    data = detect_patterns(data)

    # Plot the chart
    plot_chart_with_patterns(data, ticker)

    # Print the detected patterns
    print("Detected Patterns:")
    print("Doji:")
    print(data[data['Doji'] != 0])
    print("\nHammer:")
    print(data[data['Hammer'] != 0])
    print("\nEngulfing:")
    print(data[data['Engulfing'] != 0])
