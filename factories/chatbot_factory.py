from agents.conversation_agent import ConversationAgent
from agents.intent_agent import IntentAgent
from agents.mathematical_agent import MathematicalAgent
from agents.writer_agent import WriterAgent
from clients.llm_client import LLMClient
from clients.ollama_client import OllamaClient
from clients.openai_client import OpenAIClient
from config.settings import Settings
from memory.session_memory import SessionMemory
from orchestration.orchestrator import ChatbotOrchestrator
from services.chatbot_service import ChatbotService
from tools.expression_tools import ExpressionTool
from utils.language_detector import LanguageDetector
from utils.math_parser import MathParser
from workflows.chatbot_workflow import ChatbotWorkflow


class ChatbotFactory:
    """Creates fully configured chatbot application dependencies.

    Attributes:
        settings: Application configuration used to select dependencies.
    """

    def __init__(
        self,
        settings: Settings,
    ) -> None:
        """Initialize the chatbot factory.

        Args:
            settings: Application configuration.
        """
        self.settings = settings

    def create_service(
        self,
        llm_client: LLMClient | None = None,
    ) -> ChatbotService:
        """Create a chatbot service with all required dependencies.

        Args:
            llm_client: Optional language model client override.

        Returns:
            Fully configured chatbot service.
        """
        resolved_llm_client = llm_client or self._create_llm_client()
        memory = SessionMemory()

        orchestrator = ChatbotOrchestrator(
            mathematical_agent=MathematicalAgent(),
            writer_agent=WriterAgent(),
            memory=memory,
        )

        workflow = ChatbotWorkflow(
            memory=memory,
            orchestrator=orchestrator,
            conversation_agent=ConversationAgent(
                llm_client=resolved_llm_client,
            ),
            intent_agent=IntentAgent(
                llm_client=resolved_llm_client,
            ),
            expression_tool=ExpressionTool(),
            parser=MathParser(),
            language_detector=LanguageDetector(),
        )

        return ChatbotService(
            workflow=workflow,
        )

    def _create_llm_client(
        self,
    ) -> LLMClient:
        if self.settings.llm_provider == "openai":
            return OpenAIClient()

        return OllamaClient()
