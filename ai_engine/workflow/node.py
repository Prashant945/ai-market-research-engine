from ai_engine.agents.planner import create_research_plan
from ai_engine.agents.researcher import ResearchAgent
from ai_engine.agents.analyst import AnalysisAgent
from ai_engine.agents.validator import ValidationAgent
from ai_engine.agents.report_writer import ReportWriterAgent

from ai_engine.workflow.state import ResearchState

##############
from backend.database import (
    update_agent_status,
    fail_research_job
)
##############


researcher = ResearchAgent()
analyst = AnalysisAgent()
validator = ValidationAgent()
report_writer = ReportWriterAgent()

####################
def execute_agent(state, agent_name, agent_function):

    research_id = state["research_id"]

    # Mark agent as running
    update_agent_status(
        research_id,
        agent_name,
        "running"
    )

    try:
        result = agent_function()

        # Mark agent as completed
        update_agent_status(
            research_id,
            agent_name,
            "completed"
        )

        return result

    except Exception as e:

        update_agent_status(
            research_id,
            agent_name,
            "failed"
        )

        fail_research_job(research_id, str(e))

        raise

####################


#node functions version 1 
# def planner_node(state: ResearchState):
#     plan = create_research_plan( state["user_query"])

#     return {"research_plan":plan}


# def researcher_node(state: ResearchState):
#     research = researcher.conduct_research(state["research_plan"])
#     return {"research_output": research}


# def analyst_node(state: ResearchState):
#     analysis = analyst.conduct_analysis(state["research_output"], validation_feedback=state.get("validation_output"))
#     return {
#         "analysis_output": analysis,
#         "analysis_attempts": state.get("analysis_attempts",0)+1
#     }


# def validator_node(state:ResearchState):
#     validation = validator.validate_analysis(
#         state["research_output"],
#         state["analysis_output"]
#     )
#     return {
#         "validation_output": validation
#     }

# def report_writer_node(state: ResearchState):
#     report  = report_writer.generate_report(
#         state["research_output"],
#         state["analysis_output"],
#         state["validation_output"]
#     )

#     return {
#         "final_report": report
#     }


# norde function version 2

def planner_node(state: ResearchState):

    return execute_agent(
        state,
        "planner",
        lambda: {
            "research_plan": create_research_plan(
                state["user_query"]
            )
        }
    )


def researcher_node(state: ResearchState):

    return execute_agent(
        state,
        "researcher",
        lambda: {
            "research_output": researcher.conduct_research(
                state["research_plan"]
            )
        }
    )


def analyst_node(state: ResearchState):

    def run_analysis():

        analysis = analyst.conduct_analysis(
            state["research_output"],
            validation_feedback=state.get("validation_output")
        )

        return {
            "analysis_output": analysis,
            "analysis_attempts": state.get("analysis_attempts", 0) + 1
        }

    return execute_agent(state, "analyst", run_analysis)


def validator_node(state: ResearchState):

    return execute_agent(
        state,
        "validator",
        lambda: {
            "validation_output": validator.validate_analysis(
                state["research_output"],
                state["analysis_output"]
            )
        }
    )


def report_writer_node(state: ResearchState):

    return execute_agent(
        state,
        "report_writer",
        lambda: {
            "final_report": report_writer.generate_report(
                state["research_output"],
                state["analysis_output"],
                state["validation_output"]
            )
        }
    )
