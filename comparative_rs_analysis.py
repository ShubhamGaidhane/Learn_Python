
import yfinance as yf
import pandas as pd

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


def fetch_price_data(tickers, start_date, end_date):
    """
    Fetches historical price data for a list of tickers.
    """
    data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker')
    return data

if __name__ == '__main__':
    # Define the date range for analysis
    end_date = pd.to_datetime('today')
    start_date = end_date - pd.DateOffset(months=6)

    # Define the benchmark
    benchmark_ticker = '^NSEI'  # Nifty 50

    # Fetch data for the benchmark and the stocks
    all_tickers = [benchmark_ticker] + NIFTY_200_STOCKS
    price_data = fetch_price_data(all_tickers, start_date, end_date)

    print("Data fetched successfully.")

    # --- Calculate Comparative Relative Strength ---

    # Extract the benchmark's closing prices
    benchmark_prices = price_data[benchmark_ticker]['Close']

    rs_performance = {}

    for ticker in NIFTY_200_STOCKS:
        try:
            stock_prices = price_data[ticker]['Close']

            # Calculate the Relative Strength (RS) ratio
            rs_ratio = stock_prices / benchmark_prices

            # Calculate the percentage change in the RS ratio over the period
            # We use the first and last non-null values to be robust against missing data
            start_rs = rs_ratio.dropna().iloc[0]
            end_rs = rs_ratio.dropna().iloc[-1]

            rs_perf_pct = ((end_rs - start_rs) / start_rs) * 100

            rs_performance[ticker] = rs_perf_pct

        except (KeyError, IndexError):
            print(f"Warning: Could not process data for {ticker}. It might be missing from the dataset or have no data in the given range.")

    print("\nRelative Strength calculation complete.")

    # --- Rank the stocks ---

    # Sort the stocks by RS performance in descending order
    sorted_stocks = sorted(rs_performance.items(), key=lambda item: item[1], reverse=True)

    # Get the top 10 and bottom 10 stocks
    top_10 = sorted_stocks[:10]
    bottom_10 = sorted_stocks[-10:]

    print("\n--- Top 10 Stocks (Strongest RS) ---")
    for ticker, perf in top_10:
        print(f"{ticker}: {perf:.2f}%")

    print("\n--- Bottom 10 Stocks (Weakest RS) ---")
    for ticker, perf in reversed(bottom_10): # Reverse to show weakest first
        print(f"{ticker}: {perf:.2f}%")
