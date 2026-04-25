import pandas as pd

def load_and_clean_data(filepath):
    """
    Loads financial CSV data and prepares it for analysis.
    """
    try:
        df = pd.read_csv(filepath)
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Ensure Debit and Credit are numeric
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def calculate_daily_running_balance(df, initial_balance=0):
    """
    Aggregates net flow per day and calculates a cumulative running balance.
    """
    # Net flow per transaction
    df['Net_Transaction'] = df['Credit'] - df['Debit']
    
    # Aggregate by Date
    daily_summary = df.groupby('Date')['Net_Transaction'].sum().reset_index()
    daily_summary.rename(columns={'Net_Transaction': 'Net_Flow'}, inplace=True)
    
    # Calculate Running Balance
    daily_summary = daily_summary.sort_values('Date')
    daily_summary['Running_Balance'] = daily_summary['Net_Flow'].cumsum() + initial_balance
    
    return daily_summary

def detect_shortfalls(df, threshold=1000):
    """
    Identifies dates where the running balance drops below the specified threshold.
    """
    shortfalls = df[df['Running_Balance'] < threshold].copy()
    return shortfalls

if __name__ == "__main__":
    # Example usage with the generated data
    csv_path = 'sample_financial_data.csv'
    
    print(f"--- Analyzing {csv_path} ---")
    data = load_and_clean_data(csv_path)
    
    if data is not None:
        balance_df = calculate_daily_running_balance(data)
        print("\nDaily Flow (First 5 Days):")
        print(balance_df.head())
        
        shortfalls = detect_shortfalls(balance_df, threshold=1000)
        
        if not shortfalls.empty:
            print(f"\n[ALERT] {len(shortfalls)} Shortfall instances detected (Balance < $1000):")
            print(shortfalls.head(10))
        else:
            print("\nNo shortfalls detected with current threshold.")
