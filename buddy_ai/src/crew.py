from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
#from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileReadTool


local_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://ollama:11434"
)

txt_tool = FileReadTool(
    file_path='/app/config/sample_document.txt',
    llm=local_llm
)


@CrewBase
class BuddyAi():
    """BuddyAi crew"""

    agents_config = '/app/config/agents.yaml'
    tasks_config  = '/app/config/tasks.yaml'

    @agent
    def txt_reader(self) -> Agent:
        return Agent(
            config  = self.agents_config[ 'txt_reader' ],
            verbose = True,
            tools   = [ txt_tool ],
            llm     = local_llm
        )

    @agent
    def summarizer(self) -> Agent:
        return Agent(
            config  = self.agents_config['summarizer'],
            verbose = True,
            llm     = local_llm
        )

    @task
    def reading_task(self) -> Task:
        return Task(
            config  = self.tasks_config[ 'reading_task' ]
        )

    @task
    def summarizing_task(self) -> Task:
        return Task(
            config  = self.tasks_config[ 'summarizing_task' ],
            output_file = '/app/config/summary.md'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the BuddyAi crew"""
        return Crew(
            agents  = self.agents,
            tasks   = self.tasks,
            process = Process.sequential,
            verbose = True,

            # point to local llama3 model
            memory=False,  # <--- FORCE THIS TO FALSE
            embedder=None

        )
