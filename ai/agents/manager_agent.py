from __future__ import annotations

import logging

from ai.prompts.manager_prompt import MANAGER_PROMPT

log = logging.getLogger(__name__)


class ManagerAgent:

    def __init__(
        self,
        gemini_service,
        invoice_agent,
        product_agent,
        BL_agent,
        client_agent,
        problem_solver_agent=None,
    ):
        self.BL_agent = BL_agent
        self.gemini = gemini_service

        self.invoice_agent = invoice_agent
        self.product_agent = product_agent

        self.client_agent = client_agent
        self.problem_solver_agent = problem_solver_agent

    def run(
        self,
        message,
        context
    ):
        catalogue = context.catalogue
        history = context.history

        agent_name = self.detect_intent(message)

        log.info(
            "Agent choisi : %s",
            agent_name
        )

        # =========================================================
        # FACTURE (création + lecture + modification + suppression)
        # =========================================================
        if agent_name == "invoice":
            client_data = self.client_agent.getclient(message)
            return self.invoice_agent.run(
                message=message,
                catalogue=catalogue,
                client=client_data,
                history=history
            )

        # =========================================================
        # BL (création + lecture + modification + suppression)
        # =========================================================
        elif agent_name == "bl":
            if self.BL_agent:
                return self.BL_agent.run(
                    message=message,
                    catalogue=catalogue,
                    history=history
                )

        # =========================================================
        # PRODUIT
        # =========================================================
        elif agent_name == "product":
            if self.product_agent:
                return self.product_agent.run(
                    message=message,
                    history=history
                )

        # =========================================================
        # CLIENT
        # =========================================================
        elif agent_name == "client":
            if self.client_agent:
                return self.client_agent.run(
                    message=message,
                    history=history
                )

        # =========================================================
        # PROBLEM SOLVER
        # =========================================================
        elif agent_name == "unknown":
            if self.problem_solver_agent:
                return self.problem_solver_agent.run(
                    message=message,
                    history=history
                )

        return {
            "message": "Je n'ai pas compris votre demande."
        }

    def detect_intent(
        self,
        message
    ):
        prompt = f"""
{MANAGER_PROMPT}

Message utilisateur:

{message}
"""

        response = self.gemini.chat(prompt)
        return response.text.strip().lower()
