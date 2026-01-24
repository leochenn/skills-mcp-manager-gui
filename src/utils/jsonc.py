import json
import re


def load_jsonc(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|\"(?:\\.|[^\\\"])*\""
    regex = re.compile(pattern, re.DOTALL | re.MULTILINE)

    def replacer(match):
        s = match.group(0)
        if s.startswith("/"):
            return ""
        return s

    json_str = regex.sub(replacer, content)
    return json.loads(json_str)

