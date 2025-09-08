# --------------------------
# CHARTS
# --------------------------
if "Month_Num" in filtered_data.columns:

    # 1. Monthly Orders Trend
    st.subheader("📈 Monthly Orders Trend")
    if "Order_Id" in filtered_data.columns:
        monthly_orders = filtered_data.groupby("Month_Num")["Order_Id"].nunique().reset_index()
        monthly_orders["Month_Name"] = monthly_orders["Month_Num"].apply(lambda x: calendar.month_abbr[x])
        monthly_orders = monthly_orders.sort_values("Month_Num")
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=monthly_orders, x="Month_Name", y="Order_Id", marker="o", color="teal", ax=ax)
        for i, row in monthly_orders.iterrows():
            ax.text(row["Month_Name"], row["Order_Id"] * 1.02, f"{row['Order_Id']}", ha="center", va="bottom", fontsize=9, fontweight="bold")
        ax.set_xlabel("Month")
        ax.set_ylabel("Distinct Count of Orders")
        ax.grid(True, linestyle="--", alpha=0.6)
        st.pyplot(fig)

    # 2. Top 10 Product Categories by Revenue
    if "Category_Name" in filtered_data.columns and "Revenue" in filtered_data.columns:
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
    if "Customer_Segment" in filtered_data.columns and "Order_Id" in filtered_data.columns:
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
    if "Product_Name" in filtered_data.columns and "Revenue" in filtered_data.columns:
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

    # 5. On-Time Delivery % by Month
    if "on_time" in filtered_data.columns:
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

    # 6. Top 10 Products with Late Deliveries
    if "Late_delivery_risk" in filtered_data.columns and "Product_Name" in filtered_data.columns:
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

    # 7. On-time vs Late Deliveries by Shipping Mode
    if "Shipping_Mode" in filtered_data.columns and "Late_delivery_risk" in filtered_data.columns:
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

    # 8. Late Deliveries by Shipping Mode (Pie)
    if "Shipping_Mode" in filtered_data.columns and "Late_delivery_risk" in filtered_data.columns:
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

    # 9. Orders by Shipping Mode (Pie)
    if "Shipping_Mode" in filtered_data.columns and "Order_Id" in filtered_data.columns:
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

    # 10. Total Customers by Shipping Mode
    if "Shipping_Mode" in filtered_data.columns and "Customer_Id" in filtered_data.columns:
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

    # 11. Late Deliveries by Shipping Mode (Column)
    if "Shipping_Mode" in filtered_data.columns and "Late_delivery_risk" in filtered_data.columns:
        st.subheader("🚨 Late Deliveries by Shipping Mode")
        late_deliveries = filtered_data[filtered_data['Late_delivery_risk']==1].groupby('Shipping_Mode')['Order_Id'].count()
        late_deliveries = late_deliveries.sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10,6))
        late_deliveries.plot(kind='bar', color='salmon', ax=ax)
        for i, val in enumerate(late_deliveries):
            ax.text(i, val+0.5, f"{val}", ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax.set_xlabel("Shipping Mode")
        ax.set_ylabel("Number of Late Deliveries")
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        st.pyplot(fig)
