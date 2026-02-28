"""
PERSEPTOR v2.0 - Few-Shot Examples
Loads few-shot examples for CoT prompting from text files.
"""

import os

_TXT_DIR = os.path.join(os.path.dirname(__file__), 'txt')


def _load_prompt(filename: str) -> str:
    path = os.path.join(_TXT_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


class FewShotExamples:
    """Few-shot examples for CoT prompts."""

    @property
    def IOC_EXTRACTION_EXAMPLE(self) -> str:
        return _load_prompt("ioc_extraction_example.txt")

    @property
    def SIGMA_RULE_EXAMPLE(self) -> str:
        return _load_prompt("sigma_rule_example.txt")

    @property
    def SIEM_QUERY_EXAMPLE(self) -> str:
        return _load_prompt("siem_query_example.txt")

    @property
    def ATOMIC_TEST_EXAMPLE(self) -> str:
        return _load_prompt("atomic_test_example.txt")


# Global instance for easy access
FewShotExamples = FewShotExamples()
