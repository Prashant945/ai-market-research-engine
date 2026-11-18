# what does the information mean for the business

# For our Indian EV charging infrastructure project, it should:
# 1. Identify major market trends.
# 2. Find business opportunities and target customer segments.
# 3. Identify risks and challenges.
# 4. Compare competitors and identify market gaps.
# 5. Recommend possible business strategies.
# 6. Highlight conflicting data and insufficient evidence.

from typing import List, Literal
from pydantic import BaseModel, Field

class MarketInsight(BaseModel):
    insight: str
    insight_type: Literal['fact','inference']
    source_ids:List[str]
    business_implication:str

class BusinessOpportunity(BaseModel):
    opportunity: str
    target_segment: str
    rationale: str
    source_ids: List[str]
    potential_risks: List[str]

class StrategicRisk(BaseModel):
    risk: str
    evidence: str
    source_ids: List[str]
    mitigation: str


class DataConflict(BaseModel):
    topic: str
    conflicting_claims: List[str]
    possible_explanation: str
    source_ids: List[str]


class StrategicRecommendation(BaseModel):
    recommendation: str
    rationale: str
    supporting_source_ids: List[str]
    priority: Literal["high", "medium", "low"]


class AnalysisOutput(BaseModel):
    research_objective: str
    market_trends: List[MarketInsight]
    opportunities: List[BusinessOpportunity]
    competitor_insights: List[str]
    risks: List[StrategicRisk]
    data_conflicts: List[DataConflict]
    strategic_recommendations: List[StrategicRecommendation]
    evidence_gaps: List[str]



import os

from langchain_google_genai import ChatGoogleGenerativeAI
from ai_engine.agents.researcher import ResearchOutput
from ai_engine.prompts.analysis_prompt import analysis_prompt

class AnalysisAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI( model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite"))

        self.structured_llm = self.llm.with_structured_output(AnalysisOutput)

        self.analysis_chain = analysis_prompt | self.structured_llm


    
    def conduct_analysis(self, research_output:ResearchOutput, validation_feedback=None):
        print("Starting Strategic Analysis")

        research_data = research_output.model_dump_json(indent=2) # convert research data into json, indentation to be used in JSON output

        if validation_feedback is not None:
            feedback_data = validation_feedback.model_dump_json(indent=2)


        else:
            feedback_data = "No previous validation feedback. This is the initial analysis."


        analysis = self.analysis_chain.invoke({
            "research_data": research_data,
            "validation_feedback":feedback_data

            })

        valid_source_ids = {source.source_id for source in research_output.sources}

        # Remove any source IDs that do not exist in the research
        for insight in analysis.market_trends:
            insight.source_ids = [
                sid for sid in insight.source_ids
                if sid in valid_source_ids
            ]

        for opportunity in analysis.opportunities:
            opportunity.source_ids = [
                sid for sid in opportunity.source_ids
                if sid in valid_source_ids
            ]

        for risk in analysis.risks:
            risk.source_ids = [
                sid for sid in risk.source_ids
                if sid in valid_source_ids
            ]

        for conflict in analysis.data_conflicts:
            conflict.source_ids = [
                sid for sid in conflict.source_ids
                if sid in valid_source_ids
            ]

        for recommendation in analysis.strategic_recommendations:
            recommendation.supporting_source_ids = [
                sid for sid in recommendation.supporting_source_ids
                if sid in valid_source_ids
            ]

        print("Strategic Analysis Completed!")

        return analysis

    
