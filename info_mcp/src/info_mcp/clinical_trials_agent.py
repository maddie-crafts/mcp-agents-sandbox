import json
from mcp import types
from typing import List, Optional, Union
import requests

BASE_URL = "https://beta-ut.clinicaltrials.gov/api/v2/studies"

def fetch_trials(
    expr: str,
    max_studies: int = 5
) -> types.TextContent:
    params = {
        "query.titles": expr,
        "pageSize": max_studies
    }
    response = requests.get(BASE_URL, params=params)
    print(f"Request URL: {response.url}")
    
    if response.status_code != 200:
        raise RuntimeError(f"API call failed with status {response.status_code}: {response.text}")
    
    try:
        return json.dumps(response.json(), indent=2)
    except requests.exceptions.JSONDecodeError as e:
        raise RuntimeError(f"Invalid JSON returned from API: {e}")

def get_trials_by_condition(
    condition: str,
    fields: Optional[List[str]] = None
) -> types.TextContent:
    return fetch_trials(condition)


def get_trials_by_id(
    nct_id: Union[str, List[str]],
    fields: Optional[List[str]] = None
) -> types.TextContent:
    if isinstance(nct_id, list):
        expr = " OR ".join(nct_id)
    else:
        expr = nct_id
    return fetch_trials(expr)