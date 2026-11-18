from ai_engine.agents.planner import create_research_plan

from ai_engine.agents.researcher import ResearchAgent

from ai_engine.agents.analyst import AnalysisAgent

from ai_engine.agents.validator import ValidationAgent

from ai_engine.agents.report_writer import ReportWriterAgent

# Step 1: User research question
question = """
analyze the indian electic market and identify opportunity 
for launchihg an EV charging infrastructure company
"""


#Step 2: Execute Planner Agent
print("\n=================Planner Agent===================\n")

plan = create_research_plan(question)

print("Research plan generated successfully")

#step 3: Execute Research Agent
print("\n===========Research Agent============\n")

research_agent = ResearchAgent()
research_output = research_agent.conduct_research(plan)

#Step 4: Display findings of research agent
# print("\n===========Research Findings============\n")

# print(research_output.model_dump_json(indent=2))

# step 4: Analysis Agent
analyst = AnalysisAgent()
analysis_output = analyst.conduct_analysis(research_output)

# display analysis
# print("\n==========Strategic Analysis==========\n")
# print(analysis_output.model_dump_json(indent=2))


# Step 5: Validation Agent
validator = ValidationAgent()

validation_output = validator.validate_analysis(
    research_output,
    analysis_output
)

# Display validation report
# print("\n========== VALIDATION REPORT ==========")

# print(validation_output.model_dump_json(indent=2))



# Step 6: Report Writer Agent

report_writer = ReportWriterAgent()

final_report = report_writer.generate_report(
    research_output,
    analysis_output,
    validation_output
)

print("\n========== FINAL MARKET RESEARCH REPORT ==========")

print(final_report.model_dump_json(indent=2))


def save_report(report, filename="market_research_report.md"):

    with open(filename, "w", encoding="utf-8") as file:

        file.write(f"# {report.title}\n\n")

        file.write("## Executive Summary\n\n")
        file.write(report.executive_summary + "\n\n")

        file.write("## Research Objective\n\n")
        file.write(report.research_objective + "\n\n")

        file.write("## Scope and Methodology\n\n")
        file.write(report.scope_and_methodology + "\n\n")

        for section in report.sections:

            file.write(f"## {section.heading}\n\n")
            file.write(section.content + "\n\n")

            if section.source_ids:
                citations = ", ".join(section.source_ids)
                file.write(f"**Sources:** {citations}\n\n")

        file.write("## Strategic Recommendations\n\n")

        for recommendation in report.strategic_recommendations:
            file.write(f"- {recommendation}\n")

        file.write("\n## Validation Summary\n\n")
        file.write(report.validation_summary + "\n\n")

        file.write("## Evidence Gaps\n\n")

        for gap in report.evidence_gaps:
            file.write(f"- {gap}\n")

        file.write("\n## Conclusion\n\n")
        file.write(report.conclusion)

    print(f"\nReport saved as {filename}")


save_report(final_report)