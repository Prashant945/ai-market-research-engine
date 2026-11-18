# This agent will do four things:
# 1. Receive the Planner Agent's research plan.
# 2. Extract research keywords from each task.
# 3. Search the internet using Tavily.
# 4. Use Gemini to summarise the collected information with source references.


import os
import json

from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from ai_engine.agents.planner import ResearchPlan
from ai_engine.tools.tavily_search import TavilySearch

load_dotenv()


# tavily search result(RAW)>> ResearchSource(Stores source information and assigns source IDs)>>
# TaskSummary(Gemini summarises the information for each task) >> TaskResearch Connects the summary to its original task ID and topic >>
# ResearchOutput (Combines all task findings and sources into one object) ---> Analysis Agent

# these class are simply datastructure
#TaskSummary = Gemini's output for one research task.
class TaskSummary(BaseModel):
    summary: str=Field(
        description = "summary of research findings"
    )

    key_findings: List[str]= Field(
        description = "Important Findings from the sources"
    )

    source_ids: List[str]=Field(
        description = "Ids of sources supporting the findings"
    )


#TaskResearch – What is the final result of each task?
#Associates Gemini's summary with the original Planner task.
class TaskResearch(BaseModel):
    task_id: int
    topic:str
    summary:str
    key_findings:List[str]
    source_ids:List[str]


#ResearchSource – Where did the information come from?
#Purpose: Stores information about each web source retrieved through Tavily.
class ResearchSource(BaseModel):
    source_id:str
    title:str
    url:str
    content:str
    published_date:Optional[str]=None
    relevance_score:Optional[float]=None


#ResearchOutput – What does the entire Research Agent return?
#Purpose: Combines all the research findings and sources into one final output.
class ResearchOutput(BaseModel):
    research_objective:str
    findings:List[TaskResearch]
    sources:List[ResearchSource]


llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

)

structured_llm = llm.with_structured_output(TaskSummary)

research_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """You are an expert market research analyst.

        Your responsibility is to analyse information
        collected from web search results.

        Instructions:

        1. Summarise the collected information.
        2. Identify important market findings.
        3. Use only the information provided in the sources.
        4. Do not invent statistics or facts.
        5. Identify relevant source IDs supporting your findings.
        6. Mention uncertainty or conflicting information.
        7. If information is insufficient, clearly state that.

        IMPORTANT:
        - Do not invent source IDs.
        - Do not use external knowledge as evidence.
        - Distinguish facts from estimates and opinions.

"""
    ),
    (
         "human",
        """
        Research topic: {topic}

        Research questions:
        {questions}

        Available web search results:
        {sources}

        Analyse these sources and provide structured findings.
        """
    )

    ]
)

research_chain = research_prompt | structured_llm



class ResearchAgent:

    def __init__(self):
        self.search_tool = TavilySearch()

    def conduct_research(self, plan: ResearchPlan):

        all_sources = []
        findings = []

        # Avoid duplicate URLs
        source_lookup = {}

        source_counter = 1

        # Process each research task
        for task in plan.research_tasks:

            print("\n-----------------------------")
            print("Researching:", task.topic)
            print("Keywords:", task.search_keywords)

            task_sources = []

            # Search using all keywords (maximum 2)
            print("Topic:", task.topic)
            print("Keywords:", task.search_keywords)


            for keyword in task.search_keywords[:2]:

                print(f"Searching: {keyword}")

                results = self.search_tool.search(keyword)

                print("Results received:", len(results))

                for result in results:

                    url = result.get("url")

                    if not url:
                        continue

                    # Check duplicate URL
                    if url in source_lookup:

                        source = source_lookup[url]

                    else:

                        source = ResearchSource(
                            source_id=f"S{source_counter}",
                            title=result.get("title", "Untitled"),
                            url=url,
                            content=result.get("content", ""),
                            published_date=result.get("published_date"),
                            relevance_score=result.get("score")
                        )

                        source_lookup[url] = source
                        all_sources.append(source)

                        source_counter += 1

                    # Avoid duplicate sources within a task
                    if source not in task_sources:
                        task_sources.append(source)

            # IMPORTANT: Summary generation happens
            # AFTER all keywords have been searched

            if not task_sources:

                summary = TaskSummary(
                    summary="No relevant web sources were found.",
                    key_findings=[],
                    source_ids=[]
                )

            else:

                source_text = json.dumps(
                    [
                        source.model_dump()
                        for source in task_sources
                    ],
                    indent=2
                )

                summary = research_chain.invoke({

                    "topic": task.topic,

                    "questions": "\n".join(
                        task.research_questions
                    ),

                    "sources": source_text

                })

                # Keep only valid source references
                valid_ids = {
                    source.source_id
                    for source in task_sources
                }

                summary.source_ids = [
                    source_id
                    for source_id in summary.source_ids
                    if source_id in valid_ids
                ]

            # Store task findings
            task_result = TaskResearch(

                task_id=task.task_id,
                topic=task.topic,
                summary=summary.summary,
                key_findings=summary.key_findings,
                source_ids=summary.source_ids

            )

            findings.append(task_result)

        # Return complete research output
        return ResearchOutput(

            research_objective=plan.research_objective,
            findings=findings,
            sources=all_sources

        )
