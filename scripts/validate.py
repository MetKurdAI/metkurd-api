"""Offline repository checks. Does not call the MetKurd API or any network service."""
from pathlib import Path
import ast
import json
import re

import yaml
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate

ROOT = Path(__file__).resolve().parents[1]
spec = yaml.safe_load((ROOT / "openapi.yaml").read_text(encoding="utf-8"))
validate(spec)
assert spec["openapi"] == "3.1.0"
assert spec["servers"] == [{"url": "https://metkurd.ai/api/v2"}]
assert spec["security"] == [{"BearerAuth": []}]
operations = {(method.upper(), path) for path, item in spec["paths"].items()
              for method in item if method in {"get", "post"}}
expected = {("POST", "/" + s) for s in ["speech", "voice-clone", "transcriptions", "captions", "ocr", "stem", "zeta", "theta", "harakat", "references"]}
expected |= {("GET", p) for p in ["/services", "/voices", "/jobs/{id}", "/files/{id}/download"]}
assert operations == expected


def resolved(schema):
    if isinstance(schema, list):
        return [resolved(x) for x in schema]
    if not isinstance(schema, dict):
        return schema
    if "$ref" in schema:
        node = spec
        assert schema["$ref"].startswith("#/"), "Only local references permitted"
        for segment in schema["$ref"][2:].split("/"):
            node = node[segment.replace("~1", "/").replace("~0", "~")]
        return resolved({**node, **{k: v for k, v in schema.items() if k != "$ref"}})
    return {k: resolved(v) for k, v in schema.items()}


resolved(spec)  # Every $ref must resolve locally.
example_count = 0


def examples(node):
    global example_count
    if isinstance(node, dict):
        if "schema" in node and "example" in node:
            Draft202012Validator(resolved(node["schema"])).validate(node["example"])
            example_count += 1
        if "schema" in node and "examples" in node:
            for item in node["examples"].values():
                if "value" in item:
                    Draft202012Validator(resolved(node["schema"])).validate(item["value"])
                    example_count += 1
        for value in node.values():
            examples(value)
    elif isinstance(node, list):
        for value in node:
            examples(value)


examples(spec)
collection = json.loads((ROOT / "postman/MetKurd-API.postman_collection.json").read_text(encoding="utf-8"))
assert collection["info"]["schema"].endswith("/v2.1.0/collection.json")
assert collection["auth"]["bearer"][0]["value"] == "{{api_key}}"
assert collection["protocolProfileBehavior"]["followRedirects"] is False
variables = {x["key"]: x["value"] for x in collection["variable"]}
assert variables["api_key"] == "YOUR_API_KEY"
seen = set()
request_count = 0
for group in collection["item"]:
    for item in group["item"]:
        req = item["request"]
        path = req["url"].removeprefix("{{base_url}}")
        path = path.replace("{{job_id}}", "{id}").replace("{{file_id}}", "{id}")
        operation = req["method"], path
        assert operation in operations, operation
        seen.add(operation)
        request_count += 1
        if req["method"] == "POST":
            has_key = any(x["key"] == "Idempotency-Key" for x in req["header"])
            assert has_key == (path != "/references")
            body = req["body"]
            media = "application/json" if body["mode"] == "raw" else "multipart/form-data"
            schema = spec["paths"][path]["post"]["requestBody"]["content"][media]["schema"]
            if media == "application/json":
                rendered = body["raw"].replace("{{reference_id}}", "123").replace("{{voice_id}}", "VOICE_ID")
                payload = json.loads(rendered)
            else:
                payload = {}
                for field in body["formdata"]:
                    if field["type"] == "file":
                        payload[field["key"]] = "SYNTHETIC_UPLOAD_BYTES"
                    elif field["key"].endswith("[]"):
                        payload.setdefault(field["key"][:-2], []).append(field["value"])
                    else:
                        payload[field["key"]] = field["value"]
            Draft202012Validator(resolved(schema)).validate(payload)
assert seen == operations
assert request_count == 16

# Parse Python without importing/running examples or creating bytecode.
for path in ROOT.rglob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path.relative_to(ROOT)))


def anchor(heading):
    heading = re.sub(r"[`*_]", "", heading.strip().lower())
    return "".join(c for c in heading if c.isalnum() or c in " -_").replace(" ", "-")


link_count = 0
for path in [*ROOT.rglob("*.md"), ROOT / "llms.txt"]:
    content = path.read_text(encoding="utf-8")
    no_code = re.sub(r"```.*?```", "", content, flags=re.S)
    for href in re.findall(r"\[[^\]]+\]\(([^)]+)\)", no_code):
        if re.match(r"^[a-z]+://", href):
            continue  # External links deliberately not fetched.
        filename, _, fragment = href.partition("#")
        target = (path.parent / filename).resolve() if filename else path
        assert target.is_relative_to(ROOT), f"Link leaves repository: {path.name}"
        assert target.is_file(), f"Broken link in {path.relative_to(ROOT)}: {href}"
        if fragment:
            target_text = re.sub(r"```.*?```", "", target.read_text(encoding="utf-8"), flags=re.S)
            anchors = {anchor(h) for h in re.findall(r"^#{1,6}\s+(.+)$", target_text, re.M)}
            assert fragment in anchors, f"Missing anchor in {path.relative_to(ROOT)}: {href}"
        link_count += 1

# Pattern checks print filenames and rule names only, never matching sensitive values.
patterns = {
    "absolute drive path": r"\b[A-Za-z]:[\\/]",
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "cloud access key": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    "provider URL": r"https?://[^\s\"']*(?:runpod|amazonaws|redis|rds)[^\s\"']*",
    "storage URI": r"\bs3://",
    "private network address": r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|127\.0\.0\.1)\b",
    "assigned bearer literal": r"Bearer\s+[A-Za-z0-9_-]{25,}",
}
findings = []
for path in ROOT.rglob("*"):
    if not path.is_file() or any(p in {"__pycache__", ".git", ".venv", "node_modules"} for p in path.parts):
        continue
    if path == Path(__file__).resolve():
        continue  # The scanner contains the patterns it detects.
    text = path.read_text(encoding="utf-8")
    for label, pattern in patterns.items():
        if re.search(pattern, text, re.I):
            findings.append((str(path.relative_to(ROOT)), label))
assert not findings, findings
print(f"PASS: OpenAPI 3.1, {len(operations)} operations, {example_count} schema examples")
print(f"PASS: Postman JSON, {request_count} requests, all operations and request schemas")
print(f"PASS: Python syntax, {link_count} local Markdown links/anchors, sensitive-data pattern scan")
print("No network calls made. Pattern scanning is not a guarantee against every possible secret.")
