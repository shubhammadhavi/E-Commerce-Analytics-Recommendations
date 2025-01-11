import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load data
file_path = "OnlineRetail.xlsx"
data = pd.read_excel(file_path)

# Data cleaning
data = data.dropna(subset=['Description', 'CustomerID'])
data['TotalPrice'] = data['Quantity'] * data['UnitPrice']
data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
data['InvoiceMonth'] = data['InvoiceDate'].dt.to_period('M')

# Sidebar filters
st.sidebar.title("Filters")
country = st.sidebar.selectbox("Select Country", ["All"] + data['Country'].unique().tolist())
start_date = st.sidebar.date_input("Start Date", data['InvoiceDate'].min())
end_date = st.sidebar.date_input("End Date", data['InvoiceDate'].max())

# Filter data based on user inputs
filtered_data = data[
    (data['InvoiceDate'] >= pd.Timestamp(start_date)) &
    (data['InvoiceDate'] <= pd.Timestamp(end_date))
]
if country != "All":
    filtered_data = filtered_data[filtered_data['Country'] == country]

# Main content
st.title("E-Commerce Analytics Dashboard")

# Key metrics
total_revenue = filtered_data['TotalPrice'].sum()
total_transactions = filtered_data['InvoiceNo'].nunique()
avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0

st.metric("Total Revenue", f"${total_revenue:,.2f}")
st.metric("Number of Transactions", total_transactions)
st.metric("Average Order Value", f"${avg_order_value:,.2f}")

# Visualizations
st.subheader("Revenue by Month")
revenue_by_month = filtered_data.groupby('InvoiceMonth')['TotalPrice'].sum()
fig, ax = plt.subplots()
revenue_by_month.plot(kind='bar', ax=ax)
ax.set_title("Monthly Revenue")
ax.set_ylabel("Revenue ($)")
st.pyplot(fig)

st.subheader("Top Products")
top_products = (
    filtered_data.groupby('Description')['TotalPrice']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(top_products)

st.subheader("Top Countries")
top_countries = (
    filtered_data.groupby('Country')['TotalPrice']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
st.bar_chart(top_countries)

# Geospatial Visualization (if geolocation data is available)
# Uncomment and add latitude/longitude columns if you want to include a map
# st.subheader("Sales by Region")
# import folium
# from streamlit_folium import folium_static
# m = folium.Map(location=[50, 0], zoom_start=2)
# for _, row in top_countries.iterrows():
#     folium.CircleMarker(location=[row['Latitude'], row['Longitude']],
#                         radius=row['TotalPrice']/1e6,
#                         popup=row['Country']).add_to(m)
# folium_static(m)

# Export filtered data
st.download_button(
    label="Download Filtered Data",
    data=filtered_data.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv"
)
