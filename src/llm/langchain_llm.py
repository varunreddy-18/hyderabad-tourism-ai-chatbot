import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


load_dotenv()


class LangChainLLM:

    def __init__(self):

        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.parser = StrOutputParser()

    def generate(
        self,
        context,
        query,
        system_prompt=None
    ):

        if not system_prompt:

            system_prompt = """
You are an expert Hyderabad Tourism Guide.
Answer only from the provided context.
Do not make up information.
"""

        prompt = ChatPromptTemplate.from_template(
            """
{system_prompt}

CONTEXT:
{context}

QUESTION:
{query}
"""
        )

        chain = prompt | self.llm | self.parser

        return chain.invoke(
            {
                "system_prompt": system_prompt,
                "context": context,
                "query": query
            }
        )