import logging
from algorithms.data_processor import GeminiProcessor
from algorithms.prompts import translation, sentences, bcg_consultant
from algorithms.data_processor import TranslationEntry

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self, api_key: str, model_name: str = 'gemini-2.0-flash-exp'):
        self.processor = GeminiProcessor(api_key=api_key, model_name=model_name)

    def process_translation(self, entry: TranslationEntry) -> TranslationEntry:
        try:
            if entry.french:
                result = TranslationEntry(
                    english=self.processor.traduction_vocabulary(translation, entry.french),
                    french=entry.french,
                    context=self.processor.traduction_vocabulary(sentences, entry.french),
                    notes=""
                )
            elif entry.english:
                result = TranslationEntry(
                    english=entry.english,
                    french=self.processor.traduction_vocabulary(translation, entry.english),
                    context=self.processor.traduction_vocabulary(sentences, entry.english),
                    notes=""
                )
            else:
                raise ValueError("Entry must contain English or French")
            return result
        except Exception as e:
            logger.error(f"Error processing translation: {e}")
            raise

    def process_consulting(self, input_text: str) -> str:
        try:
            processed_text = self.processor.traduction_vocabulary(bcg_consultant, input_text)
            return processed_text
        except Exception as e:
            logger.error(f"Error processing consulting text: {e}")
            raise
