import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Inventory HQ", layout="wide")
st.markdown("""<style>.stApp { background-color: #F7F7FB; } h1,h2,h3{color:#000;font-weight:700;}</style>""", unsafe_allow_html=True)
st.title("Inventory HQ")

# --- THIS IS NEW: Auto-load sample data ---
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

# Auto-load if empty
if st.session_state.stock.empty:
    try:
        st.session_state.stock, st.session_state.po = load_sample_data()
        st.toast("✅ Loaded sample data automatically")
    except:
        pass
# --- END NEW CODE ---


tab = st.sidebar.radio("Navigate", ["🏠 Dashboard", "📦 Inventory", "🚨 Alert Center", "📤 Upload"])

if tab == "📤 Upload":
    st.header("Upload Your Own Data")
    stock_file = st.file_uploader("Upload stock_counts.csv", type="csv")
    if stock_file: 
        df = pd.read_csv(stock_file)
        st.session_state.stock = process_stock_data(df)
        st.success(f"Loaded {len(st.session_state.stock)} Stock Items")

elif tab == "🏠 Dashboard":
    if st.session_state.stock.empty: 
        st.warning("Upload data first")
    else:
        df = st.session_state.stock
        top10_variance = df.sort_values('Variance', ascending=False).head(10)
        st.markdown("<h3>Top 10 Stock Count Variance</h3>", unsafe_allow_html=True)
        fig = px.bar(top10_variance, x='Product', y='Variance', color='Variance')
        fig.update_layout(xaxis_tickangle=-45, plot_bgcolor='white', paper_bgcolor='white', font=dict(color="#000"))
        fig.add_hline(y=0, line_dash="dash", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

elif tab == "📦 Inventory":
    if st.session_state.stock.empty: st.warning("Upload data first")
    else: st.dataframe(st.session_state.stock, use_container_width=True)

elif tab == "🚨 Alert Center":
    if st.session_state.stock.empty: st.warning("Upload data first")
    else:
        alerts = st.session_state.stock[st.session_state.stock['Variance'] > 0]
        st.dataframe(alerts, use_container_width=True)
