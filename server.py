"""Schooldigger MCP Server.
An MCP server with all the tools to interact with school and district data API.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any, Union
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("SchoolDigger MCP Server")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("schooldigger-mcp")

SCHOOL_DIGGER_BASE_API = 'https://api.schooldigger.com/v2.3/'

APP_ID = os.getenv("SCHOOLDIGGER_API_ID")
APP_KEY = os.getenv("SCHOOLDIGGER_API_KEY")

def call_school_digger_api(endpoint: str, params: Dict = None):
    base_params = {'appID': APP_ID, 'appKey': APP_KEY}
    if params:
        base_params.update(params)
    
    try:
        url = SCHOOL_DIGGER_BASE_API + endpoint.lstrip('/')
        response = requests.get(url, params=base_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making request to {url}: {e}")
        return {"error": str(e)}

@mcp.tool()
def search_schools(
    query: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip_code: Optional[str] = None,
    school_level: Optional[str] = None,
    sort_by: str = 'rank',
    per_page: int = 5
) -> List[str]:
    """
    Search schools by city, state, or zip code, with optional level filtering.
    Results are ranked by statewide performance.

    Args:
        query: Partial school name to search (e.g., "Lincoln").
        city: City name (e.g., "Cypress").
        state: Two-letter US state code like CA, NY, TX (required).
        zip_code: ZIP code (e.g., "77433").
        school_level: 'Elementary', 'Middle', 'High', 'Alt', 'Public', 'Private' (optional). 'Public' returns all Elementary, Middle, High and Alternative schools.
        per_page: Number of results to return (default 10).

    Returns:
        A list of schools sorted by rank (best first).
    """
    params = {'perPage': per_page, 'sortBy': sort_by}
    if query:
        params['q'] = query
    if city:
        params['city'] = city
    if state:
        params['st'] = state
    if zip_code:
        params['zip'] = zip_code
    if school_level:
        params['level'] = school_level

    return call_school_digger_api('schools', params)

@mcp.tool()
def search_autocomplete_schools(query: str, max_results: int = 10) -> Dict:
    """
    Autocomplete schools by name.

    Args:
        query: Partial school name to search.
        max_results: Max number of suggestions (default 10).

    Returns:
        List of matching schools with IDs and names.
    """
    params = {'q': query, 'returnCount': max_results}

    return call_school_digger_api('autocomplete/schools', params)

@mcp.tool()
def get_school_details(school_id: str) -> Dict[str, any]:
    """
    Fetch school details.

    Args:
        school_id: SchoolDigger school ID.

    Returns:
        Dictionary with demographics, address, test scores, rank history, etc.
    """
    return call_school_digger_api(f'schools/{school_id}')

@mcp.tool()
def search_districts(
    city: Optional[str] = None,
    state: Optional[str] = None,
    query: Optional[str] = None,
    zip_code: Optional[str] = None,
    sort_by: str = 'rank',
    per_page: int = 5
) -> List[str]:
    """
    Find school districts by city, state, or zip code.

    Rules:
    - Always require a two-letter state code (e.g., "CA", "TX").
    - If the user gives a city or ZIP code, include it.
    - query (str): Partial district name to search for (e.g., "San").
    - Return the best-ranked districts first.
    - Limit the number of results with 'per_page' (default 5 unless user asks otherwise).

    Examples:
    - "Top school districts in San Jose, CA" → city="San Jose", state="CA"
    - "Best elementary districts in Dallas, TX" → city="Dallas", state="TX", school_level="Elementary"
    - "Districts near ZIP 77433, TX" → zip_code="77433", state="TX"
    """
    params = {'perPage': per_page, 'sort': sort_by}
    if city:
        params['city'] = city
    if state:
        params['st'] = state
    if zip_code:
        params['zip'] = zip_code
    if query:
        params['q'] = query

    return call_school_digger_api('districts', params)

@mcp.tool()
def get_district_details(district_id: str) -> Dict[str, Any]:
    """
    Fetch details of a district.

    Args:
        district_id: SchoolDigger district ID.

    Returns:
        Dictionary with demographics, rank history, boundaries, etc.
    """
    return call_school_digger_api(f'districts/{district_id}')

@mcp.resource("schooldigger://school-levels")
def get_school_levels() -> str:
    """Available school level categories"""
    return """
            Elementary: Grades K-5
            Middle: Grades 6-8  
            High: Grades 9-12
            Private: Private institutions
            Alt: Alternative education programs
            """

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SchoolDigger MCP Server")
    parser.add_argument("--http", action="store_true", help="Run as HTTP server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for HTTP server")
    parser.add_argument("--port", type=int, default=8080, help="Port for HTTP server (default: 8080)")
    args = parser.parse_args()

    if args.http:
        # HTTP transport
        print(f"Running as HTTP server on ${args.host}:${args.port}")
        mcp.run(transport="http", host=args.host, port=args.port)
    else:
        # Default STDIO transport
        mcp.run()
