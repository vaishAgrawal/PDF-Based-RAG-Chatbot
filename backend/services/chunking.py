"""Text chunking helpers."""


def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150) -> list[str]:
	"""Split text into overlapping word-based chunks."""
	if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
		raise ValueError("chunk_size must be positive and overlap must be smaller than chunk_size")

	words = text.split()
	chunks = []
	step = chunk_size - overlap
	for start in range(0, len(words), step):
		chunk = " ".join(words[start : start + chunk_size]).strip()
		if chunk:
			chunks.append(chunk)
		if start + chunk_size >= len(words):
			break
	return chunks
