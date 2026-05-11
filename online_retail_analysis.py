import pandas as pd

# ============ LOAD DATA ============
df = pd.read_csv('online_retail.csv', encoding='latin-1')
print("Original shape:", df.shape)

# ============ STEP 1: REMOVE CANCELLED ORDERS ============
cancelled = df['Invoice'].astype(str).str.startswith('C')
df = df[~cancelled]
print("After removing cancellations:", len(df))

# ============ STEP 2: REMOVE BAD QUANTITIES AND PRICES ============
df = df[df['Quantity'] > 0]
df = df[df['Price'] > 0]
print("After removing bad quantities/prices:", len(df))

# ============ STEP 3: REMOVE MISSING CUSTOMER IDs ============
df = df.dropna(subset=['Customer ID'])
print("After removing missing customers:", len(df))

# ============ STEP 4: FIX DATA TYPES ============
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['Customer ID'] = df['Customer ID'].astype(int)

# ============ STEP 5: ADD REVENUE COLUMN ============
df['Revenue'] = df['Quantity'] * df['Price']

# ============ STEP 6: ADD DATE COLUMNS ============
df['Month'] = df['InvoiceDate'].dt.month
df['Year'] = df['InvoiceDate'].dt.year

print("\nClean dataset shape:", df.shape)
print("Date range:", df['InvoiceDate'].min(), "to", df['InvoiceDate'].max())
print("Unique customers:", df['Customer ID'].nunique())
print("Unique countries:", df['Country'].nunique())
print("Total revenue: £", round(df['Revenue'].sum(), 2))

# ============ INSIGHT 1: REVENUE BY COUNTRY ============
country_revenue = df.groupby('Country')['Revenue'].sum()
country_revenue = country_revenue.sort_values(ascending=False).head(10)
print("\nTop 10 Countries by Revenue:")
print(country_revenue)

# ============ INSIGHT 2: MONTHLY REVENUE ============
monthly = df.groupby(['Year', 'Month'])['Revenue'].sum()
print("\nMonthly Revenue:")
print(monthly)

# ============ INSIGHT 3: TOP CUSTOMERS ============
top_customers = df.groupby('Customer ID')['Revenue'].sum()
top_customers = top_customers.sort_values(ascending=False).head(10)
print("\nTop 10 Customers by Revenue:")
print(top_customers)

# ============ INSIGHT 4: TOP PRODUCTS (CLEANED) ============
non_products = ['Manual', 'POSTAGE', 'AMAZONFEE', 'DOTCOM POSTAGE']
df_clean = df[~df['Description'].isin(non_products)]
top_products = df_clean.groupby('Description')['Revenue'].sum()
top_products = top_products.sort_values(ascending=False).head(10)
print("\nReal Top 10 Products:")
print(top_products)

# ============ CUSTOMER SEGMENTATION ============
customer_stats = df.groupby('Customer ID').agg(
    Total_Revenue=('Revenue', 'sum'),
    Total_Orders=('Invoice', 'nunique'),
    Total_Items=('Quantity', 'sum')
).reset_index()

customer_stats['Avg_Order_Value'] = (
    customer_stats['Total_Revenue'] / customer_stats['Total_Orders']
)

def segment(row):
    if row['Total_Revenue'] > 10000:
        return 'VIP'
    elif row['Total_Revenue'] > 3000:
        return 'High Value'
    elif row['Total_Revenue'] > 500:
        return 'Mid Value'
    else:
        return 'Low Value'

customer_stats['Segment'] = customer_stats.apply(segment, axis=1)

print("\nCustomer Segments:")
print(customer_stats['Segment'].value_counts())
print("\nRevenue per Segment:")
print(customer_stats.groupby('Segment')['Total_Revenue'].sum().sort_values(ascending=False))

# ============ SAVE FILES FOR POWER BI ============
customer_stats.to_csv('customer_segments_retail.csv', index=False)
print("\nSaved: customer_segments_retail.csv")

# Monthly summary for Power BI
monthly_summary = df.groupby(['Year', 'Month'])['Revenue'].sum().reset_index()
monthly_summary.to_csv('monthly_revenue.csv', index=False)
print("Saved: monthly_revenue.csv")

# Country summary for Power BI
country_summary = df.groupby('Country')['Revenue'].sum().reset_index()
country_summary.columns = ['Country', 'Total_Revenue']
country_summary = country_summary.sort_values('Total_Revenue', ascending=False)
country_summary.to_csv('country_revenue.csv', index=False)
print("Saved: country_revenue.csv")

# Top products for Power BI
top_products_full = df_clean.groupby('Description')['Revenue'].sum().reset_index()
top_products_full.columns = ['Product', 'Total_Revenue']
top_products_full = top_products_full.sort_values('Total_Revenue', ascending=False).head(20)
top_products_full.to_csv('top_products.csv', index=False)
print("Saved: top_products.csv")

print("\nAll files saved. Ready for Power BI.")