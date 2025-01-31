import logging
import google.generativeai as genai
from typing import Optional, Dict, Any
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TranslationEntry:
    english: str
    french: str
    context: str
    notes: str = ""
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, str]:
        return {
            "english": self.english if self.english else "",
            "french": self.french if self.french else "",
            "context": self.context if self.context else "",
            "notes": self.notes if self.notes else "",
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict[str, str]) -> 'TranslationEntry':
        return TranslationEntry(
            english=data.get("english", ""),
            french=data.get("french", ""),
            context=data.get("context", ""),
            notes=data.get("notes", ""),
            timestamp=data.get("timestamp", 0.0)
        )

class GeminiProcessor:
    """
    A class to handle interactions with Google's Gemini AI model.
    """

    def __init__(self, api_key: str, model_name: str = 'gemini-2.0-flash-exp'):
        """
        Initialize the GeminiProcessor with API key and model settings.

        Args:
            api_key (str): Google API key for authentication
            model_name (str): Name of the Gemini model to use
        """
        self.api_key = api_key
        self.model_name = model_name
        self._configure_api()
        self.model = self._initialize_model()
        logger.info(f"GeminiProcessor initialized with model: {model_name}")

    def _configure_api(self) -> None:
        """Configure the Gemini API with the provided key."""
        try:
            genai.configure(api_key=self.api_key)
            logger.debug("API configuration successful")
        except Exception as e:
            logger.error(f"Failed to configure API: {str(e)}")
            raise

    def _initialize_model(self) -> Any:
        """Initialize and return the Gemini model."""
        try:
            model = genai.GenerativeModel(self.model_name)
            logger.debug("Model initialization successful")
            return model
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise

    def validate_input(self, query: str) -> bool:
        """
        Validate the input query.

        Args:
            query (str): The input query to validate

        Returns:
            bool: True if input is valid

        Raises:
            ValueError: If input validation fails
        """
        if not isinstance(query, str):
            logger.error(f"Invalid input type: {type(query)}")
            raise ValueError("Query must be a string")

        if not query.strip():
            logger.error("Empty query provided")
            raise ValueError("Query cannot be empty")

        logger.debug("Input validation successful")
        return True

    def traduction_vocabulary(
        self,
        prompts: str,
        query: str,
        max_tokens: int = 8192,
        temperature: float = 0,
        top_p: float = 0.95
    ) -> str:
        """
        Process a query using the Gemini model.

        Args:
            query (str): The input query to process
            max_tokens (int): Maximum number of tokens in the response
            temperature (float): Temperature parameter for generation
            top_p (float): Top p parameter for generation

        Returns:
            str: The generated response text
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")
            self.validate_input(query)

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )

            logger.debug(f"Generation config: {generation_config}")

            query_gem = f"{prompts}. Here is the word or sentence: ### {query} ###"

            response = self.model.generate_content(
                query_gem,
                generation_config=generation_config
            )

            logger.info("Query processed successfully")
            return response.text

        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise
