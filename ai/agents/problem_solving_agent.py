from ai.prompts.problem_solving_prompt import PROBLEM_SOLVING_PROMPT


class ProblemSolverAgent:

    def __init__(self, gemini_service):
        self.gemini = gemini_service

    def run(self, message, history=None):

        prompt = f"""
{PROBLEM_SOLVING_PROMPT}

Historique de la conversation :
{history}

Dernier message utilisateur :
{message}
"""

        response = self.gemini.chat(prompt)

        return {
            "type": "clarification",
            "response": response.text
        }