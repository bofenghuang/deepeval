import os
import asyncio
from deepeval.integrations.langchain.callback import CallbackHandler
from deepeval.metrics import TaskCompletionMetric
import deepeval
from langgraph.prebuilt import create_react_agent
from deepeval.evaluate import dataset
from deepeval.dataset import Golden
from deepeval.evaluate.types import global_test_run_tasks as test_run

os.environ["OPENAI_API_KEY"] = "<YOUR_OPENAI_API_KEY>"
deepeval.login_with_confident_api_key("<YOUR_CONFIDENT_API_KEY>")

task_completion = TaskCompletionMetric(
    threshold=0.7,
    model="gpt-4o-mini",
    include_reason=True
)

def get_weather(city: str) -> str:
    """Returns the weather in a city"""
    return f"It's always sunny in {city}!"

agent = create_react_agent(
    model="openai:gpt-4o-mini",
    tools=[get_weather],
    prompt="You are a helpful assistant"
)

goldens = [
    Golden(input="What is the weather in Bogotá, Colombia?"),
    Golden(input="What is the weather in Paris, France?"),
]


for golden in dataset(goldens=goldens):
    task = asyncio.create_task(
        agent.ainvoke(
            input={"messages": [{"role": "user", "content": golden.input}]},
            config={"callbacks": [CallbackHandler(metrics=[task_completion], metric_collection="task_completion")]}
        )
    )
    test_run.append(task)