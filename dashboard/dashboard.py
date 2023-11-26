# Import Libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from datetime import timedelta
from babel import Locale
st.set_page_config(layout="wide")

def create_count_order_product(df):
    # Membuat dataframe untuk menghitung jumlah orderan berdasarkan kategori product
    count_order_product = df.groupby(by=["product_category_name_english"]).agg({
        "order_item_id" : "count"
    }).rename(columns={"order_item_id": "jumlah"}).reset_index().sort_values(by='jumlah', ascending=False)
    
    return count_order_product

def create_daily_orders_df(df):
    # Menggunakan resample dengan aturan 'D' untuk per hari
    daily_orders_df = df.resample(rule='D', on="order_purchase_timestamp").agg({
        "order_id" : "nunique"
    })
   
    # Reset index
    daily_orders_df = daily_orders_df.reset_index()
    
    # Mengganti nama kolom
    daily_orders_df.rename(columns={
        "order_id" : "order_count"
    }, inplace=True)

    return daily_orders_df

def create_count_state_customer(df):
    # Membuat dataframe untuk menghitung jumlah orderan berdasarkan nama statenya
    count_state_customer = df.groupby(by=["detail_state"]).agg({
        "order_id" : "nunique"
    }).rename(columns={"order_id": "jumlah_order"}).reset_index().sort_values(by='jumlah_order', ascending=False)
    
    return count_state_customer

def create_rfm_df(df):
    # Membuat dataframe untuk menghitung jumlah product yang dibeli, jumlah revenue, 
    # dan selisih hari belanja terakhir customer dengan orderan terakhir dari data pada tiap customer
    rfm_df = df.groupby(by="customer_idx", as_index=False).agg({
        "order_purchase_timestamp" : "max", # Mengambil tanggal order terakhir
        "order_item_id" : "count", # Menghitung jumlah product yang dibeli
        "price" : "sum" # Menghitung jumlah revenue yang dihasilkan
    })

    # Mengganti nama kolom
    rfm_df.columns = ["customer_idx", "max_order_timestamp", "frequency", "monetary"]
    
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    print(recent_date)
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    print(rfm_df[['customer_idx', 'recency']].sort_values(by='recency').head(5))

    # Menghapus kolom yang tidak diperlukan
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)

    return rfm_df

# Load dataset
df = pd.read_csv("dashboard/main_data.csv")


st.markdown("<h1 style='text-align: center; font-size: 65px;'>Proyek Analisis Data \U0001F4CA</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 30px;'>by : Anggita Ramadhani</p>", unsafe_allow_html=True)

st.write("")
st.write("")

# convert tipe data ke datetime
convert_datetime = ["order_purchase_timestamp", "order_estimated_delivery_date", "shipping_limit_date"]
df.sort_values(by="order_purchase_timestamp", inplace=True)
df.reset_index(inplace=True)

for column in convert_datetime:
    df[column] = pd.to_datetime(df[column])

min_date = df["order_purchase_timestamp"].min() # Inisiasi min date
max_date = df["order_purchase_timestamp"].max() # Inisiasis max date

# Membuat Date Input
start_date, end_date = st.date_input(
    label='Pilih rentang waktu untuk melihat data', 
    min_value=min_date, 
    max_value=max_date,
    value=[min_date, max_date]
)

# Filter data berdasarkan rentang tanggal
main_df = df[(df["order_purchase_timestamp"] >= str((start_date) - timedelta(days=1))) &
             (df["order_purchase_timestamp"] <= str((end_date) + timedelta(days=1)))]

# Membuat DataFrame
daily_orders_df = create_daily_orders_df(main_df)
count_order_product = create_count_order_product(main_df)
count_state_customer = create_count_state_customer(main_df)
rfm_df = create_rfm_df(main_df)

st.write("")
st.write("")
st.write("")

st.subheader("Most and Less of Category Product")

st.write("")

# Membuat subplot
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))

# Warna yang akan digunakan dalam plot
colors = ["#E74C3C", "#F5CBA7", "#F5CBA7", "#F5CBA7", "#F5CBA7"]

# Plot pertama (Top 5 kategori terbanyak)
sns.barplot(x="jumlah", y="product_category_name_english", data=count_order_product.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Most of Category Product", loc="center", fontsize=40)
ax[0].tick_params(axis="y", labelsize=35)
ax[0].tick_params(axis="x", labelsize=30)

# Plot kedua (Top 5 kategori paling sedikit)
sns.barplot(x="jumlah", y="product_category_name_english", data=count_order_product.sort_values(by="jumlah", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Less of Category Product", loc="center", fontsize=40)
ax[1].tick_params(axis="y", labelsize=30)
ax[1].tick_params(axis="x", labelsize=35)

# Menampilkan plot
st.pyplot(fig)

st.write("")
st.write("")
st.write("")

st.subheader('Daily Orders')
with st.container():
    orders = daily_orders_df.order_count.sum()
    st.metric("Jumlah Order", orders)

    st.write(daily_orders_df)
    st.write(orders)
    # Plotting
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(
        daily_orders_df["order_purchase_timestamp"],
        daily_orders_df["order_count"], 
        marker='o',
        linewidth=2,
        color="#D94B95"
    )
    plt.xticks(fontsize=10, rotation=45)
    plt.yticks(fontsize=10)

    # Menampilkan plot
    st.pyplot(fig)

st.write("")
st.write("")
st.write("")

st.subheader("Order Customer by States")

# Membuat subplot
fig, ax = plt.subplots(figsize=(10, 6))

# Warna yang akan digunakan dalam plot
colors_ = ["#A688BE", "#EAD1DC", "#EAD1DC", "#EAD1DC", "#EAD1DC"]

# Membuat plot bar dan menyimpan objek sumbu ke dalam variabel ax
ax = sns.barplot(
    x="detail_state",
    y="jumlah_order",
    data=count_state_customer.head(5).sort_values(by="jumlah_order", ascending=False),
    palette=colors_
)

# Menghapus label pada sumbu x dan y
ax.set(xlabel=None, ylabel=None)

# Menampilkan plot
st.pyplot(fig)

st.write("")
st.write("")
st.write("")

st.subheader("Best Customer Based on RFM Parameters (customer_idx)")

col1, col2, col3 = st.columns(3)

with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)

with col3:
    # Definisikan locale untuk Bahasa Portugis di Brazil
    locale = Locale('pt', 'BR')
    avg_monetary = format_currency(rfm_df.monetary.mean(), "BRL", locale=locale)
    st.metric("Average Monetary", value=avg_monetary)

# Membuat subplot
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))

# Warna yang akan digunakan dalam plot
colors = ["#B1D8D8", "#B1D8D8", "#B1D8D8", "#B1D8D8", "#B1D8D8"]

# Plot pertama (By Recency)
sns.barplot(y="recency", x="customer_idx", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='x', labelsize=35, rotation=45)
ax[0].tick_params(axis='y', labelsize=30)

# Plot kedua (By Frequency)
sns.barplot(y="frequency", x="customer_idx", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='x', labelsize=35, rotation=45)
ax[1].tick_params(axis='y', labelsize=30)

# Plot ketiga (By Monetary)
sns.barplot(y="monetary", x="customer_idx", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='x', labelsize=35, rotation=45)
ax[2].tick_params(axis='y', labelsize=30)

# Menampilkan plot
st.pyplot(fig)
