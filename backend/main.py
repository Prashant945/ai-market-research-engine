from fastapi import FastAPI


from fastapi import HTTPException

# from backend.database import get_research 
# from backend.database import get_all_research
# from backend.database import get_report
# from backend.database import save_research

from backend.database import (
    create_research_job,
    complete_research_job,
    fail_research_job,
    get_research,
    get_all_research,
    get_report,
    get_workflow_status
)


from fastapi.responses import PlainTextResponse

from fastapi import FastAPI, HTTPException, BackgroundTasks

from pydantic import BaseModel, Field
from ai_engine.workflow.graph import build_workflow


research_graph = build_workflow()

def run_research_workflow(research_id: str, question: str):

    try:

        initial_state = {
            "research_id": research_id,
            "user_query": question,
            "analysis_attempts": 0
        }

        result = research_graph.invoke(initial_state)

        report = result["final_report"]
        sources = result["research_output"].sources

        complete_research_job(
            research_id,
            report,
            sources
        )

    except Exception as e:

        fail_research_job(
            research_id,
            str(e)
        )



app = FastAPI(
    title='AI Market Research & Strategy Engine',
    description='API for AI-powered market research',
    version="1.0.0"
)

@app.get("/")       #creates an API endpoint for the homepage.
def home():
    return {
        "message": "AI Market Research Engine API is running" 
    }

@app.get("/health")
def health_check():
    return {
        "status":"healthy"      # return json response
    }




class ResearchRequest(BaseModel):
    question: str = Field(..., min_length=5, description="Business Research Question")

research_graph = build_workflow()

# @app.post("/research")
# def create_research(request: ResearchRequest):
#     initial_state = {
#         "user_query":request.question,
#         "analysis_attempts":0
#     }

#     result = research_graph.invoke(initial_state)

#     report = result["final_report"]
#     sources = result["research_output"].sources



#     #save report in mongo db
#     research_id  = save_research(request.question, report, sources)





    # return {
    #     "status":"completed",
    #     "research_id":research_id,
    #     "research_question": request.question,
    #     "report":report.model_dump()            #report.model_dump()	Converts Pydantic report into a dictionary
    # }

@app.post("/research")
def create_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):

    # Create MongoDB record first
    research_id = create_research_job(request.question)

    # Execute workflow in background
    background_tasks.add_task(
        run_research_workflow,
        research_id,
        request.question
    )

    return {
        "status": "pending",
        "research_id": research_id,
        "research_question": request.question,
        "message": "Research workflow started successfully"
    }

@app.get("/research/{research_id}/status")
def retrieve_workflow_status(research_id: str):

    status = get_workflow_status(research_id)

    if status is None:
        raise HTTPException(
            status_code=404,
            detail="Research workflow not found"
        )

    return status

@app.get("/research/{research_id}")
def retrieve_research(research_id: str):

    research = get_research(research_id)

    if research is None:
        raise HTTPException(
            status_code=404,
            detail="Research report not found"
        )

    return research



@app.get("/research")
def list_research():
    research_list = get_all_research()

    return {
        "total":len(research_list),
        "research":research_list
    }


@app.get("/reports/{research_id}")
def retrieve_report(research_id: str):

    report = get_report(research_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    return report

@app.get("/reports/{research_id}/export")
def export_report(research_id:str):
    report = get_report(research_id)

    if report is None:
        raise HTTPException (
            status_code=404,
            detail = "Report not found"
        )
    content = f"""# {report['title']}
## Executive Summary
{report['executive_summary']}

## Research Objective

{report['research_objective']}

## Scope and Methodology

{report['scope_and_methodology']}

"""
    for section in report["sections"]:
        content += f"## {section['heading']}\n\n"
        content += section["content"] + "\n\n"

        if section["source_ids"]:
            content += f"**Sources:** {', '.join(section['source_ids'])}\n\n"

    content += "## Strategic Recommendations\n\n"

    for recommendation in report["strategic_recommendations"]:
        content += f"- {recommendation}\n"

    content += f"\n## Validation Summary\n\n{report['validation_summary']}\n\n"

    content += "## Evidence Gaps\n\n"

    for gap in report["evidence_gaps"]:
        content += f"- {gap}\n"

    content += f"\n## Conclusion\n\n{report['conclusion']}"

    return PlainTextResponse(
        content=content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="research_{research_id}.md"'
        }
    )