from collections import deque
from langchain.chat_models import ChatAnthropic
from langchain_community.chat_models import ChatAnthropic
from langchain.agents import initialize_agent, AgentType
from langchain.tools import BaseTool
from dotenv import load_dotenv
import os
import G_calendar_addEvent
import G_calendar_deleteEvent
import G_calendar_getEvent

load_dotenv()

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
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False

def run():
    chat_history = deque(maxlen=10)  # Limit chat history to last 10 exchanges
    agent = setup_agent()

    print("Welcome to Schedulex, your calendar assistant!")
    print("You can ask me to add events, fetch upcoming events, or delete events from your calendar.")
    print("Type 'exit' to end the conversation.")

    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break

        success = process_user_input(user_input, chat_history, agent)
        if not success:
            print("An error occurred. Please try again.")

if __name__ == '__main__':
    run()