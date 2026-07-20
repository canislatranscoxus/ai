import os
import re
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool

TXT_PATH = '/app/config/sample_document.txt'

local_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://ollama:11434"
)

# Inicialización limpia: Sin pasar el LLM aquí, la herramienta actúa como un lector directo de archivos planos,
# no como un buscador RAG confuso para modelos pequeños.
txt_tool = FileReadTool(
    file_path=TXT_PATH
)

@CrewBase
class BuddyAi():
    """BuddyAi crew"""

    agents_config = '/app/config/agents.yaml'
    tasks_config  = '/app/config/tasks.yaml'

    @agent
    def txt_reader(self) -> Agent:
        return Agent(
            config  = self.agents_config['txt_reader'],
            verbose = True,
            tools   = [txt_tool],
            llm     = local_llm
        )

    @agent
    def summarizer(self) -> Agent:
        return Agent(
            config  = self.agents_config['summarizer'],
            verbose = True,
            llm     = local_llm
        )

    @agent
    def quiz_maker(self) -> Agent:
        return Agent(
            config          = self.agents_config['quiz_maker'],
            verbose         = True,
            llm             = local_llm,
            strict_parser   = False
        )

    @agent
    def study_buddy(self) -> Agent:
        return Agent(
            config  = self.agents_config['study_buddy'],
            verbose = True,
            llm     = local_llm,
        )

    @task
    def reading_task(self) -> Task:
        # Eliminamos 'logic' ya que CrewAI mapea las tareas nativamente usando tasks.yaml.
        # Asegúrate de aplicar las instrucciones explícitas en tu tasks.yaml como vimos antes.
        return Task(
            config  = self.tasks_config['reading_task']
        )

    @task
    def summarizing_task(self) -> Task:
        return Task(
            config      = self.tasks_config['summarizing_task'],
            output_file = '/app/config/summary.md'
        )

    @task
    def quiz_task(self) -> Task:
        return Task(
            config  = self.tasks_config['quiz_task']
        )

    @task
    def user_test_task(self) -> Task:
        # Para interactuar con el usuario de manera nativa en CrewAI usando CLI,
        # simplemente retornamos la tarea configurada. El parámetro 'human_input: true'
        # en tu tasks.yaml se encargará de pausar y pedir la entrada automáticamente.
        return Task(
            config  = self.tasks_config['user_test_task']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the BuddyAi crew"""
        return Crew(
            agents  = self.agents,
            tasks   = self.tasks,
            process = Process.sequential,
            verbose = True,
            memory  = False,  # Desactivado para evitar consumo innecesario con llama3.2
            embedder= None
        )
