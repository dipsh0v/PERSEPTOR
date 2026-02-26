"""
PERSEPTOR v2.0 - SIEM Query Generator
Generates platform-specific SIEM queries from IoC data.
Supports: Splunk SPL, QRadar AQL, Elasticsearch DSL, Microsoft Sentinel KQL.
"""

import json
from typing import List, Dict, Optional
from modules.logging_config import get_logger

logger = get_logger("siem_query_generator")


# Field mappings per SIEM platform
FIELD_MAP = {
    "splunk": {
        "process_name": "Image",
        "command_line": "CommandLine",
        "parent_process": "ParentImage",
        "source_ip": "src_ip",
        "dest_ip": "dest_ip",
        "dest_port": "dest_port",
        "domain": "query",
        "url": "url",
        "filename": "file_name",
        "registry_key": "registry_key_name",
        "hash": "file_hash",
        "user": "user",
    },
    "qradar": {
        "process_name": "Process Name",
        "command_line": "Process CommandLine",
        "parent_process": "Parent Process Name",
        "source_ip": "sourceip",
        "dest_ip": "destinationip",
        "dest_port": "destinationport",
        "domain": "DNS Query",
        "url": "URL",
        "filename": "Filename",
        "registry_key": "Registry Key",
        "hash": "File Hash",
        "user": "username",
    },
    "elastic": {
        "process_name": "process.name",
        "command_line": "process.command_line",
        "parent_process": "process.parent.name",
        "source_ip": "source.ip",
        "dest_ip": "destination.ip",
        "dest_port": "destination.port",
        "domain": "dns.question.name",
        "url": "url.full",
        "filename": "file.name",
        "registry_key": "registry.path",
        "hash": "file.hash.sha256",
        "user": "user.name",
    },
    "sentinel": {
        "process_name": "ProcessName",
        "command_line": "CommandLine",
        "parent_process": "ParentProcessName",
        "source_ip": "SourceIP",
        "dest_ip": "DestinationIP",
        "dest_port": "DestinationPort",
        "domain": "DnsQuery",
        "url": "RequestURL",
        "filename": "FileName",
        "registry_key": "RegistryKey",
        "hash": "FileHash",
        "user": "AccountName",
    },
}

# IoC type to generic field name mapping
IOC_TO_FIELD = {
    "ips": "dest_ip",
    "domains": "domain",
    "urls": "url",
    "filenames": "filename",
    "file_hashes": "hash",
    "registry_keys": "registry_key",
    "process_names": "process_name",
    "malicious_commands": "command_line",
    "email_addresses": None,  # No standard field
}

# SIEM-specific event source configs
SIEM_SOURCES = {
    "splunk": {
        "process": 'index=wineventlog sourcetype=WinEventLog:Sysmon EventCode=1',
        "network": 'index=wineventlog sourcetype=WinEventLog:Sysmon EventCode=3',
        "dns": 'index=wineventlog sourcetype=WinEventLog:Sysmon EventCode=22',
        "file": 'index=wineventlog sourcetype=WinEventLog:Sysmon EventCode=11',
        "registry": 'index=wineventlog sourcetype=WinEventLog:Sysmon EventCode=13',
    },
    "qradar": {
        "process": "SELECT * FROM events WHERE LOGSOURCETYPENAME(logsourceid)='Microsoft Windows Security Event Log' AND EventID IN (4688, 1)",
        "network": "SELECT * FROM flows WHERE",
        "dns": "SELECT * FROM events WHERE EventID=22",
        "file": "SELECT * FROM events WHERE EventID IN (11, 23, 26)",
        "registry": "SELECT * FROM events WHERE EventID IN (12, 13, 14)",
    },
    "sentinel": {
        "process": "SecurityEvent\n| where EventID == 4688",
        "network": "CommonSecurityLog\n| where DeviceEventClassID == 3",
        "dns": "DnsEvents",
        "file": "DeviceFileEvents",
        "registry": "DeviceRegistryEvents",
    },
}


def _generate_splunk_query(ioc_type: str, indicators: list, field: str) -> str:
    """Generate a Splunk SPL query for given IoCs."""
    platform_field = FIELD_MAP["splunk"].get(field, field)

    # Determine event source
    if ioc_type in ("malicious_commands", "process_names"):
        source = SIEM_SOURCES["splunk"]["process"]
    elif ioc_type in ("ips",):
        source = SIEM_SOURCES["splunk"]["network"]
    elif ioc_type in ("domains",):
        source = SIEM_SOURCES["splunk"]["dns"]
    elif ioc_type in ("filenames", "file_hashes"):
        source = SIEM_SOURCES["splunk"]["file"]
    elif ioc_type in ("registry_keys",):
        source = SIEM_SOURCES["splunk"]["registry"]
    else:
        source = 'index=* sourcetype=*'

    # Build OR conditions
    or_terms = []
    for ioc in indicators[:30]:
        safe = ioc.replace('"', '\\"')
        if ioc_type in ("malicious_commands", "process_names", "filenames"):
            or_terms.append(f'{platform_field}="*{safe}*"')
        else:
            or_terms.append(f'{platform_field}="{safe}"')

    query = f'{source}\n| where ({" OR ".join(or_terms)})'
    query += f'\n| stats count by {platform_field}, ComputerName, User'
    query += '\n| sort - count'

    return query


def _generate_qradar_query(ioc_type: str, indicators: list, field: str) -> str:
    """Generate a QRadar AQL query for given IoCs."""
    platform_field = FIELD_MAP["qradar"].get(field, field)

    # Determine event source
    if ioc_type in ("malicious_commands", "process_names"):
        base = SIEM_SOURCES["qradar"]["process"]
    elif ioc_type in ("ips",):
        base = SIEM_SOURCES["qradar"]["network"]
    elif ioc_type in ("domains",):
        base = SIEM_SOURCES["qradar"]["dns"]
    elif ioc_type in ("filenames", "file_hashes"):
        base = SIEM_SOURCES["qradar"]["file"]
    elif ioc_type in ("registry_keys",):
        base = SIEM_SOURCES["qradar"]["registry"]
    else:
        base = "SELECT * FROM events WHERE"

    # Build conditions
    conditions = []
    for ioc in indicators[:30]:
        safe = ioc.replace("'", "''")
        if ioc_type in ("malicious_commands", "process_names", "filenames"):
            conditions.append(f"UTF8(payload) LIKE '%{safe}%'")
        else:
            conditions.append(f"\"{platform_field}\" = '{safe}'")

    where_clause = " OR ".join(conditions)

    if "WHERE" in base:
        query = f"{base} AND ({where_clause})"
    else:
        query = f"{base} ({where_clause})"

    query += " ORDER BY starttime DESC LAST 24 HOURS"
    return query


def _generate_elastic_query(ioc_type: str, indicators: list, field: str) -> dict:
    """Generate an Elasticsearch DSL query for given IoCs."""
    platform_field = FIELD_MAP["elastic"].get(field, field)

    if ioc_type in ("malicious_commands", "process_names", "filenames"):
        should_clauses = [{"wildcard": {platform_field: f"*{ioc}*"}} for ioc in indicators[:30]]
    else:
        should_clauses = [{"term": {platform_field: ioc}} for ioc in indicators[:30]]

    query = {
        "query": {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1,
            }
        },
        "sort": [{"@timestamp": {"order": "desc"}}],
        "size": 100,
    }

    return query


def _generate_sentinel_query(ioc_type: str, indicators: list, field: str) -> str:
    """Generate a Microsoft Sentinel KQL query for given IoCs."""
    platform_field = FIELD_MAP["sentinel"].get(field, field)

    # Determine event source
    if ioc_type in ("malicious_commands", "process_names"):
        source = SIEM_SOURCES["sentinel"]["process"]
    elif ioc_type in ("ips",):
        source = SIEM_SOURCES["sentinel"]["network"]
    elif ioc_type in ("domains",):
        source = SIEM_SOURCES["sentinel"]["dns"]
    elif ioc_type in ("filenames", "file_hashes"):
        source = SIEM_SOURCES["sentinel"]["file"]
    elif ioc_type in ("registry_keys",):
        source = SIEM_SOURCES["sentinel"]["registry"]
    else:
        source = "SecurityEvent"

    # Build where conditions
    if ioc_type in ("malicious_commands", "process_names", "filenames"):
        conditions = [f'{platform_field} contains "{ioc}"' for ioc in indicators[:30]]
    else:
        escaped = [f'"{ioc}"' for ioc in indicators[:30]]
        conditions = [f'{platform_field} in ({", ".join(escaped)})']

    where_clause = " or ".join(conditions) if len(conditions) > 1 else conditions[0]

    query = f"{source}\n| where {where_clause}"
    query += f"\n| project TimeGenerated, {platform_field}, Computer, Account"
    query += "\n| sort by TimeGenerated desc"

    return query


def generate_siem_queries(analysis_data: dict) -> Dict[str, List[dict]]:
    """
    Generate SIEM queries for all 4 platforms from analysis data.

    Returns a dict with keys: splunk, qradar, elastic, sentinel.
    Each value is a list of query dicts: {ioc_type, description, query, severity}.
    """
    results = {
        "splunk": [],
        "qradar": [],
        "elastic": [],
        "sentinel": [],
    }

    iocs = analysis_data.get("indicators_of_compromise", {})

    for ioc_type, indicators in iocs.items():
        if not indicators or ioc_type not in IOC_TO_FIELD:
            continue

        field = IOC_TO_FIELD[ioc_type]
        if field is None:
            continue

        description = f"Detection query for {ioc_type.replace('_', ' ')} ({len(indicators)} indicators)"
        severity = "high" if ioc_type in ("malicious_commands", "file_hashes") else "medium"

        try:
            splunk_q = _generate_splunk_query(ioc_type, indicators, field)
            results["splunk"].append({
                "ioc_type": ioc_type,
                "description": description,
                "query": splunk_q,
                "severity": severity,
            })
        except Exception as e:
            logger.error(f"Error generating Splunk query for {ioc_type}: {e}")

        try:
            qradar_q = _generate_qradar_query(ioc_type, indicators, field)
            results["qradar"].append({
                "ioc_type": ioc_type,
                "description": description,
                "query": qradar_q,
                "severity": severity,
            })
        except Exception as e:
            logger.error(f"Error generating QRadar query for {ioc_type}: {e}")

        try:
            elastic_q = _generate_elastic_query(ioc_type, indicators, field)
            results["elastic"].append({
                "ioc_type": ioc_type,
                "description": description,
                "query": json.dumps(elastic_q, indent=2),
                "severity": severity,
            })
        except Exception as e:
            logger.error(f"Error generating Elastic query for {ioc_type}: {e}")

        try:
            sentinel_q = _generate_sentinel_query(ioc_type, indicators, field)
            results["sentinel"].append({
                "ioc_type": ioc_type,
                "description": description,
                "query": sentinel_q,
                "severity": severity,
            })
        except Exception as e:
            logger.error(f"Error generating Sentinel query for {ioc_type}: {e}")

    total = sum(len(v) for v in results.values())
    logger.info(f"Generated {total} SIEM queries across 4 platforms")

    return results


def siem_queries_to_flat(results: Dict[str, List[dict]]) -> dict:
    """
    Convert structured SIEM queries to flat format for backward compatibility.
    Returns dict with keys: splunk, qradar, elastic, sentinel - each with description, query, notes.
    """
    flat = {}
    for platform, queries in results.items():
        if queries:
            combined_query = "\n\n/* --- */\n\n".join(q["query"] for q in queries)
            descriptions = ", ".join(q["description"] for q in queries)
            flat[platform] = {
                "description": descriptions,
                "query": combined_query,
                "notes": f"{len(queries)} detection queries generated by PERSEPTOR",
            }
        else:
            flat[platform] = {
                "description": "No IoC indicators available",
                "query": "N/A",
                "notes": "No relevant indicators found for this platform",
            }
    return flat
