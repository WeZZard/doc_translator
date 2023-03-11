from pathlib import Path
from typing import Optional, Dict, Any, List

import sys

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
        test_count: int = 5,
    ):
        self.translated_lines: List[str] = list()
        name = input_path.stem
        suffix = input_path.suffix
        self.resume_file_path = f"{name}_translated.{suffix}.resume"
        self.temp_file_path = f"{name}_translated_temp.{suffix}"
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
            test_count=test_count,
        )
        if resume:
            self.load_state()

    def load_state(self):
        with open(self.resume, "r") as resume_file:
            self.translated_lines = resume_file.readlines()

    def make(self):
        with open(self.input_path, "r") as input_file:
            lines = input_file.readlines()
            try:
                iteration_count = 0
                for each_line in lines:
                    t = self.translate_model.translate(each_line)
                    self.translated_lines.append(t)
                    iteration_count += 1
                    if iteration_count % 20 == 0:
                        self._save_progress()
                    if self.is_test and iteration_count >= self.test_count:
                        break
                name = self.input_path.stem
                suffix = self.input_path.suffix
                output_path = self.output_path if self.output_path is not None else f"{name}_translated.{suffix}"
                with open(output_path, 'w') as output_file:
                    output_file.writelines(self.translated_lines)
            except (KeyboardInterrupt, Exception) as e:
                print(e)
                print("You can resume it at the next time.")
                self._save_progress()
                self._save_translated_contents()
                sys.exit(0)

    def _save_progress(self):
        try:
            with open(self.resume_file_path, 'w') as resume_file:
                resume_file.writelines(self.translated_lines)
        except Exception:
            raise Exception("can not save resume file")

    def _save_translated_contents(self):
        with open(self.temp_file_path, 'w') as temp_file:
            temp_file.writelines(self.translated_lines)
