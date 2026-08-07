import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
from datetime import timedelta

# Set page configurations
st.set_page_config(
    page_title="Olist Store Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply global styling
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'

# Custom CSS modern look
st.markdown("""
    <style>
    /* Main container styling forcing white background and dark text */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
    }
    
    /* Sidebar styling for light theme consistency and high contrast */
    [data-testid="stSidebar"], section[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] * {
        color: #1E293B !important;
    }
    
    /* Style date inputs inside the sidebar to be light and clear */
    [data-testid="stSidebar"] div[data-testid="stDateInput"] input {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] div[data-testid="stDateInput"] label,
    [data-testid="stSidebar"] div[data-testid="stDateInput"] p {
        color: #1E293B !important;
        font-weight: 500 !important;
    }
    
    /* Styled Metric Cards with subtle hover micro-animation */
    div[data-testid="stMetric"] {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0;
        padding: 15px 20px !important;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.08);
        border-color: #CBD5E1;
    }
    
    /* Metric label and value custom typography */
    div[data-testid="stMetricLabel"] * {
        font-size: 13px !important;
        color: #64748B !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }
    div[data-testid="stMetricValue"] * {
        font-size: 24px !important;
        color: #0F172A !important;
        font-weight: 700 !important;
    }
    
    /* Custom style for tab headers */
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #64748B !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #1E88E5 !important;
    }
    
    /* Clean headers and text */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        color: #1E293B !important;
    }
    p, .stMarkdown p {
        color: #334155 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Menyiapkan dataframe order items
def create_sum_order_items_df(df):
    sum_order_items_df = df.groupby(by="product_category_name").agg({
        "order_id": "count",
    }).sort_values(by="order_id", ascending=False)
    return sum_order_items_df

# Menyiapkan df untuk menghasilkan rfm
def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": "max", # mengambil tanggal order terakhir
        "order_id": "nunique", # menghitung jumlah order
        "price": "sum" # menghitung jumlah revenue yang dihasilkan
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    # menghitung kapan terakhir pelanggan melakukan transaksi (hari)
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    # Mempersingkat customer_id agar lebih terbaca pada visualisasi
    rfm_df["customer_id"] = rfm_df["customer_id"].apply(lambda x: x[:8] + "...")
    
    return rfm_df

# Load dataset yang sudah dianalisis
all_df = pd.read_csv("dashboard/all_data.csv")

# Memastikan kolom format datetime
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"], errors="coerce")

# Inisialisasi filter rentang tanggal
min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()+timedelta(days=1)

#Tampilin sidebar dengan Date Input
with st.sidebar:
    # Menambahkan logo perusahaan
    layout1, layout2, layout3 = st.columns([1, 2, 1])
    with layout2:
        st.image("dashboard/olist_logo.png", width=100)
    
    st.markdown("<h3 style='text-align: center; color: #475569;'>Filter Dashboard</h3>", unsafe_allow_html=True)
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Simpan hasil filter all_df ke main_df
main_df = all_df[(all_df["order_purchase_timestamp"] >= str(start_date)) & 
                (all_df["order_purchase_timestamp"] <= str(end_date))]

# Memanggil Helper Function
sum_order_items_df = create_sum_order_items_df(main_df)
rfm_df = create_rfm_df(main_df)

# Membuat Main Content Dashboard
st.title('🛍️ Olist Store Analysis Dashboard')
st.markdown("Visualisasi dan analisis performa bisnis E-Commerce Olist.")

# Membuat layout Tab agar pas dalam satu halaman tanpa scroll berlebih
tab1, tab2 = st.tabs(["📊 Analisis Kategori Produk", "👥 RFM Analisis Pelanggan"])

with tab1:
    st.subheader("Kategori Produk Terbaik & Terburuk")
    top_5_categories = sum_order_items_df.head(5)
    bottom_5_categories = sum_order_items_df.tail(5)

    # Membuat 2 kanvas bersebelahan dengan ukuran kompak agar pas di layar
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    fig.patch.set_facecolor('#FFFFFF')

    colors = ["#1E88E5", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

    # Bar chart kategori produk teratas
    sns.barplot(x="order_id", y="product_category_name", data=top_5_categories, hue="product_category_name", palette=colors, legend=False, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("Best Performing Product Categories", loc="center", fontsize=12, fontweight='bold', pad=10)
    ax[0].tick_params(axis='y', labelsize=10)
    ax[0].tick_params(axis='x', labelsize=9)

    # Bar chart kategori produk terbawah
    sns.barplot(x="order_id", y="product_category_name", data=bottom_5_categories.sort_values(by="order_id", ascending=True), hue="product_category_name", palette=colors, legend=False, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    ax[1].set_title("Worst Performing Product Categories", loc="center", fontsize=12, fontweight='bold', pad=10)
    ax[1].tick_params(axis='y', labelsize=10)
    ax[1].tick_params(axis='x', labelsize=9)

    plt.tight_layout()
    st.pyplot(fig)

with tab2:
    st.subheader("Analisis Pelanggan Terbaik Berdasarkan Parameter RFM")
     
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_recency = round(rfm_df.recency.mean(), 1)
        st.metric("Average Recency (days)", value=avg_recency)
     
    with col2:
        avg_frequency = round(rfm_df.frequency.mean(), 2)
        st.metric("Average Frequency", value=avg_frequency)
     
    with col3:
        avg_monetary = format_currency(rfm_df.monetary.mean(), "R$", locale='es_CO') 
        st.metric("Average Monetary", value=avg_monetary)
     
    # Membuat 3 kanvas bersebelahan dengan ukuran kompak agar pas di layar
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(16, 5))
    fig.patch.set_facecolor('#FFFFFF')
    colors = ["#1E88E5", "#2196F3", "#42A5F5", "#64B5F6", "#90CAF9"]
     
    sns.barplot(y="recency", x="customer_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), hue="customer_id", palette=colors, legend=False, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("customer_id", fontsize=10)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=12, fontweight='bold', pad=10)
    ax[0].tick_params(axis='y', labelsize=9)
    ax[0].tick_params(axis='x', labelsize=10, rotation=45)
     
    sns.barplot(y="frequency", x="customer_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), hue="customer_id", palette=colors, legend=False, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("customer_id", fontsize=10)
    ax[1].set_title("By Frequency", loc="center", fontsize=12, fontweight='bold', pad=10)
    ax[1].tick_params(axis='y', labelsize=9)
    ax[1].tick_params(axis='x', labelsize=10, rotation=45)
     
    sns.barplot(y="monetary", x="customer_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), hue="customer_id", palette=colors, legend=False, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("customer_id", fontsize=10)
    ax[2].set_title("By Monetary", loc="center", fontsize=12, fontweight='bold', pad=10)
    ax[2].tick_params(axis='y', labelsize=9)
    ax[2].tick_params(axis='x', labelsize=10, rotation=45)
     
    plt.tight_layout()
    st.pyplot(fig)
