<<<<<<< HEAD
from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.tools import Tool
from pydantic import BaseModel, Field, ValidationError
=======
from collections import deque
from langchain.chat_models import ChatAnthropic
from langchain_community.chat_models import ChatAnthropic
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
>>>>>>> origin/master
from dotenv import load_dotenv
import os
import G_calendar_addEvent
import G_calendar_deleteEvent
import G_calendar_getEvent

load_dotenv()

<<<<<<< HEAD
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Setting up the ChatAnthropic LLM
llm = ChatAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), model_name='claude-3-sonnet-20240229', temperature=0)

calendar_assistant_template = """
You are a calendar assistant chatbot named "Schedulex". Your expertise is exclusively in providing information and advice about anything related to calendars, scheduling, and time management. This includes appointment setting, time zone conversions, scheduling best practices, and general calendar-related queries. You do not provide information outside of this scope. If a question is not about calendars or scheduling, respond with, "I specialise only in calendar and scheduling related queries." Question: {question} Answer:"""

calendar_assistant_prompt = PromptTemplate(
    input_variables=["question"],
    template=calendar_assistant_template
)

# Define input schemas for tools
class EventDetails(BaseModel):
    title: str = Field(description="Title of the event")
    date: str = Field(description="Date of the event")
    time: str = Field(description="Time of the event")

class EventId(BaseModel):
    event_id: str = Field(description="ID of the event to delete")

# Define tool callbacks leveraging G_calendar module
def add_event(args):
    try:
        validated_args = EventDetails(**args)
        return G_calendar_addEvent.addEvent(**validated_args.dict())
    except ValidationError as e:
        return str(e)

def get_events(args):
    return G_calendar_getEvent.getEvent()

def delete_event(args):
    try:
        validated_args = EventId(**args)
        return G_calendar_deleteEvent.deleteEvent(**validated_args.dict())
    except ValidationError as e:
        return str(e)

# Define Tools
tools = [
    Tool(name="AddEvent", func=add_event, description="Add an event to the calendar."),
    Tool(name="GetEvents", func=get_events, description="Fetch upcoming events from the calendar."),
    Tool(name="DeleteEvent", func=delete_event, description="Delete an event from the calendar."),
]

tool_names = [tool.name for tool in tools]

# Create a prompt for the agent
agent_prompt = PromptTemplate.from_template(
    """You are a helpful calendar assistant named Schedulex. Your expertise is exclusively in providing information and advice about calendars, scheduling, and time management. Use the available tools to help with calendar-related tasks.
    
    Current conversation:
    {chat_history}
    Human: {input}
    AI: Let's approach this step-by-step:
    Here is the current state: {agent_scratchpad}
    Available tools: {tools}
    Tool names: {tool_names}
    """
)

# Create an agent with the bound LLM and tools
agent = create_structured_chat_agent(
    llm=llm,
    tools=tools,
    prompt=agent_prompt,
)

# Create an AgentExecutor to run the agent with tools
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def process_user_input(user_input, chat_history, max_get_events, get_events_count):
    try:
        response = agent_executor.invoke({
            "input": user_input,
            "chat_history": list(chat_history)
        })
        print("AI:", response['output'])

        chat_history.append(f"Human: {user_input}")
        chat_history.append(f"AI: {response['output']}")

        # Check if GetEvents was called and increment counter
        if 'GetEvents' in response.get('output', ''):
            get_events_count += 1

        # Stop if GetEvents has been invoked too many times
        if get_events_count >= max_get_events:
            print("Reached maximum GetEvents invocations. Stopping.")
            return False, get_events_count

        return True, get_events_count
=======
class AddEventTool(BaseTool):
    name = "AddEvent"
    description = "Add an event to the calendar. Event details should be provided as a string in the format: 'title, YYYY-MM-DD, HH:MM'."

    def _run(self, event_details: str):
        result = G_calendar_addEvent.addEvent(event_details)
        return result
    
    def _arun(self, event_details: str):
        raise NotImplementedError("AddEventTool does not support asynchronous execution.")

class GetEventsTool(BaseTool):
    name = "GetEvents"
    description = "Retrieve the list of upcoming events from the calendar."

    def _run(self, query: str):
        events = G_calendar_getEvent.getEvent()
        if not events:
            return "No upcoming events found."
        else:
            event_list = "\n".join([f"{event['summary']} - {event['start']['dateTime']}" for event in events])
            return f"Upcoming events:\n{event_list}"
    
    def _arun(self, query: str):
        raise NotImplementedError("GetEventsTool does not support asynchronous execution.")

class DeleteEventTool(BaseTool):
    name = "DeleteEvent"
    description = "Delete an event from the calendar. Event details should be provided as a string in the format: 'title, YYYY-MM-DD, HH:MM'."

    def _run(self, event_details: str):
        return G_calendar_deleteEvent.deleteEvent(event_details)
    
    def _arun(self, event_details: str):
        raise NotImplementedError("DeleteEventTool does not support asynchronous execution.")

def setup_agent():
    api_key = os.environ.get("ANTHROPIC_API_KEY")  # Retrieve the API key from environment variables
    llm = ChatAnthropic(model="claude-instant-v1", temperature=0, max_tokens_to_sample=1024, anthropic_api_key=api_key)
    tools = [AddEventTool(), GetEventsTool(), DeleteEventTool()]
    agent = initialize_agent(tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
    return agent

def process_user_input(user_input, chat_history, agent):
    try:
        chat_history.append(f"Human: {user_input}")
        response = agent.run(input=user_input)
        chat_history.append(f"Assistant: {response}")
        print(f"Assistant: {response}")
        return True
>>>>>>> origin/master
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return True, get_events_count

def run():
<<<<<<< HEAD
    chat_history = []  # Limit chat history to last 4 exchanges
=======
    chat_history = deque(maxlen=10)  # Limit chat history to last 10 exchanges
    agent = setup_agent()
>>>>>>> origin/master

    # Add a counter to limit the number of GetEvents invocations
    get_events_count = 0
    max_get_events = 2  # Set a maximum number of invocations

    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print("Exiting the programme. Goodbye!")
            break

<<<<<<< HEAD
        continue_running, get_events_count = process_user_input(
            user_input, chat_history, max_get_events, get_events_count)

        if not continue_running:
            break
=======
        success = process_user_input(user_input, chat_history, agent)
        if not success:
            print("An error occurred. Please try again.")
>>>>>>> origin/master

if __name__ == '__main__':
    run()