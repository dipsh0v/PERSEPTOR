import re
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
from rich.table import Table

console = Console()

def print_yara_rules_pretty(yara_rules: str):
    """
    This function splits YARA rules by `rule` keyword to display each rule separately.
    Each rule will be shown in a panel for improved readability.
    """
    yara_rules_cleaned = yara_rules.strip()

    # Split rules using regex for YARA's 'rule' keyword
    rules = re.split(r'(?=rule\s)', yara_rules_cleaned)

    if not rules:
        rprint("[yellow]No YARA rules found.[/yellow]")
        return

    for i, rule_content in enumerate(rules, start=1):
        if rule_content.strip():
            panel_title = f"YARA Rule {i}"
            panel = Panel(
                rule_content.strip(),
                title=panel_title,
                subtitle="YARA Rule Syntax",
                expand=True
            )
            console.print(panel)
            console.rule()

def print_additional_sigma_rules_in_tables(rules_text: str):
    """
    Splits the 'Additional Sigma Rules' text by '---' (multi-doc YAML).
    Then prints each doc as a separate table row.
    Also removes any triple backticks like ```yaml ... ```
    """
    cleaned = rules_text.replace("```yaml", "").replace("```", "").strip()

    docs = [doc.strip() for doc in cleaned.split("---") if doc.strip()]

    if not docs:
        rprint("[yellow]No additional sigma rules found.[/yellow]")
        return

    for i, doc_content in enumerate(docs, start=1):
        table = Table(title=f"Additional Sigma Rule {i}")
        table.add_column("YAML Document", style="white")
        table.add_row(doc_content)
        console.print(table)
        console.rule()

def print_refined_sigma_in_tables(refined_text: str):
    """
    Takes the 'AI-Refined Sigma & Queries' text, removes lines like:
      - '# Rule 1 ...'
      - 'Refined Document X'
      - '2) Refined Splunk Queries' or '3) Refined QRadar Queries', etc.
      - lines with box-drawing characters (────────────────, etc.)
      - lines starting with '# This query searches...' to remove explanations
    Then splits by '---' and prints each chunk in a table.

    This helps avoid empty docs (like 'Refined Document 2' with no content)
    and merges multi-line blocks more cleanly, so final output is just
    queries + any refined Sigma text – no extra commentary lines.
    """
    step1 = re.sub(r"^.*Refined Document\s+\d+.*$", "", refined_text, flags=re.MULTILINE)

    step2 = re.sub(r"^# Rule.*$", "", step1, flags=re.MULTILINE)
    step2 = re.sub(r"^\s*\d\)\s*Refined.*$", "", step2, flags=re.MULTILINE)

    step3 = re.sub(r"^-{2,}\s*$", "", step2, flags=re.MULTILINE)
    step3 = re.sub(r"^--$", "", step3, flags=re.MULTILINE)

    step4 = re.sub(r"^[─━─]+.*$", "", step3, flags=re.MULTILINE)

    step5 = re.sub(r"^# This query.*$", "", step4, flags=re.MULTILINE)
    step5 = re.sub(r"^# The UTF8.*$", "", step5, flags=re.MULTILINE)
    step5 = re.sub(r"^# \s?.*$", "", step5, flags=re.MULTILINE)  

    cleaned_text = step5.strip()

    docs = [doc.strip() for doc in cleaned_text.split("---") if doc.strip()]

    if not docs:
        table = Table(title="Refined Sigma & Queries")
        table.add_column("Data", style="white")
        table.add_row(cleaned_text if cleaned_text else "No refined output found.")
        console.print(table)
        console.rule()
        return

    for i, doc_content in enumerate(docs, start=1):
        if doc_content.strip() in ("--", ""):
            continue

        table = Table(title=f"Refined Document {i}")
        table.add_column("Content", style="white")
        table.add_row(doc_content)
        console.print(table)
        console.rule()

def print_sigma_rules_pretty(sigma_yaml: str):
    """
    This function splits the multi-doc YAML output by '---' and prints each document
    in a visually separated style for improved readability.
    """
    docs = [doc.strip() for doc in sigma_yaml.split('---') if doc.strip()]

    for i, doc_content in enumerate(docs, start=1):
        panel_title = f"Sigma Rule {i}"
        panel = Panel(
            doc_content,
            title=panel_title,
            subtitle="Multi-Document YAML",
            expand=True
        )
        console.print(panel)
        console.rule()

def print_refined_text_pretty(refined_text: str):
    """
    Splits the refined text by '---' and prints each block in a separate Panel.
    This is similar to the print_sigma_rules_pretty approach but for the
    'AI-Refined Sigma & Queries' block that also uses '---' separators.
    """
    docs = [doc.strip() for doc in refined_text.split('---') if doc.strip()]
    for i, doc_content in enumerate(docs, start=1):
        panel_title = f"Refined Document {i}"
        panel = Panel(
            doc_content,
            title=panel_title,
            expand=True
        )
        console.print(panel)
        console.rule()

def print_colored(text: str, color: str = "white") -> None:
    """
    Prints text in a specified color.
    The 'color' parameter can be any Rich color name,
    e.g., 'red', 'green', 'cyan', 'yellow', 'bold magenta', etc.
    """
    rprint(f"[{color}]{text}[/{color}]")

def print_panel(text: str, title: str = "INFO") -> None:
    """
    Displays the given text within a Rich Panel.
    """
    panel = Panel.fit(text, title=title)
    console.print(panel)

def print_rule(title: str):
    """
    Draws a horizontal rule with a centered title.
    """
    console.rule(f"[bold cyan]{title}[/bold cyan]")

def print_table(rows: list[str], title: str = "Table"):
    """
    Displays the given rows as a table.
    """
    table = Table(title=title)
    table.add_column("Data", style="dim")
    for row in rows:
        table.add_row(row)
    console.print(table)

def print_analysis_summary(data: dict):
    """
    Displays key fields (sigma_title, sigma_description, confidence_level, notes)
    from the analysis JSON data in a simple table.
    """
    table = Table(title="Basic Analysis Info", show_lines=True)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value", style="white")

    sigma_title = data.get("sigma_title", "N/A")
    sigma_description = data.get("sigma_description", "N/A")
    confidence_level = data.get("confidence_level", "N/A")
    notes = data.get("notes", "N/A")

    table.add_row("Sigma Title", sigma_title)
    table.add_row("Description", sigma_description)
    table.add_row("Confidence", confidence_level)
    table.add_row("Notes", notes)

    console.print(table)

def print_iocs_table(iocs: dict):
    """
    Converts the 'indicators_of_compromise' dictionary to a table.
    Example: {"ips": [...], "domains": [...], ...}
    """
    table = Table(title="Indicators of Compromise", show_lines=True)
    table.add_column("IoC Type", style="bold magenta")
    table.add_column("Values", style="white")

    for ioc_type, values in iocs.items():
        if isinstance(values, list):
            values_str = "\n".join(values) if values else "N/A"
        else:
            values_str = str(values) if values else "N/A"
        table.add_row(ioc_type, values_str)

    console.print(table)

def print_ttps_table(ttps: list):
    """
    Displays the list of TTPs in a table.
    Expected format:
    [
      { "mitre_id": "T1106", "technique_name": "...", "description": "..." }, ...
    ]
    """
    if not ttps:
        rprint("[yellow]No TTPs found.[/yellow]")
        return

    table = Table(title="TTP Details", show_lines=True)
    table.add_column("MITRE ID", style="bold cyan")
    table.add_column("Technique Name", style="bold green")
    table.add_column("Description", style="white", overflow="fold")

    for item in ttps:
        mitre_id = item.get("mitre_id", "N/A")
        technique_name = item.get("technique_name", "N/A")
        description = item.get("description", "")
        table.add_row(mitre_id, technique_name, description)

    console.print(table)

def print_list_table(items: list, title: str):
    """
    Displays a simple list-based table (e.g., for threat actors, tools, etc.).
    """
    if not items:
        rprint(f"[yellow]No data for {title}[/yellow]")
        return

    table = Table(title=title, show_lines=True)
    table.add_column("Items", style="bold white")

    for i in items:
        table.add_row(str(i))

    console.print(table)

def display_analysis_data(analysis_data: dict):
    """
    Calls all table functions to display the JSON analysis data in parts.
    """
    console.rule("[bold cyan]AI JSON Analysis (Tabular)[/bold cyan]")

    print_analysis_summary(analysis_data)

    iocs = analysis_data.get("indicators_of_compromise", {})
    print_iocs_table(iocs)

    ttps = analysis_data.get("ttps", [])
    print_ttps_table(ttps)

    threat_actors = analysis_data.get("threat_actors", [])
    print_list_table(threat_actors, "Threat Actors")

    tools_or_malware = analysis_data.get("tools_or_malware", [])
    print_list_table(tools_or_malware, "Tools or Malware")
