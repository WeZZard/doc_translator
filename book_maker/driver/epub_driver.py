import os
import pickle
import sys
from copy import copy
from pathlib import Path
from typing import Optional, Dict, Any

from bs4 import BeautifulSoup as bs
from ebooklib import ITEM_DOCUMENT, epub
from rich import print
from tqdm import tqdm

from book_maker.translator import Translator
from .document_driver import DocumentDriver


class EPUBBookDriver(DocumentDriver):

    @staticmethod
    def create_user_info(args) -> Dict[str, Any]:
        return {
            'translate_tags' : args.translate_tags,
            'allow_navigable_strings' : args.allow_navigable_strings
        }

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
        translate_tags: str = user_info[translate_tags]
        allow_navigable_strings: bool = user_info[allow_navigable_strings]
        self.translate_tags = translate_tags
        self.allow_navigable_strings = allow_navigable_strings
        self.new_epub = epub.EpubBook()
        try:
            self.origin_book = epub.read_epub(self.input_path.absolute)
        except Exception:
            # tricky for #71 if you don't know why please check the issue and ignore this
            # when upstream change will TODO fix this
            def _load_spine(self):
                spine = self.container.find(
                    "{%s}%s" % (epub.NAMESPACES["OPF"], "spine")
                )

                self.book.spine = [
                    (t.get("idref"), t.get("linear", "yes")) for t in spine
                ]
                self.book.set_direction(spine.get("page-progression-direction", None))

            epub.EpubReader._load_spine = _load_spine
            self.origin_book = epub.read_epub(self.input_path.absolute)

        self.p_to_save = []
        self.bin_path = f"{input_path.parent}/.{input_path.stem}.temp.bin"
        if resume:
            self.load_state()
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

    @staticmethod
    def _is_special_text(text):
        return text.isdigit() or text.isspace()

    def _make_new_book(self, book):
        new_book = epub.EpubBook()
        new_book.metadata = book.metadata
        new_book.spine = book.spine
        new_book.toc = book.toc
        return new_book

    def make(self):
        new_book = self._make_new_book(self.origin_book)
        all_items = list(self.origin_book.get_items())
        trans_taglist = self.translate_tags.split(",")
        all_p_length = sum(
            0
            if i.get_type() != ITEM_DOCUMENT
            else len(bs(i.content, "html.parser").findAll(trans_taglist))
            for i in all_items
        )
        all_p_length += self.allow_navigable_strings * sum(
            0
            if i.get_type() != ITEM_DOCUMENT
            else len(bs(i.content, "html.parser").findAll(text=True))
            for i in all_items
        )
        pbar = tqdm(total=self.test_count) if self.is_test else tqdm(total=all_p_length)
        index = 0
        p_to_save_len = len(self.p_to_save)
        try:
            for item in self.origin_book.get_items():
                if item.get_type() == ITEM_DOCUMENT:
                    soup = bs(item.content, "html.parser")
                    p_list = soup.findAll(trans_taglist)
                    if self.allow_navigable_strings:
                        p_list.extend(soup.findAll(text=True))
                    is_test_done = self.is_test and index > self.test_count
                    for p in p_list:
                        if is_test_done or not p.text or self._is_special_text(p.text):
                            continue
                        new_p = copy(p)
                        # TODO banch of p to translate then combine
                        # PR welcome here
                        if self.resume and index < p_to_save_len:
                            new_p.string = self.p_to_save[index]
                        else:
                            new_p.string = self.translate_model.translate(p.text)
                            self.p_to_save.append(new_p.text)
                        p.insert_after(new_p)
                        index += 1
                        if index % 20 == 0:
                            self._save_progress()
                        # pbar.update(delta) not pbar.update(index)?
                        pbar.update(1)
                        if self.is_test and index >= self.test_count:
                            break
                    item.content = soup.prettify().encode()
                new_book.add_item(item)
            name = self.input_path.stem
            output_path = self.output_path if self.output_path is not None else f"{name}_bilingual.epub"
            epub.write_epub(output_path, new_book, {})
            pbar.close()
        except (KeyboardInterrupt, Exception) as e:
            print(e)
            print("you can resume it next time")
            self._save_progress()
            self._save_temp_book()
            sys.exit(0)

    def load_state(self):
        try:
            with open(self.bin_path, "rb") as f:
                self.p_to_save = pickle.load(f)
        except Exception:
            raise Exception("can not load resume file")

    def _save_temp_book(self):
        origin_book_temp = epub.read_epub(self.input_path.absolute)
        new_temp_book = self._make_new_book(origin_book_temp)
        p_to_save_len = len(self.p_to_save)
        trans_taglist = self.translate_tags.split(",")
        index = 0
        try:
            for item in origin_book_temp.get_items():
                if item.get_type() == ITEM_DOCUMENT:
                    soup = bs(item.content, "html.parser")
                    p_list = soup.findAll(trans_taglist)
                    for p in p_list:
                        if not p.text or self._is_special_text(p.text):
                            continue
                        # TODO banch of p to translate then combine
                        # PR welcome here
                        if index < p_to_save_len:
                            new_p = copy(p)
                            new_p.string = self.p_to_save[index]
                            print(new_p.string)
                            p.insert_after(new_p)
                            index += 1
                        else:
                            break
                    # for save temp book
                    item.content = soup.prettify().encode()
                new_temp_book.add_item(item)
            name = self.input_path.stem
            epub.write_epub(f"{name}_bilingual_temp.epub", new_temp_book, {})
        except Exception as e:
            # TODO handle it
            print(e)

    def _save_progress(self):
        try:
            with open(self.bin_path, "wb") as f:
                pickle.dump(self.p_to_save, f)
        except Exception:
            raise Exception("can not save resume file")
