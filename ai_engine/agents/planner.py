
# LLM return an ordinary paragraph, but our next agent need predictable info
# pydantic defines the structure that LLm must return


# pydantic defines the structure of research plan, tell agent -info must generate and what format that info should follow

#BaseModel: AI output format
#Field: add descriptions to each field, what field contains
#List : store multiple research questions
#Literal: restrict values to predefined options

from pydantic import BaseModel, Field
from typing import List, Literal

#question = """analyze the indian electic market and identify opportunity  for launchihg an EV charging infrastructure company """

class ResearchTask(BaseModel):      # ResearchTask inherit the functionality of pydantic's basemodel
    task_id: int
    
    topic: str = Field(description="Research topic")

    research_questions: List[str] = Field(description="Questions that need to be answered")

    search_keywords: List[str] = Field(description="Keywords to search on the web")

    expected_output: str= Field(description="Expected findings from the task")

    priority: Literal["High", "Medium","Low"]



class ResearchPlan(BaseModel):
    research_objective: str
    industry: str
    geography: str
    timeframe: str
    research_tasks: List[ResearchTask]
    assumptions: List[str]


import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from ai_engine.prompts.planner_prompt import planner_prompt

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = "gemini-3.5-flash-lite",
    temperature = 0
)

structured_llm = llm.with_structured_output(ResearchPlan)       #instruct llm to return response in the structure defined by the pydantic model

planner_chain = planner_prompt | structured_llm


#planner agent function
def create_research_plan(question: str)-> ResearchPlan:
    if not question.strip():
        raise ValueError("Research question cannot be empty")

    response  = planner_chain.invoke({
        "question": question
    })

    return response