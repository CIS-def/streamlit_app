#!/usr/bin/env python
# coding: utf-8

# In[2]:


import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
import plotly.graph_objects as go 
import re 
import streamlit as st 
st.set_page_config(page_title="House Listings Dashboard" , layout="wide")
@st.cache_data 

def load_data(file_path):
    df = pd.read_csv(file_path,encoding='ISO-8859-1')
    def convert_price(value): 
        if pd.isna(value): return np.nan
        value = value.strip().lower().replace(',','')
        if 'cr' in value:
            return float(re.findall(r"[\d.]+" , value)[0]) * 1e7
        elif 'lac' in value:
            return float(re.findall(r"[\d.]+" , value)[0]) * 1e5
        else:
            try: return float(value)
            except: return np.nan
    def extract_sqft(area):
        if pd.isna(area): return np.nan
        match = re.search(r'(\d+[\d,.]*)' , area.replace(',',''))
        return float(match.group(1)) if match else np.nan
    def extract_floor_info(floor_str, part='current'):
        if pd.isna(floor_str): return np.nan
        match = re.findall(r'\d+' , floor_str)
        if not match:
            return 0 if 'ground' in floor_str.lower() and part == 'current' else np.nan
        return int(match[0]) if part == 'current' else (int(match[1]) if len(match) > 1 else np.nan)
    df['Amount (numeric)'] = df['Amount(in rupees)'].apply(convert_price)
    df['Carpet Area (sqft)'] = df['Carpet Area'].apply(extract_sqft)
    df['Super Area (sqft)'] = df['Super Area'].apply(extract_sqft)
    df['Current Floor'] = df['Floor'].apply(lambda x: extract_floor_info(x,'current'))
    df['Total Floors'] = df['Floor'].apply(lambda x: extract_floor_info(x,'total'))
    return df

df = load_data("D:/pythonproject/house_data.csv")

st.title("🏠 House Listings Analysis Dashboard")

st.sidebar.header("Filter Listings")

locations = df['location'].dropna().unique()
selected_locations = st.sidebar.multiselect("select Location(s)",locations)

price_min,price_max = int(df['Amount (numeric)'].min()), int(df['Amount (numeric)'].max())
selected_price = st.sidebar.slider("Select Price Range (Rs.)",price_min,price_max,(price_min,price_max))

area_min,area_max = int(df['Carpet Area (sqft)'].min()), int(df['Carpet Area (sqft)'].max())
selected_area = st.sidebar.slider("Carpet Area Range (sqft)", area_min, area_max, (area_min, area_max)) 

df_filtered = df[(df['Amount (numeric)'].between(*selected_price)) & (df['Carpet Area (sqft)'].between(*selected_area))] 

if selected_locations:
    df_filtered = df_filtered[df_filtered['location'].isin(selected_locations)]

st.subheader("📊 Summary KPIs")
col1, col2, col3 = st.columns(3)
col1.metric("Total Listings", f"{df_filtered.shape[0]:,}")
col2.metric("Avg. Price (₹)", f"{df_filtered['Amount (numeric)'].mean():,.0f}")
col3.metric("Avg. Carpet Area (sqft)", f"{df_filtered['Carpet Area (sqft)'].mean():.0f}")

# Visualizations
st.subheader("📈 Visual Insights")

fig1, ax1 = plt.subplots()
sns.histplot(df_filtered['Amount (numeric)'], bins=40, ax=ax1, kde=True)
ax1.set_title("Price Distribution")
st.pyplot(fig1)

fig2, ax2 = plt.subplots()
sns.histplot(df_filtered['Carpet Area (sqft)'], bins=40, ax=ax2, kde=True, color='orange')
ax2.set_title("Carpet Area Distribution")
st.pyplot(fig2)

fig3, ax3 = plt.subplots()
sns.scatterplot(data=df_filtered, x='Carpet Area (sqft)', y='Amount (numeric)', alpha=0.5, ax=ax3)
ax3.set_title("Price vs. Carpet Area")
st.pyplot(fig3)

fig4, ax4 = plt.subplots()
sns.countplot(data=df_filtered[df_filtered['Current Floor'] < 50], x='Current Floor', ax=ax4)
ax4.set_title("Current Floor Distribution")
ax4.tick_params(axis='x', rotation=90)
st.pyplot(fig4)
# Additional visualizations
st.subheader("📌 Additional Visuals")

# Ownership type distribution
fig5, ax5 = plt.subplots()
sns.countplot(data=df_filtered, y='Ownership', order=df_filtered['Ownership'].value_counts().index, ax=ax5)
ax5.set_title("Ownership Type Distribution")
st.pyplot(fig5)

# Transaction type pie chart
fig6, ax6 = plt.subplots()
transaction_counts = df_filtered['Transaction'].value_counts()
ax6.pie(transaction_counts, labels=transaction_counts.index, autopct='%1.1f%%', startangle=140)
ax6.axis('equal')
ax6.set_title("Transaction Type Share")
st.pyplot(fig6)

# Status bar chart
fig7, ax7 = plt.subplots()
sns.countplot(data=df_filtered, x='Status', order=df_filtered['Status'].value_counts().index, ax=ax7)
ax7.set_title("Property Status Distribution")
st.pyplot(fig7)

# Correlation heatmap
numeric_cols = df_filtered[['Amount (numeric)', 'Carpet Area (sqft)', 'Super Area (sqft)', 'Current Floor', 'Total Floors']]
corr = numeric_cols.corr()
fig8, ax8 = plt.subplots()
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax8)
ax8.set_title("Correlation Heatmap")
st.pyplot(fig8)

# Show filtered data (optional)
with st.expander("🔍 Show Filtered Data"):
    st.dataframe(df_filtered.reset_index(drop=True))


# In[ ]:




