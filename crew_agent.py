""" 
This is a module for testing out crewai agents in isolaiton. Their job is to read events from posthog and determine upsell opportunities.

Lets model a flow for crewai based on the following:
1. Read events from posthog
2. Determine if there is an upsell opportunity
3. If there is an upsell opportunity, create a task in a file called tasks.txt

"""
import json
import requests
from crewai import Crew, Process, Agent, Task
from crewai.tools import BaseTool
from crewai.memory import ShortTermMemory

class PostHogTool(BaseTool):
    """Tool to interact with PostHog API and read events from files"""

    def __init__(self, api_key: str = None, project_id: str = None):
        super().__init__(
            name="posthog_tool",
            description="Tool to fetch events from PostHog API or read events from a file"
        )
        self._api_key = api_key
        self._project_id = project_id
        if project_id:
            self._base_url = f"https://app.posthog.com/api/projects/{self._project_id}/events/"

    def _run(self, limit: int = 100, source: str = "api", file_path: str = None) -> str:
        """Execute the tool to fetch events from PostHog API or read from file
        
        Args:
            limit: Number of events to fetch (only used for API)
            source: Either "api" or "file" to specify data source
            file_path: Path to JSON file containing events (required if source="file")
        """
        if source == "file":
            return self._read_events_from_file(file_path)
        elif source == "api":
            return self._fetch_events_from_api(limit)
        else:
            return f"Error: Invalid source '{source}'. Must be 'api' or 'file'"

    def _fetch_events_from_api(self, limit: int) -> str:
        """Fetch events from PostHog API"""
        if not self._api_key or not self._project_id:
            return "Error: API key and project ID required for API access"
        
        try:
            headers = {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json"
            }
            params = {
                "limit": limit
            }
            response = requests.get(self._base_url, headers=headers, params=params)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch events from PostHog: {response.text}")
            
            events = response.json().get("results", [])
            return json.dumps(events, indent=2)
        except (requests.RequestException, json.JSONDecodeError, KeyError) as e:
            return f"Error fetching events from API: {str(e)}"

    def _read_events_from_file(self, file_path: str) -> str:
        """Read events from a JSON file"""
        if not file_path:
            return "Error: File path required when reading from file"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                events = json.load(f)
            
            # Handle different file formats
            if isinstance(events, list):
                # Direct array of events
                events_data = events
            elif isinstance(events, dict) and 'results' in events:
                # PostHog API response format
                events_data = events['results']
            elif isinstance(events, dict) and 'events' in events:
                # Custom format with events key
                events_data = events['events']
            else:
                return f"Error: Unsupported file format. Expected array of events or object with 'results'/'events' key"
            
            return json.dumps(events_data, indent=2)
        except FileNotFoundError:
            return f"Error: File '{file_path}' not found"
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON in file '{file_path}': {str(e)}"
        except Exception as e:
            return f"Error reading file '{file_path}': {str(e)}"

def write_tasks_to_file(tasks_output: str, filename: str = "tasks.txt"):
    """Write the tasks output to a file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(tasks_output)
        print(f"Tasks written to {filename}")
    except Exception as e:
        print(f"Error writing tasks to file: {str(e)}")
    
def create_upsell_agent(posthog_tool: PostHogTool) -> Agent:
    """Create an agent for analyzing upsell opportunities"""
    
    return Agent(
        role="Upsell Opportunity Analyst",
        goal="Analyze PostHog events to identify potential upsell opportunities",
        backstory="""You are an expert data analyst specializing in identifying upsell opportunities 
        from user behavior data. You analyze user events to find patterns that suggest 
        customers might be interested in upgrading or purchasing additional products.""",
        tools=[posthog_tool],
        memory=ShortTermMemory(),
        verbose=True,
        allow_delegation=False
    )

def create_upsell_task(agent: Agent, events_file: str = None) -> Task:
    """Create a task for analyzing upsell opportunities"""
    
    if events_file:
        task_description = f"""Analyze PostHog events from file '{events_file}' to identify upsell opportunities. 
        Look for patterns such as:
        - Users viewing high-value products
        - Users frequently using premium features
        - Users reaching usage limits
        - Users showing engagement with multiple product categories
        
        For each opportunity found, create a detailed task entry in tasks.txt with:
        - User ID
        - Opportunity type
        - Reasoning
        - Recommended action
        
        Use the posthog_tool with source="file" and file_path="{events_file}" to read the events."""
    else:
        task_description = """Analyze PostHog events to identify upsell opportunities. 
        Look for patterns such as:
        - Users viewing high-value products
        - Users frequently using premium features
        - Users reaching usage limits
        - Users showing engagement with multiple product categories
        
        For each opportunity found, create a detailed task entry in tasks.txt with:
        - User ID
        - Opportunity type
        - Reasoning
        - Recommended action
        
        Use the posthog_tool with source="api" to fetch events from PostHog API."""
    
    return Task(
        description=task_description,
        agent=agent,
        expected_output="A list of identified upsell opportunities written to tasks.txt file",
        tools=[agent.tools[0]]
    )

def main():
    """Main function to run the upsell analysis crew"""
    
    # Load configuration
    config = {}
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("WARNING: config.json file not found. Will use file-based analysis if events file is provided.")
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON in config.json file.")
        return
    
    posthog_api_key = config.get("posthog_api_key")
    posthog_project_id = config.get("posthog_project_id")
    events_file = config.get("events_file")
    
    # Create the PostHog tool (API credentials are optional now)
    posthog_tool = PostHogTool(api_key=posthog_api_key, project_id=posthog_project_id)
    
    # Create the agent
    upsell_agent = create_upsell_agent(posthog_tool)
    
    # Create the task
    upsell_task = create_upsell_task(upsell_agent, events_file)
    
    # Create and run the crew
    crew = Crew(
        agents=[upsell_agent],
        tasks=[upsell_task],
        process=Process.sequential,
        verbose=True
    )
    
    try:
        print("Starting upsell opportunity analysis...")
        result = crew.kickoff()
        print("Analysis completed successfully!")
        print(f"Result: {result}")
        # Write results to tasks.txt file
        write_tasks_to_file(str(result))
    except (Exception, requests.RequestException, json.JSONDecodeError) as e:
        print(f"ERROR: Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()
    





