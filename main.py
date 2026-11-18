
from ai_engine.workflow.graph import build_workflow


# Step 1: User research question
question = """
Analyze the Indian electric vehicle market and identify
opportunities for launching an EV charging infrastructure company.
"""


# Step 2: Build LangGraph workflow
print("\n========== BUILDING WORKFLOW ==========\n")

app = build_workflow()

print("LangGraph workflow compiled successfully!")


# Step 3: Prepare initial state
initial_state = {
    "user_query": question,
    "analysis_attempts": 0
}


# Step 4: Execute complete workflow
print("\n========== EXECUTING AI RESEARCH ENGINE ==========\n")

result = app.invoke(initial_state)


# Step 5: Retrieve final report
final_report = result["final_report"]

print("\n========== FINAL MARKET RESEARCH REPORT ==========\n")

print(final_report.model_dump_json(indent=2))


# Step 6: Save report
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
