import hashlib
import math
import re

HASH_EMBEDDING_MODEL = "synthetic-hash-embedding"
HASH_EMBEDDING_VERSION = "v1"
TOKEN_PATTERN = re.compile(r"[a-z0-9]+")


def hash_embedding(text: str, dimension: int = 384) -> list[float]:
    """Create a deterministic local retrieval baseline; this is not a trained embedding."""

    vector = [0.0] * dimension
    for token in TOKEN_PATTERN.findall(text.casefold()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:4], "big") % dimension
        sign = 1.0 if digest[4] & 1 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector
