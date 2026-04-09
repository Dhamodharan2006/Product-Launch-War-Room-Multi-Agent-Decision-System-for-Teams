import streamlit as st
import json
import os
import plotly.graph_objects as go
from utils.loader import safe_get

def render():
    st.header("Execution Traces")
    
    results = st.session_state.results or {}
    
    st.subheader("Trace Metadata")
    cols = st.columns(3)
    cols[0].metric("Total Events", results.get("total_events", 0))
    cols[1].metric("Duration", f"{results.get('execution_duration_ms', 0) / 1000:.2f}s")
    cols[2].metric("Run ID", results.get("run_id", "Unknown")[:8])
    
    st.subheader("Risk Score Timeline")
    risk_scores = results.get("risk_scores", [])
    if risk_scores:
        fig = go.Figure()
        agents = ["Data Analyst", "PM", "Marketing", "Risk"]
        colors