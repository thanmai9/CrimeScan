import streamlit as st
import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from geopy.geocoders import Nominatim
import time
import pickle
import os
from datetime import datetime
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# =============================================
# ENHANCED UI CONFIGURATION
# =============================================
st.set_page_config(
    page_title="CrimeScan",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
   
)

# Custom CSS with professional crime analytics theme
st.markdown("""
    <style>
    :root {
        --primary: #0d47a1;  /* Dark blue */
        --secondary: #1565c0;  /* Police blue */
        --danger: #c62828;  /* Emergency red */
        --warning: #f57c00;  /* Amber */
        --success: #2e7d32;  /* Green */
    }
    
    .main {
        background-color: #f8f9fa;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .title {
        font-size: 36px !important;
        color: var(--primary) !important;
        font-weight: 800;
        margin-bottom: 0;
        padding: 10px 0;
    }
    
    .header-container {
        display: flex;
        align-items: center;
        padding: 15px 0;
        border-bottom: 2px solid var(--primary);
        margin-bottom: 20px;
    }
  
    
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid var(--secondary);
    }
    
    .metric-label {
        font-size: 14px;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: var(--primary);
        margin: 5px 0;
    }
    
    .stAlert {
        border-radius: 8px;
        padding: 15px;
    }
    
    .alert-high {
        background-color: #ffebee !important;
        border-left: 4px solid var(--danger) !important;
    }
    
    .alert-medium {
        background-color: #fff8e1 !important;
        border-left: 4px solid var(--warning) !important;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50, #34495e);
        color: white;
    }
    
    .sidebar .stSelectbox label, 
    .sidebar .stFileUploader label {
        color: white !important;
    }
    
    .map-container {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        border: 1px solid #e0e0e0;
    }
    
    .stDataFrame {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .tab-container {
        background: white;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# =============================================
# HEADER SECTION - SIMPLIFIED
# =============================================
st.markdown("""
    <style>
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background-color: #0a1f44;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        }
        .logo-group {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .logo-text {
            font-size: 24px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.5px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .tagline {
            font-size: 16px;
            color: #a7c6ff;
            font-style: italic;
            font-weight: 400;
            letter-spacing: 0.3px;
        }
        .logo-icon {
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); }
        }
    </style>
    
    <div class="header-container">
        <div class="logo-group">
            <svg class="logo-icon" xmlns="http://www.w3.org/2000/svg" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#4a90e2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                <circle cx="12" cy="9" r="3" fill="#4a90e2"></circle>
                <path d="M15 16.77c-.22.48-.51.92-.85 1.33-.36.44-.78.83-1.24 1.16-.47.33-1.01.6-1.57.8-1.13.4-2.41.48-3.62.24"></path>
            </svg>
            <span class="logo-text">CRIMESCAN</span>
        </div>
        <div class="tagline">Intelligent Crime Prediction & Prevention System</div>
    </div>
""", unsafe_allow_html=True)


# =============================================
# SIDEBAR - DATA CONFIGURATION
# =============================================
with st.sidebar:
    st.markdown("""
        <div style="text-align:center; margin-bottom:20px;">
            <h3 style="color:black; margin-bottom:5px;">CRIME DATA INPUT</h3>
            <div style="height:2px; background:linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent);"></div>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(" Upload Crime Data (CSV)", type=["csv"])
    
    if uploaded_file:
        try:
            # Try multiple encodings
            encodings = ['utf-8', 'latin1', 'utf-16', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding=encoding)
                    st.success(f"✔️ File loaded successfully with {encoding} encoding!")
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    st.error(f"Error with {encoding}: {str(e)}")
                    continue
            else:
                st.error("❌ Failed to read file. Please convert to UTF-8.")
                st.stop()
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")
            st.stop()
    else:
        st.info("ℹ️ Using sample dataset")
        df = pd.DataFrame({
            'Area_Name': ["Delhi Central", "Mumbai Downtown", "Chennai Port", 
                         "Kolkata Market", "Bangalore Tech Park", "Hyderabad Old City",
                         "Pune Nightlife", "Jaipur Tourist Zone"],
            'Year': [2023, 2023, 2023, 2023, 2023, 2023, 2023, 2023],
            'Group_Name': ["Armed Robbery", "Gang Violence", "Drug Trafficking", 
                         "Mass Theft", "Cyber Crime", "Communal Violence", "Drug Offenses", "Scams"],
            'Cases_Property_Stolen': [45, 38, 28, 22, 15, 44, 33, 27],
            'Latitude': [28.6139, 19.0760, 13.0827, 22.5726, 12.9716, 17.3616, 18.5204, 26.9124],
            'Longitude': [77.2090, 72.8777, 80.2707, 88.3639, 77.5946, 78.4747, 73.8567, 75.7873],
            'Severity': [5, 4, 4, 3, 2, 5, 3, 2]
        })

    st.markdown("###  Data Configuration")
    sample_cols = df.columns.tolist()
    
    # Auto-detect columns
    def find_col(possible_names):
        for name in possible_names:
            if name in sample_cols:
                return name
        return sample_cols[0]
    
    col_area = st.selectbox(" Location column", 
                          options=sample_cols,
                          index=sample_cols.index(find_col(['Area_Name', 'Location', 'District'])))
    
    col_cases = st.selectbox(" Cases count column", 
                           options=sample_cols,
                           index=sample_cols.index(find_col(['Cases_Property_Stolen', 'Cases', 'Count'])))
    
    # Check for severity column
    if 'Severity' not in df.columns:
        st.warning(" No severity column found - will calculate from cases")
        severity_col = None
    else:
        severity_col = 'Severity'

# =============================================
# DATA PROCESSING
# =============================================
try:
    # Handle cases
    df['cases'] = pd.to_numeric(df[col_cases], errors='coerce').fillna(0)
    
    # Calculate severity if not provided
    if severity_col is None:
        df['Severity'] = pd.cut(df['cases'],
                              bins=[0, 10, 20, 30, 40, float('inf')],
                              labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Check for coordinates
    if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
        st.warning(" No coordinates found. Using default coordinates for Indian cities.")
        city_coords = {
            'Delhi': (28.6139, 77.2090),
            'Mumbai': (19.0760, 72.8777),
            'Chennai': (13.0827, 80.2707),
            'Kolkata': (22.5726, 88.3639),
            'Bangalore': (12.9716, 77.5946),
            'Hyderabad': (17.3616, 78.4747),
            'Pune': (18.5204, 73.8567),
            'Jaipur': (26.9124, 75.7873)
        }
        df['Latitude'] = df[col_area].map(lambda x: city_coords.get(x.split()[0], (0, 0))[0])
        df['Longitude'] = df[col_area].map(lambda x: city_coords.get(x.split()[0], (0, 0))[1])
    
    # Clean data
    df = df.dropna(subset=['Latitude', 'Longitude'])
    df = df[df['cases'] > 0]  # Remove rows with 0 cases
    
except Exception as e:
    st.error(f"❌ Error processing data: {str(e)}")
    st.stop()

# =============================================
# DASHBOARD - METRICS SECTION
# =============================================
st.markdown("""<div style="margin-top:20px; margin-bottom:20px;"><h2 class="title"> Executive Summary</h2>
</div>""", unsafe_allow_html=True)
          
cols = st.columns(4)
with cols[0]:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Incidents</div>
            <div class="metric-value">{:,}</div>
            <div style="font-size:12px;color:#7f8c8d;">Across all locations</div>
        </div>
    """.format(int(df["cases"].sum())), unsafe_allow_html=True)
    
with cols[1]:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">High Risk Zones</div>
            <div class="metric-value">{}</div>
            <div style="font-size:12px;color:#7f8c8d;">Severity ≥ 4</div>
        </div>
    """.format(len(df[df['Severity'] >= 4])), unsafe_allow_html=True) 
    
with cols[2]:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Time Period</div>
            <div class="metric-value">{}</div>
            <div style="font-size:12px;color:#7f8c8d;">{}</div>
        </div>
    """.format(
        df['Year'].nunique(),
        f"{df['Year'].min()} - {df['Year'].max()}" if df['Year'].nunique() > 1 else str(df['Year'].min())
    ), unsafe_allow_html=True)
    
with cols[3]:
    st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Crime Types</div>
            <div class="metric-value">{}</div>
            <div style="font-size:12px;color:#7f8c8d;">Unique categories</div>
        </div>
    """.format(df["Group_Name"].nunique()), unsafe_allow_html=True)
    st.markdown("<div style='padding-top:30px;padding-bottom:30px;'></div>", unsafe_allow_html=True)

# =============================================
# HOTSPOT VISUALIZATION
# =============================================
st.markdown("""
    <div style='padding-top:40px; padding-bottom:40px;'>
        <h2> Crime Hotspot Analysis</h2>
    </div>
""", unsafe_allow_html=True)

def get_color(severity, cases):
    """Return color based on severity and case count"""
    if severity >= 4 or cases > 30:
        return '#c62828'  # Emergency red
    elif severity >= 3 or cases > 15:
        return '#ef6c00'  # Dark amber
    else:
        return '#388e3c'  # Dark green
# Create map with enhanced styling
map_center = [df['Latitude'].mean(), df['Longitude'].mean()]
m = folium.Map(
    location=map_center, 
    zoom_start=5,
    tiles='cartodbpositron',
    attr='CrimeScan'
)

# Add heatmap with custom gradient
HeatMap(
    data=df[['Latitude', 'Longitude', 'cases']].values,
    radius=25,
    blur=20,
    gradient={0.1: 'blue', 0.3: 'lime', 0.5: 'yellow', 1: 'red'}
).add_to(m)

# Add markers with color-coding and custom icons
marker_cluster = MarkerCluster(
    name="Crime Clusters",
    overlay=True,
    control=True,
    icon_create_function=None
).add_to(m)

for _, row in df.iterrows():
    color = get_color(row['Severity'], row['cases'])
    
    # Custom icon based on crime type
    icon_type = "exclamation-triangle" if row['Severity'] >= 4 else "exclamation-circle" if row['Severity'] >= 3 else "info-circle"
    
    folium.CircleMarker(
        location=[row['Latitude'], row['Longitude']],
        radius=8 + (row['cases'] / df['cases'].max() * 15),
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        popup=folium.Popup(f"""
            <div style="font-family: Arial; width: 250px;">
                <h4 style="color:{color}; margin-bottom:5px;">{row[col_area]}</h4>
                <div style="border-top:1px solid #eee; padding-top:5px;">
                    <p style="margin:2px 0;"><b>Type:</b> {row.get('Group_Name', 'N/A')}</p>
                    <p style="margin:2px 0;"><b>Cases:</b> {row['cases']}</p>
                    <p style="margin:2px 0;"><b>Severity:</b> 
                        <span style="color:{color}">{row['Severity']}/5</span>
                    </p>
                </div>
            </div>
        """, max_width=300),
        tooltip=f"{row[col_area]} - {row['cases']} cases"
    ).add_to(marker_cluster)

# Add layer control
folium.LayerControl().add_to(m)

# Display map in a styled container
with st.container():
    st.markdown("""
        <div class="map-container">
    """, unsafe_allow_html=True)
    st_folium(m, width=1200, height=600)
    st.markdown("</div>", unsafe_allow_html=True)

# =============================================
# ALERT SYSTEM
# =============================================
high_alert = df[df['Severity'] >= 4]
if not high_alert.empty:
    st.markdown("""
    <h2 style='margin-top:30px; margin-bottom:30px;'>  Critical Alerts</h2>""",unsafe_allow_html=True)
    
    alert_cols = st.columns(1)
    with alert_cols[0]:
        for _, row in high_alert.iterrows():
            st.markdown(f"""
                <div class="stAlert alert-high">
                    <div style="display:flex; align-items:center;">
                        <span style="font-size:24px; margin-right:15px;">⚠️</span>
                        <div>
                            <h3 style="margin:0 0 5px 0; color:#c62828;">{row[col_area]}</h3>
                            <p style="margin:2px 0;"><b>Crime Type:</b> {row.get('Group_Name', 'N/A')}</p>
                            <p style="margin:2px 0;"><b>Cases Reported:</b> {row['cases']}</p>
                            <p style="margin:2px 0;"><b>Severity Level:</b> {row['Severity']}/5 (High Risk)</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

# =============================================
# TIME SERIES ANALYSIS
# =============================================
st.markdown("""
    <h2 style='margin-top:40px; margin-bottom:40px;'> Crime Trend Forecast</h2>
""", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["Location Trends", "Crime Type Analysis"])

with tab1:
    selected_location = st.selectbox("Select location for analysis", df[col_area].unique())
    loc_data = df[df[col_area] == selected_location].groupby('Year')['cases'].sum()
    
    if len(loc_data) > 1:
        try:
            model = SARIMAX(loc_data, order=(1,1,1), seasonal_order=(1,1,1,7))
            results = model.fit(disp=False)
            forecast = results.get_forecast(steps=1)
            pred = forecast.predicted_mean
            
            fig, ax = plt.subplots(figsize=(10, 5))
            loc_data.plot(ax=ax, label='Historical Data', linewidth=2.5, color='#3498db')
            pred.plot(ax=ax, style='r--', label='1-Year Forecast', linewidth=2.5)
            
            # Highlight if predicted increase
            if pred.iloc[0] > loc_data.mean():
                ax.axvspan(loc_data.index[-1], pred.index[0], facecolor='#ffcccc', alpha=0.3)
                ax.annotate('Projected Increase', 
                           xy=(pred.index[0], pred.iloc[0]),
                           xytext=(10,10), textcoords='offset points',
                           bbox=dict(boxstyle='round,pad=0.5', fc='red', alpha=0.1),
                           arrowprops=dict(arrowstyle='->'))
            
            ax.set_title(f"Crime Trend in {selected_location}", pad=20, fontsize=14)
            ax.set_xlabel("Year", labelpad=10)
            ax.set_ylabel("Reported Cases", labelpad=10)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            st.pyplot(fig)
            
            # Display forecast metrics
            change_pct = ((pred.iloc[0] - loc_data.iloc[-1]) / loc_data.iloc[-1]) * 100
            alert_type = "danger" if change_pct > 0 else "success"
            
            st.markdown(f"""
                <div class="stAlert alert-{'high' if change_pct > 0 else 'medium'}">
                    <h4 style="margin-top:0;">Forecast for Next Period</h4>
                    <p><b>Expected Cases:</b> {int(pred.iloc[0])} ({change_pct:+.1f}% change)</p>
                    <p><b>Confidence Interval:</b> {forecast.conf_int().iloc[0,0]:.1f} to {forecast.conf_int().iloc[0,1]:.1f} cases</p>
                </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Error in time series analysis: {str(e)}")
    else:
        st.warning("Not enough data points for time series analysis")

with tab2:
    selected_crime = st.selectbox("Select crime type for analysis", df['Group_Name'].unique())
    crime_data = df[df['Group_Name'] == selected_crime].groupby('Year')['cases'].sum()
    
    if len(crime_data) > 1:
        fig, ax = plt.subplots(figsize=(10, 5))
        crime_data.plot(
            kind='bar', 
            ax=ax, 
            color=['#e74c3c' if val > crime_data.mean() else '#3498db' for val in crime_data]
        )
        ax.axhline(crime_data.mean(), color='#2c3e50', linestyle='--', label='Mean')
        ax.set_title(f"Trend for {selected_crime}", pad=20, fontsize=14)
        ax.set_xlabel("Year", labelpad=10)
        ax.set_ylabel("Reported Cases", labelpad=10)
        ax.legend(["Mean Cases", selected_crime])
        st.pyplot(fig)
    else:
        st.warning("Not enough data points for analysis")

# =============================================
# TOP LOCATIONS TABLE
# =============================================
st.markdown("""
    <h2 style='margin-top:30px; margin-bottom:30px;'> Top Crime Zones</h2>
""", unsafe_allow_html=True)
top_locations = df.sort_values(['Severity', 'cases'], ascending=False).head(10)

# Enhanced dataframe display
st.dataframe(
    top_locations[[col_area, 'Group_Name', 'cases', 'Severity']]
    .rename(columns={
        col_area: 'Location',
        'Group_Name': 'Crime Type',
        'cases': 'Cases',
        'Severity': 'Severity Level'
    })
    .style
    .background_gradient(subset=['Cases'], cmap='Reds')
    .applymap(lambda x: f"color: {'red' if x >=4 else 'orange' if x ==3 else 'green'}", subset=['Severity Level'])
    .format({'Cases': '{:,}'}),
    use_container_width=True,
    height=400
)

# =============================================
# FOOTER
# =============================================
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #7f8c8d; font-size: 14px; padding: 20px;">
        <p>CrimeScan | Advanced Crime Analytics Platform</p>
        <p>For official use only | Data is anonymized and encrypted</p>
    </div>
""", unsafe_allow_html=True)