from src.llm.groq_llm import GroqLLM

llm = GroqLLM()

print(
    llm.generate(
        "Tell me about Hyderabad in 3 lines."
    )
)