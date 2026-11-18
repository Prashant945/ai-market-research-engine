from pydantic import BaseModel, Field
from typing import List, Literal

class ValidationIssue(BaseModel):
    category: Literal[
     "unsupported_claim",
        "logical_gap",
        "data_conflict",
        "missing_evidence",
        "other"]
    
    severity: Literal["high", "medium", "low"]      #high means a major issue, medium means it needs attention, and low means a minor improvement.
    affected_item: str
    explanation: str
    suggested_fix: str
    source_ids: List[str]


class ValidationOutput(BaseModel):
    overall_status: Literal[
        "pass",
        "pass_with_warnings",
        "needs_revision"
    ]

    validation_summary: str
    strengths: List[str]
    issues: List[ValidationIssue]
    revision_instructions: List[str]


import os

from langchain_google_genai import ChatGoogleGenerativeAI

from ai_engine.agents.researcher import ResearchOutput
from ai_engine.agents.analyst import AnalysisOutput
from ai_engine.prompts.validation_prompt import validation_prompt

    
class ValidationAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI( model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite" ))

        self.structured_llm =self.llm.with_structured_output(ValidationOutput)

        self.validation_chain  = (validation_prompt | self.structured_llm)

    def validate_analysis(
        self,
        research_output: ResearchOutput,
        analysis_output: AnalysisOutput
    ):

        print("\nStarting Analysis Validation...")

        # Convert both inputs into JSON
        research_data = research_output.model_dump_json(indent=2)
        analysis_data = analysis_output.model_dump_json(indent=2)

        # Invoke Gemini
        validation = self.validation_chain.invoke({
            "research_data": research_data,
            "analysis_data": analysis_data
        })

        # Get valid source IDs from original research
        valid_source_ids = {
            source.source_id
            for source in research_output.sources
        }

        # Check source references in the analysis itself
        referenced_source_ids = set()

        for insight in analysis_output.market_trends:
            referenced_source_ids.update(insight.source_ids)

        for opportunity in analysis_output.opportunities:
            referenced_source_ids.update(opportunity.source_ids)

        for risk in analysis_output.risks:
            referenced_source_ids.update(risk.source_ids)

        for conflict in analysis_output.data_conflicts:
            referenced_source_ids.update(conflict.source_ids)

        for recommendation in analysis_output.strategic_recommendations:
            referenced_source_ids.update(
                recommendation.supporting_source_ids
            )

        invalid_source_ids = referenced_source_ids - valid_source_ids

        # Independently flag invalid source references
        if invalid_source_ids:

            validation.issues.append(
                ValidationIssue(
                    category="other",
                    severity="high",
                    affected_item="Source references",
                    explanation=(
                        "The analysis contains source IDs that "
                        "do not exist in the original research: "
                        + ", ".join(sorted(invalid_source_ids))
                    ),
                    suggested_fix=(
                        "Replace invalid source IDs with valid "
                        "references or remove unsupported citations."
                    ),
                    source_ids=sorted(invalid_source_ids)
                )
            )

            validation.overall_status = "needs_revision"

        # Remove invalid source IDs from the validator's own citations
        for issue in validation.issues:
            issue.source_ids = [
                sid for sid in issue.source_ids
                if sid in valid_source_ids
            ]

        print("Analysis Validation Completed!")

        return validation
                                          