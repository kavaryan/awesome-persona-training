"""Strict bootstrap contract; model output supplies research configuration, not code."""

from urllib.parse import urlsplit

from jsonschema import validate


def obj(properties):
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }


def array(item, minimum=0, maximum=200):
    return {"type": "array", "items": item, "minItems": minimum, "maxItems": maximum}


STRING = {"type": "string", "minLength": 1, "maxLength": 3000}
STRINGS = array(STRING)
HTTPS = {"type": "string", "pattern": "^https://[^\\s]+$", "maxLength": 3000}
PLAN_SCHEMA = obj(
    {
        "title": STRING,
        "slug": {"type": "string", "pattern": "^awesome-[a-z0-9]+(?:-[a-z0-9]+)*$"},
        "description": STRING,
        "include": array(STRING, 1, 15),
        "exclude": array(STRING, 1, 15),
        "boundaries": array(STRING, 1, 15),
        "keywords": array(obj({"concept": STRING, "terms": array(STRING, 1, 20), "reason": STRING}), 3, 30),
        "openalex_queries": array(STRING, 4, 40),
        "web_queries": array(STRING, 4, 40),
        "feeds": array(obj({"name": STRING, "url": HTTPS}), 0, 15),
        "indexes": array(obj({"name": STRING, "url": HTTPS, "path_pattern": STRING}), 0, 15),
        "repositories": array(HTTPS, 0, 10),
        "dimensions": array(
            obj(
                {
                    "name": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
                    "description": STRING,
                    "values": array(STRING, 2, 40),
                }
            ),
            2,
            10,
        ),
        "works": array(
            obj({"title": STRING, "url": HTTPS, "seed": {"type": "boolean"}, "found_via": STRING}), 4, 150
        ),
        "search_log": array(obj({"query": STRING, "source": STRING, "finding": STRING}), 1, 80),
        "coverage_limits": array(STRING, 1, 20),
    }
)


def validate_plan(plan):
    validate(plan, PLAN_SCHEMA)
    names = [d["name"] for d in plan["dimensions"]]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate taxonomy dimensions")
    urls = (
        [w["url"] for w in plan["works"]]
        + [s["url"] for s in plan["feeds"] + plan["indexes"]]
        + plan["repositories"]
    )
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Research URLs must be credential-free HTTPS URLs")
    for source in plan["indexes"]:
        if len(source["path_pattern"]) > 200:
            raise ValueError("Index pattern too long")
    return plan
