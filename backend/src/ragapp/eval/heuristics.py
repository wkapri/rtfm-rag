import re

from ragapp.models import Chunk, Document

# Substrings that indicate the model declined to answer rather than guessing.
# Checked against a lowercased answer, so case doesn't matter.
REFUSAL_PHRASES = [
    "don't know",
    "do not know",
    "doesn't contain",
    "does not contain",
    "no information",
    "cannot find",
    "can't find",
    "not mentioned",
    "not covered",
    "isn't covered",
    "not in the manual",
    "not present in the provided",
    "i don't have",
    "i do not have",
    "unable to find",
]

_CITED_WITH_FILENAME_RE = re.compile(
    r"([\w\-. ]+\.pdf)\s*,?\s*page\s*(\d+)", re.IGNORECASE
)
_BARE_PAGE_RE = re.compile(r"\bpage\s*(\d+)\b", re.IGNORECASE)


def is_refusal(answer: str) -> bool:
    lowered = answer.lower()
    return any(phrase in lowered for phrase in REFUSAL_PHRASES)


def extract_citations(answer: str, retrieved: list[tuple[Chunk, Document]]) -> list[dict]:
    """Best-effort parse of (filename, page) citations out of free-text answer.

    Explicit "<filename>.pdf, page N" mentions are always trusted. Bare
    "page N" mentions are attributed to a document only when every retrieved
    chunk came from a single document (the common case for now) — otherwise
    they're ambiguous and dropped rather than guessed.
    """
    found: dict[tuple[str, int], dict] = {}

    for filename, page in _CITED_WITH_FILENAME_RE.findall(answer):
        key = (filename.strip(), int(page))
        found[key] = {"filename": key[0], "page": key[1]}

    distinct_filenames = {doc.filename for _, doc in retrieved}
    if len(distinct_filenames) == 1:
        only_filename = next(iter(distinct_filenames))
        for page in _BARE_PAGE_RE.findall(answer):
            key = (only_filename, int(page))
            found.setdefault(key, {"filename": key[0], "page": key[1]})

    return list(found.values())
