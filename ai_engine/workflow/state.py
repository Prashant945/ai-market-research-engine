from typing import TypedDict, Any

class ResearchState(TypedDict, total=False):        #TypedDict expected keys and values types of a dictionary  #total=False means all fields are optional when creating the dictionary
    research_id : str       # this one is added
    user_query : str
    research_plan : Any
    research_output: Any
    analysis_output: Any
    validation_output: Any
    final_report: Any
    analysis_attempts: int
    

#initially, we only have the user's query. The research plan, analysis and report will be added as the workflow progresses.
#any allow us to store those objects without defining all their types here yet.


#step 2 building nodes
# node- a python function that calls one of existing agents and update the shared state
# 
#  
