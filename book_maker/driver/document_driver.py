from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
from book_maker.translator import Translator

class DocumentDriver(ABC):
    """
    TODO: Extract DocumentDriver to DocumentLoader, TranslateWorker and DocumentGenerator.
    In the future:
    - DocumentLoader shall only load documents into translatable items.
    - TranslateWorker shall only receive translatable items.
    - DocumentGenerator shall generates new documents with translated items.
    """

    @staticmethod
    @abstractmethod
    def create_user_info(args) -> Dict[str, Any]:
        """
        Create user info from command line arguments.
        """
        pass

    @abstractmethod
    def __init__(
        self,
        input_path: Path,
        model_type: Translator,
        key: str,
        resume: bool,
        language: str,
        user_info: Dict[str, Any],
        output_path: Optional[Path]=None,
        api_url: Optional[str] = None,
        is_test: bool = False,
        test_num: int = 5,
    ):
        self.input_path: Path = input_path
        self.output_path: Optional[Path] = output_path
        self.translate_model: Translator = model_type(key, language, api_url)
        self.is_test: bool = is_test
        self.test_num: int = test_num
        self.resume: bool = resume

    @abstractmethod
    def load_state(self):
        pass
        
    @abstractmethod
    def make(self):
        """
        Do the driver's job.
        """
        pass
