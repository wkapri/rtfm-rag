from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class EvalQuestion:
    question: str
    document: str
    relevant_pages: list[int]


def load_dataset(path: Path) -> list[EvalQuestion]:
    raw = yaml.safe_load(path.read_text()) or []
    return [
        EvalQuestion(
            question=item["question"],
            document=item["document"],
            relevant_pages=item["relevant_pages"],
        )
        for item in raw
    ]
