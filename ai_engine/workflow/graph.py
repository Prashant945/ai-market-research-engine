from langgraph.graph import StateGraph, START, END      # StateGraph creates the workflow graph

from ai_engine.workflow.state import ResearchState      #Defines shared workflow data

from ai_engine.workflow.node import (
    planner_node,
    researcher_node,
    analyst_node,
    validator_node,
    report_writer_node
)

def build_workflow():
    workflow = StateGraph(ResearchState)

    workflow.add_node("planner", planner_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("analyst", analyst_node)
    workflow.add_node("validator", validator_node)
    workflow.add_node("report_writer", report_writer_node)

    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "researcher")
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", "validator")
    
    # workflow.add_edge("validator", "report_writer")
    workflow.add_conditional_edges("validator", route_after_validation,
                                   {
                                       "revise": "analyst",
                                       "report": "report_writer"
                                   })
    
    workflow.add_edge("report_writer", END)


    app = workflow.compile()

    return app


MAX_ANALYSIS_EVENTS = 2
def route_after_validation(state: ResearchState):
    status = state["validation_output"].overall_status

    attempts = state.get("analysis_attempts",0)

    if status == "needs_revision" and attempts <MAX_ANALYSIS_EVENTS:
        return "revise"
    return "report"
