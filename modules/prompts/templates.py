"""
PERSEPTOR v2.0 - Prompt Templates
Loads Chain-of-Thought (CoT) prompts and system prompts from text files.
"""

import os

_TXT_DIR = os.path.join(os.path.dirname(__file__), 'txt')


def _load_prompt(filename: str) -> str:
    path = os.path.join(_TXT_DIR, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""


class PromptTemplates:
    """Central repository for all PERSEPTOR prompt templates."""

    @property
    def THREAT_ANALYST_SYSTEM(self) -> str:
        return _load_prompt("threat_analyst_system.txt")

    @property
    def IOC_EXTRACTOR_SYSTEM(self) -> str:
        return _load_prompt("ioc_extractor_system.txt")

    @property
    def DETECTION_ENGINEER_SYSTEM(self) -> str:
        return _load_prompt("detection_engineer_system.txt")

    @property
    def SIEM_SPECIALIST_SYSTEM(self) -> str:
        return _load_prompt("siem_specialist_system.txt")

    @property
    def RULE_QA_SYSTEM(self) -> str:
        return _load_prompt("rule_qa_system.txt")

    @property
    def THREAT_SUMMARY_COT(self) -> str:
        return _load_prompt("threat_summary_cot.txt")

    @property
    def IOC_EXTRACTION_COT(self) -> str:
        return _load_prompt("ioc_extraction_cot.txt")

    @property
    def SIGMA_GENERATION_COT(self) -> str:
        return _load_prompt("sigma_generation_cot.txt")

    @property
    def SIEM_CONVERSION_COT(self) -> str:
        return _load_prompt("siem_conversion_cot.txt")

    @property
    def RULE_GENERATION_COT(self) -> str:
        return _load_prompt("rule_generation_cot.txt")

    @property
    def ATOMIC_TEST_ENGINEER_SYSTEM(self) -> str:
        return _load_prompt("atomic_test_engineer_system.txt")

    @property
    def ATOMIC_TEST_GENERATION_COT(self) -> str:
        return _load_prompt("atomic_test_generation_cot.txt")

    @property
    def YARA_GENERATION_COT(self) -> str:
        return _load_prompt("yara_generation_cot.txt")


# Global instance for easy access
PromptTemplates = PromptTemplates()
