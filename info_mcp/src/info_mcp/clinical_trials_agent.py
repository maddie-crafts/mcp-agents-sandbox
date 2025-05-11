import json
from mcp import types
from typing import List, Optional, Union
import requests

BASE_URL = "https://clinicaltrials.gov/api/query/study_fields"

def fetch_trials(
    expr: str,
    fields: Optional[List[str]] = None,
    max_studies: int = 5
) -> types.TextContent:
    field_str = ",".join(fields) if fields else "NCTId,BriefTitle,Condition"
    params = {
        "expr": expr,
        "fields": field_str,
        "min_rnk": 1,
        "max_rnk": max_studies,
        "fmt": "json"
    }
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    return json.dumps(response.json(), indent=2)

def get_trials_by_condition(
    condition: str,
    fields: Optional[List[str]] = None
) -> types.TextContent:
    return fetch_trials(condition, fields)

def get_trials_by_location(
    location: str,
    fields: Optional[List[str]] = None
) -> types.TextContent:
    query = f"AREA[{location}]"
    return fetch_trials(query, fields)

def get_trials_by_id(
    nct_id: Union[str, List[str]],
    fields: Optional[List[str]] = None
) -> types.TextContent:
    if isinstance(nct_id, list):
        expr = " OR ".join(nct_id)
    else:
        expr = nct_id
    return fetch_trials(expr, fields)