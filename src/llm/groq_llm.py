import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqLLM:
    def __init__(self):
        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def generate(self, *args, **kwargs):
        """
        Backwards-compatible generate.
        Usage patterns supported:
          - generate(prompt)
          - generate(context=..., query=..., system_prompt=...)

        If called with context/query/system_prompt, build a single prompt string and send it to Groq.
        """
        # If called as generate(prompt)
        if args and isinstance(args[0], str) and not kwargs:
            prompt = args[0]
        else:
            # Accept either explicit 'prompt' kw or build from context/query/system_prompt
            prompt = kwargs.get('prompt')
            if not prompt:
                system_prompt = kwargs.get('system_prompt', '') or ''
                context = kwargs.get('context', '') or ''
                query = kwargs.get('query', '') or ''

                # Compose the prompt in a conservative, explicit format
                parts = []
                if system_prompt:
                    parts.append(system_prompt.strip())
                if context:
                    parts.append("CONTEXT:\n" + context.strip())
                if query:
                    parts.append("QUESTION:\n" + query.strip())

                prompt = "\n\n".join(parts)

        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content
