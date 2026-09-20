"""Retrieval-augmented answer generation."""

import os
import re

from groq import APIStatusError, Groq


class RAGPipeline:
    def __init__(self, store) -> None:
        self.store = store
        api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=api_key) if api_key else None

    def answer(
        self,
        question: str,
        document_id: str | None,
        history: list[dict[str, str]] | None = None,
    ) -> dict:
        if not document_id:
            return {
                "answer": "Upload a PDF in this conversation before asking a question.",
                "sources": [],
            }
        contexts = list(dict.fromkeys(self.store.search(question, document_id)))
        if not contexts:
            return {"answer": "No documents have been indexed yet.", "sources": []}

        context = "\n\n---\n\n".join(contexts)
        if not self.client:
            return self._fallback(question, contexts)

        conversation = [
            {"role": message["role"], "content": message["content"]}
            for message in (history or [])[-10:]
            if message.get("role") in {"user", "assistant"} and message.get("content")
        ]
        try:
            response = self.client.chat.completions.create(
                model="qwen/qwen3.8-27b",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You answer questions about the active document. Use only the supplied document context "
                            "and conversation history. Answer directly and concisely, preserve names and numbers "
                            "exactly, do not repeat the context, and say 'Not found in the document.' when the "
                            "answer is absent."
                        ),
                    },
                    *conversation,
                    {"role": "user", "content": f"Document context:\n{context}\n\nQuestion: {question}"},
                ],
            )
        except APIStatusError:
            return self._fallback(question, contexts)
        return {"answer": response.choices[0].message.content, "sources": contexts}

    @staticmethod
    def _fallback(question: str, sources: list[str]) -> dict:
        """Return short relevant excerpts when answer generation is unavailable."""
        stop_words = {"what", "which", "where", "when", "who", "is", "the", "a", "an", "of", "in", "on", "to", "does", "do"}
        terms = [term for term in re.findall(r"[a-z0-9]+", question.lower()) if term not in stop_words]
        excerpts = []
        for source in sources:
            sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", source) if part.strip()]
            matches = [sentence for sentence in sentences if any(term in sentence.lower() for term in terms)]
            if matches:
                for match in matches[:2]:
                    words = match.split()
                    if len(words) > 12:
                        match_terms = [index for index, word in enumerate(words) if any(term in word.lower() for term in terms)]
                        if match_terms:
                            index = match_terms[0]
                            match = " ".join(words[max(0, index - 1) : index + 6])
                    excerpts.append(match)
            elif not excerpts:
                excerpts.append(" ".join(source.split()[:40]))
        unique_excerpts = list(dict.fromkeys(excerpts))
        answer = "\n\n".join(unique_excerpts[:3])
        return {"answer": answer, "sources": unique_excerpts[:3]}
