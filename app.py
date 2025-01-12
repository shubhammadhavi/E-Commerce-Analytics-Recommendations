import streamlit as st
import pandas as pd
import plotly.express as px

# Cached function to load data
@st.cache_data
def load_data(file_path):
    return pd.read_parquet(file_path)

# File paths
processed_data_file = "processed_data.parquet"
monthly_revenue_file = "monthly_revenue.parquet"

# Load the main data and pre-aggregated data
data = load_data(processed_data_file)
monthly_revenue = load_data(monthly_revenue_file)

# Sidebar filters
st.sidebar.title("Filters")
country = st.sidebar.selectbox(
    "Select Country", 
    ["All"] + sorted(data['Country'].unique().tolist())
)
start_date = st.sidebar.date_input("Start Date", data['InvoiceDate'].min().date())
end_date = st.sidebar.date_input("End Date", data['InvoiceDate'].max().date())

# Filter data based on user inputs
filtered_data = data[
    (data['InvoiceDate'] >= pd.Timestamp(start_date)) &
    (data['InvoiceDate'] <= pd.Timestamp(end_date))
]
if country != "All":
    filtered_data = filtered_data[filtered_data['Country'] == country]

# Main dashboard
st.title("E-Commerce Analytics Dashboard")

# Key metrics
total_revenue = filtered_data['TotalPrice'].sum()
total_transactions = filtered_data['InvoiceNo'].nunique()
avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0

st.metric("Total Revenue", f"${total_revenue:,.2f}")
st.metric("Number of Transactions", total_transactions)
st.metric("Average Order Value", f"${avg_order_value:,.2f}")

# Monthly Revenue Visualization
st.subheader("Revenue by Month")
# Convert start_date and end_date to Period type for comparison
start_period = pd.Period(start_date, freq='M')
end_period = pd.Period(end_date, freq='M')

revenue_filtered = monthly_revenue[
    (monthly_revenue['InvoiceMonth'] >= start_period) &
    (monthly_revenue['InvoiceMonth'] <= end_period)
]
fig_monthly_revenue = px.bar(
    revenue_filtered,
    x='InvoiceMonth',
    y='TotalRevenue',
    title="Monthly Revenue",
    labels={'TotalRevenue': 'Revenue ($)', 'InvoiceMonth': 'Month'},
)
st.plotly_chart(fig_monthly_revenue)

# Top Products Visualization
st.subheader("Top Products")
top_products = (
    filtered_data.groupby('Description')['TotalPrice']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
fig_top_products = px.bar(
    top_products,
    x='TotalPrice',
    y='Description',
    orientation='h',
    title="Top 10 Products by Revenue",
    labels={'TotalPrice': 'Revenue ($)', 'Description': 'Product'},
)
st.plotly_chart(fig_top_products)

# Top Countries Visualization
st.subheader("Top Countries")
top_countries = (
    filtered_data.groupby('Country')['TotalPrice']
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)
fig_top_countries = px.bar(
    top_countries,
    x='TotalPrice',
    y='Country',
    orientation='h',
    title="Top 10 Countries by Revenue",
    labels={'TotalPrice': 'Revenue ($)', 'Country': 'Country'},
)
st.plotly_chart(fig_top_countries)

# Download Filtered Data
st.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)
