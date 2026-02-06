"""
Client per l'interazione con modelli OpenAI (chat completions).
Permette di generare risposte LLM a partire da prompt di sistema e utente.
"""

from openai import OpenAI
from dotenv import load_dotenv
import os   

load_dotenv()

class OpenAIClient:
    """
    Wrapper semplice per la generazione di completions tramite OpenAI API.
    """
    def __init__(self, model: str = "gpt-4.1-mini"):
        """
        Inizializza il client OpenAI con il modello specificato.

        Args:
            model (str, optional): Nome del modello OpenAI da usare. Default "gpt-4.1-mini".
        """
        self.client = OpenAI()
        self.model = model

    def generate(self, system_prompt: str, user_prompt: str, expect_json: bool = False) -> str:
        """
        Genera una risposta dal modello OpenAI dato un prompt di sistema e uno utente.

        Args:
            system_prompt (str): Prompt di contesto per il sistema.
            user_prompt (str): Prompt dell'utente.

        Returns:
            str: Risposta generata dal modello.
        """
        kwargs = {}

        if expect_json:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            **kwargs
        )
        return response.choices[0].message.content
