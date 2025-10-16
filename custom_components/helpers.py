import re


def _normalize_version(version: str) -> list[int]:
    version: str = re.sub(r"[^0-9a-zA-Z]+", ".", version)
    parts: list[str] = re.findall(r"\d+|[a-zA-Z]+", version)
    normalize: list[int] = []

    for part in parts:
        if part.isdigit():
            normalize.append(int(part))
        else:
            normalize.append(ord(part.lower()[0]) - 96)

    return normalize


def compare_versions(v1: str, v2: str) -> int:
    return (_normalize_version(v1) > _normalize_version(v2)) - (_normalize_version(v1) < _normalize_version(v2))
