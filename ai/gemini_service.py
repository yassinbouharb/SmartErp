from __future__ import annotations

import logging

from dotenv import load_dotenv
from google import genai


log = logging.getLogger(__name__)

load_dotenv()
class GeminiService:


    def __init__(
        self,
        model="gemini-3.5-flash-lite"
    ):

        self.model = model

        self.client = genai.Client()



    def chat(
        self,
        messages,
        tools=None,
        system_instruction=None
    ):

        try:

            # Si on reçoit un texte simple
            if isinstance(messages, str):

                prompt = messages


            # Si on reçoit une liste de messages
            elif isinstance(messages, list):

                prompt = "\n".join(
                    [
                        msg["text"]
                        for msg in messages
                    ]
                )


            else:

                raise ValueError(
                    "Format message non supporté"
                )


            response = self.client.models.generate_content(

                model=self.model,

                contents=prompt,

                config={

                    "system_instruction":
                        system_instruction,

                    "tools":
                        tools
                }
            )


            return response


        except Exception as e:

            log.error(
                "Gemini error : %s",
                e
            )

            raise