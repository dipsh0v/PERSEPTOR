import os
import yaml
import concurrent.futures
from rich.table import Table
from rich.console import Console
import re

console = Console()

try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader

import os

# Use environment variable for SigmaHQ base URL
SIGMAHQ_BASE_URL = os.environ.get('SIGMAHQ_BASE_URL', 'https://github.com/SigmaHQ/sigma/blob/master')

def load_yaml_file(file_path: str, root_directory: str) -> list:
    """
    Reads a single YAML file and returns all its documents along with the file path 
    and its relative path.
    """
    relative_path = os.path.relpath(file_path, root_directory)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                docs = list(yaml.load_all(f, Loader=Loader))
            except yaml.YAMLError as e:
                console.print(f"[yellow][!] YAML syntax error in {file_path}: {str(e)}[/yellow]")
                return []
        rules = []
        for doc in docs:
            if isinstance(doc, dict):
                rules.append({
                    "file_path": file_path,
                    "relative_path": relative_path,
                    "rule_data": doc
                })
        return rules
    except Exception as e:
        console.print(f"[red][!] Failed to load: {file_path}, error: {e}[/red]")
        return []

def load_sigma_rules_local(root_directory: str) -> list:
    """
    root_directory: The root directory containing the Sigma rules 
    (e.g., "/Users/<your_username>/Desktop/SigmaHQ - Process Creation")
    
    Returns: A list containing each rule along with its file information.
    File reading is performed in parallel using a thread pool.
    """
    sigma_rules = []
    file_paths = []
    total_files = 0
    loaded_files = 0
    error_files = 0
    
    console.print(f"[cyan]Scanning directory: {root_directory}[/cyan]")
    
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith((".yml", ".yaml")):
                total_files += 1
                file_paths.append(os.path.join(subdir, file))
    
    console.print(f"[green]Found {total_files} YAML files[/green]")
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(load_yaml_file, fp, root_directory) for fp in file_paths]
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if result:
                    sigma_rules.extend(result)
                    loaded_files += 1
                else:
                    error_files += 1
            except Exception as e:
                console.print(f"[red]Error processing file: {e}[/red]")
                error_files += 1
    
    console.print(f"[green]Successfully loaded {loaded_files} files[/green]")
    if error_files > 0:
        console.print(f"[yellow]Failed to load {error_files} files[/yellow]")
    
    return sigma_rules

def build_github_link(root_directory: str, rule_info: dict, sigma_repo_path: str = "rules/windows/process_creation") -> str:
    relative_path = rule_info["relative_path"].replace("\\", "/")
    return f"{SIGMAHQ_BASE_URL}/{sigma_repo_path}/{relative_path}"

def get_stopwords():
    try:
        from nltk.corpus import stopwords
        nltk_stopwords = set(stopwords.words("english"))
    except Exception as e:
        nltk_stopwords = set()
    custom_stopwords = {
        "of", "c:", "and", "the", "a", "an", "to", "in", "for", "by", "on", "with", "or", "if", "is", "at", "as", "all", "windows", "microsoft"
    }
    return nltk_stopwords.union(custom_stopwords)

STOPWORDS = get_stopwords()

def extract_detection_keywords(detection_data) -> list:
    """
    Extracts tokens from the detection section of a Sigma rule.
    If detection_data is a dict and contains the "selection" key,
    token extraction is performed only on detection_data["selection"].
    Tokens are substrings containing letters, numbers, dashes, dots, colons, and semicolons.
    Tokens present in the STOPWORDS list or those with a single character are excluded.
    """
    if isinstance(detection_data, dict) and "selection" in detection_data:
        detection_data = detection_data["selection"]

    keywords = []

    def recurse_detection(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(k, str):
                    tokens = re.findall(r"[A-Za-z0-9\-\.:;]+", k)
                    for token in tokens:
                        token_lower = token.lower()
                        if token_lower not in STOPWORDS and len(token_lower) > 1:
                            keywords.append(token)
                if isinstance(v, str):
                    if " " in v.strip():
                        keywords.append(v.strip())
                    else:
                        tokens = re.findall(r"[A-Za-z0-9\-\.:;]+", v)
                        for token in tokens:
                            token_lower = token.lower()
                            if token_lower not in STOPWORDS and len(token_lower) > 1:
                                keywords.append(token)
                else:
                    recurse_detection(v)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, str):
                    if " " in item.strip():
                        keywords.append(item.strip())
                    else:
                        tokens = re.findall(r"[A-Za-z0-9\-\.:;]+", item)
                        for token in tokens:
                            token_lower = token.lower()
                            if token_lower not in STOPWORDS and len(token_lower) > 1:
                                keywords.append(token)
                else:
                    recurse_detection(item)
        elif isinstance(obj, str):
            tokens = re.findall(r"[A-Za-z0-9\-\.:;]+", obj)
            for token in tokens:
                token_lower = token.lower()
                if token_lower not in STOPWORDS and len(token_lower) > 1:
                    keywords.append(token)
    recurse_detection(detection_data)
    return list(set(keywords))

def gather_report_keywords(analysis_data: dict) -> set:
    """
    Extracts tokens from the IoC and TTP fields within analysis_data,
    filters out those present in the stopword list, and returns all tokens 
    as a lower-case set.
    This includes extracting meaningful tokens from fields like "malicious_commands."
    """
    keywords = set()
    iocs = analysis_data.get("indicators_of_compromise", {})
    for key, value in iocs.items():
        if isinstance(value, list):
            for item in value:
                tokens = re.findall(r"[A-Za-z0-9\-\.:;]+", str(item))
                for token in tokens:
                    token_lower = token.lower()
                    if token_lower not in STOPWORDS and len(token_lower) > 1:
                        keywords.add(token_lower)
        elif isinstance(value, str):
            tokens = re.findall(r"[A-Za-z0-9\-\.:;]+", value)
            for token in tokens:
                token_lower = token.lower()
                if token_lower not in STOPWORDS and len(token_lower) > 1:
                    keywords.add(token_lower)
    ttps = analysis_data.get("ttps", [])
    for ttp in ttps:
        for val in ttp.values():
            tokens = re.findall(r"[A-Za-z0-9\-\.:;]+", str(val))
            for token in tokens:
                token_lower = token.lower()
                if token_lower not in STOPWORDS and len(token_lower) > 1:
                    keywords.add(token_lower)
    return keywords

def compute_match_ratio_and_hits(detection_keywords: list, report_keywords: set, report_text: str) -> (float, list):
    """
    Computes the match ratio between detection keywords and report keywords.
    For multi-word detection keywords, it performs substring matching on report_text.
    For single-word keywords, it checks if they exist in the report_keywords set.
    
    Returns:
      - match ratio (float): between 0.0 and 1.0.
      - matched: List of matching keywords.
    """
    if not detection_keywords:
        return 0.0, []
    matched = set()
    for kw in detection_keywords:
        kw_lower = kw.lower()
        if " " in kw_lower:
            if kw_lower in report_text:
                matched.add(kw_lower)
        else:
            if kw_lower in report_keywords:
                matched.add(kw_lower)
    ratio = len(matched) / len(detection_keywords)
    return ratio, list(matched)

def match_sigma_rules_with_report(
    sigma_rules: list,
    analysis_data: dict,
    report_text: str,
    root_directory: str,
    sigma_repo_path: str = "sigma/rules/windows/process_creation",
    threshold: float = 0.0
) -> list:
    """
    sigma_rules: List of rules loaded via load_sigma_rules_local().
    analysis_data: Dynamically produced report data.
    report_text: The original text (lowercase) used in analysis (for substring matching).
    root_directory: The local directory containing Sigma rules.
    sigma_repo_path: The corresponding path on GitHub.
    threshold: Match ratio threshold (between 0.0 and 1.0); only rules exceeding this value will be displayed.
    
    Returns: List of dictionaries containing match information
    """
    report_keywords = gather_report_keywords(analysis_data)
    results = []

    for rule_info in sigma_rules:
        rule_data = rule_info["rule_data"]
        title = rule_data.get("title", "Untitled Sigma Rule")
        detection_data = rule_data.get("detection", {})
        detection_keywords = extract_detection_keywords(detection_data)
        ratio, matched = compute_match_ratio_and_hits(detection_keywords, report_keywords, report_text)
        
        if ratio < 0.10 and len(matched) == 1:
            continue
        if len(matched) < 2:
            continue
        if ratio > threshold:
            github_link = build_github_link(root_directory, rule_info, sigma_repo_path)
            results.append({
                "id": rule_data.get("id", "unknown"),
                "title": title,
                "description": rule_data.get("description", ""),
                "level": rule_data.get("level", "medium"),
                "match_ratio": round(ratio * 100, 2),
                "matched_keywords": list(matched) if isinstance(matched, (list, set)) else [],
                "tags": rule_data.get("tags", []),
                "github_link": github_link
            })
    
    return sorted(results, key=lambda x: x["match_ratio"], reverse=True)


