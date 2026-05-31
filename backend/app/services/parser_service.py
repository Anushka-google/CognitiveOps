from pathlib import Path


def parse_txt(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()

    return text