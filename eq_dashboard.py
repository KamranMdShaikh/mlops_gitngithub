import streamlit as st
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import plotly.express as px
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")



## Page Configaration

st.set_page_config(
    page_title="Earthquake Decision Support",
    layout="wide",
    initial_sidebar_state="expanded"
)

### Titles

st.title("Earthquake Decision Support")
st.markdown ("**Real Time Monitoring System**")



########################
#### Upload file
########################


#### Basic

# uploaded_file = st.file_uploader("Choose a file", type=["csv"])
# if uploaded_file is None:
#     warnings.warn("Not uploaded")
# if uploaded_file is not None:
#     st.markdown ("File Uploaded")
    

#### Advanced
    
def load_and_process_data(uploaded_file):
    
    ## Step 01: Read CSV df
    df = pd.read_csv(uploaded_file)

    ## Step 02: Format Date Column & Drop if any 'Date' is missing
    df['time']=pd.to_datetime(df["time"], format="%Y-%m-%dT%H:%M:%S.%f", errors='coerce')
    df.dropna(subset=['time'])
    
    ## Step 03: Time feature (Saperate date, year, month, hour)
    df['date'] = df['time'].dt.date
    df['year'] = df['time'].dt.year
    df['month'] = df['time'].dt.month
    df['hour'] = df['time'].dt.hour
    df['week_of_date'] = df['time'].dt.day_name()
    

    ## Step 04: Using cut methode to saperate magnitude lavels 
    df['risk_level']=pd.cut(
        df['magnitude'],
        bins=[0,4,5.5,6.5,np.inf],
        labels=['Low', 'Medium', 'High', 'Extreme']        
    )
    
    df['tectonic_type'] = np.where(
        df['depth'] < 70,
        'Shallow-focus earthquakes (0–70 km)',
        np.where(
            (df['depth'] >= 70) & (df['depth'] < 300),
            'Intermediate-focus earthquakes (70–300 km)',
            'Deep-focus earthquakes (300–700 km)'
        )
    )
    
    
    ## Step 05: Sort value and cluster detection
    df=df.sort_values('time').reset_index(drop=True)
    df['hours_since_prev']=df['time'].diff().dt.total_seconds()/3600
    df['hours_since_prev']= df['hours_since_prev'].fillna(0)
    df['cluster_flag']=df['hours_since_prev']<24
    
    return df




uploaded_file = st.file_uploader("Choose a file", type=["csv"])
if uploaded_file is not None:
    st.markdown ("File Uploaded Successfully")
    with st.spinner('Wait for it...loading data..'):
        df=load_and_process_data(uploaded_file)
        
    
    
    ### Excecutive summary 
    
    st.markdown("-------")
    st.header("Excecutive Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
  
  
    total_events = len(df)
    critical_events = len(df[df['risk_level'] == 'Extreme'])
    low_risk_events = len(df[df['risk_level'] == 'Low'])
    medium_risk_events = len(df[df['risk_level'] == 'Medium'])
    high_risk_events = len(df[df['risk_level'] == 'High'])

    with col1:
        st.metric("Total Events", total_events)
    with col2:
        st.metric("Critical Events", critical_events)
    with col3:
        st.metric("Low Risk Events", low_risk_events)
    with col4:
        st.metric("Medium Risk Events", medium_risk_events)
    with col5:
        st.metric("High Risk Events", high_risk_events) 
    
    
    ## Alarts
    
    st.markdown("-------")
    st.header("Current Alerts")

    now = datetime.now()
    recent_events = df[df['time'] >= (now - timedelta(hours=24))]
    alert_df = recent_events[recent_events['magnitude'] >= 4.5].copy()
    alert_df['time_ago'] = (now - alert_df['time']).dt.total_seconds() / 3600

    if len(alert_df) > 0:
        st.error(f"High Risk Events in Last 24h: {len(alert_df)}")

        for _, row in alert_df.iterrows():
            st.warning(
                f"**M{row['magnitude']:.1f}** - {row['place'][:50]} | {row['time_ago']:.1f} hours ago"
            )

    else:
        st.success("No High Risk Events")
    
    
    
    
    
    ###### Sidebar
    
    st.markdown("-------")
    st.sidebar.header("Filters") 


    # Time
    time_window = st.sidebar.selectbox(
        "Time Window",
        ["All Time", "Last 7 Days", "Last 30 Days", "Last 90 Days",
        "Last 1 Year", "Last 3 Years", "Last 5 Years", "Last 10 Years", "Custom"]
    )

    if time_window == "Custom":
        start_date = st.sidebar.date_input("Start Date", df['date'].min())
        end_date = st.sidebar.date_input("End Date", df['date'].max())

        filter_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    else:
        days = {
            "All Time": 99999,
            "Last 7 Days": 7,
            "Last 30 Days": 30,
            "Last 90 Days": 90,
            "Last 1 Year": 365,
            "Last 3 Years": 365 * 3,
            "Last 5 Years": 365 * 5,
            "Last 10 Years": 365 * 10
        }

        cutoff = df['time'].max() - timedelta(days=days[time_window])
        filter_df = df[df['time'] >= cutoff]
       
    
    # assume, df 
    
    ### Sidebars Manitude & Depth
    
    mag_range = st.sidebar.slider("Magnitude Range", 
                                  float(df['magnitude'].min()), float(df['magnitude'].max()), 
                                  (float(df['magnitude'].min()), float(df['magnitude'].max())))
    
    depth_range = st.sidebar.slider("Depth Range", 
                                    float(df['depth'].min()), float(df['depth'].max()), 
                                    (float(df['depth'].min()), float(df['depth'].max())))


    
    
    ####
    