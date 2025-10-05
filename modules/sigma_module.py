import yaml
from sigma.collection import SigmaCollection
from sigma.rule import SigmaRule
from sigma.conditions import ConditionFieldEqualsValueExpression
import uuid

def render_condition(cond) -> str:
    if cond is None:
        return "condition: none"
    if isinstance(cond, ConditionFieldEqualsValueExpression):
        return f"{cond.field} == {cond.value}"
    return repr(cond)

def sigma_collection_to_sigma_yaml(collection: SigmaCollection) -> str:
    all_docs = []
    for rule in collection.rules:
        if not isinstance(rule, SigmaRule):
            continue

        doc = {}
        doc["title"] = rule.title or "Untitled Sigma Rule"
        doc["id"] = str(rule.id) if rule.id else "no-id"
        doc["status"] = rule.status
        doc["description"] = rule.description
        doc["references"] = rule.references
        doc["tags"] = rule.tags
        doc["author"] = rule.author
        doc["logsource"] = rule.logsource
        doc["detection"] = render_condition(rule.detection)
        doc["fields"] = rule.fields
        doc["falsepositives"] = rule.falsepositives
        doc["level"] = rule.level

        all_docs.append(doc)

    yaml_str = yaml.dump_all(all_docs, sort_keys=False)
    return yaml_str

def generate_sigma_rules_for_commands(malicious_cmds, gpt_title, gpt_description, article_url) -> SigmaCollection:
    rules = []
    if not malicious_cmds:
        rule = SigmaRule(
            title=gpt_title if gpt_title else "No malicious commands found",
            id=uuid.uuid4(),
            status="experimental",
            description=gpt_description if gpt_description else "No malicious commands in AI analysis",
            references=[article_url],
            tags=["attack.execution"],
            author="Aytek AYTEMUR",
            logsource={"category":"process_creation","product":"windows"},
            detection=None,
            fields=["CommandLine","ParentCommandLine"],
            level="low",
            falsepositives=[]
        )
        rules.append(rule)
    else:
        for cmd in malicious_cmds:
            expr = ConditionFieldEqualsValueExpression(field="CommandLine", value=cmd)
            rule = SigmaRule(
                title=gpt_title if gpt_title else f"Suspicious Command: {cmd}",
                id=uuid.uuid4(),
                status="experimental",
                description=gpt_description if gpt_description else f"Detects usage of {cmd} in CommandLine",
                references=[article_url],
                tags=["attack.execution"],
                author="Aytek AYTEMUR",
                logsource={"category":"process_creation","product":"windows"},
                detection=expr,
                fields=["CommandLine","ParentCommandLine"],
                level="high",
                falsepositives=[]
            )
            rules.append(rule)
    return SigmaCollection(rules)

def generate_splunk_and_qradar_queries(analysis_data: dict):
    splunk_queries = []
    qradar_queries = []

    iocs = analysis_data.get("indicators_of_compromise", {})
    malicious_cmds = iocs.get("malicious_commands", [])
    suspicious_processes = iocs.get("process_names", [])

    or_terms_splunk = []
    or_terms_qradar = []

    for cmd in malicious_cmds:
        safe_cmd = cmd.replace('"', '\\"')
        or_terms_splunk.append(f'CommandLine="*{safe_cmd}*"')
        or_terms_qradar.append(f'UTF8(payload) LIKE "%{safe_cmd}%"')

    for proc in suspicious_processes:
        safe_proc = proc.replace('"','\\"')
        or_terms_splunk.append(f'(Image="*{safe_proc}*" OR ParentImage="*{safe_proc}*")')
        or_terms_qradar.append(f'UTF8(payload) LIKE "%{safe_proc}%"')

    if or_terms_splunk:
        splunk_q = (
            'index=wineventlog (EventID=4688 OR EventCode=1) '
            f'({ " OR ".join(or_terms_splunk) })'
        )
        splunk_queries.append(splunk_q)

    if or_terms_qradar:
        qradar_q = (
            'SELECT * FROM events '
            'WHERE (EventID=4688 OR EventCode=1) AND '
            f'({ " OR ".join(or_terms_qradar) })'
        )
        qradar_queries.append(qradar_q)

    return splunk_queries, qradar_queries


