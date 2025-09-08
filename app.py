import streamlit as st
import pandas as pd
import pyodbc
import matplotlib.pyplot as plt
import seaborn as sns
import calendar

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
        server = 'localhost\\SQLEXPRESS'
        database = 'Supply_Chain'
        driver = '{ODBC Driver 17 for SQL Server}'
        conn = pyodbc.connect(f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;')
        df = pd.read_sql("SELECT * FROM dbo.DataCo", conn)
        conn.close()

        # Convert date column
        df['order_date_DateOrders'] = pd.to_datetime(df['order_date_DateOrders'])
        df['Year'] = df['order_date_DateOrders'].dt.year
        df['Month_Num'] = df['order_date_DateOrders'].dt.month
        df['Month_Name'] = df['Month_Num'].apply(lambda x: calendar.month_abbr[x])

        # Revenue & On-time
        df['Revenue'] = (df["Order_Item_Product_Price"] * df["Order_Item_Quantity"]) - df["Order_Item_Discount"]
        df['on_time'] = df['Late_delivery_risk'].apply(lambda x: 1 if x == 0 else 0)
        return df

    data_co = load_data()
    st.success(f"Data loaded successfully! Rows: {len(data_co)}")

    # --- Sidebar Filters ---
    st.sidebar.header("🔎 Filter Options")
    years = sorted(data_co['Year'].unique())
    selected_years = st.sidebar.multiselect("Select Year(s)", years, default=years)

    shipping_modes = data_co['Shipping_Mode'].unique()
    selected_ship = st.sidebar.multiselect("Select Shipping Mode(s)", shipping_modes, default=shipping_modes)

    customer_segments = data_co['Customer_Segment'].unique()
    selected_segment = st.sidebar.multiselect("Select Customer Segment(s)", customer_segments, default=customer_segments)

    products = data_co['Product_Name'].unique()
    selected_product = st.sidebar.multiselect("Select Product(s)", products, default=products)

    # --- Apply Filters ---
    filtered_data = data_co[
        (data_co['Year'].isin(selected_years)) &
        (data_co['Shipping_Mode'].isin(selected_ship)) &
        (data_co['Customer_Segment'].isin(selected_segment)) &
        (data_co['Product_Name'].isin(selected_product))
    ]

    st.subheader(f"Filtered Data Rows: {len(filtered_data)}")

    # --- KPIs ---
    total_orders = filtered_data["Order_Id"].nunique()
    total_customers = filtered_data["Customer_Id"].nunique()
    total_revenue = filtered_data["Revenue"].sum()
    total_profit = filtered_data["Order_Profit_Per_Order"].sum() if "Order_Profit_Per_Order" in filtered_data.columns else 0
    aov = total_revenue / total_orders if total_orders > 0 else 0
    total_items_sold = filtered_data["Order_Item_Quantity"].sum()
    total_deliveries = filtered_data[filtered_data["shipping_date_DateOrders"].notna()]["Order_Id"].nunique()
    on_time_deliveries = filtered_data[filtered_data["Late_delivery_risk"] == 0]["Order_Id"].nunique()
    on_time_delivery_pct = (on_time_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0
    late_deliveries = filtered_data[filtered_data["Late_delivery_risk"] == 1]["Order_Id"].nunique()
    delivery_sla_breach_pct = (late_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0

    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Customers", total_customers)
    col3.metric("Total Revenue", f"${total_revenue:,.2f}")
    col4.metric("Total Profit", f"${total_profit:,.2f}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Average Order Value (AOV)", f"${aov:,.2f}")
    col6.metric("Total Items Sold", total_items_sold)
    col7.metric("On-Time Delivery %", f"{on_time_delivery_pct:.2f}%")
    col8.metric("Delivery SLA Breach %", f"{delivery_sla_breach_pct:.2f}%")

    # --------------------------
    # CHARTS
    # --------------------------

    # 1. Monthly Orders Trend
    st.subheader("📈 Monthly Orders Trend")
    monthly_orders = filtered_data.groupby("Month_Num")["Order_Id"].nunique().reset_index()
    monthly_orders["Month_Name"] = monthly_orders["Month_Num"].apply(lambda x: calendar.month_abbr[x])
    monthly_orders = monthly_orders.sort_values("Month_Num")
    fig, ax = plt.subplots(figsize=(12,6))
    sns.lineplot(data=monthly_orders, x="Month_Name", y="Order_Id", marker="o", color="teal", ax=ax)
    for i, row in monthly_orders.iterrows():
        ax.text(row["Month_Name"], row["Order_Id"]*1.02, f"{row['Order_Id']}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_xlabel("Month")
    ax.set_ylabel("Distinct Count of Orders")
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # 2. Top 10 Product Categories by Revenue
    st.subheader("🏆 Top 10 Product Categories by Revenue")
    revenue_by_category = filtered_data.groupby("Category_Name")["Revenue"].sum().nlargest(10).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10,6))
    revenue_by_category.plot(kind="barh", color="teal", ax=ax)
    for i, val in enumerate(revenue_by_category):
        ax.text(val, i, f"{val:,.0f}", va="center", ha="left", fontsize=9, fontweight="bold")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Category")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # 3. Orders by Customer Segment (Pie)
    st.subheader("📊 Orders by Customer Segment")
    orders_by_segment = filtered_data.groupby("Customer_Segment")["Order_Id"].nunique().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7,7))
    ax.pie(
        orders_by_segment,
        labels=orders_by_segment.index,
        autopct=lambda p: f'{p:.1f}%\n({int(p*orders_by_segment.sum()/100):,})',
        startangle=90,
        counterclock=False
    )
    st.pyplot(fig)

    # 4. Top 10 Products by Revenue
    st.subheader("💰 Top 10 Products by Revenue")
    revenue_by_product = filtered_data.groupby("Product_Name")["Revenue"].sum().nlargest(10).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10,6))
    revenue_by_product.plot(kind="barh", color="teal", ax=ax)
    for i, val in enumerate(revenue_by_product):
        ax.text(val, i, f"${val:,.0f}", va="center", ha="left", fontsize=9, fontweight="bold")
    ax.set_xlabel("Revenue")
    ax.set_ylabel("Product Name")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # --- Chart 5: On-Time Delivery % by Month ---
    st.subheader("🚚 Average On-Time Delivery % by Month")
    on_time_trend = filtered_data.groupby('Month_Num')['on_time'].mean()*100
    on_time_trend = on_time_trend.reset_index()
    on_time_trend['Month_Name'] = on_time_trend['Month_Num'].apply(lambda x: calendar.month_abbr[x])
    on_time_trend = on_time_trend.sort_values('Month_Num')
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(on_time_trend['Month_Name'], on_time_trend['on_time'], marker='o', color='teal', linewidth=2)
    for i, val in enumerate(on_time_trend['on_time']):
        ax.text(i, val + 0.1, f"{val:.1f}%", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylim(on_time_trend['on_time'].min()-1, on_time_trend['on_time'].max()+1)
    ax.set_xlabel("Month")
    ax.set_ylabel("On-Time Delivery %")
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # --- Chart 6: Top 10 Products with Late Deliveries ---
    st.subheader("❌ Top 10 Products with Late Deliveries")
    late_by_product = filtered_data[filtered_data['Late_delivery_risk']==1]['Product_Name'].value_counts().nlargest(10).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10,6))
    late_by_product.plot(kind="barh", color="salmon", ax=ax)
    for i, val in enumerate(late_by_product):
        ax.text(val, i, f"{val}", va='center', ha='left', fontsize=9, fontweight='bold')
    ax.set_xlabel("Late Deliveries Count")
    ax.set_ylabel("Product Name")
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # --- Chart 7: On-time vs Late Deliveries by Shipping Mode ---
    st.subheader("🚛 On-Time vs Late Deliveries by Shipping Mode")
    delivery_by_shipmode = filtered_data.groupby(['Shipping_Mode','Late_delivery_risk']).size().unstack(fill_value=0)
    delivery_by_shipmode.columns = ['On-time','Late']
    fig, ax = plt.subplots(figsize=(10,6))
    delivery_by_shipmode.plot(kind='bar', color=['teal','salmon'], ax=ax)
    for p in ax.patches:
        ax.annotate(str(int(p.get_height())), (p.get_x()+p.get_width()/2, p.get_height()), ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_ylabel("Number of Deliveries")
    ax.set_xlabel("Shipping Mode")
    ax.set_xticklabels(delivery_by_shipmode.index, rotation=0)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    st.pyplot(fig)

    # --- Chart 8: Late Deliveries by Shipping Mode (Pie) ---
    st.subheader("⏱ Late Deliveries by Shipping Mode")
    late_by_shipmode = filtered_data[filtered_data['Late_delivery_risk']==1]['Shipping_Mode'].value_counts()
    fig, ax = plt.subplots(figsize=(7,7))
    ax.pie(
        late_by_shipmode,
        labels=late_by_shipmode.index,
        autopct=lambda p: f'{p:.1f}%\n({int(p*late_by_shipmode.sum()/100):,})',
        startangle=90,
        counterclock=False,
        colors=['teal','salmon','gold','lightblue']
    )
    st.pyplot(fig)

    # --- Chart 9: Orders by Shipping Mode (Pie) ---
    st.subheader("📦 Orders by Shipping Mode")
    orders_by_shipmode = filtered_data.groupby('Shipping_Mode')['Order_Id'].nunique()
    fig, ax = plt.subplots(figsize=(7,7))
    ax.pie(
        orders_by_shipmode,
        labels=orders_by_shipmode.index,
        autopct=lambda p: f'{p:.1f}%\n({int(p*orders_by_shipmode.sum()/100):,})',
        startangle=90,
        counterclock=False,
        colors=['teal','salmon','gold','lightblue']
    )
    st.pyplot(fig)

    # --- Chart 10: Total Customers by Shipping Mode ---
    st.subheader("👥 Total Customers by Shipping Mode")
    customers_by_shipmode = filtered_data.groupby('Shipping_Mode')['Customer_Id'].nunique().sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(10,6))
    customers_by_shipmode.plot(kind='barh', color='teal', ax=ax)
    for i, val in enumerate(customers_by_shipmode):
        ax.text(val, i, f"{val}", va='center', ha='left', fontsize=9, fontweight='bold')
    ax.set_xlabel("Number of Distinct Customers")
    ax.set_ylabel("Shipping Mode")
    ax.grid(axis='x', linestyle='--', alpha=0.6)
    st.pyplot(fig)

    # --- Chart 11: Late Deliveries by Shipping Mode (Column) ---
    st.subheader("🚨 Late Deliveries by Shipping Mode")
    late_deliveries = filtered_data[filtered_data['Late_delivery_risk']==1].groupby('Shipping_Mode')['Order_Id'].count()
    fig, ax = plt.subplots(figsize=(10,6))
    late_deliveries.sort_values(ascending=False).plot(kind='bar', color='salmon', ax=ax)
    for i, val in enumerate(late_deliveries.sort_values(ascending=False)):
        ax.text(i, val+0.5, f"{val}", ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.set_xlabel("Shipping Mode")
    ax.set_ylabel("Number of Late Deliveries")
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    st.pyplot(fig)

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

