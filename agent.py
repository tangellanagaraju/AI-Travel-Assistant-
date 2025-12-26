import os
import sys
import json
from typing import TypedDict, Annotated, Sequence, Union
import functools
import operator

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation

# Import our tools and schemas
import tool_implementations
from tool_schemas import TOOL_SCHEMAS

# --- Configuration ---
# Hardcoded key as per user request (Note: In production, use env vars)
OPENAI_API_KEY = "paste your_openai_api_key_here"
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- Tool Setup ---

# Map schemas to actual functions
tools_map = {
    "get_current_weather": tool_implementations.get_current_weather,
    "get_weather_forecast": tool_implementations.get_weather_forecast,
    "search_attractions": tool_implementations.search_attractions,
    "calculate_travel_distance": tool_implementations.calculate_travel_distance,
    "get_packing_suggestions": tool_implementations.get_packing_suggestions,
}

# Define a tool executor
tool_executor = ToolExecutor(tools_map.values()) # ToolExecutor usually takes a list of tools

# However, ToolExecutor expects LangChain "Tool" objects if we pass a list. 
# Since we have raw functions, we'll manually invoke them in the node.
# Let's simple create a dictionary lookup for execution.
def execute_tool_call(tool_name, tool_input):
    if tool_name not in tools_map:
        return f"Error: Tool {tool_name} not found."
    try:
        # tool_input is a dict
        func = tools_map[tool_name]
        return func(**tool_input)
    except Exception as e:
        return f"Error executing tool {tool_name}: {str(e)}"

# --- Agent State ---
#agent memory state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- Nodes ---

def agent_node(state: AgentState):
    """
    Invokes the model.
    """
    messages = list(state["messages"])
    
    # Ensure System Message is present for behavior instructions
    if not isinstance(messages[0], SystemMessage):
        system_msg = SystemMessage(content="You are a helpful travel assistant. You have access to tools specifically for weather, attractions, distance, and packing. Use them when needed. Always respond in a slightly excited, helpful tone. Formats your response in Markdown.")
        messages.insert(0, system_msg)
    
    # Initialize Model with Tools
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
    )
    # Bind tools using the JSON schemas we defined
    llm_with_tools = llm.bind_tools(TOOL_SCHEMAS)
    
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def tool_node(state: AgentState):
    """
    Executes tools requested by the model.
    """
    messages = state["messages"]
    last_message = messages[-1]
    

    #tool execution node
    # construct tool inputs
    tool_calls = last_message.tool_calls
    
    tool_messages = []
    
    for tool_call in tool_calls:
        function_name = tool_call["name"]
        arguments = tool_call["args"]
        
        # specific handling: if args is a string (rare but possible), parse it
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments) 
            except:
                pass

        print(f"  [Tool Call]: {function_name}({arguments})")
        
        result = execute_tool_call(function_name, arguments)
        
        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"],
                name=function_name
            )
        )
        
    return {"messages": tool_messages}

def should_continue(state: AgentState):
    """
    Determines if we should continue to tool node or end.
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return "continue"
    return "end"

# --- Graph Definition ---

workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

workflow.add_edge("tools", "agent")

app = workflow.compile()

# --- CLI Loop (Legacy/Testing) ---

def main():
    print("--------------------------------------------------")
    print("Smart Weather & Travel Assistant (CLI)")
    print("Type 'quit', 'exit', or 'q' to stop.")
    print("--------------------------------------------------")
    
    # Initial system message is vital for behavior
    conversation_history = [
        SystemMessage(content="You are a helpful travel assistant. You have access to tools specifically for weather, attractions, distance, and packing. Use them when needed. Always respond in a slightly excited, helpful tone.")
    ]
    
    while True:
        try:
            user_input = input("\nUser: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                break
            if not user_input:
                continue

            conversation_history.append(HumanMessage(content=user_input))
            
            inputs = {"messages": conversation_history}
            
            # Run the graph
            final_state = app.invoke(inputs)
            
            # Upgrade history
            conversation_history = final_state["messages"]
            
            # Print response
            last_msg = conversation_history[-1]
            if isinstance(last_msg, AIMessage):
                print(f"Assistant: {last_msg.content}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
