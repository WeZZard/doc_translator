import argparse
import os
import pathlib

from typing import Optional

from book_maker.driver import DRIVER_TYPE_FOR_FILE_EXTENSION
from book_maker.translator import MODEL_DICT, Translator
from book_maker.utils import LANGUAGES, TO_LANGUAGE_CODE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-path",
        dest="input_path",
        type=str,
        help="path of the file to be translated",
    )
    parser.add_argument(
        "--output-path",
        dest="output_path",
        type=str,
        help="path of the translated document to output",
    )
    parser.add_argument(
        "--openai-key",
        dest="openai_key",
        type=str,
        default="",
        help="OpenAI api key,if you have more than one key, please use comma"
        " to split them to go beyond the rate limits",
    )
    parser.add_argument(
        "--test",
        dest="is_test",
        action="store_true",
        help="only the first 10 paragraphs will be translated, for testing",
    )
    parser.add_argument(
        "--test-count",
        dest="test_count",
        type=int,
        default=10,
        help="how many paragraphs will be translated for testing",
    )
    parser.add_argument(
        "-m",
        "--model",
        dest="model",
        type=str,
        default="chatgptapi",
        choices=["chatgptapi", "gpt3", "google"],  # support DeepL later
        metavar="MODEL",
        help="model to use, available: {%(choices)s}",
    )
    parser.add_argument(
        "--language",
        type=str,
        choices=sorted(LANGUAGES.keys())
        + sorted([k.title() for k in TO_LANGUAGE_CODE.keys()]),
        default="zh-hans",
        metavar="LANGUAGE",
        help="language to translate to, available: {%(choices)s}",
    )
    parser.add_argument(
        "--resume",
        dest="resume",
        action="store_true",
        help="if program stop unexpected you can use this to resume",
    )
    parser.add_argument(
        "-p",
        "--proxy",
        dest="proxy",
        type=str,
        default="",
        help="use proxy like http://127.0.0.1:7890",
    )
    # args to change api_url
    parser.add_argument(
        "--api-url",
        dest="api_url",
        type=str,
        help="specify API's url other than the OpenAI's official API address",
    )
    parser.add_argument(
        "--translate-tags",
        dest="translate_tags",
        type=str,
        default="p",
        help="example --translate-tags p,blockquote",
    )
    parser.add_argument(
        "--allow-navigable-strings",
        dest="allow_navigable_strings",
        action="store_true",
        default=False,
        help="allow NavigableStrings to be translated",
    )

    args = parser.parse_args()
    PROXY = args.proxy
    if PROXY != "":
        os.environ["http_proxy"] = PROXY
        os.environ["https_proxy"] = PROXY

    translate_model: Optional[Translator] = MODEL_DICT.get(args.model)
    assert translate_model is not None, "unsupported model"
    if args.model in ["gpt3", "chatgptapi"]:
        OPENAI_API_KEY = args.openai_key or os.environ.get("OPENAI_API_KEY")
        if not OPENAI_API_KEY:
            raise Exception(
                "OpenAI API key not provided, please google how to obtain it"
            )
    else:
        OPENAI_API_KEY = ""

    # this will return a tuple of root and extension
    input_path = pathlib.Path(args.input_path)
    output_path = pathlib.Path(args.output_path) if args.output_path is not None else None
    file_extension = input_path.suffix
    support_type_list = list(DRIVER_TYPE_FOR_FILE_EXTENSION.keys())
    if file_extension not in support_type_list:
        raise Exception(
            f"Supported file extension: {file_extension}, Now only support files of these formats: {','.join(support_type_list)}"
        )

    driver_type = DRIVER_TYPE_FOR_FILE_EXTENSION.get(file_extension)
    assert driver_type is not None, "unsupported type: {}".format(file_extension)

    language = args.language
    if args.language in LANGUAGES:
        # use the value for prompt
        language = LANGUAGES.get(language, language)

    user_info = driver_type.create_user_info(args)

    driver = driver_type(
        input_path,
        translate_model,
        OPENAI_API_KEY,
        args.resume,
        language=language,
        user_info=user_info,
        output_path=output_path,
        api_url=args.api_url,
        is_test=args.is_test,
        test_count=args.test_count,
    )

    driver.make()


if __name__ == "__main__":
    main()
