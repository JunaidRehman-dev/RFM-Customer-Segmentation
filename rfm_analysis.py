import pandas as pd
import os

# Reading the Excel file 
print("1- Loading raw dataset from Excel...")
df = pd.read_excel('data/raw/online_retail_II.xlsx',sheet_name='Year 2009-2010')

# Droping rows where customer ID is missing because we need every row to have a valid customer so we can group purchases by customer.
print("2- Cleaning dataset...")
df_clean = df.dropna(subset=['Customer ID'])                                          #using "subset" with "dropna" so that we only drop the row which has a customer id missing because without this it would drop the whole row even if any column was missing which we dont want .            

# Filtering out negative values 
df_clean = df_clean[df_clean['Quantity'] > 0]
df_clean = df_clean[df_clean['Price'] > 0]

# Creating a new column
df_clean['TotalSum'] = df_clean['Quantity'] * df_clean['Price']


# Grouping by 'customer id' and calculating frequency and Monetary value
print("3- Performing RFM aggregations by Customer ID...")

rfm = df_clean.groupby('Customer ID').agg({
    'Invoice': 'count',    # Frequency: Total number of purchases/items
    'TotalSum': 'sum'      # Monetary: Total money spent across all purchases
})

# Rename columns so they are easy to understand
rfm.columns = ['Frequency', 'Monetary']



# Ensuring InvoiceDate is in proper datetime format
df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])

# Set the reference date (1 day after the last transaction date in the dataset)
today_date = df_clean['InvoiceDate'].max() + pd.Timedelta(days=1)

# Defining a regular function to compute days since last order
def get_recency(dates):
    last_date = dates.max()
    days_difference = (today_date - last_date).days
    return days_difference

# Update the grouped RFM aggregation using our recency function
rfm = df_clean.groupby('Customer ID').agg({
    'InvoiceDate': get_recency,   # Recency: Days since last order
    'Invoice': 'count',           # Frequency: Total items bought
    'TotalSum': 'sum'             # Monetary: Total spending
})

# Renaming columns cleanly
rfm.columns = ['Recency', 'Frequency', 'Monetary']

# creating a function to determine levels of the customers based on their last purchase
print("4- Scoring Recency, Frequency, and Monetary metrics (1 to 5)...")

def get_recency_score(days):
    if days <= 30:
        return 5
    elif days <= 90:
        return 4
    elif days <= 180:
        return 3
    elif days <= 365:
        return 2
    else:
        return 1

# 2. creating a function to determine levels of the customers based on their frequent purchases
def get_frequency_score(count):
    if count >= 100:
        return 5
    elif count >= 50:
        return 4
    elif count >= 20:
        return 3
    elif count >= 5:
        return 2
    else:
        return 1

# 3. creating a function to determine levels of the customers based on their monetary value
print("5- Categorizing customers into business segments...")
def get_monetary_score(money): 
    if money >= 2000:
        return 5
    elif money >= 1000:
        return 4
    elif money >= 500:
        return 3
    elif money >= 200:
        return 2
    else:
        return 1

# Appling the custom functions to create our new score columns
rfm['R_Score'] = rfm['Recency'].apply(get_recency_score)
rfm['F_Score'] = rfm['Frequency'].apply(get_frequency_score)
rfm['M_Score'] = rfm['Monetary'].apply(get_monetary_score)



# categorizing customers based on Recency Score and Frequency Score

def assign_segment(row):
    r = row['R_Score']
    f = row['F_Score']
    
    if r >= 4 and f >= 4:
        return 'Champions'
    elif r >= 3 and f >= 4:
        return 'Loyal Customers'
    elif r <= 2 and f >= 3:
        return 'At Risk'
    elif r <= 3 and f <= 2:
        return 'About to Sleep'
    elif r == 1 and f == 1:
        return 'Lost'
    else:
        return 'Needs Attention'

# Appling the function across rows using axis=1
rfm['Segment'] = rfm.apply(assign_segment, axis=1)

# Exporting the entire customer dataset to Excel
print("6- Exporting entire customer dataset to Excel...")

# Reset index so Customer ID becomes a standard column in Excel
rfm_export = rfm.reset_index()

# Save complete dataset
excel_filename = 'RFM_Customer_Segmentation_Report.xlsx'
rfm_export.to_excel(excel_filename, index=False)

print(f"[SUCCESS] Full report saved as '{excel_filename}' ({len(rfm_export):,} customer rows exported).")

print("\n")
print("------------------------------ FINAL RFM SEGMENTATION RESULT ------------------------------")
print(rfm.head(10))

# Summary count of customers per segment
print("\n")
print("------------------------------  Customer Count per Segment ------------------------------")
print(rfm['Segment'].value_counts())

