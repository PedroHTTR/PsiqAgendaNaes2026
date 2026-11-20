import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai


class GeminiClient:
    """Inicializa um cliente Gemini usando a chave configurada no ambiente."""

    def __init__(self) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        load_dotenv(base_dir / ".env")

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "A variável de ambiente GEMINI_API_KEY não está configurada."
            )

        self.client = genai.Client(api_key=api_key)

    def create_chat(self, model: str | None = None):
        """Cria uma sessão de chat; o SDK mantém o histórico dos turnos."""
        selected_model = model or os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        )
        return self.client.chats.create(model=selected_model)

    def send_message(self, chat, message: str) -> str:
        """Envia uma mensagem à sessão e retorna apenas o texto gerado."""
        response = chat.send_message(message)
        return response.text
