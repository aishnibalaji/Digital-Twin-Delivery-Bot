import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import time
import random
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Digital Twin Delivery Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.metric-container {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    margin: 0.5rem 0;
}
.status-success {
    color: #28a745;
    font-weight: bold;
}
.status-warning {
    color: #ffc107;
    font-weight: bold;
}
.status-error {
    color: #dc3545;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Title and header
st.title("🤖 Digital Twin Delivery Bot Dashboard")
st.markdown("Real-time monitoring of warehouse delivery operations")

# Sidebar for controls
st.sidebar.header("🎛️ Control Panel")
simulation_running = st.sidebar.toggle("Simulation Running", True)
auto_refresh = st.sidebar.toggle("Auto Refresh", True)
refresh_rate = st.sidebar.slider("Refresh Rate (seconds)", 1, 10, 3)

# Mock data generation (in real implementation, this would come from your robot)
def generate_mock_data():
    # Simulate robot position over time
    t = time.time() % 100
    
    # Simulate movement between pickup and dropoff zones
    if t < 30:
        # Moving to pickup zone
        progress = t / 30
        x = progress * 1.0
        z = progress * 1.0
        status = "SEEKING_PICKUP"
    elif t < 35:
        # At pickup zone
        x = 1.0 + random.uniform(-0.1, 0.1)
        z = 1.0 + random.uniform(-0.1, 0.1)
        status = "PICKING_UP"
    elif t < 70:
        # Moving to dropoff zone
        progress = (t - 35) / 35
        x = 1.0 - progress * 2.0
        z = 1.0 - progress * 2.0
        status = "HAS_PACKAGE"
    elif t < 75:
        # At dropoff zone
        x = -1.0 + random.uniform(-0.1, 0.1)
        z = -1.0 + random.uniform(-0.1, 0.1)
        status = "DROPPING_OFF"
    else:
        # Mission complete
        x = -1.0
        z = -1.0
        status = "DELIVERED"
    
    return {
        "position": {"x": x, "y": 0, "z": z},
        "status": status,
        "battery": max(20, 100 - (t * 0.8)),
        "speed": random.uniform(0.5, 3.0) if status in ["SEEKING_PICKUP", "HAS_PACKAGE"] else 0,
        "obstacles_detected": random.randint(0, 3),
        "distance_traveled": t * 0.05,
        "mission_time": timedelta(seconds=int(t))
    }

# Main dashboard layout
if simulation_running:
    # Generate current robot data
    robot_data = generate_mock_data()
    
    # Create three columns for main metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="🤖 Robot Status",
            value=robot_data["status"].replace("_", " ").title(),
            delta="Active" if robot_data["status"] != "DELIVERED" else "Complete"
        )
        
        st.metric(
            label="🔋 Battery Level",
            value=f"{robot_data['battery']:.1f}%",
            delta=f"{-0.8:.1f}%/min" if robot_data['battery'] > 20 else None
        )
    
    with col2:
        st.metric(
            label="⚡ Current Speed",
            value=f"{robot_data['speed']:.2f} m/s",
            delta=None
        )
        
        st.metric(
            label="📍 Distance Traveled",
            value=f"{robot_data['distance_traveled']:.2f} m",
            delta=f"+{0.05:.2f} m/s"
        )
    
    with col3:
        st.metric(
            label="⚠️ Obstacles Detected",
            value=robot_data["obstacles_detected"],
            delta=f"Last scan" if robot_data["obstacles_detected"] > 0 else "Clear path"
        )
        
        st.metric(
            label="⏱️ Mission Time",
            value=str(robot_data["mission_time"]).split('.')[0],
            delta="In progress" if robot_data["status"] != "DELIVERED" else "Complete"
        )
    
    # Create warehouse map
    st.subheader("🗺️ Warehouse Map")
    
    # Create plotly figure for warehouse layout
    fig = go.Figure()
    
    # Add warehouse boundaries
    fig.add_shape(
        type="rect",
        x0=-2, y0=-2, x1=2, y1=2,
        line=dict(color="black", width=2),
        fillcolor="lightgray",
        opacity=0.1
    )
    
    # Add pickup zone
    fig.add_shape(
        type="rect",
        x0=0.5, y0=0.5, x1=1.5, y1=1.5,
        line=dict(color="green", width=2),
        fillcolor="lightgreen",
        opacity=0.3
    )
    
    # Add dropoff zone
    fig.add_shape(
        type="rect",
        x0=-1.5, y0=-1.5, x1=-0.5, y1=-0.5,
        line=dict(color="red", width=2),
        fillcolor="lightcoral",
        opacity=0.3
    )
    
    # Add robot position
    fig.add_trace(go.Scatter(
        x=[robot_data["position"]["x"]],
        y=[robot_data["position"]["z"]],
        mode='markers+text',
        marker=dict(size=15, color='blue'),
        text=['🤖'],
        textposition="middle center",
        name="Robot"
    ))
    
    # Add some obstacles
    obstacles_x = [0.8, -0.3, 0.2, -1.0]
    obstacles_y = [-0.5, 0.8, 1.3, 0.3]
    fig.add_trace(go.Scatter(
        x=obstacles_x,
        y=obstacles_y,
        mode='markers+text',
        marker=dict(size=10, color='brown'),
        text=['📦'] * len(obstacles_x),
        textposition="middle center",
        name="Obstacles"
    ))
    
    fig.update_layout(
        width=600,
        height=500,
        xaxis=dict(range=[-2.5, 2.5], title="X Position (m)"),
        yaxis=dict(range=[-2.5, 2.5], title="Z Position (m)"),
        title="Robot Position in Warehouse",
        showlegend=True
    )
    
    # Add zone labels
    fig.add_annotation(x=1, y=1, text="Pickup Zone", showarrow=False, font=dict(color="green"))
    fig.add_annotation(x=-1, y=-1, text="Dropoff Zone", showarrow=False, font=dict(color="red"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Battery History")
        # Generate mock battery history
        time_points = list(range(0, 101, 5))
        battery_levels = [100 - (t * 0.8) for t in time_points]
        
        battery_fig = go.Figure()
        battery_fig.add_trace(go.Scatter(
            x=time_points,
            y=battery_levels,
            mode='lines+markers',
            name='Battery Level',
            line=dict(color='green')
        ))
        battery_fig.update_layout(
            xaxis_title="Time (seconds)",
            yaxis_title="Battery Level (%)",
            height=300
        )
        st.plotly_chart(battery_fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Mission Progress")
        # Calculate mission progress
        progress_mapping = {
            "SEEKING_PICKUP": 25,
            "PICKING_UP": 40,
            "HAS_PACKAGE": 75,
            "DROPPING_OFF": 90,
            "DELIVERED": 100
        }
        progress = progress_mapping.get(robot_data["status"], 0)
        
        progress_fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = progress,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Mission Progress (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "green"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        progress_fig.update_layout(height=300)
        st.plotly_chart(progress_fig, use_container_width=True)
    
    # System logs
    st.subheader("📋 System Logs")
    log_container = st.container()
    
    with log_container:
        current_time = datetime.now().strftime("%H:%M:%S")
        
        if robot_data["status"] == "SEEKING_PICKUP":
            st.text(f"[{current_time}] 🤖 Robot navigating to pickup zone...")
        elif robot_data["status"] == "PICKING_UP":
            st.text(f"[{current_time}] 📦 Robot picking up package...")
        elif robot_data["status"] == "HAS_PACKAGE":
            st.text(f"[{current_time}] 🚚 Robot transporting package to dropoff zone...")
        elif robot_data["status"] == "DROPPING_OFF":
            st.text(f"[{current_time}] 📤 Robot dropping off package...")
        elif robot_data["status"] == "DELIVERED":
            st.text(f"[{current_time}] ✅ Mission completed successfully!")
        
        if robot_data["obstacles_detected"] > 0:
            st.text(f"[{current_time}] ⚠️ {robot_data['obstacles_detected']} obstacles detected - avoiding...")
        
        if robot_data["battery"] < 30:
            st.text(f"[{current_time}] 🔋 Low battery warning - {robot_data['battery']:.1f}% remaining")

else:
    st.info("🔴 Simulation stopped. Toggle 'Simulation Running' to start monitoring.")

# Auto-refresh functionality
if auto_refresh and simulation_running:
    time.sleep(refresh_rate)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("🤖 Digital Twin Delivery Bot Dashboard | Built with Streamlit & Webots")