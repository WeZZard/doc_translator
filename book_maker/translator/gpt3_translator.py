import requests
from rich import print

from .translator import Translator


class GPT3(Translator):
    def __init__(self, key, language, api_url=None):
        super().__init__(key, language)
        self.api_url = (
            f"{api_url}v1/completions"
            if api_url
            else "https://api.openai.com/v1/completions"
        )
        self.headers = {
            "Content-Type": "application/json",
        }
        # TODO support more models here
        self.data = {
            "prompt": "",
            "model": "text-davinci-003",
            "max_tokens": 1024,
            "temperature": 1,
            "top_p": 1,
        }
        self.session = requests.session()
        self.language = language

    def rotate_key(self):
        self.headers["Authorization"] = f"Bearer {next(self.keys)}"

    def translate(self, text):
        print(text)
        self.rotate_key()
        self.data["prompt"] = f"Please help me to translate，`{text}` to {self.language}"
        r = self.session.post(self.api_url, headers=self.headers, json=self.data)
        if not r.ok:
            return text
        t_text = r.json().get("choices")[0].get("text", "").strip()
        print(t_text)
        return t_text
