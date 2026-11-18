import os

from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

class TavilySearch:     # we create class so that one instance of the class can be used to multiple research tasks 
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")

        if not api_key :
            raise ValueError("TAVILY_API_KEY is missing")

        self.client = TavilyClient(api_key=api_key)     #TavilyClient()	Connects to Tavily API

    def search(self, query:str):
        response = self.client.search(
            query=query,
            search_depth="basic",
            max_results=3)

        results =  response.get("results",[])

        print("Results received:", len(results))

        if not results:
            print("WARNING: Tavily returned no results!")

        return results

