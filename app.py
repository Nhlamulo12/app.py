import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="KPI Dashboard", layout="wide")

# --- CSS for KPI cards ---
st.markdown("""
<style>
    .stApp { background-color: #F5F6FA; }
    h1, h2, h3 { color: #2D3748; font-weight: 700; }
    .kpi-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-left: 5px solid;
    }
    .kpi-title { font-size: 14px; color: #718096; margin-bottom: 8px; }
    .kpi-value { font-size: 28px; font-weight: 800; color: #1A202C; }
</style>
""", unsafe_allow_html=True)

# --- Data functions ---
@st.cache_data
def load_sample_data():
    stock = pd.read_csv("stock_counts.csv")
    po = pd.read_csv("purchase_orders.csv")
    return process_stock_data(stock), po

def process_stock_data(df):
    df['Variance'] = df['Reorder_Level'] - df['Current_Stock']
    return df

if 'stock' not in st.session_state: st.session_state.stock = pd.DataFrame()
if 'po' not in st.session_state: st.session_state.po = pd.DataFrame()

if st.session_state.stock.empty:
    try:
        st.session_state.stock, st.session_state.po = load_sample_data()
    except:
        pass

# --- Sidebar ---
st.sidebar.title("Navigate")
tab = st.sidebar.radio("", ["🏠 Dashboard", "📦 Inventory", "🚨 Alert Center", "📤 Upload"])

# --- DASHBOARD TAB ---
if tab == "🏠 Dashboard":
    st.caption("Data-Driven Supply Chain Dashboard")
    st.title("KPI Dashboard")
    
    if not st.session_state.stock.empty:
        df = st.session_state.stock
        df_po = st.session_state.po
        
        # KPI Calculations
        total_skus = len(df)
        low_stock = len(df[df['Variance'] > 0])
        avg_lead = df_po['Lead_Time_Days'].mean() if not df_po.empty else 0
        otif = (len(df_po[df_po['Status'] == 'On Time']) / len(df_po) * 100) if not df_po.empty else 0
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="kpi-card" style="border-color:#805AD5;"><div class="kpi-title">Total SKUs</div><div class="kpi-value">{total_skus}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card" style="border-color:#ED8936;"><div class="kpi-title">Low Stock Alerts</div><div class="kpi-value">{low_stock}</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card" style="border-color:#38A169;"><div class="kpi-title">Avg Lead Time</div><div class="kpi-value">{avg_lead:.1f} days</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="kpi-card" style="border-color:#E53E3E;"><div class="kpi-title">OTIF %</div><div class="kpi-value">{otif:.1f}%</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Top 10 Variance Chart
        st.subheader("Top 10 Stock Count Variance")
        top10 = df.sort_values('Variance', ascending=False).head(10)
        
        fig = px.bar(
            top10, 
            x='Product', 
            y='Variance',
            color='Variance',
            color_continuous_scale=['#38A169', '#F6AD55', '#E53E3E'],
            text='Variance'
        )
        fig.update_layout(
            title="Top 10 Items with Highest Variance",
            xaxis_title="Variance = Reorder Level - Current Stock",
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(color="#2D3748"),
            xaxis_tickangle=-45,
            showlegend=False
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data loaded")

# --- OTHER TABS ---
elif tab == "📦 Inventory":
    st.title("Inventory")
    if not st.session_state.stock.empty: st.dataframe(st.session_state.stock, use_container_width=True)
    else: st.warning("Upload data first")

elif tab == "🚨 Alert Center":
    st.title("Alert Center")
    if not st.session_state.stock.empty:
        alerts = st.session_state.stock[st.session_state.stock['Variance'] > 0]
        st.dataframe(alerts, use_container_width=True)
    else: st.warning("Upload data first")

elif tab == "📤 Upload":
    st.title("Upload")
    stock_file = st.file_uploader("Upload stock_counts.csv", type="csv")
    po_file = st.file_uploader("Upload purchase_orders.csv", type="csv")
    if stock_file and po_file:
        st.session_state.stock = process_stock_data(pd.read_csv(stock_file))
        st.session_state.po = pd.read_csv(po_file)
        st.success("Data uploaded successfully")
