import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import calendar
import os

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

# --------------------------
# LOGIN SYSTEM
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def dashboard():
    st.title("📊 Supply Chain Dashboard")

    # --- Load Data ---
    @st.cache_data(ttl=600)
    def load_data():
        file_path = "DataCo.zip"

        if not os.path.exists(file_path):
            st.error(f"File not found at {file_path}")
            return pd.DataFrame()  # Return empty dataframe if file missing

        # Fix: specify encoding to avoid UnicodeDecodeError
        try:
            df = pd.read_csv(file_path, compression="zip", encoding="latin1")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, compression="zip", encoding="cp1252")  # fallback for Windows

        # --- Handle Order Date Column Robustly ---
        date_cols = [c for c in df.columns if "order_date" in c.lower()]
        if date_cols:
            date_col = date_cols[0]  # take first match
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            df["Year"] = df[date_col].dt.year
            df["Month_Num"] = df[date_col].dt.month
            df["Month_Name"] = df["Month_Num"].apply(
                lambda x: calendar.month_abbr[x] if pd.notnull(x) else ""
            )
        else:
            st.error("⚠️ No order date column found in dataset!")

        # Revenue & On-time
        if all(
            col in df.columns
            for col in ["Order_Item_Product_Price", "Order_Item_Quantity", "Order_Item_Discount"]
        ):
            df["Revenue"] = (
                df["Order_Item_Product_Price"] * df["Order_Item_Quantity"]
            ) - df["Order_Item_Discount"]

        if "Late_delivery_risk" in df.columns:
            df["on_time"] = df["Late_delivery_risk"].apply(lambda x: 1 if x == 0 else 0)

        return df

    data_co = load_data()
    if data_co.empty:
        return  # Stop dashboard if no data
    st.success(f"Data loaded successfully! Rows: {len(data_co)}")

    # --- Sidebar Filters ---
    st.sidebar.header("🔎 Filter Options")
    years = sorted(data_co["Year"].dropna().unique()) if "Year" in data_co.columns else []
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)

    shipping_modes = data_co["Shipping_Mode"].unique() if "Shipping_Mode" in data_co.columns else []
    selected_ship = st.sidebar.multiselect("Select Shipping Mode(s)", shipping_modes, default=shipping_modes)

    customer_segments = data_co["Customer_Segment"].unique() if "Customer_Segment" in data_co.columns else []
    selected_segment = st.sidebar.multiselect("Select Customer Segment(s)", customer_segments, default=customer_segments)

    products = data_co["Product_Name"].unique() if "Product_Name" in data_co.columns else []
    selected_product = st.sidebar.multiselect("Select Product(s)", products, default=products)

    # --- Apply Filters ---
    filtered_data = data_co.copy()
    if "Year" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["Year"].isin(selected_years)]
    if "Shipping_Mode" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["Shipping_Mode"].isin(selected_ship)]
    if "Customer_Segment" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["Customer_Segment"].isin(selected_segment)]
    if "Product_Name" in filtered_data.columns:
        filtered_data = filtered_data[filtered_data["Product_Name"].isin(selected_product)]

    st.subheader(f"Filtered Data Rows: {len(filtered_data)}")

    # --- KPIs ---
    total_orders = filtered_data["Order_Id"].nunique() if "Order_Id" in filtered_data.columns else 0
    total_customers = filtered_data["Customer_Id"].nunique() if "Customer_Id" in filtered_data.columns else 0
    total_revenue = filtered_data["Revenue"].sum() if "Revenue" in filtered_data.columns else 0
    total_profit = (
        filtered_data["Order_Profit_Per_Order"].sum()
        if "Order_Profit_Per_Order" in filtered_data.columns
        else 0
    )

    # Convert revenue and profit to millions
    total_revenue_m = total_revenue / 1_000_000
    total_profit_m = total_profit / 1_000_000

    aov = total_revenue / total_orders if total_orders > 0 else 0
    total_items_sold = (
        filtered_data["Order_Item_Quantity"].sum()
        if "Order_Item_Quantity" in filtered_data.columns
        else 0
    )
    total_deliveries = (
        filtered_data[filtered_data["shipping_date_DateOrders"].notna()]["Order_Id"].nunique()
        if "shipping_date_DateOrders" in filtered_data.columns
        else 0
    )
    on_time_deliveries = (
        filtered_data[filtered_data["Late_delivery_risk"] == 0]["Order_Id"].nunique()
        if "Late_delivery_risk" in filtered_data.columns
        else 0
    )
    on_time_delivery_pct = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    late_deliveries = (
        filtered_data[filtered_data["Late_delivery_risk"] == 1]["Order_Id"].nunique()
        if "Late_delivery_risk" in filtered_data.columns
        else 0
    )
    delivery_sla_breach_pct = (late_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0

    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Customers", total_customers)
    col3.metric("Total Revenue", f"${total_revenue_m:,.2f}M")
    col4.metric("Total Profit", f"${total_profit_m:,.2f}M")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Average Order Value (AOV)", f"${aov:,.2f}")
    col6.metric("Total Items Sold", total_items_sold)
    col7.metric("On-Time Delivery %", f"{on_time_delivery_pct:.2f}%")
    col8.metric("Delivery SLA Breach %", f"{delivery_sla_breach_pct:.2f}%")

    # --------------------------
    # CHARTS
    # --------------------------
    # (All your chart code goes here, unchanged)
    # ...
    

# --------------------------
# LOGIN OR DASHBOARD
# --------------------------
if not st.session_state.logged_in:
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "Ramya" and password == "Ramya123":
            st.session_state.logged_in = True
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password")
else:
    dashboard()
