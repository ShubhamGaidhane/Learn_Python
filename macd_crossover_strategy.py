
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def fetch_stock_data(ticker, start_date, end_date):
    """
    Fetches historical stock data from Yahoo Finance.
    """
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

def calculate_macd(data, short_window=12, long_window=26, signal_window=9):
    """
    Calculates the MACD (Moving Average Convergence Divergence) indicator.
    """
    data['EMA12'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=long_window, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal_Line'] = data['MACD'].ewm(span=signal_window, adjust=False).mean()
    data['Histogram'] = data['MACD'] - data['Signal_Line']
    return data

def calculate_rsi(data, window=14):
    """
    Calculates the RSI (Relative Strength Index) indicator.
    """
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def generate_signals(data):
    """
    Generates buy and sell signals based on the MACD Crossover strategy.
    """
    data['Buy_Signal'] = np.where((data['MACD'] > data['Signal_Line']) & (data['MACD'].shift(1) < data['Signal_Line'].shift(1)) & (data['RSI'] > 50), 1, 0)
    data['Sell_Signal'] = np.where((data['MACD'] < data['Signal_Line']) & (data['MACD'].shift(1) > data['Signal_Line'].shift(1)) & (data['RSI'] < 50), -1, 0)
    return data

def plot_data(data, ticker):
    """
    Plots the stock data, MACD, and buy/sell signals.
    """
    plt.figure(figsize=(14, 7))

    # Plot closing price
    plt.subplot(2, 1, 1)
    plt.plot(data['Close'], label='Close Price')
    plt.scatter(data.index[data['Buy_Signal'] == 1], data['Close'][data['Buy_Signal'] == 1], marker='^', color='g', label='Buy Signal', s=100)
    plt.scatter(data.index[data['Sell_Signal'] == -1], data['Close'][data['Sell_Signal'] == -1], marker='v', color='r', label='Sell Signal', s=100)
    plt.title(f'{ticker} MACD Crossover Strategy')
    plt.legend()

    # Plot MACD
    plt.subplot(2, 1, 2)
    plt.plot(data['MACD'], label='MACD')
    plt.plot(data['Signal_Line'], label='Signal Line')
    plt.bar(data.index, data['Histogram'], color=np.where(data['Histogram'] > 0, 'g', 'r'), alpha=0.5, label='Histogram')
    plt.legend()

    plt.show()

if __name__ == '__main__':
    # Define the stock ticker and the date range for analysis
    ticker = 'AAPL'  # Example: Apple Inc.
    start_date = '2023-01-01'
    end_date = '2024-01-01'

    # Fetch the stock data
    data = fetch_stock_data(ticker, start_date, end_date)

    # Calculate the indicators
    data = calculate_macd(data)
    data = calculate_rsi(data)

    # Generate the trading signals
    data = generate_signals(data)

    # Plot the results
    plot_data(data, ticker)

    # Print the last few rows of the data to show the signals
    print(data.tail())
