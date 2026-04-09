import streamlit as st
import os
from pathlib import Path

def show():
    st.title("Settings")
    
    # Run Analysis
    st.subheader("Run Analysis")
    with st.form("run_form"):
        st.write("Execute the full multi-agent pipeline (takes ~30s)")
        submitted = st.form_submit_button("Run Analysis", type="primary")
        
        if submitted:
            with st.spinner("Running war room agents..."):
                try:
                    # Import and run
                    from src.graph.workflow import run_war_room
                    from src.data.mock_data import generate_metrics, generate_feedback, generate_release_notes
                    
                    metrics = generate_metrics()
                    feedback = generate_feedback()
                    release_notes = generate_release_notes()
                    
                    result = run_war_room(metrics, feedback, release_notes, thread_id="ui_run")
                    
                    if result:
                        st.session_state.results = {
                            "final_decision": result,
                            "metrics": metrics,
                            "feedback": feedback,
                            "data_analysis": {"summary": "Completed"},
                            "pm_analysis": {"summary": "Completed"},
                            "marketing_analysis": {"summary": "Completed"},
                            "risk_analysis": {"summary": "Completed"},
                            "run_id": "ui_run",
                            "timestamp": "now"
                        }
                        st.session_state.data_loaded = True
                        st.success("Analysis complete! Go to Dashboard.")
                        st.balloons()
                    else:
                        st.error("No result generated")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Load existing
    if st.button("Load from tracer.json"):
        from utils.loader import load_from_tracer
        results = load_from_tracer("outputs/tracer.json")
        if results:
            st.session_state.results = results
            st.session_state.data_loaded = True
            st.success("Loaded successfully!")
        else:
            st.error("tracer.json not found")
    
    # API Keys
    st.subheader("Configuration")
    with st.form("config"):
        groq_key = st.text_input("GROQ_API_KEY", 
                                value=os.getenv("GROQ_API_KEY", ""), 
                                type="password")
        langsmith_key = st.text_input("LANGCHAIN_API_KEY", 
                                     value=os.getenv("LANGCHAIN_API_KEY", ""), 
                                     type="password")
        
        if st.form_submit_button("Save"):
            # Write to .env
            env_path = Path(".env")
            lines = []
            if env_path.exists():
                lines = env_path.read_text().splitlines()
            
            # Update or add keys
            new_lines = []
            found_groq = found_lang = False
            for line in lines:
                if line.startswith("GROQ_API_KEY="):
                    new_lines.append(f"GROQ_API_KEY={groq_key}")
                    found_groq = True
                elif line.startswith("LANGCHAIN_API_KEY="):
                    new_lines.append(f"LANGCHAIN_API_KEY={langsmith_key}")
                    found_lang = True
                else:
                    new_lines.append(line)
            
            if not found_groq:
                new_lines.append(f"GROQ_API_KEY={groq_key}")
            if not found_lang:
                new_lines.append(f"LANGCHAIN_API_KEY={langsmith_key}")
            
            env_path.write_text("\n".join(new_lines))
            st.success("Saved to .env")