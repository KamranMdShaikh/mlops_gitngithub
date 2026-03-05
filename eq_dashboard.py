import streamlit as st
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import plotly.express as px
# from datetime import datetime
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

##### start form 50 min 

uploaded_file = st.file_uploader("Choose a file", type=["csv"])
if uploaded_file is not None:
    st.markdown ("File Uploaded Successfully")
    df=load_and_process_data(uploaded_file)
