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

#txt_tool = FileReadTool(
#    file_path=TXT_PATH
#)

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
            #tools   = [txt_tool],
            llm     = local_llm,
            allow_delegation = False,
            max_iter = 3, # Le da oportunidades de corregir si escribe un JSON erróneo
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

    @agent
    def flashcard_maker(self) -> Agent:
        return Agent(
            config  = self.agents_config['flashcard_maker'],
            verbose = False,
            strict_parser = False,
            #function_calling_LLm = None,
            llm=local_llm

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


    @task
    def flashcard_task(self) -> Task:
        return Task(
            config = self.tasks_config[ 'flashcard_task' ]
        )

    @task
    def study_flashcards_task(self) -> Task:
        def study_logic( agent, inputs, context ):
            # parse the flashcards from the flashcard_task output
            # let the user type show, flip or quit t navigate them.

            flashcards_text = context.get( 'flashcards_task', '' )

            if not flashcards_text.strip():
                return "BuddyAi.study_flashcards_task.study_logic(), No flashcards found. Possibly an error."

            agent.think( "Parsing flashcards from text ..." )

            # 1) front: ...
            #    back:  ...

            lines = [ l.strip() for l in flashcards_text.splitlines() if l.strip() ]
            flashcards = []
            current_fc = {}

            for line in lines:

                if line.lower().startswith( "front:" ):
                    current_fc = {
                                    "front": line[ 6: ].strip(),
                                    "back": ""
                                   }
                elif line.lower().startswith( "back:" ):
                    current_fc[ "back" ] = line[ 5: ].strip()
                    flashcards.append( current_fc )
                    current_fc = {}

            if not flashcards:
                return "BuddyAi.study_flashcards_task.study_logic(), Couldn't parse flashcards from text."

            agent.say( f"I have { len( flashcards ) } flashcards loaded. We'll go through them now \n" )
            agent.say( "Type 'show' to see the next flashcard, 'flip' to see its back, or 'quit' to exit.'  " )

            index = 0
            showing_front = False
            user_input = inputs.get( 'human_input', '' ).lower()

            if user_input == 'quit':
                return "Exiting flashcard study session"

            if index >= len( flashcards ):
                return "No more flashcards left."

            if user_input == 'show':
                agent.say( f"Flashcard { index + 1 } front: { flashcards[ index ][ 'front' ] }\n " )
                showing_front = True
                return "Type 'flip' next time to see the back, or 'quit' to exit. "
            elif user_input == 'flip' and not showing_front:
                return "You need to 'show' the card first. Then you can 'flip' it "
            elif user_input == 'flip' and     showing_front:
                #show the back
                agent.say( f"Flashcard { index + 1} back: { flashcards[ index ][ 'back' ] }" )
                return f"Now you can type 'show' to move to the next flashcard, or 'quit' to exit. "
            else:
                return "Invalid command. Please type 'show', 'flip' or 'quit' "


        return Task(
            config       = self.tasks_config[ 'study_flashcard_task' ],
            Logic        = study_logic,
            human_inputs = True
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
