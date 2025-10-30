import yfinance as yf
import pandas as pd
import numpy as np
from scipy.signal import find_peaks

# Nifty 200 stock tickers
NIFTY_200_STOCKS = [
    'ACC.NS', 'ASHOKLEY.NS', 'ASIANPAINT.NS', 'BAJAJHLDNG.NS', 'BHARATFORG.NS', 'BLUESTARCO.NS',
    'BRITANNIA.NS', 'EXIDEIND.NS', 'CIPLA.NS', 'COLPAL.NS', 'COROMANDEL.NS', 'CGPOWER.NS',
    'EICHERMOT.NS', 'NESTLEIND.NS', 'AMBUJACEM.NS', 'GRASIM.NS', 'HEROMOTOCO.NS', 'ABB.NS',
    'HINDALCO.NS', 'HINDUNILVR.NS', 'INDHOTEL.NS', 'ITC.NS', 'CUMMINSIND.NS', 'TRENT.NS', 'LT.NS',
    'M&M.NS', 'MFSL.NS', 'BOSCHLTD.NS', 'MRF.NS', 'RELIANCE.NS', 'VEDL.NS', 'SHREECEM.NS', 'SRF.NS',
    'SIEMENS.NS', 'SUPREMEIND.NS', 'TATAPOWER.NS', 'TATACONSUM.NS', 'TATASTEEL.NS', 'VOLTAS.NS',
    'WIPRO.NS', 'APOLLOHOSP.NS', 'GODFRYPHLP.NS', 'PATANJALI.NS', 'DRREDDY.NS', 'TITAN.NS', 'SBIN.NS',
    'SHRIRAMFIN.NS', 'CHOLAFIN.NS', 'BPCL.NS', 'TATACOMM.NS', 'BEL.NS', 'SAIL.NS', 'NATIONALUM.NS',
    'HINDPETRO.NS', 'BHEL.NS', 'HINDZINC.NS', 'TATAELXSI.NS', 'KOTAKBANK.NS', 'UPL.NS', 'PIIND.NS',
    'INFY.NS', 'MOTHERSON.NS', 'LUPIN.NS', 'PIDILITIND.NS', 'HAVELLS.NS', 'MPHASIS.NS', 'DABUR.NS',
    'TORNTPHARM.NS', 'FEDERALBNK.NS', 'BAJFINANCE.NS', 'ADANIENT.NS', 'LICHSGFIN.NS', 'SUNPHARMA.NS',
    'AUROPHARMA.NS', 'KEI.NS', 'JSWSTEEL.NS', 'HDFCBANK.NS', 'TCS.NS', 'ICICIBANK.NS', 'OIL.NS',
    'POWERGRID.NS', 'BANKBARODA.NS', 'CANBK.NS', 'UNIONBANK.NS', 'MARUTI.NS', 'INDUSINDBK.NS',
    'AXISBANK.NS', 'BANKINDIA.NS', 'HCLTECH.NS', 'COCHINSHIP.NS', 'INDIANB.NS', 'ONGC.NS',
    'PHOENIXLTD.NS', 'DLF.NS', 'PNB.NS', 'TVSMOTOR.NS', 'UNITDSPR.NS', 'NTPC.NS', 'IOC.NS',
    'COALINDIA.NS', 'LICI.NS', 'HAL.NS', 'NMDC.NS', 'PFC.NS', 'HUDCO.NS', 'APLAPOLLO.NS',
    'GAIL.NS', 'PAGEIND.NS', 'NHPC.NS', 'MARICO.NS', 'CONCOR.NS', 'IRFC.NS', 'MAZDOCK.NS',
    'OFSS.NS', 'PRESTIGE.NS', 'SUZLON.NS', 'JUBLFOOD.NS', 'BIOCON.NS', 'BHARTIHEXA.NS',
    'BHARTIARTL.NS', 'IREDA.NS', 'GODREJPROP.NS', 'M&MFIN.NS', 'TECHM.NS', 'BDL.NS',
    'ADANIPOWER.NS', 'RECLTD.NS', 'LTIM.NS', 'PERSISTENT.NS', 'TATATECH.NS', 'SONACOMS.NS',
    'TORNTPOWER.NS', 'NAUKRI.NS', 'ALKEM.NS', 'SBICARD.NS', 'JINDALSTEL.NS', 'GLENMARK.NS',
    'IGL.NS', 'JIOFIN.NS', 'ZYDUSLIFE.NS', 'DIVISLAB.NS', 'BSE.NS', 'HDFCAMC.NS', 'ADANIPORTS.NS',
    'GODREJCP.NS', 'HDFCLIFE.NS', 'SBILIFE.NS', 'ICICIGI.NS', 'MAXHEALTH.NS', 'GMRAIRPORT.NS',
    'IDEA.NS', 'IRCTC.NS', 'FORTIS.NS', 'VBL.NS', 'MUTHOOTFIN.NS', 'ULTRACEMCO.NS', 'COFORGE.NS',
    'YESBANK.NS', 'SOLARINDS.NS', 'POLYCAB.NS', 'RVNL.NS', 'JSWENERGY.NS', 'ASTRAL.NS',
    'MOTILALOFS.NS', 'BAJAJ-AUTO.NS', 'BAJAJFINSV.NS', 'IRB.NS', 'INDIGO.NS', 'AUBANK.NS',
    'LODHA.NS', 'DIXON.NS', 'OBEROIRLTY.NS', 'MANKIND.NS', 'ATGL.NS', 'PAYTM.NS',
    'INDUSTOWER.NS', 'ABCAPITAL.NS', 'DMART.NS', 'TIINDIA.NS', 'LTF.NS', 'POLICYBZR.NS',
    'KALYANKJIL.NS', 'IDFCFIRSTB.NS', '360ONE.NS', 'ADANIENSOL.NS', 'BAJAJHFL.NS',
    'ADANIGREEN.NS', 'KPITTECH.NS', 'POWERINDIA.NS', 'NYKAA.NS', 'PREMIERENE.NS'
]

def fetch_price_data_for_rs(tickers, start_date, end_date):
    """
    Fetches historical price data for a list of tickers for RS analysis.
    """
    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
    return data

def get_rs_stocks():
    """
    Calculates the relative strength of Nifty 200 stocks against Nifty 50
    and returns the top 20 and bottom 20 performing stocks.
    """
    end_date = pd.to_datetime('today')
    start_date = end_date - pd.DateOffset(months=6)
    benchmark_ticker = '^NSEI'
    all_tickers = [benchmark_ticker] + NIFTY_200_STOCKS
    price_data = fetch_price_data_for_rs(all_tickers, start_date, end_date)
    print("Data fetched successfully for RS analysis.")
    benchmark_prices = price_data[benchmark_ticker]['Close']
    rs_performance = {}
    for ticker in NIFTY_200_STOCKS:
        try:
            stock_prices = price_data[ticker]['Close']
            rs_ratio = stock_prices / benchmark_prices
            start_rs = rs_ratio.dropna().iloc[0]
            end_rs = rs_ratio.dropna().iloc[-1]
            rs_perf_pct = ((end_rs - start_rs) / start_rs) * 100
            rs_performance[ticker] = rs_perf_pct
        except (KeyError, IndexError):
            print(f"Warning: Could not process data for {ticker}.")
    print("\nRelative Strength calculation complete.")
    sorted_stocks = sorted(rs_performance.items(), key=lambda item: item[1], reverse=True)
    top_20 = sorted_stocks[:20]
    bottom_20 = sorted_stocks[-20:]
    print("\n--- Top 20 Stocks (Strongest RS) ---")
    for ticker, perf in top_20:
        print(f"{ticker}: {perf:.2f}%")
    print("\n--- Bottom 20 Stocks (Weakest RS) ---")
    for ticker, perf in reversed(bottom_20):
        print(f"{ticker}: {perf:.2f}%")
    top_20_tickers = [stock[0] for stock in top_20]
    bottom_20_tickers = [stock[0] for stock in bottom_20]
    return top_20_tickers + bottom_20_tickers

def fetch_price_data_for_sr(ticker, period="1y"):
    """
    Fetches historical price data for a given stock for S/R analysis.
    """
    data = yf.download(ticker, period=period)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    return data

def find_levels(data, prominence=0.05):
    """
    Identifies significant swing highs and lows in the price data.
    """
    highs = data['High'].to_numpy()
    lows = data['Low'].to_numpy()
    price_range = highs.max() - lows.min()
    prominence_threshold = price_range * prominence
    resistance_indices, _ = find_peaks(highs, prominence=prominence_threshold)
    resistance_levels = highs[resistance_indices]
    support_indices, _ = find_peaks(-lows, prominence=prominence_threshold)
    support_levels = lows[support_indices]
    return support_levels, resistance_levels

def cluster_levels(levels, tolerance=0.01):
    """
    Groups individual support or resistance levels into clustered zones.
    """
    if levels.size == 0:
        return []
    sorted_levels = np.sort(levels)
    zones = []
    current_zone = [sorted_levels[0]]
    for level in sorted_levels[1:]:
        if level <= current_zone[-1] * (1 + tolerance):
            current_zone.append(level)
        else:
            zones.append((np.mean(current_zone), len(current_zone)))
            current_zone = [level]
    zones.append((np.mean(current_zone), len(current_zone)))
    return zones

def screen_stocks_for_sr(stock_list, proximity_pct=0.01, min_touches=2):
    """
    Screens a list of stocks to see if they are near strong support or resistance zones.
    """
    near_support = []
    near_resistance = []
    print("\nScreening stocks for support and resistance...")
    for ticker in stock_list:
        try:
            data = fetch_price_data_for_sr(ticker)
            if data.empty:
                continue
            current_price = data['Close'].iloc[-1]
            support_levels, resistance_levels = find_levels(data)
            support_zones = cluster_levels(support_levels)
            resistance_zones = cluster_levels(resistance_levels)
            for zone_price, touches in support_zones:
                if touches >= min_touches and abs(current_price - zone_price) / zone_price <= proximity_pct:
                    near_support.append((ticker, zone_price))
                    break
            for zone_price, touches in resistance_zones:
                if touches >= min_touches and abs(current_price - zone_price) / zone_price <= proximity_pct:
                    near_resistance.append((ticker, zone_price))
                    break
        except Exception as e:
            print(f"Could not process {ticker} for S/R analysis: {e}")
    return near_support, near_resistance

if __name__ == '__main__':
    print("Starting the RS Support/Resistance Screener...")
    rs_stocks = get_rs_stocks()
    print("\nTotal stocks to screen for support/resistance:", len(rs_stocks))

    near_support, near_resistance = screen_stocks_for_sr(rs_stocks)

    print("\n--- Stocks Near Strong Support ---")
    for ticker, price in near_support:
        print(f"{ticker} is near support at {price:.2f}")

    print("\n--- Stocks Near Strong Resistance ---")
    for ticker, price in near_resistance:
        print(f"{ticker} is near resistance at {price:.2f}")
