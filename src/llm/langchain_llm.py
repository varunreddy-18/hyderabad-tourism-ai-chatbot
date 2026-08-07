import logging
import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

logger = logging.getLogger(__name__)


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

        prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "CONTEXT:\n{context}\n\nQUESTION:\n{query}")
        ])

        chain = prompt | self.llm | self.parser

        payload = {
            "system_prompt": system_prompt,
            "context": context or "",
            "query": query or ""
        }

        logger.debug(
            "Invoking LLM with context length=%s",
            len(payload["context"])
        )

        return chain.invoke(payload)