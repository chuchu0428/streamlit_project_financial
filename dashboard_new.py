import streamlit as st
import yfinance as yf
import pandas as pd
import time

# -----------------------------
# Safe fetching with retry
# -----------------------------
@st.cache_data(ttl=3600)
def fetch_index_data_safe(ticker):
    """Fetch index data safely with retry and delay."""
    for attempt in range(5):
        try:
            index = yf.Ticker(ticker)
            hist = index.history(period="1y")
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            hist['EMA_20'] = hist['Close'].ewm(span=20, adjust=False).mean()
            hist['Volatility'] = hist['Close'].rolling(window=20).std()
            return hist
        except Exception as e:
            st.warning(f"Error fetching {ticker}: {e}. Retrying in 60 seconds...")
            time.sleep(60)
    st.error(f"Could not fetch data for {ticker} after multiple attempts.")
    return pd.DataFrame()

@st.cache_data(ttl=3600)
def fetch_stock_data_safe(ticker):
    """Fetch stock data safely with retry and delay."""
    for attempt in range(5):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            info = stock.info
            metrics = {
                'PE Ratio': info.get('trailingPE', 'N/A'),
                'Dividend Yield': f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A',
                'Beta': info.get('beta', 'N/A'),
                'Market Cap': info.get('marketCap', 'N/A')
            }
            return hist, metrics
        except Exception as e:
            st.warning(f"Error fetching {ticker}: {e}. Retrying in 60 seconds...")
            time.sleep(60)
    st.error(f"Could not fetch data for {ticker} after multiple attempts.")
    return pd.DataFrame(), {}

@st.cache_data(ttl=3600)
def metrics_table_safe(ticker):
    """Fetch financials safely with retry and delay."""
    for attempt in range(5):
        try:
            stock = yf.Ticker(ticker)
            financials = stock.financials
            balance_sheet = stock.balance_sheet
            output1 = balance_sheet.T[['Total Assets','Total Debt']]
            output2 = financials.T[['Total Revenue','EBITDA','Basic EPS','Operating Income','Operating Expense']]
            output = output1.join(output2)
            return output.T
        except Exception as e:
            st.warning(f"Error fetching financial data for {ticker}: {e}. Retrying in 60 seconds...")
            time.sleep(60)
    st.error(f"Could not fetch financial data for {ticker} after multiple attempts.")
    return pd.DataFrame()

# -----------------------------
# Streamlit UI for Index Dashboard
# -----------------------------
def display_index_dashboard():
    st.title('Industry Indices Dashboard')
    indices = ['^DJI', '^GSPC', '^IXIC', '^RUT']
    selected_index = st.sidebar.selectbox('Select an Index', indices)
    
    # Retry button
    if st.button("Retry Fetch Index Data"):
        st.cache_data.clear()  # clear cache to force re-fetch
    
    index_data = fetch_index_data_safe(selected_index)
    if index_data.empty:
        st.warning("No data available.")
        return
    
    st.write(f"Data for {selected_index}")
    st.dataframe(index_data[['Open','High','Low','Close','Volume','SMA_20','EMA_20','Volatility']])
    st.line_chart(index_data[['Close','SMA_20','EMA_20']])

# -----------------------------
# Streamlit UI for Stock Dashboard
# -----------------------------
def display_stock_dashboard():
    st.title('Stocks Dashboard')
    stocks = ['AAPL','MSFT','GOOGL','AMZN','TSLA']
    selected_stock = st.sidebar.selectbox('Select a Stock', stocks)
    
    # Retry button
    if st.button("Retry Fetch Stock Data"):
        st.cache_data.clear()  # clear cache to force re-fetch
    
    stock_data, metrics = fetch_stock_data_safe(selected_stock)
    metr = metrics_table_safe(selected_stock)
    
    if stock_data.empty:
        st.warning("No stock data available.")
        return
    
    st.write(f"Data for {selected_stock}")
    st.dataframe(stock_data[['Open','High','Low','Close','Volume']])
    
    st.title(f"Financials for {selected_stock}")
    st.dataframe(metr)
    
    st.metric(label="PE Ratio", value=metrics.get('PE Ratio', 'N/A'))
    st.metric(label="Dividend Yield", value=metrics.get('Dividend Yield', 'N/A'))
    st.metric(label="Beta", value=metrics.get('Beta', 'N/A'))
    st.metric(label="Market Cap", value=metrics.get('Market Cap', 'N/A'))
    
    st.line_chart(stock_data['Close'])

# -----------------------------
# Main function
# -----------------------------
def main():
    st.sidebar.title('Dashboard Selection')
    dashboard_type = st.sidebar.radio('Choose a Dashboard', ('Industry Indices', 'Stocks'))

    if dashboard_type == 'Industry Indices':
        display_index_dashboard()
    else:
        display_stock_dashboard()

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    main()
