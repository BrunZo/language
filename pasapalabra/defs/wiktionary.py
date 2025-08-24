import requests

WIKTIONARY_API = "https://es.wiktionary.org/w/api.php"

def get_definition(word):
    """Fetch definition from Wiktionary via API"""

    params = {
        "action": "query",
        "prop": "extracts",
        "titles": word,
        "format": "json",
        "explaintext": True
    }
    r = requests.get(WIKTIONARY_API, params=params)

    if r.status_code != 200:
        return None

    data = r.json()
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        extract = page.get("extract", "")
        if extract:
            start = extract.find("1\n") + 2
            end = extract.find("\n", start)
            definition = extract[start:end]
            return definition
    return None