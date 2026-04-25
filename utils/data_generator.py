import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_financial_data(filename='data/sample_financial_data.csv', scenario='normal'):
    # ensure data directory exists
    os.makedirs('data', exist_ok=True)
    
    # 1. Setup constants
    start_date = datetime(2026, 1, 1)
    end_date = start_date + timedelta(days=180) # Approximately 6 months
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    # Categories and base amounts
    categories = {
        'Sales': {'type': 'Credit', 'base': 500, 'freq': 'daily'},
        'Rent': {'type': 'Debit', 'base': 12000, 'freq': 'monthly'},
        'Software': {'type': 'Debit', 'base': 1500, 'freq': 'monthly'},
        'Consulting Fee': {'type': 'Credit', 'base': 15000, 'freq': 'irregular'},
        'Tax': {'type': 'Debit', 'base': 0, 'freq': 'one-time'}
    }

    # Tracking variable for cash crunch scenario
    late_paying_clients = ["TechCorp", "GlobalSystems", "DeltaWorks"]
    
    for current_date in date_range:
        month = current_date.month
        day = current_date.day
        
        # Adjust sales based on scenario
        if scenario == 'good':
            sales_mean = 3000
        elif scenario == 'crisis':
            sales_mean = 300
        else: # moderate/normal
            sales_mean = 500
            
        # Regular Sales (Daily)
        sales_amt = np.random.normal(sales_mean, 100)
        data.append({
            'Date': current_date.strftime('%Y-%m-%d'),
            'Description': 'Daily Store Sales',
            'Category': 'Sales',
            'Debit': 0,
            'Credit': round(max(0, sales_amt), 2)
        })
        
        # Monthly Expenses (1st of the month)
        if day == 1:
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Description': 'Office Rent',
                'Category': 'Rent',
                'Debit': categories['Rent']['base'],
                'Credit': 0
            })
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Description': 'SaaS Subscriptions',
                'Category': 'Software',
                'Debit': categories['Software']['base'],
                'Credit': 0
            })

        # Scenario Logic
        if scenario == 'crisis' and month == 3:
            # Large Tax Payment on March 15
            if day == 15:
                data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Description': 'Annual Corporate Tax Payment',
                    'Category': 'Tax',
                    'Debit': 45000,
                    'Credit': 0
                })
            
            # Late Paying Clients
            if day in [5, 12, 25]:
                client = late_paying_clients.pop(0) if late_paying_clients else "Client"
                data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Description': f'Consulting Fee - {client} (LATE PAYMENT - RECORDED BUT UNPAID)',
                    'Category': 'Consulting Fee',
                    'Debit': 0,
                    'Credit': 0 
                })
        elif scenario == 'good':
            # bonus sales or higher consulting fees
            if day == 15:
                data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Description': 'Project Milestone Payment (BONUS)',
                    'Category': 'Consulting Fee',
                    'Debit': 0,
                    'Credit': 100000
                })
        else: # Moderate/Normal
            # Regular Consulting Fees in other months
            if day == 15:
                data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Description': 'Project Milestone Payment',
                    'Category': 'Consulting Fee',
                    'Debit': 0,
                    'Credit': 15000
                })

    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Sort by date
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Write to CSV
    df.to_csv(filename, index=False)
    print(f"Successfully generated {len(df)} transactions to {filename}")
    
    return df

if __name__ == "__main__":
    # Generate the requested datasets
    generate_financial_data('data/good_performance.csv', scenario='good')
    generate_financial_data('data/moderate_performance.csv', scenario='normal')
    generate_financial_data('data/crisis_mock_data.csv', scenario='crisis')
    # Also generate the default sample file
    generate_financial_data('data/sample_financial_data.csv', scenario='normal')
