import os
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from app.rag import get_retriever
from dotenv import load_dotenv

load_dotenv()
retriever = get_retriever()


@tool
def search_runbooks(query: str) -> str:
  """Searches company operational runbooks and documentation for troubleshooting steps."""
  docs = retriever.invoke(query)
  if not docs:
    return "No relevant runbooks found."
  return "\n\n".join([doc.page_content for doc in docs])


@tool
def check_system_health(service_name: str) -> str:
  """Simulates checking live health status, CPU usage, and connection pool."""
  mock_statuses = {
      "database": (
          "WARNING: Database connection pool at 98% capacity. Active queries"
          " timing out."
      ),
      "api-gateway": (
          "CRITICAL: Upstream service returning HTTP 502 Bad Gateway."
      ),
      "worker-node": "OK: CPU usage at 45%, memory normal.",
  }
  return mock_statuses.get(
      service_name.lower(),
      f"Service '{service_name}' status: Unknown or unreachable.",
  )


tools = {
    "search_runbooks": search_runbooks,
    "check_system_health": check_system_health,
}


class FlowAIAgent:

  def __init__(self):
    # Automatically switch between OpenAI Cloud API and Local Ollama
    if os.getenv("OPENAI_API_KEY"):
      self.llm = ChatOpenAI(
          model="gpt-4o-mini", temperature=0
      ).bind_tools(list(tools.values()))
    else:
      self.llm = ChatOllama(model="llama3.1", temperature=0).bind_tools(
          list(tools.values())
      )

  def invoke(self, query: str):
    messages = [
        (
            "system",
            (
                "You are FlowAI, an autonomous DevOps and incident assistant."
                " You MUST use your available tools (`check_system_health` and"
                " `search_runbooks`) to investigate issues before providing a"
                " final response. Combine health check results and runbook"
                " instructions into a clear, actionable remediation summary."
            ),
        ),
        ("human", query),
    ]

    response = self.llm.invoke(messages)

    if response.tool_calls:
      messages.append(response)
      for tool_call in response.tool_calls:
        tool_call_id = tool_call.get("id")
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        selected_tool = tools.get(tool_name)
        if selected_tool:
          tool_result = selected_tool.invoke(tool_args)
          messages.append(
              ToolMessage(content=str(tool_result), tool_call_id=tool_call_id)
          )

      final_response = self.llm.invoke(messages)
      return final_response.content

    return response.content