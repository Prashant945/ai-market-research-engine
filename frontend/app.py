import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh
import os



API_URL = st.secrets.get(
    "API_URL",
    os.getenv("API_URL", "http://127.0.0.1:8000")
).rstrip("/")

def display_report(report):

    st.title(report["title"])

    st.divider()

    # Executive Summary
    st.header("Executive Summary")
    st.markdown(report["executive_summary"])

    # Research Objective
    st.header("Research Objective")
    st.markdown(report["research_objective"])

    # Scope and Methodology
    st.header("Scope & Methodology")
    st.markdown(report["scope_and_methodology"])

    # Research Findings
    st.header("Market Research Findings")

    for section in report["sections"]:

        with st.expander(section["heading"], expanded=True):

            st.markdown(section["content"])
            if section.get("source_ids"):

                sources_by_id = {
                    source["source_id"]: source
                    for source in report.get("sources", [])
                }

                for source_id in section["source_ids"]:

                    source = sources_by_id.get(source_id)

                    if source:
                        st.markdown(
                        f"- [{source['title']}]({source['url']})"
                    )
                    else:
                        st.caption(source_id)

            # if section.get("source_ids"):
            #     st.caption(
            #         "Sources: " + ", ".join(section["source_ids"])
            #     )

    # Strategic Recommendations
    st.header("Strategic Recommendations")

    for index, recommendation in enumerate(
        report["strategic_recommendations"], start=1
    ):
        st.write(f"**{index}.** {recommendation}")

    # Validation Summary
    st.header("Validation Summary")
    st.info(report["validation_summary"])

    # Evidence Gaps
    st.header("Evidence Gaps")

    for gap in report["evidence_gaps"]:
        st.write("•", gap)

    # Conclusion
    st.header("Conclusion")
    st.markdown(report["conclusion"])


    #import json

    report_markdown = f"""# {report['title']}

## Executive Summary

{report['executive_summary']}

## Research Objective

{report['research_objective']}

## Scope & Methodology

{report['scope_and_methodology']}

## Research Findings
"""
    sources_by_id = {
    source["source_id"]: source
    for source in report.get("sources", [])
}

    for section in report["sections"]:

        source_links = []

        for source_id in section.get("source_ids", []):

            source = sources_by_id.get(source_id)

            if source:
                source_links.append(
                    f"[{source['title']}]({source['url']})"
                )
            else:
                source_links.append(source_id)

        report_markdown += f"""
    ### {section['heading']}

    {section['content']}

    **Sources:** {' | '.join(source_links)}
    """

    report_markdown += "\n## Strategic Recommendations\n"

    for recommendation in report["strategic_recommendations"]:
        report_markdown += f"\n- {recommendation}"

    report_markdown += f"""

## Validation Summary

{report['validation_summary']}

## Evidence Gaps

"""

    for gap in report["evidence_gaps"]:
        report_markdown += f"\n- {gap}"

    report_markdown += f"""

## Conclusion

{report['conclusion']}
"""

    st.download_button(
        label="Download Research Report",
        data=report_markdown,
        file_name="market_research_report.md",
        mime="text/markdown"
    )


st.set_page_config(
    page_title="AI Market Research Engine",
    page_icon="📊",
    layout="wide"
)

st.title("AI Market Research & Strategy Engine")

st.write(
    "Transform business questions into structured "
    "market research and strategic recommendations."
)

st.sidebar.title("Navigation")


page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "New Research",
        "Workflow Monitor",
        "Research History"
    ]
)

# Dashboard page
if page == "Dashboard":

    st.header("Dashboard Overview")

    try:
        response = requests.get(
            f"{API_URL}/research"
        )

        if response.status_code == 200:

            data = response.json()
            research_list = data["research"]

            total_projects = len(research_list)

            completed_projects = sum(
                1 for research in research_list
                if research["status"] == "completed"
            )

            active_projects = sum(
                1 for research in research_list
                if research["status"] in ["pending", "processing"]
            )

            col1, col2, col3 = st.columns(3)

            col1.metric("Total Projects", total_projects)
            col2.metric("Completed Projects", completed_projects)
            col3.metric("Active Projects", active_projects)

            st.divider()

            st.subheader("Recent Research Activity")

            if research_list:

                recent_research = []

                for research in research_list[:5]:

                    recent_research.append({
                        "Research Question": research["question"],
                        "Status": research["status"].title(),
                        "Created At": research["created_at"]
                    })

                st.dataframe(
                    recent_research,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No research projects available yet.")

        else:
            st.error("Could not load dashboard data.")

    except requests.exceptions.ConnectionError:
        st.error("Backend server is not running.")

# New Research page


elif page == "New Research":

    st.header("Start New Research")

    question = st.text_area(
        "Enter your business research question",
        placeholder="Example: Analyze the Indian EV market..."
    )

    if st.button("Start Research"):

        if question.strip():

            try:
                response = requests.post(
                    f"{API_URL}/research",
                    json={"question": question}
                )
                
                st.write("HTTP METHOD:", response.request.method)

                if response.status_code == 200:

                    result = response.json()

                    

                    st.write("Response URL:", response.url)
                    st.write("Status Code:", response.status_code)
                    st.write("Actual Response:", result)
                    st.write("Available Keys:", list(result.keys()))



                    # research_id = result["research"][0]["research_id"] or 
                    research_id = result["research_id"]
                    st.write(research_id)

                    st.session_state["monitor_research_id"] = research_id

                    st.success("Research workflow started successfully!")

                    st.write("Research ID:", research_id)

                    st.info(
                        "Go to Workflow Monitor to track your AI agents."
                    )

                else:
                    st.error(f"API Error: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to FastAPI.")

        else:
            st.warning("Please enter a research question.")



# Research History page
elif page == "Research History":


    st.header("Research History")

    try:
        response = requests.get(
            f"{API_URL}/research"
        )

        if response.status_code == 200:

            research_list = response.json()["research"]

            

            if research_list:

                for research in research_list:

                    with st.expander(research["question"]):

                        col1, col2 = st.columns(2)

                        with col1:
                            st.write("**Status:**", research["status"])

                        with col2:
                            st.write("**Created At:**", research["created_at"])

                        st.caption(f"Research ID: {research['research_id']}")

                        if st.button("View Report", key=research["research_id"]):

                            report_response = requests.get(
                                f"{API_URL}/reports/{research['research_id']}"
                                    )

                            # if report_response.status_code == 200:

                            #     report = report_response.json()

                            #     st.subheader(report["title"])
                            #     st.markdown(report["executive_summary"])

                            #     for section in report["sections"]:
                            #         st.subheader(section["heading"])
                            #         st.markdown(section["content"])

                            #     st.subheader("Strategic Recommendations")

                            #     for recommendation in report["strategic_recommendations"]:
                            #         st.write("•", recommendation)

                            # else:
                            #     st.error("Could not retrieve report.")

                            if report_response.status_code == 200:

                                report = report_response.json()

                                display_report(report)

                            else:
                                st.error("Could not retrieve report.")

                

            else:
                st.info("No research projects found.")

        else:
            st.error("Unable to fetch research history.")

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to FastAPI backend.")



# Workflow Monitor page
elif page == "Workflow Monitor":

    st.header("AI Agent Workflow Monitor")

    st.write(
        "Track the execution and completion status of each AI agent."
    )

    try:

        response = requests.get(
            f"{API_URL}/research"
        )

        if response.status_code == 200:

            research_list = response.json()["research"]

            if research_list:

                # Find previously selected research ID
                saved_id = st.session_state.get(
                    "monitor_research_id"
                )

                research_ids = [
                    research["research_id"]
                    for research in research_list
                ]

                default_index = (
                    research_ids.index(saved_id)
                    if saved_id in research_ids
                    else 0
                )

                selected_id = st.selectbox(
                    "Select Research Project",
                    research_ids,
                    index=default_index,
                    format_func=lambda x: next(
                        (
                            r["question"][:70]
                            for r in research_list
                            if r["research_id"] == x
                        ),
                        x
                    )
                )

                st.session_state["monitor_research_id"] = selected_id

                # Get workflow status
                status_response = requests.get(
                    f"{API_URL}/research/{selected_id}/status"
                )

                if status_response.status_code == 200:

                    workflow = status_response.json()

                    overall_status = workflow["status"]
                    agent_status = workflow["agent_status"]

                    if overall_status in ["pending", "running"]:
                        st_autorefresh(
                            interval=2000,
                            limit=None,
                            key=f"workflow_refresh_{selected_id}"
                        )

                    st.divider()

                    st.subheader("Overall Research Status")

                    st.write(
                        f"**Status:** {overall_status.upper()}"
                    )

                    # Calculate progress
                    total_agents = len(agent_status)

                    completed_agents = sum(
                        1 for status in agent_status.values()
                        if status == "completed"
                    )

                    progress = (
                        completed_agents / total_agents
                        if total_agents else 0
                    )

                    col1, col2 = st.columns(2)

                    col1.metric(
                        "Completed Agents",
                        f"{completed_agents}/{total_agents}"
                    )

                    col2.metric(
                        "Progress",
                        f"{progress * 100:.0f}%"
                    )

                    st.progress(progress)

                    st.divider()

                    st.subheader("Agent Execution Status")

                    agent_icons = {
                        "planner": "🧠",
                        "researcher": "🔍",
                        "analyst": "📊",
                        "validator": "✅",
                        "report_writer": "📝"
                    }

                    agent_names = {
                        "planner": "Planner Agent",
                        "researcher": "Research Agent",
                        "analyst": "Analysis Agent",
                        "validator": "Validation Agent",
                        "report_writer": "Report Writer Agent"
                    }

                    columns = st.columns(len(agent_status))

                    for index, (agent, status) in enumerate(
                        agent_status.items()
                    ):

                        with columns[index]:

                            icon = agent_icons.get(agent, "🤖")
                            name = agent_names.get(agent, agent)

                            st.markdown(f"### {icon}")

                            st.write(f"**{name}**")

                            if status == "completed":
                                st.success("Completed")

                            elif status == "running":
                                st.info("Running")

                            elif status == "failed":
                                st.error("Failed")

                            else:
                                st.warning("Pending")

                    st.divider()

                    # Refresh status manually
                    # if st.button("Refresh Workflow Status"):
                    #     st.rerun()

                    # Show error if workflow failed
                    if overall_status == "failed":
                        st.error(
                            workflow.get(
                                "error",
                                "Research workflow failed."
                            )
                        )

                    # Show final report after completion
                    elif overall_status == "completed":

                        st.success(
                            "All agents completed successfully!"
                        )

                        report_response = requests.get(
                            f"{API_URL}/reports/{selected_id}"
                        )

                        if report_response.status_code == 200:

                            st.subheader("Generated Research Report")

                            display_report(report_response.json())

                    else:
                        st.info(
                            "Research is still in progress. "
                            "Click Refresh Workflow Status to check again."
                        )

                else:
                    st.error("Unable to retrieve workflow status.")

            else:
                st.info("No research projects available.")

        else:
            st.error("Unable to retrieve research projects.")

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to FastAPI backend.")