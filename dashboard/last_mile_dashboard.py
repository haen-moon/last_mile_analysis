import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_csv('../data/amazon_delivery_cleaned.csv')

st.set_page_config(page_title='Last Mile Delivery Dashboard', layout='wide')

st.title('Last Mile Delivery Analysis Dashboard')

st.sidebar.header("Filter Options")
selected_area = st.sidebar.multiselect("Select Area", options=df['Area'].unique(), default=df['Area'].unique())
selected_traffic = st.sidebar.multiselect("Select Traffic Level", options=df['Traffic'].unique(), default=df['Traffic'].unique())

df_filtered = df[(df['Area'].isin(selected_area)) & (df['Traffic'].isin(selected_traffic))]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Deliveries", len(df_filtered))

with col2:
    avg_duration = round(df_filtered['pickup_to_delivery_mins'].mean(), 1)
    st.metric("Avg. Delivery Duration", f"{avg_duration} mins")

with col3:
    fast_deliveries = len(df_filtered[df_filtered['pickup_to_delivery_mins'] <= 90])
    percent_fast = round(fast_deliveries / len(df_filtered) * 100, 1) if len(df_filtered) > 0 else 0
    st.metric("% Under 90 mins", f"{percent_fast}%")

with col4:
    same_day = len(df_filtered[df_filtered['pickup_to_delivery_mins'] <= 1440])
    st.metric("Same-day Deliveries", same_day)