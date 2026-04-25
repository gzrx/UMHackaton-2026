import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_financial_data():
    # 1. Setup constants
    start_date = datetime(2026, 1, 1)
    end_date = start_date + timedelta(days=180) # Approximately 6 months
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    # Categories and base amounts
    categories = {
        'Sales': {'type': 'Credit', 'base': 5000, 'freq': 'daily'},
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
        
        # Regular Sales (Daily)
        sales_amt = np.random.normal(500, 100)
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

        # Month 3 Scenario: Large Tax Payment and Late Paying Clients
        if month == 3:
            # Large Tax Payment on March 15
            if day == 15:
                data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Description': 'Annual Corporate Tax Payment',
                    'Category': 'Tax',
                    'Debit': 45000,
                    'Credit': 0
                })
            
            # Late Paying Clients (Revenue recorded, but no cash - simplified as 0 Credit for Sales/Consulting)
            if day in [5, 12, 25]:
                client = late_paying_clients.pop(0) if late_paying_clients else "Client"
                data.append({
                    'Date': current_date.strftime('%Y-%m-%d'),
                    'Description': f'Consulting Fee - {client} (LATE PAYMENT - RECORDED BUT UNPAID)',
                    'Category': 'Consulting Fee',
                    'Debit': 0,
                    'Credit': 0 # Proves the cash crunch: revenue is recorded in accounting sense usually, but here we show 0 cash inflow
                })
        elif month != 3:
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
    output_file = 'sample_financial_data.csv'
    df.to_csv(output_file, index=False)
    print(f"Successfully generated {len(df)} transactions to {output_file}")
    
    return df

if __name__ == "__main__":
    generate_financial_data()
