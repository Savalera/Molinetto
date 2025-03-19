from agents.chat import graph as app

for chunk in app.stream(
    {"messages": [("human", "pls create a json schema for a todo app")]},
    stream_mode="values",
):
    chunk["messages"][-1].pretty_print()
