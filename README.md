# FlowAI: Autonomous DevOps Incident Assistant & Cloud RAG Platform
Live Web App Link - **Interactive Web App Demo:** https://flow-ai-agent-rk.streamlit.app/

## 1. Overview

IT systems experience severe downtime and outages due to delayed incident triage and fragmented documentation. To tackle this engineering problem, I built flow-ai-agent autonomous DevOps assistant. It combines LLM tool orchestration with Retrieval-Augmented Generation (RAG) to run live diagnostic health checks, inspect system infrastructure bottlenecks, query operational runbooks and formulate structured remediation plans.

## 2. Why This Project

This project mirrors the core lifecycle of Machine Learning and Platform Operations:
- **RAG Architecture:** Parsing markdown operational runbooks, computing vector embeddings and indexing them locally using Chroma storage for precise semantic search.
- **LLM Function Calling and Agentic Loops:** Implementing robust state-management workflows handling native tool calls (`ToolMessage` and `tool_call_id` mapping) via LangChain.
- **Hybrid Infrastructure and Migration Journey:** 
  - *Initial Local Setup:* Originally developed as a fully offline-first agent leveraging local **Ollama (`llama3.1`)** hardware execution to prioritize absolute data privacy.
  - *Cloud Production Migration:* To make the application publicly available, the architecture was extended to dynamically support **OpenAI (`gpt-4o-mini`)** via environment fallback. This resolves the hardware limitations of cloud-hosted runners while maintaining high-speed, reliable tool-calling behavior.
- **Interactive Product Frontend:** Designing an information-rich Streamlit web application featuring real-time diagnostic progress blocks (`st.status`), chat history management and architectural sidebars.
- **Automation and DevOps:** Organising modular Python packages (`app/`), managing strict environment separation via `.env` / Streamlit Secrets and configuring cloud deployment pipelines.

## 3. Tech Stack

- **Languages and Core Frameworks:** Python | LangChain | Pydantic | Streamlit
- **LLM and Inference Ecosystem:** Local Ollama (`llama3.1`) | Cloud OpenAI API (`gpt-4o-mini`) | Nomic Embeddings
- **Vector Database and RAG:** ChromaDB | Markdown Runbook Pipeline
- **Cloud and Deployment:** Streamlit Community Cloud | Git | GitHub Version Control

## 4. Data Source

- **Runbook Documentation Data:** Proprietary simulated enterprise operational data stored under `data/runbooks/` covering database connection pool exhaustions, gateway timeouts (`502 Bad Gateway`) and worker node diagnostics.
- **Embeddings:** `nomic-embed-text` local embedding model mapping context blocks for vector similarity search.

## 5. Architecture & Pipeline

The system is built on a modular architecture separating data ingestion, tool registration, agent logic and UI rendering:
1. **User Query Input:** The user enters an alert or incident symptom via the Streamlit chat interface.
2. **Intent Parsing and Tool Matching:** The LLM evaluates the prompt and invokes native diagnostic functions (`check_system_health`) alongside semantic vector queries (`search_runbooks`).
3. **Telemetry and Retrieval Execution:** Live status values (e.g., database connection pool at 98%) are fetched concurrently with markdown snippet matches.
4. **Contextual Synthesis:** All tool outputs are wrapped into structured state messages and sent back to the model to generate a clean, prioritized, step-by-step technical remediation report.
