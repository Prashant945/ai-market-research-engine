from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model = "gemini-3.8-flash",
    temperature = 0)
response = llm.invoke('explain ev market in 3 words')
print(response.text)