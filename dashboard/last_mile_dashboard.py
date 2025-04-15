import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
import folium

df = pd.read_csv('../data/amazon_delivery_cleaned.csv')
df['Order_Date'] = pd.to_datetime(df['Order_Date'], errors='coerce')
df['order_month'] = df['Order_Date'].dt.to_period('M').astype(str)

st.set_page_config(page_title='Last Mile Delivery Performance Report', layout='wide')

st.title('Last Mile Delivery Performance Report')

header_col1, header_col2 = st.columns([5, 1])
with header_col2:
    selected_month = st.selectbox("Month", options=sorted(df['order_month'].unique()))

df_filtered = df[df['order_month'] == selected_month]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Deliveries", len(df_filtered))

with col2:
    avg_pickup = round(df_filtered['order_to_pickup_mins'].mean(), 1)
    st.metric("Avg. Pickup Duration", f"{avg_pickup} mins")

with col3:
    avg_duration = round(df_filtered['pickup_to_delivery_mins'].mean(), 1)
    st.metric("Avg. Delivery Duration", f"{avg_duration} mins")

with col4:
    fast_deliveries = len(df_filtered[df_filtered['pickup_to_delivery_mins'] <= 60])
    percent_fast = round(fast_deliveries / len(df_filtered) * 100, 1) if len(df_filtered) > 0 else 0
    st.metric("% Fast Deliveries (Less than 1 hour)", f"{percent_fast}%")

st.markdown("####")

left_col, right_col = st.columns([1, 1])

with left_col:
    st.markdown("#### Delivery Duration by Selected Metric")
    breakdown_option = st.selectbox("Select Metric", options=['Traffic', 'Weather', 'Area', 'Vehicle'])

    if breakdown_option in df_filtered.columns:
        fig_box, ax_box = plt.subplots(figsize=(10, 5))
        sns.boxplot(data=df_filtered, x=breakdown_option, y='pickup_to_delivery_mins', ax=ax_box)
        ax_box.set_ylabel("Delivery Duration (mins)")
        ax_box.set_xlabel(breakdown_option)
        ax_box.set_title(f"Delivery Duration by {breakdown_option}")
        st.pyplot(fig_box)

with right_col:
    st.write("#### Agent and Delivery Duration")
    st.write("####")
    df_filtered['rating_bin'] = pd.cut(df_filtered['Agent_Rating'], bins=[2.5, 4.0, 4.5, 4.7, 4.9, 5.0])
    df_filtered['age_group'] = pd.cut(df_filtered['Agent_Age'], bins=[20, 24, 28, 32, 36, 40])

    heatmap_data = df_filtered.pivot_table(
        index='age_group',
        columns='rating_bin',
        values='pickup_to_delivery_mins',
        aggfunc='mean'
    )

    fig_heatmap, ax_heatmap = plt.subplots(figsize=(4, 2.5))
    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.1f',
        cmap='YlGnBu',
        cbar_kws={'label': 'Ave Delivery Duration'},
        annot_kws={'size': 6}
    )
    cbar = ax_heatmap.collections[0].colorbar
    cbar.ax.tick_params(labelsize=4)
    cbar.set_label("Avg. Delivery Duration", fontsize=5)

    ax_heatmap.set_title("Avg Delivery Duration by Age and Rating", fontsize=5)
    ax_heatmap.set_xlabel("Agent Rating", fontsize=5)
    ax_heatmap.set_ylabel("Agent Age Group", fontsize=5)
    ax_heatmap.tick_params(axis='both', labelsize=4)
    st.pyplot(fig_heatmap)

st.markdown("#### Delivery Routes")

selected_columns = ['Order_ID', 'Order_Date', 'Traffic', 'Weather', 'Vehicle', 'Area', 'Category']
location_columns = ['Store_Latitude', 'Store_Longitude', 'Drop_Latitude', 'Drop_Longitude']
selected_df = df_filtered[selected_columns + location_columns].reset_index(drop=True)

map_col, table_col = st.columns([1, 2])

with map_col:
    selected_index = st.selectbox(
        "Select a delivery to view route",
        options=selected_df.index,
        format_func=lambda x: f"Order ID: {selected_df.loc[x, 'Order_ID']}",
        index=0
    )

    selected_row_data = selected_df.loc[selected_index]

    route_map = folium.Map(
        location=[
            (selected_row_data['Store_Latitude'] + selected_row_data['Drop_Latitude']) / 2,
            (selected_row_data['Store_Longitude'] + selected_row_data['Drop_Longitude']) / 2
        ],
        zoom_start=13
    )

    folium.CircleMarker(
        location=[selected_row_data['Store_Latitude'], selected_row_data['Store_Longitude']],
        radius=5, color='green', fill=True, fill_opacity=0.6, popup='Store'
    ).add_to(route_map)

    folium.CircleMarker(
        location=[selected_row_data['Drop_Latitude'], selected_row_data['Drop_Longitude']],
        radius=5, color='red', fill=True, fill_opacity=0.6, popup='Drop'
    ).add_to(route_map)

    folium.PolyLine(
        locations=[
            [selected_row_data['Store_Latitude'], selected_row_data['Store_Longitude']],
            [selected_row_data['Drop_Latitude'], selected_row_data['Drop_Longitude']],
        ],
        color='blue', weight=4, opacity=0.8
    ).add_to(route_map)

    folium_static(route_map)

with table_col:
    st.markdown("#")
    selected_row = st.dataframe(selected_df, use_container_width=True, height=500)
