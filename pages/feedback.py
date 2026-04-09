import streamlit as st
from utils.loader import extract_feedback_df

def show():
    st.title("Feedback Analysis")
    
    if not st.session_state.data_loaded:
        st.info("Run analysis first")
        return
    
    results = st.session_state.results
    df = extract_feedback_df(results)
    
    if df.empty:
        st.error("No feedback data")
        return
    
    # Summary Metrics
    cols = st.columns(4)
    cols[0].metric("Total", len(df))
    cols[1].metric("Positive", len(df[df['category'] == 'positive']))
    cols[2].metric("Negative", len(df[df['category'] == 'negative']))
    cols[3].metric("Avg Sentiment", f"{df['sentiment_score'].mean():.2f}")
    
    # Filters
    st.subheader("Browse Feedback")
    col1, col2 = st.columns(2)
    category = col1.selectbox("Category", ["All"] + df['category'].unique().tolist())
    segment = col2.selectbox("Segment", ["All"] + df['user_segment'].unique().tolist())
    
    # Filter
    filtered = df
    if category != "All":
        filtered = filtered[filtered['category'] == category]
    if segment != "All":
        filtered = filtered[filtered['user_segment'] == segment]
    
    st.caption(f"Showing {len(filtered)} entries")
    
    # Display
    for _, row in filtered.iterrows():
        with st.expander(f"{row['text'][:60]}... ({row['category']})"):
            st.write(f"**Text:** {row['text']}")
            st.write(f"**Segment:** {row['user_segment']} | **Score:** {row['sentiment_score']}")
            st.write(f"**Source:** {row['source']} | **Time:** {row['timestamp']}")