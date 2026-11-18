import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

api_key = os.getenv("TAVILY_API_KEY")

# Check API key
if not api_key:
    raise ValueError("Tavily API key not loaded!")

print("API key loaded successfully!")

# Initialize Tavily
client = TavilyClient(api_key=api_key)

# Perform search
response = client.search(
    query="India electric vehicle market size and growth",
    search_depth="basic",
    max_results=3
)

# Display results
print("\nTotal results:", len(response.get("results", [])))

for result in response.get("results", []):

    print("\nTitle:", result.get("title"))
    print("URL:", result.get("url"))
    print("Content:", result.get("content"))
    print("Score:", result.get("score"))