# from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# llm = ChatGroq(
#     model="llama-3.3-70b-versatile",
#     # model = "openai/gpt-oss-120b", 
#     temperature=0
# )

llm  = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 0)