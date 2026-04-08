# Product Launch War Room

A production-grade multi-agent system that simulates a cross-functional "war room" during product launches. The system analyzes real-time metrics and user feedback to generate structured go/no-go decisions using LangGraph orchestration and Groq LLM inference.

## Overview

This system implements a coordinated decision-making workflow among four specialized AI agents that analyze product launch data and produce structured recommendations: **Proceed**, **Pause**, or **Roll Back**. The architecture leverages LangGraph for stateful workflow management, LangChain for agent implementations, and LlamaIndex for RAG-based feedback analysis.

---

## RAG (Retrieval-Augmented Generation) — Design Decision & Live Demonstration

> **Why RAG is here, what it does, and how to see it working.**

### What Problem RAG Solves

The Marketing/Comms Agent needs to answer targeted questions like:

- *"What are customers saying specifically about payment issues?"*
- *"What sentiment do enterprise-tier users express?"*
- *"Which feedback entries mention app crashes?"*

Without RAG, the only option is dumping **all 35 feedback entries** into every LLM prompt. That works at 35 entries — but at 3,500 entries it becomes expensive, slow, and hits context-window limits. RAG solves this by retrieving only the **most semantically relevant** entries for each query, keeping prompts focused and the system scalable.

### How It Works in This Project

```
35 user feedback entries (feedback.json)
            │
            ▼
BAAI/bge-small-en-v1.5  ← HuggingFace embedding model
(converts each entry into a 384-dim semantic vector)
            │
            ▼
LlamaIndex VectorStoreIndex
(stores all vectors in-memory)
            │
            ▼
Marketing Agent asks: "What do users say about payment failures?"
            │
            ▼
Semantic similarity search → Top-K most relevant entries retrieved
            │
            ▼
Only those K entries sent to LLM → Focused, accurate analysis
```

### Embedding Model Choice

| Property | Value |
|---|---|
| Model | `BAAI/bge-small-en-v1.5` |
| Dimensions | 384 |
| Size | ~130 MB (downloads once on first run) |
| Why chosen | Best-in-class small embedding model — outperforms OpenAI ada-002 on retrieval benchmarks at zero API cost |
| Framework | LlamaIndex `VectorStoreIndex` |

### Seeing RAG in Action — What to Watch in the Console

When you run `python -m src.main`, the Marketing Agent node prints a **RAG retrieval trace** showing exactly which feedback entries were retrieved and their similarity scores:

```
[RAG RETRIEVAL — Marketing Agent]
──────────────────────────────────────────────────────
Query  : "payment failures and transaction errors"
Top-3 semantically retrieved entries:
  1. [score: 0.921] "Payment failed 3 times in a row, had to use competitor app"
  2. [score: 0.887] "Checkout keeps timing out, lost my cart twice"
  3. [score: 0.743] "App crashes exactly at payment confirmation screen"
──────────────────────────────────────────────────────
→ These 3 entries (not all 35) are passed to the LLM for analysis.
```

This demonstrates that the system is doing **semantic search**, not keyword search. Notice entry 3 — it mentions "crashes" not "payment" — but it was retrieved because it is semantically related to the payment flow failure context.

### RAG vs. Keyword Search — The Key Difference

| | Keyword Search | RAG (this system) |
|---|---|---|
| Query: "payment problem" | Finds entries with the word "payment" | Finds entries about payment issues **even if they use different words** (e.g. "checkout failure", "transaction error") |
| Scalability | Degrades as entries grow | Stays fast regardless of dataset size |
| Context quality | Broad, noisy | Focused, relevant |
| Used in | Simple grep/filter | Production ML systems |

### Why This Architecture Scales

This same pattern is used in production systems like:
- Customer support ticket triage (retrieve similar past tickets)
- Legal document search (retrieve relevant case law)
- Product feedback analysis (retrieve thematically similar reviews)

The only change needed to scale this system from 35 → 35,000 feedback entries is swapping the in-memory `VectorStoreIndex` for a persistent vector database (Pinecone, Weaviate, ChromaDB) — the agent code stays identical.

### Files Involved

```
src/data/vector_store.py     ← Initializes LlamaIndex index + embeddings
src/agents/marketing.py      ← Marketing Agent queries the vector store
outputs/feedback.json        ← Source feedback data (35 entries)
```

---

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
   - Analyzes customer sentiment across 35+ feedback entries using RAG-powered semantic search
   - Clusters feedback by themes (crash reports, payment issues, UI/UX complaints)
   - Assesses communication urgency and brand impact
   - Generates internal and external messaging strategies
   - **Implements RAG pipeline using BAAI/bge-small-en-v1.5 embeddings** — see RAG section above

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
5. Marketing Analysis Node: Sentiment and perception analysis *(RAG active here)*
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
- **RAG retrieval trace** showing retrieved feedback entries and similarity scores per query

### Output Schema

**Structured JSON Output:**
- Decision: Proceed, Pause, or Roll Back
- Rationale: Key drivers, metric references, feedback summary
- Risk Register: Top risks with severity levels and mitigation strategies
- Action Plan: Next 24-48 hours with assigned owners and deadlines
- Communication Plan: Internal and external messaging guidance
- Confidence Score: 0-1 scale with factors that would increase confidence

---

## Project Structure

```
product_launch_war_room/
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
│   │   ├── marketing.py        # Marketing Agent — uses RAG for feedback search
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
│   │   └── vector_store.py     # LlamaIndex RAG — embedding + vector index (see RAG section)
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
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- UV package manager (`pip install uv`)
- Groq API key (obtain from [console.groq.com](https://console.groq.com))
- LangSmith API key (optional, for tracing)

> **Note on first run:** The RAG pipeline downloads the `BAAI/bge-small-en-v1.5` embedding model (~130 MB) from HuggingFace automatically. This happens once and is cached locally. Ensure internet connectivity on first run.

### Setup

#### Clone Repository
```bash
git clone https://github.com/username/product-launch-war-room.git
cd product_launch_war_room
```

#### Create Virtual Environment & Install Dependencies
```bash
uv venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Configure Environment Variables
```bash
cp .env.example .env
```

Edit the `.env` file and add:
```
GROQ_API_KEY=your_groq_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here   # optional
```

#### Run the Application
```bash
python -m src.main
```

---

## Expected Output

The system executes a full multi-agent workflow and generates:

1. **Console output** — agent execution trace with RAG retrieval logs, formatted decision summary
2. **`outputs/final_decision.json`** — complete structured decision in JSON
3. **LangSmith trace URL** — detailed execution graph (if `LANGCHAIN_API_KEY` is set)

### Sample console output (abbreviated)

```
[Load Data] Initializing vector store with 35 feedback entries...
[RAG] Embedding model loaded: BAAI/bge-small-en-v1.5
[RAG] VectorStoreIndex built — 35 documents indexed

[Data Analyst] Running metric aggregation...
[Data Analyst] Anomaly detected: crash_rate z-score = 2.8 (threshold: 2.0)
[Data Analyst] Trend: payment_success ↓ 4.2% post-launch

[RAG RETRIEVAL — Marketing Agent]
Query: "payment failures and transaction errors"
Top-3 retrieved: [score: 0.921] [score: 0.887] [score: 0.743]

[Risk Critic] Composite risk score: 0.68 (threshold: 0.70)
[Coordinator] Decision: PAUSE

Decision saved → outputs/final_decision.json
```

---

## View Traces

Access detailed execution traces at:
https://smith.langchain.com

Note: Requires `LANGCHAIN_API_KEY` in `.env`

---

## Technical Architecture

### LLM Configuration

| Agent | Model | Temperature | Max Tokens | Rationale |
|---|---|---|---|---|
| Data Analyst | llama-3.3-70b-versatile | 0.1 | 2000 | Low temp for deterministic metric analysis |
| Risk Critic | llama-3.3-70b-versatile | 0.2 | 2000 | Near-deterministic for risk scoring |
| Marketing | llama-3.1-8b-instant | 0.3 | 1500 | Smaller model sufficient; RAG pre-filters context |
| Product Manager | llama-3.3-70b-versatile | 0.1 | 3000 | Highest tokens for verbose strategic output |

> The Marketing Agent uses a smaller 8B model intentionally — because RAG pre-filters the most relevant feedback before the LLM sees it, a smaller model is sufficient and reduces inference cost.

### State Management

- **LangGraph** — Stateful workflow orchestration with checkpoint persistence
- **Pydantic** — Strict output validation and type safety
- **TypedDict** — Defines state schema with annotated reducers for list appending

### External APIs

| Service | Purpose | Required |
|---|---|---|
| Groq API | LLM inference for all 4 agents | Yes |
| HuggingFace | Local BAAI/bge-small-en-v1.5 embeddings for RAG | Auto-downloaded |
| LangSmith | Execution tracing and observability | Optional |
