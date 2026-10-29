"""A second bounded research pass for vocabulary and citation neighborhoods missed initially."""

import json
from pathlib import Path

from .compile import query_text
from .runtime.store import read_json, write_json
from .schema import PLAN_SCHEMA, STRING, array, obj

EXPANSION_SCHEMA = obj(
    {
        "works": array(PLAN_SCHEMA["properties"]["works"]["items"], 0, 35),
        "openalex_queries": array(STRING, 4, 20),
        "web_queries": array(STRING, 4, 20),
        "search_log": array(PLAN_SCHEMA["properties"]["search_log"]["items"], 1, 30),
        "coverage_limits": array(STRING, 1, 10),
    }
)


def expand(agent, brief, plan, directory, cutoff, round_number=1):
    directory = Path(directory)
    name = "expansion" if round_number == 1 else f"expansion-{round_number}"
    saved = directory / f"{name}.json"
    if saved.exists():
        return read_json(saved)
    prompt = (
        "Perform a bounded second-pass literature search for this research repository. Use web search "
        "and primary sources, but do not edit code, inspect other projects or benchmarks, or read credentials. "
        "Spend at most 4 minutes searching and then return the structured JSON. Do not keep searching "
        "instead of finishing. The earlier pass's leads are below so avoid repeating them. "
        "Find overlooked intervention families, effects, measurement methods, counterexamples and "
        "neighboring terminology. Follow reference/citation neighborhoods of the supplied seeds; "
        "search each conceptual family rather than repeatedly searching the topic name. Look for "
        "relevant papers whose titles lack the obvious keywords, and distinguish keyword-rich hard "
        "negatives by reading their abstracts. Return up to 35 new primary URLs as discovery leads, "
        "not accepted papers. Include concrete additional OpenAlex search strings (NOT API URLs or "
        "search= parameters) and web queries for continued daily discovery. Note coverage gaps honestly. "
        f"Cutoff: {cutoff}. Do not consult a prior catalogue or test labels.\nBRIEF:\n{brief}\n"
        + json.dumps({k: plan[k] for k in ["include", "exclude", "keywords", "works"]})
    )
    result = agent.call(prompt, EXPANSION_SCHEMA, directory, name, search=True)
    result["openalex_queries"] = [query_text(q) for q in result["openalex_queries"] if query_text(q)]
    write_json(saved, result)
    return result
