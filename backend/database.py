import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)

db = client["prashantagarwal945_db_user"]

research_collection = db["research_reports"]

def test_connection():
    try:
        client.admin.command("ping")
        print("Mongodb connected successfully")
    except Exception as e:
        print("mongodb connection failed ",e)



from datetime import datetime,timezone
from uuid import uuid4

# def save_research(question:str, report):
#     research_id = str(uuid4())            #uuid4()	Generates a unique ID for each research job

#     research_document = {
#         "research_id": research_id,
#         "question": question,
#         "status": "completed",
#         "created_at": datetime.now(timezone.utc),
#         "report": report.model_dump()       #report.model_dump()	Converts your Pydantic report into a Python dictionary

#     }

#     research_collection.insert_one(research_document)       #insert_one()	Inserts one document into MongoDB
#     return research_id

def save_research(question: str, report, sources):
    research_id = str(uuid4())

    report = report.model_dump()

    # Add original research sources to the report
    report["sources"] = [
        source.model_dump() for source in sources
    ]

    research_document = {
        "research_id": research_id,
        "question": question,
        "status": "completed",
        "created_at": datetime.now(timezone.utc),
        "report": report
    }

    research_collection.insert_one(research_document)

    return research_id

##############################################################################


# Agent names used by the LangGraph workflow
AGENT_NAMES = [
    "planner",
    "researcher",
    "analyst",
    "validator",
    "report_writer"
]


# Create a research record BEFORE starting the workflow
def create_research_job(question: str):

    research_id = str(uuid4())

    agent_status = {
        agent: "pending"
        for agent in AGENT_NAMES
    }

    research_document = {
        "research_id": research_id,
        "question": question,
        "status": "pending",
        "agent_status": agent_status,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "report": None
    }

    research_collection.insert_one(research_document)

    return research_id


# Update an individual agent's status
# def update_agent_status(research_id: str, agent: str, status: str):

#     research_collection.update_one(
#         {"research_id": research_id},
#         {
#             "$set": {
#                 f"agent_status.{agent}": status,
#                 "status": "running",
#                 "updated_at": datetime.now(timezone.utc)
#             }
#         }
#     )


def update_agent_status(research_id: str, agent: str, status: str):

    update_fields = {
        f"agent_status.{agent}": status,
        "updated_at": datetime.now(timezone.utc)
    }

    if status == "running":
        update_fields["status"] = "running"

    research_collection.update_one(
        {"research_id": research_id},
        {"$set": update_fields}
    )


# Save the final report after workflow completion
def complete_research_job(research_id: str, report, sources):

    report_data = report.model_dump()

    report_data["sources"] = [
        source.model_dump() for source in sources
    ]

    research_collection.update_one(
        {"research_id": research_id},
        {
            "$set": {
                "report": report_data,
                "status": "completed",
                "updated_at": datetime.now(timezone.utc),
                "completed_at": datetime.now(timezone.utc)
            }
        }
    )


# Record workflow failure
def fail_research_job(research_id: str, error: str):

    research_collection.update_one(
        {"research_id": research_id},
        {
            "$set": {
                "status": "failed",
                "error": error,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )


# Retrieve workflow status
def get_workflow_status(research_id: str):

    return research_collection.find_one(
        {"research_id": research_id},
        {
            "_id": 0,
            "research_id": 1,
            "question": 1,
            "status": 1,
            "agent_status": 1,
            "created_at": 1,
            "updated_at": 1,
            "completed_at": 1,
            "error": 1
        }
    )










##################################################################################3








# Create GET /research/{research_id}
# Objective: Retrieve a stored report using its unique research ID, without executing LangGraph again.
def get_research(research_id:str):
    research = research_collection.find_one(            #find_one() searches for one matching document.
        {"research_id":research_id},
        {"_id":0}
    )

    return research


def get_all_research():
    research_list = list(
        research_collection.find(
            {}, 
            {"_id":0,"report":0}
        ).sort("created_at", -1)
    )
    return research_list

# find({}) retrieves all documents.
# {"_id": 0, "report": 0} excludes internal ID and large report content.
# sort("created_at", -1) displays newest research first.
# list() converts MongoDB results into a Python list.

def get_report(research_id:str):
    research = research_collection.find_one(
        {"research_id": research_id},
        {"_id":0, "report":1}
    )

    if research is None:
        return None

    return research["report"]
