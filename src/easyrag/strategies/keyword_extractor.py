"""
Keyword Extraction Utility

Simple keyword extraction for improved search capabilities.
"""

import re

# Common stop words to filter out
STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "for", "from",
    "has", "have", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "will", "with", "what", "when", "where", "which", "who",
    "why", "how", "can", "could", "should", "would", "may", "might", "must",
    "shall", "do", "does", "did", "done", "this", "these", "those", "there",
    "their", "them", "they", "we", "you", "your", "our", "us", "am", "im",
    "me", "my", "i", "if", "so", "or", "but", "not", "no", "yes",
}


class KeywordExtractor:
    """Simple keyword extraction for search queries"""

    def __init__(self):
        self.stop_words = STOP_WORDS

    def extract_keywords(
        self, query: str, min_length: int = 2, max_keywords: int = 10
    ) -> list[str]:
        """
        Extract meaningful keywords from a search query.

        Args:
            query: The search query string
            min_length: Minimum keyword length (default: 2)
            max_keywords: Maximum number of keywords to return (default: 10)

        Returns:
            List of extracted keywords
        """
        # Convert to lowercase for processing
        query_lower = query.lower()

        # Extract potential keywords
        tokens = re.findall(r"[a-z0-9_-]+", query_lower)

        # Filter tokens
        keywords = []
        for token in tokens:
            if len(token) >= min_length and token not in self.stop_words:
                keywords.append(token)

        # Deduplicate while preserving order
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)

        return unique_keywords[:max_keywords]


# Global instance
keyword_extractor = KeywordExtractor()


def extract_keywords(query: str, min_length: int = 2, max_keywords: int = 10) -> list[str]:
    """
    Convenience function to extract keywords from a query.

    Args:
        query: The search query string
        min_length: Minimum keyword length
        max_keywords: Maximum number of keywords to return

    Returns:
        List of extracted keywords
    """
    return keyword_extractor.extract_keywords(query, min_length, max_keywords)
