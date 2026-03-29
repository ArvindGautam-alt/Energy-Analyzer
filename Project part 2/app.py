import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import timedelta
import json
import os

st.set_page_config(page_title="Society Energy Analytics", layout="wide", page_icon="⚡")

# --- Custom CSS for Premium Design ---
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stApp { font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card {
        background-color: white; padding: 20px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center; transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateY(-5px); }
    .metric-value { font-size: 2rem; font-weight: bold; color: #2e66ff; }
    .metric-title { color: #6c757d; font-size: 1rem; text-transform: uppercase; letter-spacing: 1px; }
    .society-badge { background-color: #ffd700; color: #333; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

# --- Authentication Logic ---
USER_FILE = 'users.json'
HOUSES = ['House A', 'House B', 'House C', 'House D', 'House E']

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, 'w') as f:
            json.dump({'admin': {'password': 'admin123', 'role': 'admin', 'house_id': 'All'}}, f)
    with open(USER_FILE, 'r') as f:
        users = json.load(f)
        # Migrate old format if necessary
        for k, v in users.items():
            if isinstance(v, str):
                users[k] = {
                    'password': v,
                    'role': 'admin' if k == 'admin' else 'user',
                    'house_id': 'All' if k == 'admin' else HOUSES[0]
                }
        return users

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'username': '', 'role': 'user', 'house_id': ''})

def auth_page():
    st.title("🔐 Welcome to Society Energy Analytics")
    st.markdown("Please authenticate to access your household or society dashboard.")
    
    users = load_users()
    auth_mode = st.radio("Select an option:", ["Login", "Create Account", "Forgot Password"], horizontal=True)
    
    if auth_mode == "Login":
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Log In")
            
            if submit:
                if username in users and users[username]['password'] == password:
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['role'] = users[username]['role']
                    st.session_state['house_id'] = users[username]['house_id']
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
                    
    elif auth_mode == "Create Account":
        with st.form("signup_form"):
            st.subheader("Create New Household Account")
            new_user = st.text_input("Choose a Username")
            new_pass = st.text_input("Choose a Password", type="password")
            selected_house = st.selectbox("Select Your Household", HOUSES)
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if new_user in users:
                    st.error("Username already exists. Please choose another one.")
                elif len(new_user) < 3 or len(new_pass) < 3:
                    st.error("Username and password must be at least 3 characters long.")
                else:
                    users[new_user] = {'password': new_pass, 'role': 'user', 'house_id': selected_house}
                    save_users(users)
                    st.success("Account created successfully! Please switch to 'Login' to enter the app.")
                    
    elif auth_mode == "Forgot Password":
        with st.form("forgot_password_form"):
            st.subheader("Reset Password")
            reset_user = st.text_input("Enter your Username")
            new_pass = st.text_input("Enter New Password", type="password")
            submit = st.form_submit_button("Reset Password")
            
            if submit:
                if reset_user in users:
                    users[reset_user]['password'] = new_pass
                    save_users(users)
                    st.success("Password reset successfully! You can now log in.")
                else:
                    st.error("Username not found. Cannot reset password.")

def main_dashboard():
    # Sidebar
    st.sidebar.markdown(f"### ✨ Welcome, {st.session_state['username']}!")
    
    if st.session_state['role'] == 'admin':
        st.sidebar.markdown('<span class="society-badge">👑 Society Admin</span>', unsafe_allow_html=True)
        view_mode = st.sidebar.radio("Dashboard View", ["Society Aggregate"] + HOUSES)
        active_house = view_mode
    else:
        st.sidebar.markdown(f'<span class="society-badge">🏠 {st.session_state["house_id"]}</span>', unsafe_allow_html=True)
        active_house = st.session_state['house_id']
        
    st.sidebar.write("")
    if st.sidebar.button("Log Out"):
        st.session_state.update({'logged_in': False, 'username': '', 'role': 'user', 'house_id': ''})
        st.rerun()

    # Title
    st.title("⚡ Society Energy Analytics & Forecasting")
    if st.session_state['role'] == 'admin' and active_house == "Society Aggregate":
        st.markdown("*Viewing aggregated consumption across the entire society (All Houses).*")
    else:
        st.markdown(f"*Viewing detailed consumption data for **{active_house}**.*")
    st.markdown("---")
    
    # Data Loading
    @st.cache_data
    def load_data():
        try:
            energy_df = pd.read_csv('data/energy_data.csv', parse_dates=['timestamp'])
            weather_df = pd.read_csv('data/weather_data.csv', parse_dates=['timestamp'])
            
            # If house_id doesn't exist (old data), fake it for backward compatibility
            if 'house_id' not in energy_df.columns:
                energy_df['house_id'] = HOUSES[0]
                
            df = pd.merge(energy_df, weather_df, on='timestamp', how='inner')
            df.set_index('timestamp', inplace=True)
            df.ffill(inplace=True)
            df['hour'] = df.index.hour
            df['dayofweek'] = df.index.dayofweek
            df['month'] = df.index.month
            return df
        except FileNotFoundError:
            return None
    
    raw_df = load_data()
    if raw_df is None:
        st.error("Data files not found. Please run `python data_generator.py` first.")
        st.stop()
        
    # Filter Data based on Active View
    if active_house == "Society Aggregate":
        # Group by timestamp to sum energy, average temp
        df = raw_df.groupby('timestamp').agg({
            'energy_consumption_kwh': 'sum',
            'temperature_c': 'mean',
            'humidity_percent': 'mean',
            'hour': 'first',
            'dayofweek': 'first',
            'month': 'first'
        })
        # Note: Condition (Rain/Snow) is categorical, taking the mode or first
        df['condition'] = raw_df.groupby('timestamp')['condition'].first()
    else:
        df = raw_df[raw_df['house_id'] == active_house].copy()
    
    # --- Tabs ---
    tab1, tab2, tab3 = st.tabs(["📊 Overview & EDA", "🔍 Interactive Analysis", "🤖 Forecasting Model"])
    
    with tab1:
        st.header("Executive Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-title">{"Society Records" if active_house=="Society Aggregate" else "House Records"}</div><div class="metric-value">{len(df):,}</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Consumption</div><div class="metric-value">{df["energy_consumption_kwh"].mean():.1f} kWh</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Peak Usage</div><div class="metric-value">{df["energy_consumption_kwh"].max():.1f} kWh</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Avg Temp</div><div class="metric-value">{df["temperature_c"].mean():.1f} °C</div></div>', unsafe_allow_html=True)
            
        st.write("")
        
        if active_house == "Society Aggregate":
            st.subheader("Society Energy Distribution Map")
            house_sums = raw_df.groupby('house_id')['energy_consumption_kwh'].sum().reset_index()
            fig_pie = px.pie(house_sums, names='house_id', values='energy_consumption_kwh', hole=0.4,
                             title="Total Consumption Share by House", color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("7-Day Consumption Heatmap (Hour vs Day of Week)")
        pivot_df = df.pivot_table(values='energy_consumption_kwh', index='hour', columns='dayofweek', aggfunc='mean')
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        pivot_df.columns = days
        fig = px.imshow(pivot_df, labels=dict(x="Day of Week", y="Hour of Day", color="Avg kWh"), x=days, y=pivot_df.index, color_continuous_scale='Viridis', aspect="auto")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.header("Exploratory Data Analysis")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Temperature vs Energy Consumption")
            sample_df = df.sample(n=min(5000, len(df)), random_state=42)
            fig_scatter = px.scatter(sample_df, x='temperature_c', y='energy_consumption_kwh', color='condition', opacity=0.6,
                                     labels={'temperature_c': 'Temperature (°C)', 'energy_consumption_kwh': 'Energy (kWh)'},
                                     color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with col_b:
            st.subheader("Average Hourly Demand Profile")
            hourly_avg = df.groupby('hour')['energy_consumption_kwh'].mean().reset_index()
            fig_line = px.line(hourly_avg, x='hour', y='energy_consumption_kwh', markers=True, 
                               line_shape='spline', labels={'hour': 'Hour of Day (0-23)', 'energy_consumption_kwh': 'Avg Energy (kWh)'})
            fig_line.update_traces(line_color='#2e66ff', line_width=4)
            st.plotly_chart(fig_line, use_container_width=True)
            
        st.subheader("Time Series Explorer")
        # Find default start_date safely
        min_date = df.index.min().date() if not df.empty else datetime.now().date()
        start_date = st.date_input("Start Date", min_date)
        end_date = st.date_input("End Date", min_date + timedelta(days=14))
        
        mask = (df.index.date >= start_date) & (df.index.date <= end_date)
        filtered_df = df.loc[mask]
        
        if not filtered_df.empty:
            if active_house == "Society Aggregate":
                # Show all houses over time
                society_ts = raw_df[(raw_df['timestamp'].dt.date >= start_date) & (raw_df['timestamp'].dt.date <= end_date)]
                fig_ts = px.line(society_ts, x='timestamp', y='energy_consumption_kwh', color='house_id', title="Energy Consumption Comparison (All Houses)")
            else:
                fig_ts = px.line(filtered_df.reset_index(), x='timestamp', y='energy_consumption_kwh', title="Energy Consumption over Selected Period")
            fig_ts.update_xaxes(rangeslider_visible=True)
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.warning("No data found for the selected date range.")
    
    with tab3:
        st.header(f"AI Forecasting Engine ({active_house} Mode)")
        st.write("This section trains a Machine Learning model using Historical Weather and Time data to predict future energy demand.")
        
        @st.cache_resource(show_spinner="Training Model...")
        def train_model(data, scope_name):
            # scope_name ensures a unique model per house/society aggregate
            features = ['temperature_c', 'humidity_percent', 'hour', 'dayofweek', 'month']
            X = data[features]
            y = data['energy_consumption_kwh']
            model = RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42)
            model.fit(X, y)
            return model, features
    
        model, features_list = train_model(df, active_house)
        
        st.success(f"✅ Random Forest model trained successfully on historical data for {active_house}!")
        st.subheader("Forecast Simulator")
        st.write("Adjust the parameters below to see how the predicted energy consumption changes.")
        
        days_label = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        col_sim1, col_sim2, col_sim3 = st.columns(3)
        with col_sim1:
            sim_temp = st.slider("Temperature (°C)", min_value=-10.0, max_value=40.0, value=20.0, step=0.5)
            sim_hum = st.slider("Humidity (%)", min_value=10, max_value=100, value=50, step=1)
        with col_sim2:
            sim_hour = st.slider("Hour of Day", min_value=0, max_value=23, value=12, step=1)
            sim_dow = st.selectbox("Day of Week", options=[0,1,2,3,4,5,6], format_func=lambda x: days_label[x])
        with col_sim3:
            sim_month = st.selectbox("Month", options=list(range(1,13)))
            
        input_data = pd.DataFrame([[sim_temp, sim_hum, sim_hour, sim_dow, sim_month]], columns=features_list)
        prediction = model.predict(input_data)[0]
        
        st.markdown(f"### Predicted Demand ({active_house}):")
        st.markdown(f'<div style="text-align: center; font-size: 3rem; font-weight: bold; color: {"#ff4b4b" if active_house == "Society Aggregate" else "#2e66ff"}; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">{prediction:.2f} kWh</div>', unsafe_allow_html=True)

if not st.session_state['logged_in']:
    auth_page()
else:
    main_dashboard()
