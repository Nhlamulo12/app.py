import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Inventory Analyst", layout="wide", page_icon="📊")

# MONDAY.COM STYLE
st.markdown("""
<style>
    .stApp { background-color: #F7F7FB; }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-left: 4px solid #6750F3;
    }
    h1, h2, h3 { color: #000; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #000 !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #000 !important; font-size: 28px; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

st.title("Inventory Analyst")
st.caption("Data-Driven Supply Chain Dashboard")

# Session state
if 'stock' not in st.session_state: st.session_state.stock = pd.DataFrame()
if 'po' not in st.session_state: st.session_state.po = pd.DataFrame()

def process_stock_data(df):
    # AUTO CALCULATE VARIANCE
    df['Variance'] = df['Reorder_Level'] - df['Current_Stock']
    return df

tab = st.sidebar.radio("Navigate", ["🏠 Dashboard", "📦 Inventory", "🚨 Alert Center", "📤 Upload"])

# 1. UPLOAD
if tab == "📤 Upload":
    st.header("Upload Your Data")
    col1, col2 = st.columns(2)
    with col1:
        stock_file = st.file_uploader("Upload stock_counts.csv", type="csv")
        if stock_file: 
            df = pd.read_csv(stock_file)
            st.session_state.stock = process_stock_data(df)
            st.success(f"Loaded {len(st.session_state.stock)} Stock Items. Variance Calculated")
    with col2:
        po_file = st.file_uploader("Upload purchase_orders.csv", type="csv")
        if po_file: 
            st.session_state.po = pd.read_csv(po_file)
            st.success(f"Loaded {len(st.session_state.po)} Purchase Orders")

# 2. DASHBOARD
elif tab == "🏠 Dashboard":
    st.header("KPI Dashboard")
    if st.session_state.stock.empty:
        st.warning("Please upload data first")
    else:
        df = st.session_state.stock
        col1, col2, col3, col4 = st.columns(4)
        total_skus = len(df)
        low_stock = len(df[df['Variance'] > 0])
        avg_lead = st.session_state.po['Lead_Time_Days'].mean() if not st.session_state.po.empty else 0
        otif = (st.session_state.po['Status'] == 'On Time').mean() * 100 if not st.session_state.po.empty else 0
        
        with col1: 
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(label="Total SKUs", value=total_skus)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2: 
            st.markdown('<div class="metric-card" style="border-left-color:#FDAB3D;">', unsafe_allow_html=True)
            st.metric(label="Low Stock Alerts", value=low_stock)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3: 
            st.markdown('<div class="metric-card" style="border-left-color:#00C875;">', unsafe_allow_html=True)
            st.metric(label="Avg Lead Time", value=f"{avg_lead:.1f} days")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4: 
            st.markdown('<div class="metric-card" style="border-left-color:#E2445C;">', unsafe_allow_html=True)
            st.metric(label="OTIF %", value=f"{otif:.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # TOP 10 VARIANCE GRAPH ON DASHBOARD
        st.markdown("<h3>Top 10 Stock Count Variance</h3>", unsafe_allow_html=True)
        top10_variance = df.sort_values('Variance', ascending=False).head(10)
        
        fig_top10 = px.bar(top10_variance, 
                     x='Product', 
                     y='Variance',
                     title="Top 10 Items with Highest Variance",
                     color='Variance', 
                     color_continuous_scale=[[0, "#00C875"], [0.5, "#FDAB3D"], [1, "#E2445C"]])
        
        fig_top10.update_layout(
            xaxis_title="Product Name",
            yaxis_title="Variance = Reorder Level - Current Stock",
            xaxis_tickangle=-45,
            plot_bgcolor='white', paper_bgcolor='white',
            font=dict(size=14, color="#000000"),
            title_font=dict(size=18, color="#000")
        )
        fig_top10.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Reorder Line")
        fig_top10.update_traces(texttemplate='%{y}', textposition='outside')
        st.plotly_chart(fig_top10, use_container_width=True)

# 3. INVENTORY
elif tab == "📦 Inventory":
    st.header("Inventory Browser")
    if st.session_state.stock.empty:
        st.warning("Please upload data first")
    else:
        df = st.session_state.stock
        col1, col2 = st.columns([1,3])
        with col1:
            warehouse = st.selectbox("Filter by Warehouse", ["All"] + list(df['Warehouse'].unique()))
            category = st.selectbox("Filter by Category", ["All"] + list(df['Category'].unique()))
        
        df_view = df
        if warehouse != "All":
            df_view = df_view[df_view['Warehouse'] == warehouse]
        if category != "All":
            df_view = df_view[df_view['Category'] == category]
            
        st.markdown(f"<h3>Showing {len(df_view)} Items</h3>", unsafe_allow_html=True)
        st.dataframe(df_view, use_container_width=True, height=500)

# 4. ALERT CENTER
elif tab == "🚨 Alert Center":
    st.header("Alert Center")
    if st.session_state.stock.empty:
        st.warning("Please upload data first")
    else:
        df = st.session_state.stock
        
        # Only items below reorder
        alerts = df[df['Variance'] > 0].sort_values('Variance', ascending=False)
        
        st.markdown(f"<h3 style='color:#E2445C;'>🚨 {len(alerts)} Items Below Reorder Level</h3>", unsafe_allow_html=True)
        
        # TOP 10 ALERTS GRAPH
        top10_alerts = alerts.head(10)
        if len(top10_alerts) > 0:
            fig_alerts = px.bar(top10_alerts, 
                         x='Product', 
                         y='Variance',
                         title="Top 10 Critical Low Stock Items",
                         color='Variance', 
                         color_continuous_scale=[[0, "#FDAB3D"], [1, "#E2445C"]])
            
            fig_alerts.update_layout(
                xaxis_title="Product Name",
                yaxis_title="Units Below Reorder Level",
                xaxis_tickangle=-45,
                plot_bgcolor='white', paper_bgcolor='white',
                font=dict(size=14, color="#000000"),
                title_font=dict(size=18, color="#000")
            )
            fig_alerts.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig_alerts, use_container_width=True)
        
        st.markdown("<h3>Full Alert Details</h3>", unsafe_allow_html=True)
        st.dataframe(alerts[['Product','Category','Warehouse','Current_Stock','Reorder_Level','Variance']], use_container_width=True, height=300)
        
        # LATE PO
        if not st.session_state.po.empty:
            late = st.session_state.po[st.session_state.po['Status'] == 'Late']
            st.markdown(f"<h3 style='color:#FDAB3D;'>⚠️ {len(late)} Late Purchase Orders</h3>", unsafe_allow_html=True)
            st.dataframe(late, use_container_width=True)