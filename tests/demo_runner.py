import sys
import os
import time

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import app
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def run_demo():
    scenarios = [
        {
            "name": "Scenario 1: Simple Query",
            "inputs": ["What is the current weather in Paris?"]
        },
        {
            "name": "Scenario 2: Multi-Step Planning",
            "inputs": [
                "I am planning a 3-day business trip to London next week.", 
                "Can you check the weather and suggest what I should pack?",
                "Also, are there any museums I can visit there in the evening?"
            ]
        },
        {
            "name": "Scenario 3: Error Handling / Edge Case",
            "inputs": ["Check the weather in Narnia, Middle Earth."]
        }
    ]

    transcript = []

    for scenario in scenarios:
        print(f"\n--- Running {scenario['name']} ---\n")
        transcript.append(f"# {scenario['name']}\n")
        
        # Reset state for each scenario (simulating fresh start)
        # Note: In LangGraph, passing a new list of messages effectively resets if we don't pass previous history.
        # But we need to maintain history WITHIN the scenario.
        chat_history = []
        
        for user_input in scenario["inputs"]:
            print(f"User: {user_input}")
            transcript.append(f"**User**: {user_input}\n")
            
            chat_history.append(HumanMessage(content=user_input))
            
            inputs = {"messages": chat_history}
            final_state = app.invoke(inputs)
            
            new_messages = final_state["messages"][len(chat_history):]
            
            # Update history with full state
            chat_history = final_state["messages"]
            
            # Print/Log output
            for msg in new_messages:
                if isinstance(msg, AIMessage):
                    if msg.tool_calls:
                         for tc in msg.tool_calls:
                             log = f"**Assistant (Tool Call)**: `{tc['name']}` args=`{tc['args']}`\n"
                             print(f"  [Tool Call]: {tc['name']} {tc['args']}")
                             transcript.append(log)
                    else:
                        print(f"Assistant: {msg.content}")
                        transcript.append(f"**Assistant**: {msg.content}\n")
                elif isinstance(msg, ToolMessage):
                    print(f"  [Tool Result]: {msg.content[:100]}...") # Truncate for display
                    transcript.append(f"**Tool Output**: `{msg.content}`\n")
            
            transcript.append("\n")
            time.sleep(1) # Be nice to API

    # Save transcript
    with open("demo_transcript.md", "w", encoding="utf-8") as f:
        f.write("\n".join(transcript))
    print("\nDemo transcript saved to demo_transcript.md")

if __name__ == "__main__":
    run_demo()
