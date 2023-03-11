from pathlib import Path
from typing import Optional, Dict, Any

from book_maker.translator import Translator
from .document_driver import DocumentDriver

class TXTDriver(DocumentDriver):
    
    @staticmethod
    def create_user_info(args) -> Dict[str, Any]:
        return {}

    def __init__(
        self,
        input_path: Path,
        model_type: Translator,
        key: str,
        resume: bool,
        language: str,
        user_info: Dict[str, Any],
        output_path: Optional[Path] = None,
        api_url: Optional[str] = None,
        is_test: bool = False,
        test_num: int = 5,
    ):
        super().__init__(
            input_path,
            model_type,
            key,
            resume,
            language,
            user_info,
            output_path=output_path,
            api_url=api_url,
            is_test=is_test, 
            test_num=test_num,
        )

    def load_state(self):
        pass

    def make(self):
        pass
