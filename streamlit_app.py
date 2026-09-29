import streamlit as st
from app.agent import FlowAIAgent
from langchain_core.messages import ToolMessage
from app.agent import tools

# Page Config
st.set_page_config(
    page_title="FlowAI: Autonomous DevOps Assistant",
    page_icon="🤖",
    layout="wide",
)

# --- Sidebar: Detailed Context & Architecture ---
with st.sidebar:
  st.image(
      "https://img.icons8.com/color/96/artificial-intelligence.png", width=64
  )
  st.header("About FlowAI")
  st.markdown(
      "**FlowAI** is an autonomous, offline-first yet cloud-deployed DevOps and"
      " incident response assistant designed to triage system health and automate"
      " troubleshooting workflows."
  )

  st.divider()

  st.subheader("⚙️ How It Works")
  st.markdown("""
    1. **Hybrid LLM Backend:** Runs offline via **Ollama (`llama3.1`)** for local development, and scales seamlessly via **OpenAI Cloud API (`gpt-4o-mini`)** for public cloud deployment.
    2. **Autonomous Health Triage:** Automatically runs live diagnostic checks on infrastructure components (Databases, API Gateways, Worker Nodes).
    3. **RAG Runbook Retrieval:** Queries your local Markdown operational documentation via **Chroma vector storage** to pull relevant remediation steps.
    4. **Smart Synthesis:** Combines real-time telemetry with historical runbooks into a single, cohesive action plan.
    """)

  st.divider()
  st.subheader("🛠️ Active Tools")
  st.markdown(
      "- `check_system_health`: Live service telemetry & pool status.\n- "
      "`search_runbooks`: Vector search across local markdown runbooks."
  )


# --- Main Chat Interface ---
st.title("🤖 FlowAI: Autonomous Incident Assistant")
st.markdown(
    "Your intelligent DevOps copilot. Ask about failing services, timeouts, or"
    " system alerts below."
)

# Initialize agent in session state
if "agent" not in st.session_state:
  with st.spinner(
      "Initializing FlowAI engine and loading RAG vector store..."
  ):
    st.session_state.agent = FlowAIAgent()

# Initialize chat history
if "messages" not in st.session_state:
  st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
    st.markdown(message["content"])

# Chat input widget
if prompt := st.chat_input(
    "Ask FlowAI to check system health or look up runbooks..."
):
  # Append and display user message
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  # Generate and display assistant response
  with st.chat_message("assistant"):
    # Use st.status to show live progress of tool execution in the UI
    with st.status(
        "🤖 FlowAI analyzing telemetry and searching runbooks...", expanded=True
    ) as status:
      try:
        agent = st.session_state.agent
        messages = [
            (
                "system",
                (
                    "You are FlowAI, an autonomous DevOps and incident"
                    " assistant. You MUST use your available tools"
                    " (`check_system_health` and `search_runbooks`) to"
                    " investigate issues before providing a final response."
                    " Combine the health check results and runbook"
                    " instructions into a clear, actionable remediation"
                    " summary."
                ),
            ),
            ("human", prompt),
        ]

        st.write("🔍 Sending query to LLM model...")
        response = agent.llm.invoke(messages)

        if response.tool_calls:
          messages.append(response)
          for tool_call in response.tool_calls:
            tool_call_id = tool_call.get("id")
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            st.write(
                f"⚙️ **Executing tool:** `{tool_name}` with args:"
                f" `{tool_args}`"
            )

            selected_tool = tools.get(tool_name)
            if selected_tool:
              tool_result = selected_tool.invoke(tool_args)
              st.write(f"📋 **Tool Output received:**\n> {tool_result}")

              messages.append(
                  ToolMessage(
                      content=str(tool_result), tool_call_id=tool_call_id
                  )
              )

          st.write("💡 Synthesizing final remediation report...")
          final_response = agent.llm.invoke(messages)
          response_output = final_response.content
        else:
          response_output = response.content

        status.update(
            label="✅ FlowAI completed incident analysis!",
            state="complete",
            expanded=False,
        )

        st.markdown(response_output)
        st.session_state.messages.append(
            {"role": "assistant", "content": response_output}
        )

      except Exception as e:
        status.update(
            label="❌ Error during execution", state="error", expanded=True
        )
        error_msg = f"❌ Error during agent execution: {e}"
        st.error(error_msg)
        st.session_state.messages.append(
            {"role": "assistant", "content": error_msg}
        )