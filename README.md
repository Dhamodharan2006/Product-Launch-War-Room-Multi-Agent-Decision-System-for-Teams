# Product Launch War Room

A production-grade multi-agent system that simulates a cross-functional "war room" during product launches. The system analyzes real-time metrics and user feedback to generate structured go/no-go decisions using LangGraph orchestration and Groq LLM inference.

## Overview

This system implements a coordinated decision-making workflow among four specialized AI agents that analyze product launch data and produce structured recommendations: **Proceed**, **Pause**, or **Roll Back**. The architecture leverages LangGraph for stateful workflow management, LangChain for agent implementations, and LlamaIndex for RAG-based feedback analysis.

## Features

### Multi-Agent Architecture

**Four Specialized Agents with Distinct Responsibilities:**

1. **Data Analyst Agent**
   - Performs statistical analysis on 9 key metrics including activation rates, retention (D1/D7), crash rates, API latency (p95), payment success rates, support ticket volumes, feature adoption, and churn rates
   - Implements z-score anomaly detection with configurable thresholds
   - Calculates trend comparisons between pre-launch and post-launch periods
   - Triggers immediate rollback protocols when crash rates exceed 5%

2. **Product Manager Agent**
   - Defines success criteria and evaluates feature adoption benchmarks
   - Assesses user activation trends and strategic alignment
   - Frames go/no-go recommendations based on business impact
   - Evaluates success criteria met/not met with specific thresholds

3. **Marketing and Communications Agent**
   - Analyzes customer sentiment across 35+ feedback entries using NLP techniques
   - Clusters feedback by themes (crash reports, payment issues, UI/UX complaints)
   - Assesses communication urgency and brand impact
   - Generates internal and external messaging strategies
   - Implements RAG (Retrieval-Augmented Generation) pipeline using BAAI/bge-small-en-v1.5 embeddings for semantic feedback search

4. **Risk and Critic Agent**
   - Challenges assumptions and validates evidence across all analyses
   - Calculates composite risk scores using weighted algorithms (crash rate: 25%, sentiment: 20%, volatility: 30%, payment issues: 10%, anomalies: 15%)
   - Assesses rollback feasibility and impact
   - Identifies hidden risks and requests additional data when confidence is insufficient
   - Implements circuit-breaker logic for emergency interventions

### Orchestration and Workflow

**LangGraph State Machine:**
- Implements directed graph workflow with conditional routing
- State management using TypedDict with strict type hints
- Checkpoint persistence using MemorySaver for debugging and replay
- Conditional edges that trigger emergency protocols:
  - Crash rate > 5%: Immediate Rollback node (bypasses normal flow)
  - Risk score > 0.7: Emergency Pause node
  - Agent handoffs: Risk agent can dynamically request more data from Data Analyst

**Execution Flow:**
1. Load Data Node: Initializes vector store with feedback embeddings
2. Data Analyst Node: Metric analysis and anomaly detection
3. Conditional Router: Checks for critical thresholds
4. PM Analysis Node: Strategic assessment
5. Marketing Analysis Node: Sentiment and perception analysis
6. Risk Analysis Node: Comprehensive risk scoring and validation
7. Coordinator Node: Synthesizes all inputs into final decision
8. Action Plan Node: Generates structured output

### Analytical Tools (7 Implemented)

1. **metric_aggregation_tool**: Calculates mean, median, standard deviation, and z-score anomalies for time-series metrics
2. **anomaly_detection_tool**: Identifies threshold violations with configurable business rules (e.g., crash rate max 2%, payment success min 97%)
3. **trend_comparison_tool**: Compares pre-launch vs post-launch metrics with percentage change calculations
4. **sentiment_analysis_tool**: Performs sentiment scoring, keyword extraction, and segment breakdown (enterprise/pro/free)
5. **feedback_clustering_tool**: Groups feedback by issue type using keyword matching (crash, payment, UI, performance)
6. **risk_scoring_tool**: Calculates composite risk scores (0-1) with weighted factors and severity classifications
7. **rollback_impact_assessment_tool**: Evaluates rollback feasibility, estimated downtime, data loss risk, and alternative actions

### Data Generation

**Realistic Mock Data:**
- **Metrics**: 14-day time series with realistic patterns including launch-day dip (15% reduction), recovery curves, and injected anomalies
- **Feedback**: 35 entries with 60% positive/neutral, 30% negative, 10% outliers
- **Repeated Issues**: Three intentionally repeated issues (app crashes, payment failures, UI confusion) to test clustering
- **Release Notes**: Structured documentation with known risks and rollback procedures

### Observability and Monitoring

**LangSmith Integration:**
- Full execution tracing with 17.84s average latency
- Token usage tracking (1.1k tokens per run)
- Cost analysis (~$0.02 per execution)
- LLM call inspection with prompt/response logging
- State transition visualization
- Agent execution timeline with performance metrics

**Console Logging:**
- Rich-formatted console output with progress indicators
- Color-coded agent execution status
- Structured tables for risk registers and action plans
- Real-time decision confidence scoring

### Output Schema

**Structured JSON Output:**
- Decision: Proceed, Pause, or Roll Back
- Rationale: Key drivers, metric references, feedback summary
- Risk Register: Top risks with severity levels and mitigation strategies
- Action Plan: Next 24-48 hours with assigned owners and deadlines
- Communication Plan: Internal and external messaging guidance
- Confidence Score: 0-1 scale with factors that would increase confidence

## Project Structure
## Project Structure

<pre style="background-color: #f6f8fa; padding: 16px; border-radius: 6px; font-family: 'Courier New', Courier, monospace; font-size: 14px; line-height: 1.5; overflow-x: auto; color: #24292f;">
<code>product_launch_war_room/
├── pyproject.toml              # UV package manager configuration and dependencies
├── .env.example                # Environment variables template for API keys
├── .gitignore                  # Excludes .venv, outputs, checkpoints, and cache files
├── README.md                   # Project documentation and setup instructions
├── src/                        # Source code directory
│   ├── __init__.py             # Package initialization with version info
│   ├── main.py                 # Application entry point and CLI interface
│   ├── config.py               # LLM configuration and settings management
│   ├── agents/                 # Agent implementations
│   │   ├── __init__.py         # Agent module exports
│   │   ├── base.py             # Base agent class with LangChain integration
│   │   ├── data_analyst.py     # Data Analyst Agent with metric analysis tools
│   │   ├── product_manager.py  # Product Manager Agent for strategic decisions
│   │   ├── marketing.py        # Marketing Agent for sentiment analysis
│   │   └── risk_critic.py      # Risk Critic Agent for validation and scoring
│   ├── tools/                  # Analytical tools and utilities
│   │   ├── __init__.py         # Tools module exports
│   │   ├── metrics_tools.py    # Metric aggregation and anomaly detection
│   │   ├── sentiment_tools.py  # Sentiment analysis and feedback clustering
│   │   ├── risk_tools.py       # Risk scoring and rollback assessment
│   │   └── trend_tools.py      # Trend comparison and volatility analysis
│   ├── data/                   # Data generation and storage
│   │   ├── __init__.py         # Data module exports
│   │   ├── mock_data.py        # Generates realistic metrics, feedback, and release notes
│   │   └── vector_store.py     # LlamaIndex RAG implementation for feedback search
│   ├── graph/                  # LangGraph workflow orchestration
│   │   ├── __init__.py         # Graph module exports
│   │   ├── nodes.py            # Agent node implementations for workflow
│   │   ├── edges.py            # Conditional routing logic and decision trees
│   │   └── workflow.py         # Graph builder, compiler, and execution runner
│   └── models/                 # Pydantic schemas and type definitions
│       ├── __init__.py         # Models module exports
│       ├── schemas.py          # Output validation schemas (LaunchDecision, RiskItem, etc.)
│       └── state.py            # LangGraph state type definitions (WarRoomState)
└── outputs/                    # Generated artifacts directory
    ├── metrics.json            # Serialized time-series metrics
    ├── feedback.json           # User feedback with sentiment scores
    ├── release_notes.txt       # Release documentation
    └── final_decision.json     # Structured decision output
</code>
</pre>

## Installation

### Prerequisites
- Python 3.10 or higher
- UV package manager (`pip install uv`)
- Groq API key (obtain from [console.groq.com](https://console.groq.com))
- LangSmith API key (optional, for tracing)

### Setup

# Product Launch War Room

## Setup Instructions

### Clone Repository
```bash
git clone https://github.com/username/product-launch-war-room.git
cd product_launch_war_room
```

### Create Virtual Environment & Install Dependencies
```bash
uv venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### Configure Environment Variables
```bash
cp .env.example .env
```
Edit the `.env` file and add:
- GROQ_API_KEY
- LANGCHAIN_API_KEY (optional)

### Run the Application
```bash
python -m src.main
```

---

## Expected Output

The system executes a full multi-agent workflow and generates:

- Console output with agent execution trace and formatted decision
- JSON file at:
  outputs/final_decision.json
  containing structured decision data
- LangSmith trace URL for detailed execution analysis (if tracing is enabled)

---

## View Traces

Access detailed execution traces at:
https://smith.langchain.com

Note: Requires LANGCHAIN_API_KEY in .env

---

## Technical Architecture

### LLM Configuration

- Data Analyst
  - Model: llama-3.3-70b-versatile
  - Temperature: 0.1
  - Max Tokens: 2000

- Risk Critic
  - Model: llama-3.3-70b-versatile
  - Temperature: 0.2
  - Max Tokens: 2000

- Marketing
  - Model: llama-3.1-8b-instant
  - Temperature: 0.3
  - Max Tokens: 1500

- Product Manager
  - Model: llama-3.3-70b-versatile
  - Temperature: 0.1
  - Max Tokens: 3000

---

## State Management

- LangGraph
  - Stateful workflow orchestration with checkpoint persistence

- Pydantic
  - Strict output validation and type safety

- TypedDict
  - Defines state schema with annotated reducers for list appending

---

## External APIs

- Groq API
  - High-performance LLM inference (default endpoint)

- HuggingFace
  - Local embeddings for Retrieval-Augmented Generation
  - Model: BAAI/bge-small-en-v1.5

- LangSmith
  - Optional observability and execution tracing
