import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
sns.set(style='dark')

def create_by_customer_city(df):
    by_customer_city = df.groupby(by="customer_city").customer_id.nunique().sort_values(ascending=False).reset_index()
    return by_customer_city

def create_by_customer_state(df):
    by_customer_state = df.groupby(by="customer_state").customer_id.nunique().sort_values(ascending=False).reset_index()
    return by_customer_state

def create_by_payment_sequential(df):
    by_payment_sequential = df.groupby(by="payment_sequential").order_id.nunique().sort_values(ascending=False).reset_index()
    return by_payment_sequential

def create_by_payment_type(df):
    by_payment_type = df.groupby(by="payment_type").order_id.nunique().sort_values(ascending=False).reset_index()
    return by_payment_type

def create_by_payment_installment(df):
    by_payment_installment = df.groupby(by="payment_installments").order_id.nunique().sort_values(ascending=False).reset_index()
    return by_payment_installment

def create_by_review(df):
    by_review = df.groupby(by="review_score").order_id.nunique().reset_index()
    return by_review

def create_by_order_status(df):
    by_order_status = df.groupby(by="order_status").order_id.nunique().sort_values(ascending=False).reset_index()
    return by_order_status

def create_estimated_delivery_time(df):
    df = df.assign(order_purchase_timestamp=pd.to_datetime(df['order_purchase_timestamp'])).reset_index(drop=True)
    df = df.assign(order_estimated_delivery_date=pd.to_datetime(df['order_estimated_delivery_date'])).reset_index(drop=True)
    estimated_delivery_time = df['order_estimated_delivery_date'] - df['order_purchase_timestamp']
    estimated_delivery_time = estimated_delivery_time.dt.total_seconds() / 86400
    df = df.assign(estimated_delivery_time=round(estimated_delivery_time)).reset_index(drop=True)
    mean_estimated_delivery_time = df['estimated_delivery_time'].mean()
    return mean_estimated_delivery_time

def create_delivery_time(df):
    df = df.assign(order_purchase_timestamp=pd.to_datetime(df['order_purchase_timestamp'])).reset_index(drop=True)
    df = df.assign(order_delivered_customer_date=pd.to_datetime(df['order_delivered_customer_date'])).reset_index(drop=True)
    delivery_time = df['order_delivered_customer_date'] - df['order_purchase_timestamp']
    delivery_time = delivery_time.dt.total_seconds() / 86400
    df = df.assign(delivery_time=round(delivery_time)).reset_index(drop=True)
    mean_delivery_time = df['delivery_time'].mean()
    return mean_delivery_time

def create_late_delivery_time(df):
    late_delivery = (df['delivery_time'] > df['estimated_delivery_time']).sum()
    return late_delivery

def create_monthly_order(df):
    df = df.assign(order_purchase_timestamp=pd.to_datetime(df['order_purchase_timestamp'])).reset_index(drop=True)
    monthly_order = df.resample(rule='M', on='order_purchase_timestamp').agg({
    "order_id" : "nunique",
    "price" : "sum",
    "freight_value" : "mean"
    })
    monthly_order.index = monthly_order.index.strftime('%Y-%m')
    monthly_order = monthly_order.reset_index()
    monthly_order.rename(columns={
    "order_purchase_timestamp" : "Months",
    "order_id" : "Total Orders",
    "price" : "Total Revenue",
    "freight_value" : "Average Shipping Cost per Order"
    }, inplace=True)
    monthly_order['average_order_value'] = monthly_order['Total Revenue'] / monthly_order['Total Orders']
    monthly_order.rename(columns={"average_order_value" : "Average Order Value"}, inplace=True)
    return monthly_order

def create_rfm(df):
    df = df.assign(order_purchase_timestamp=pd.to_datetime(df['order_purchase_timestamp'])).reset_index(drop=True)
    rfm = df.groupby(by="customer_unique_id", as_index=False).agg({
    "order_purchase_timestamp": "max",
    "order_id": "nunique",
    "price": "sum"
    })
    rfm.columns = ["customer_unique_id", "max_order_timestamp", "frequency", "monetary"]
    recent_date = df['order_purchase_timestamp'].max()
    rfm['recency'] = (recent_date - rfm['max_order_timestamp']).dt.days
    rfm.drop("max_order_timestamp", axis=1, inplace=True)
    return rfm

def create_by_product_category(df):
    by_product_category = df.groupby(by="product_category_name").agg({
    "order_id" : "nunique",
    "price" : "sum"
    })
    by_product_category = by_product_category.reset_index()
    by_product_category.rename(columns={
    "order_id" : "Total Orders",
    "price" : "Total Revenue"
    }, inplace=True)
    return by_product_category

def create_by_seller_city(df):
    by_seller_city = df.groupby(by="seller_city").seller_id.nunique().sort_values(ascending=False).reset_index()
    return by_seller_city

def create_by_seller_state(df):
    by_seller_state = df.groupby(by="seller_state").seller_id.nunique().sort_values(ascending=False).reset_index()
    return by_seller_state

all_df = pd.read_csv("main_data.csv")

datetime_columns = ['order_purchase_timestamp', 'order_delivered_customer_date', 'order_estimated_delivery_date']
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

with st.sidebar:
    start_date, end_date = st.date_input(
        label="Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filtered_data = all_df[(all_df['order_purchase_timestamp'] >= str(start_date)) &
                 (all_df['order_purchase_timestamp'] <= str(end_date))]

by_customer_city = create_by_customer_city(filtered_data)
by_customer_state = create_by_customer_state(filtered_data)
by_payment_sequential = create_by_payment_sequential(filtered_data)
by_payment_type = create_by_payment_type(filtered_data)
by_payment_installment = create_by_payment_installment(filtered_data)
by_review = create_by_review(filtered_data)
by_order_status = create_by_order_status(filtered_data)
mean_estimated_delivery_time = create_estimated_delivery_time(filtered_data)
mean_delivery_time = create_delivery_time(filtered_data)
late_delivery = create_late_delivery_time(filtered_data)
monthly_order = create_monthly_order(filtered_data)
rfm = create_rfm(filtered_data)
by_product_category = create_by_product_category(filtered_data)
by_seller_city = create_by_seller_city(filtered_data)
by_seller_state = create_by_seller_state(filtered_data)

st.header('Brazilian E-Commerce Dashboard :sparkles:')
 
tab1, tab2, tab3 = st.tabs(["Sales Performance Overview", "Sales Analysis", "Payment Preferences"])

with tab1:
    col1, col2, col3 = st.columns(3)
 
    with col1:
        total_order = monthly_order['Total Orders'].sum()
        st.metric("Total Orders", value=total_order)
    
    with col2:
        total_revenue = int(monthly_order['Total Revenue'].sum())
        st.metric("Total Revenue", value=total_revenue)

    with col3:
        average_order_value = round(monthly_order['Average Order Value'].mean(), 2)
        st.metric("Average Order Value", value=average_order_value)

    st.subheader('Monthly Order in 2017-2018')

    fig, ax = plt.subplots(figsize=(24,12))
    ax.plot(
        monthly_order['Months'],
        monthly_order['Total Orders'],
        marker='o',
        linewidth=3,
        color="#72BCD4"
    )
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=16)
    st.pyplot(fig)

    st.subheader('Monthly Revenue in 2017-2018')

    fig, ax = plt.subplots(figsize=(24,12))
    ax.plot(
        monthly_order['Months'],
        monthly_order['Total Revenue'],
        marker='o',
        linewidth=3,
        color="#72BCD4"
    )
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=16)
    st.pyplot(fig)

    st.subheader('Monthly AOV in 2017-2018')

    fig, ax = plt.subplots(figsize=(24,12))
    ax.plot(
        monthly_order['Months'],
        monthly_order['Average Order Value'],
        marker='o',
        linewidth=3,
        color="#72BCD4"
    )
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=16)
    st.pyplot(fig)

    col1, col2 = st.columns(2)

    with col1:
        customer_city_count = by_customer_city['customer_city'].nunique()
        st.metric("Customer City", value=customer_city_count)
    
    with col2:
        customer_state_count = by_customer_state['customer_state'].nunique()
        st.metric("Customer State", value=customer_state_count)
    
    st.subheader('Regional Order Performance')

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16,8))

    colors_1 = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    sns.barplot(x="customer_id", y="customer_city", data=by_customer_city.head(5), palette=colors_1, ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Total Orders", fontsize=15)
    ax[0].set_title("Top 5 Cities by Order Volume", loc="center", fontsize=30)
    ax[0].tick_params(axis ='y', labelsize=12)

    sns.barplot(x="customer_id", y="customer_city", data=by_customer_city.sort_values(by="customer_id", ascending=True).head(5), palette=colors_1, ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Total Orders", fontsize=15)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Bottom 5 Cities by Order Volume", loc="center", fontsize=30)
    ax[1].tick_params(axis='y', labelsize=12)

    for i, bar in enumerate(ax[0].patches):
        ax[0].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='right', color='black', fontsize=12)

    for i, bar in enumerate(ax[1].patches):
        ax[1].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='left', color='black', fontsize=12)

    st.pyplot(fig)

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16,8))

    sns.barplot(x="customer_id", y="customer_state", data=by_customer_state.head(5), palette=colors_1, ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Total Orders", fontsize=15)
    ax[0].set_title("Top 5 States by Order Volume", loc="center", fontsize=30)
    ax[0].tick_params(axis ='y', labelsize=12)

    sns.barplot(x="customer_id", y="customer_state", data=by_customer_state.sort_values(by="customer_id", ascending=True).head(5), palette=colors_1, ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Total Orders", fontsize=15)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Bottom 5 States by Order Volume", loc="center", fontsize=30)
    ax[1].tick_params(axis='y', labelsize=12)

    for i, bar in enumerate(ax[0].patches):
        ax[0].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='right', color='black', fontsize=12)

    for i, bar in enumerate(ax[1].patches):
        ax[1].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='left', color='black', fontsize=12)
        
    st.pyplot(fig)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Average Est. Delivery Time", value=round(mean_estimated_delivery_time, 2))

    with col2:
        st.metric("Average Delivery Time", value=round(mean_delivery_time, 2))

    with col3:
        st.metric("Late Deliveries", value=late_delivery)
    
    with col4:
        average_shipping_cost = round(monthly_order['Average Shipping Cost per Order'].mean(), 2)
        st.metric("Average Shipping Cost", value=average_shipping_cost)
    
    st.subheader('Monthly Average Shipping Cost per Order in 2017-2018')

    fig, ax = plt.subplots(figsize=(24,12))
    ax.plot(
        monthly_order['Months'],
        monthly_order['Average Shipping Cost per Order'],
        marker='o',
        linewidth=3,
        color="#72BCD4"
    )
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=16)
    st.pyplot(fig)

with tab2:
    col1, col2, col3 = st.columns(3)

    with col1:
        product_category_count = by_product_category['product_category_name'].nunique()
        st.metric("Product Category", value=product_category_count)
    
    with col2:
        seller_city_count = by_seller_city['seller_city'].nunique()
        st.metric("Seller City", value=seller_city_count)
    
    with col3:
        seller_state_count = by_seller_state['seller_state'].nunique()
        st.metric("Seller State", value=seller_state_count)
    
    st.subheader('Product Performance Overview')

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10,5))

    sns.barplot(x="Total Orders", y="product_category_name", data=by_product_category.sort_values(by="Total Orders", ascending=False).head(5), palette=colors_1, ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Total Orders", fontsize=15)
    ax[0].set_title("Top 5 Best-Sellers", loc="center", fontsize=20)
    ax[0].tick_params(axis ='y', labelsize=12)

    sns.barplot(x="Total Orders", y="product_category_name", data=by_product_category.sort_values(by="Total Orders", ascending=True).head(5), palette=colors_1, ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Total Orders", fontsize=15)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Bottom 5 Worst-Sellers", loc="center", fontsize=20)
    ax[1].tick_params(axis='y', labelsize=12)

    for i, bar in enumerate(ax[0].patches):
        ax[0].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='right', color='black', fontsize=12)

    for i, bar in enumerate(ax[1].patches):
        ax[1].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='left', color='black', fontsize=12)
        
    st.pyplot(fig)
    
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10,5))

    sns.barplot(x="Total Revenue", y="product_category_name", data=by_product_category.sort_values(by="Total Revenue", ascending=False).head(5), palette=colors_1, ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Total Revenue", fontsize=15)
    ax[0].set_title("Highest Revenue Products", loc="center", fontsize=20)
    ax[0].tick_params(axis ='y', labelsize=12)

    sns.barplot(x="Total Revenue", y="product_category_name", data=by_product_category.sort_values(by="Total Revenue", ascending=True).head(5), palette=colors_1, ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Total Revenue", fontsize=15)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Lowest Revenue Products", loc="center", fontsize=20)
    ax[1].tick_params(axis='y', labelsize=12)

    for i, bar in enumerate(ax[0].patches):
        ax[0].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='right', color='black', fontsize=12)

    for i, bar in enumerate(ax[1].patches):
        ax[1].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='left', color='black', fontsize=12)
        
    st.pyplot(fig)
    
    st.subheader('Regional Seller Performance')

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12,6))

    sns.barplot(x="seller_id", y="seller_city", data=by_seller_city.sort_values(by="seller_id", ascending=False).head(5), palette=colors_1, ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Total Sellers", fontsize=15)
    ax[0].set_title("TOP 5 Seller Cites", loc="center", fontsize=20)
    ax[0].tick_params(axis ='y', labelsize=12)

    sns.barplot(x="seller_id", y="seller_city", data=by_seller_city.sort_values(by="seller_id", ascending=True).head(5), palette=colors_1, ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Total Sellers", fontsize=15)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("BOTTOM 5 Seller Cities", loc="center", fontsize=20)
    ax[1].tick_params(axis='y', labelsize=12)

    for i, bar in enumerate(ax[0].patches):
        ax[0].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='right', color='black', fontsize=12)

    for i, bar in enumerate(ax[1].patches):
        ax[1].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='left', color='black', fontsize=12)
        
    st.pyplot(fig)

    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(12,6))

    sns.barplot(x="seller_id", y="seller_state", data=by_seller_state.sort_values(by="seller_id", ascending=False).head(5), palette=colors_1, ax=ax[0], legend=False)
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Total Sellers", fontsize=15)
    ax[0].set_title("TOP 5 Seller States", loc="center", fontsize=20)
    ax[0].tick_params(axis ='y', labelsize=12)

    sns.barplot(x="seller_id", y="seller_state", data=by_seller_state.sort_values(by="seller_id", ascending=True).head(5), palette=colors_1, ax=ax[1], legend=False)
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Total Sellers", fontsize=15)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("BOTTOM 5 Seller States", loc="center", fontsize=20)
    ax[1].tick_params(axis='y', labelsize=12)

    for i, bar in enumerate(ax[0].patches):
        ax[0].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='right', color='black', fontsize=12)

    for i, bar in enumerate(ax[1].patches):
        ax[1].text(bar.get_width(), bar.get_y() + bar.get_height()/2, f'{int(bar.get_width())}',
                    va='center', ha='left', color='black', fontsize=12)
    
    st.pyplot(fig)

    st.subheader('Order Status Overview')

    fig = plt.figure(figsize=(16, 8))

    colors_5 = ["#72BCD4"] + ["#D3D3D3"] * 7

    sns.barplot(
        x="order_id", 
        y="order_status",
        data=by_order_status.sort_values(by="order_id", ascending=False),
        palette=colors_5,
        legend=False
    )
    plt.ylabel(None)
    plt.xlabel("Total Orders", fontsize=15)
    plt.tick_params(axis='y', labelsize=12)

    for i, value in enumerate(by_order_status["order_id"]):
        plt.text(value, i, f' {value}', va='center', color='black')

    st.pyplot(fig)
    
    st.subheader('Customer Reviews')

    by_review["review_score"] = by_review["review_score"].astype(int)

    fig = plt.figure()

    colors_4 = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]

    sns.barplot(x="review_score", y="order_id", data=by_review, palette=colors_4, legend=False)
    plt.ylabel("Total Orders", fontsize=15)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)

    for i, value in enumerate(by_review["order_id"]):
        plt.text(i, value, f' {value}', va='bottom', ha='center', color='black', fontsize=10)

    st.pyplot(fig)

    st.subheader('RFM Analysis')
    
    col1, col2, col3 = st.columns(3)

    with col1:
        average_recency = round(rfm['recency'].mean(), 2)
        st.metric("Average Recency", value=average_recency)

    with col2:
        average_frequency = round(rfm['frequency'].mean(), 2)
        st.metric("Average Frequency", value=average_frequency)

    with col3:
        average_monetary = round(rfm['monetary'].mean(), 2)
        st.metric("Average Monetary", value=average_monetary)
    
    rfm['customer_unique_id'] = rfm['customer_unique_id'].str[:3] + ".." + rfm['customer_unique_id'].str[-3:]

    fig = plt.figure(figsize= (15,5))

    colors_6 = ["#72BCD4"] * 10

    sns.barplot(y="recency", x="customer_unique_id", data=rfm.sort_values(by="recency", ascending=True).head(10), palette=colors_6, legend=False)
    plt.title("Customer by Recency (days)", fontsize=25)
    plt.ylabel(None)
    plt.xlabel("Customer Unique ID", fontsize=15)
    plt.ylim(0)
    plt.tick_params(axis='x', labelsize=12)

    st.pyplot(fig)

    rfm['customer_unique_id'] = rfm['customer_unique_id'].str[:3] + ".." + rfm['customer_unique_id'].str[-3:]

    fig = plt.figure(figsize= (15,5))

    ax = sns.barplot(y="frequency", x="customer_unique_id", data=rfm.sort_values(by="frequency", ascending=False).head(10), palette=colors_6, legend=False)
    plt.title("Customer by Frequency", fontsize=25)
    plt.ylabel(None)
    plt.xlabel("Customer Unique ID", fontsize=15)
    plt.ylim(0)
    plt.tick_params(axis='x', labelsize=12)

    for i, p in enumerate(ax.patches):
        ax.annotate(f'{p.get_height():.0f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='bottom', fontsize=10, color='black')

    st.pyplot(fig)

    rfm['customer_unique_id'] = rfm['customer_unique_id'].str[:3] + ".." + rfm['customer_unique_id'].str[-3:]

    rfm["monetary"] = rfm["monetary"].astype(int)

    fig = plt.figure(figsize= (16,8))

    sns.barplot(y="monetary", x="customer_unique_id", data=rfm.sort_values(by="monetary", ascending=False).head(10), palette=colors_6, legend=False)
    plt.title("Customer by Monetary", fontsize=25)
    plt.ylabel(None)
    plt.xlabel("Customer Unique ID", fontsize=15)
    plt.ylim(0)
    plt.tick_params(axis='x', labelsize=12)

    for i, v in enumerate(rfm.sort_values(by="monetary", ascending=False).head(10)['monetary']):
        plt.text(i, v + 10, str(v), color='#333333', ha='center', va='bottom', fontsize=10)
    
    st.pyplot(fig)

with tab3:
    st.subheader('Payment Sequentials')

    st.write('A customer may pay for an order with more than one payment method. If they do so, a sequence will be created.')

    by_payment_sequential['payment_sequential'] = by_payment_sequential['payment_sequential'].astype(int)
    
    fig = plt.figure(figsize=(18,9))

    colors_2 = ["#72BCD4"] + ["#D3D3D3"] * 28

    sns.barplot(x="payment_sequential", y="order_id", data=by_payment_sequential, palette=colors_2, legend=False)
    plt.ylabel("Total Orders", fontsize=15)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)

    for i, value in enumerate(by_payment_sequential["order_id"]):
        plt.text(i, value, f' {value}', va='bottom', ha='center', color='black', fontsize=10)

    st.pyplot(fig)

    st.subheader('Payment Types')

    fig = plt.figure(figsize=(9,9))
    
    plt.pie(
    x=by_payment_type["order_id"],
    labels=by_payment_type["payment_type"],
    autopct='%1.1f%%')
    
    st.pyplot(fig)

    st.subheader('Payment Installments')

    by_payment_installment['payment_installments'] = by_payment_installment['payment_installments'].astype(int)
    by_payment_installment = by_payment_installment.sort_values(by="order_id", ascending=False)
    sort_payment_installment = by_payment_installment['payment_installments'].tolist()

    fig = plt.figure(figsize=(16,8))

    colors_3 = ["#72BCD4"] + ["#D3D3D3"] * 22

    sns.barplot(x="payment_installments", y="order_id", data=by_payment_installment, palette=colors_3, order=sort_payment_installment, legend=False)
    plt.ylabel("Total Orders", fontsize=15)
    plt.xlabel(None)
    plt.tick_params(axis='x', labelsize=12)

    for i, value in enumerate(by_payment_installment["order_id"], start=1):
        plt.text(i - 1, value, f' {value}', va='bottom', ha='center', color='black', fontsize=10)

    st.pyplot(fig)