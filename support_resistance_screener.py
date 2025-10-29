
import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

def fetch_price_data(ticker, period="1y"):
    """
    Fetches historical price data for a given stock.
    """
    data = yf.download(ticker, period=period)
    # If yfinance returns a multi-level column index, flatten it
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

def find_levels(data, prominence=0.05):
    """
    Identifies significant swing highs and lows in the price data.
    """
    # Use the High and Low prices to find peaks and troughs
    highs = data['High'].to_numpy()
    lows = data['Low'].to_numpy()

    # Calculate a prominence threshold based on the price range
    price_range = highs.max() - lows.min()
    prominence_threshold = price_range * prominence

    # Find peaks (resistance)
    resistance_indices, _ = find_peaks(highs, prominence=prominence_threshold)
    resistance_levels = highs[resistance_indices]

    # Find troughs (support) - find_peaks on the inverted series
    support_indices, _ = find_peaks(-lows, prominence=prominence_threshold)
    support_levels = lows[support_indices]

    return support_levels, resistance_levels

def cluster_levels(levels, tolerance=0.01):
    """
    Groups individual support or resistance levels into clustered zones.
    """
    if levels.size == 0:
        return []

    # Sort the levels to make clustering easier
    sorted_levels = np.sort(levels)

    zones = []
    current_zone = [sorted_levels[0]]

    for level in sorted_levels[1:]:
        # If the current level is within the tolerance of the last level in the zone, add it
        if level <= current_zone[-1] * (1 + tolerance):
            current_zone.append(level)
        else:
            # Otherwise, finalize the current zone and start a new one
            zones.append((np.mean(current_zone), len(current_zone)))
            current_zone = [level]

    # Add the last zone
    zones.append((np.mean(current_zone), len(current_zone)))

    return zones

def screen_stock(ticker, proximity_pct=0.01, min_touches=2):
    """
    Screens a single stock to see if it's near a strong support or resistance zone.
    """
    try:
        data = fetch_price_data(ticker)
        if data.empty:
            return None, None

        current_price = data['Close'].iloc[-1]

        support_levels, resistance_levels = find_levels(data)

        support_zones = cluster_levels(support_levels)
        resistance_zones = cluster_levels(resistance_levels)

        # Check for proximity to strong support zones
        for zone_price, touches in support_zones:
            if touches >= min_touches and abs(current_price - zone_price) / zone_price <= proximity_pct:
                return "Support", zone_price

        # Check for proximity to strong resistance zones
        for zone_price, touches in resistance_zones:
            if touches >= min_touches and abs(current_price - zone_price) / zone_price <= proximity_pct:
                return "Resistance", zone_price

    except Exception as e:
        print(f"Could not process {ticker}: {e}")

    return None, None

if __name__ == '__main__':
    # Define a list of stocks to screen
    stock_list = [
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "HINDUNILVR.NS",
        "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "BAJFINANCE.NS", "KOTAKBANK.NS"
    ]

    near_support = []
    near_resistance = []

    print("Screening stocks...")
    for ticker in stock_list:
        level_type, level_price = screen_stock(ticker)
        if level_type == "Support":
            near_support.append((ticker, level_price))
        elif level_type == "Resistance":
            near_resistance.append((ticker, level_price))

    print("\n--- Stocks Near Strong Support ---")
    for ticker, price in near_support:
        print(f"{ticker} is near support at {price:.2f}")

    print("\n--- Stocks Near Strong Resistance ---")
    for ticker, price in near_resistance:
        print(f"{ticker} is near resistance at {price:.2f}")
