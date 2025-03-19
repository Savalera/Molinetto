from langchain_core.messages import (
    SystemMessage,
)
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode

from tools import validate_json_schema

MODEL_NAME = "qwen2.5-coder:latest"

tools = [validate_json_schema]

llm = ChatOllama(model=MODEL_NAME).bind_tools(tools)

tool_node = ToolNode(tools)


def chat_node(state: MessagesState):
    """
    Solution architect chat node.
    """

    system_message = SystemMessage(
        content="""
        You are an expert JSON schema generator.

        **When the user asks for a schema creation:**
        - Generate a valid JSON schema using Draft202012 format.
        - **ALWAYS call the validate_json_schema tool** immediately after generating the schema.

        **When the user asks for an update to an existing schema:**
        - Modify the schema according to the user’s request.
        - **ALWAYS call the validate_json_schema tool again** after making changes.
        - Never assume an updated schema is valid without validation.

        When compiling the schema validation tool call:
        - ALWAYS validate the schema only, do not create example instance data for the 
        validation, just use the validate_json_schema tool with the created / updated schema 
        as the input.

        Always return the json schema in a code block in your final response, i.e. between
        ``` json
        ```
        blocks.

        In your final response, after successful schema validation, return the 
        generated shema to the user. Do not mention tools in your final response.
        Do not mention `you can validate data against this schema` in your final
        response. 

        In your final response add a short explanation of the
        schema besides returning the schema itself.

        Your main goal is to provide a valid and meaningful schema. 
        """
    )

    messages = [system_message] + state["messages"]

    response = llm.invoke(messages)

    return {"messages": [response]}


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END


workflow = StateGraph(MessagesState)
workflow.add_node("agent", chat_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")
workflow.add_edge("agent", END)
graph = workflow.compile()
