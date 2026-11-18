# We'll use Pydantic to define the report's structure.

# The report will contain:
# 1. Executive Summary
# 2. Research Objective and Scope
# 3. Market Overview
# 4. Regulatory Landscape
# 5. Competitor Analysis
# 6. Market Opportunities
# 7. Risks and Challenges
# 8. Strategic Recommendations
# 9. Validation Findings
# 10. Sources and Evidence Gaps

import os
from typing import List
from pydantic import BaseModel


class ReportSection(BaseModel):
    heading: str
    content: str
    source_ids: List[str]


class MarketResearchReport(BaseModel):
    title: str
    executive_summary: str
    research_objective: str
    scope_and_methodology: str

    sections: List[ReportSection]

    strategic_recommendations: List[str]
    validation_summary: str
    evidence_gaps: List[str]

    conclusion: str


from langchain_google_genai import ChatGoogleGenerativeAI

from ai_engine.agents.researcher import ResearchOutput
from ai_engine.agents.analyst import AnalysisOutput
from ai_engine.agents.validator import ValidationOutput

from ai_engine.prompts.report_prompt import report_prompt


class ReportWriterAgent:

    def __init__(self):

        # Initialize Gemini
        self.llm = ChatGoogleGenerativeAI(
            model=os.getenv(
                "GEMINI_MODEL",
                "gemini-3.5-flash-lite"
            )
        )

        # Enable structured output
        self.structured_llm = self.llm.with_structured_output(
            MarketResearchReport
        )

        # Create report writing chain
        self.report_chain = report_prompt | self.structured_llm

    def generate_report(
        self,
        research_output: ResearchOutput,
        analysis_output: AnalysisOutput,
        validation_output: ValidationOutput
    ):

        print("\nGenerating Market Research Report...")

        # Convert inputs into JSON
        research_data = research_output.model_dump_json(indent=2)

        analysis_data = analysis_output.model_dump_json(indent=2)

        validation_data = validation_output.model_dump_json(indent=2)

        # Generate report
        report = self.report_chain.invoke({
            "research_data": research_data,
            "analysis_data": analysis_data,
            "validation_data": validation_data
        })

        # Validate report source references
        valid_source_ids = {
            source.source_id
            for source in research_output.sources
        }

        for section in report.sections:
            section.source_ids = [
                sid for sid in section.source_ids
                if sid in valid_source_ids
            ]

        print("Market Research Report Generated!")

        return report