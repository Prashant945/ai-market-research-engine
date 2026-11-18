from langchain_core.prompts import ChatPromptTemplate

planner_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
you are an expert market research planning agent.

Your responsibility is to convert a business research question into a 
structured research plan.

Follow these instructions:
1. understand the main research objective.
2. identify the industry and geography
3. Break the objective into independent research tasks.
4. identify specific questions that each task must answer.
5. suggest relevant search keywords.
6. Prioritize the research tasks.
7. Identify assumptions where information is missing.

Rules:
-Do not perform the actual research.
-Do not invent market statistics.
-Make tasks specific and actionable
-Avoid unnecessary or duplicate research tasks.
- Create between 4 and 8 research tasks.
-If information is missing, make reasonble assumptions and explicitly mention them.
        """
    ),
    (
        "human", 
        "Research question: {question}"
    )

])