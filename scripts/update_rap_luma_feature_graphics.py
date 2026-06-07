#!/usr/bin/env python3
"""Upload selected RAP feature graphics to private Luma drafts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_BASE = "https://public-api.luma.com/v1"
REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPO_ROOT / "output"
PROJECT = "rap-cohort-feature-graphics-2026-native"
PROJECT_DIR = OUTPUT_ROOT / PROJECT
LUMA_DIR = PROJECT_DIR / "luma"
UA = "rafiki-rap-cohort-feature-graphics/1.0"
SEARCH_AFTER = "2026-08-01T00:00:00-07:00"
SEARCH_BEFORE = "2026-10-15T23:59:59-07:00"
TARGETS = {
    "august": {
        "cohort": "Cohort 2",
        "date": "August 7, 2026",
        "date_iso": "2026-08-07",
        "alt": "RAP Cohort 2 feature graphic: starts August 7, 2026",
    },
    "september": {
        "cohort": "Cohort 3",
        "date": "September 18, 2026",
        "date_iso": "2026-09-18",
        "alt": "RAP Cohort 3 feature graphic: starts September 18, 2026",
    },
}
INVARIANT_FIELDS = [
    "name",
    "start_at",
    "end_at",
    "timezone",
    "visibility",
    "max_capacity",
    "can_register_for_multiple_tickets",
    "registration_questions",
    "ticket_types",
    "hosts",
]


def stamp() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%SZ")


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_luma_api_key() -> str:
    key = os.environ.get("LUMA_API_KEY", "").strip()
    if key:
        return key
    env_path = Path(
        os.environ.get("BCAI_CANONICAL_ENV_PATH", "")
        or Path.home() / "Code" / "notion-local" / "kk-ai-ecosystem" / ".env"
    )
    if not env_path.exists():
        raise FileNotFoundError(f"Cannot find Luma env file: {env_path}")
    match = re.search(r"^LUMA_API_KEY=(.+)$", env_path.read_text(encoding="utf-8"), re.MULTILINE)
    if not match:
        raise RuntimeError("LUMA_API_KEY is not set in the resolved env file")
    return match.group(1).strip()


def luma_json(path: str, key: str, *, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None
    headers = {"accept": "application/json", "x-luma-api-key": key, "user-agent": UA}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["content-type"] = "application/json"
    req = urllib.request.Request(f"{API_BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Luma {method} {path} failed HTTP {exc.code}: {body[:800]}") from exc


def event_payload(raw: dict[str, Any]) -> dict[str, Any]:
    event = raw.get("event")
    return event if isinstance(event, dict) else raw


def event_id(event: dict[str, Any]) -> str:
    for key in ("id", "event_id", "api_id"):
        value = str(event.get(key) or "")
        if value.startswith("evt-"):
            return value
    return str(event.get("id") or event.get("event_id") or event.get("api_id") or "")


def get_event(key: str, event_id_value: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"id": event_id_value})
    return luma_json(f"/event/get?{query}", key)


def list_events(key: str) -> list[dict[str, Any]]:
    all_events: list[dict[str, Any]] = []
    for status in ("approved", "pending"):
        cursor = ""
        while True:
            params = {
                "after": SEARCH_AFTER,
                "before": SEARCH_BEFORE,
                "pagination_limit": "100",
                "sort_column": "start_at",
                "sort_direction": "asc",
                "status": status,
                "platforms": "luma",
            }
            if cursor:
                params["pagination_cursor"] = cursor
            query = urllib.parse.urlencode(params)
            data = luma_json(f"/calendar/list-events?{query}", key)
            rows = data.get("entries") or data.get("events") or data.get("data") or []
            if not isinstance(rows, list):
                rows = []
            for row in rows:
                if isinstance(row, dict):
                    all_events.append(event_payload(row))
            cursor = str(data.get("next_cursor") or data.get("pagination_cursor") or "")
            if not cursor:
                break
    return all_events


def target_score(event: dict[str, Any], target: dict[str, str]) -> int:
    text = " ".join(str(event.get(key) or "") for key in ("name", "url", "slug", "description_md")).lower()
    start = str(event.get("start_at") or "")
    score = 0
    if target["date_iso"] in start:
        score += 6
    if "responsible ai" in text:
        score += 3
    if "professional" in text:
        score += 2
    if "rap" in text:
        score += 2
    if "ai-ethics" in text or "2026-05" in start:
        score -= 20
    return score


def discover_targets(key: str, overrides: dict[str, str]) -> dict[str, dict[str, Any]]:
    found: dict[str, dict[str, Any]] = {}
    if all(overrides.values()):
        for name, eid in overrides.items():
            found[name] = event_payload(get_event(key, eid))
        return found

    events = list_events(key)
    for name, target in TARGETS.items():
        if overrides.get(name):
            found[name] = event_payload(get_event(key, overrides[name]))
            continue
        candidates = [
            event for event in events
            if target_score(event, target) >= 8 and event_id(event)
        ]
        if len(candidates) != 1:
            preview = [
                {
                    "id": event_id(event),
                    "name": event.get("name"),
                    "start_at": event.get("start_at"),
                    "visibility": event.get("visibility"),
                    "score": target_score(event, target),
                    "url": event.get("url"),
                }
                for event in sorted(events, key=lambda e: target_score(e, target), reverse=True)[:10]
            ]
            raise RuntimeError(f"Expected exactly one {name} RAP draft, found {len(candidates)}. Top candidates: {preview}")
        found[name] = event_payload(get_event(key, event_id(candidates[0])))
    return found


def ratings_path() -> Path:
    return OUTPUT_ROOT / "ratings.json"


def selected_from_ratings() -> dict[str, Path]:
    path = ratings_path()
    if not path.exists():
        return {}
    ratings = read_json(path)
    if not isinstance(ratings, dict):
        return {}
    selected: dict[str, list[Path]] = {"august": [], "september": []}
    for key, value in ratings.items():
        if value != "star" or not str(key).startswith(f"{PROJECT}/run-"):
            continue
        parts = str(key).split("/", 2)
        if len(parts) != 3:
            continue
        _, run_id, filename = parts
        candidate = PROJECT_DIR / run_id / filename
        if not candidate.exists():
            continue
        lower = filename.lower()
        for target in selected:
            if target in lower:
                selected[target].append(candidate.resolve())
    winners = {}
    for target, paths in selected.items():
        unique = sorted(set(paths))
        if len(unique) == 1:
            winners[target] = unique[0]
        elif len(unique) > 1:
            raise RuntimeError(f"Multiple starred {target} candidates: {unique}")
    return winners


def resolve_winners(args: argparse.Namespace) -> dict[str, Path]:
    explicit = {
        "august": Path(args.august_image).expanduser().resolve() if args.august_image else None,
        "september": Path(args.september_image).expanduser().resolve() if args.september_image else None,
    }
    if explicit["august"] or explicit["september"]:
        missing = [name for name, path in explicit.items() if path is None or not path.exists()]
        if missing:
            raise RuntimeError(f"Explicit winner image(s) missing: {missing}")
        return {name: path for name, path in explicit.items() if path is not None}
    return selected_from_ratings()


def create_upload_url(key: str) -> dict[str, str]:
    data = luma_json("/images/create-upload-url", key, method="POST", payload={"content_type": "image/png"})
    upload_url = str(data.get("upload_url") or data.get("signed_url") or data.get("url") or "")
    file_url = str(data.get("file_url") or data.get("cdn_url") or data.get("public_url") or "")
    nested = data.get("upload") if isinstance(data.get("upload"), dict) else {}
    upload_url = upload_url or str(nested.get("upload_url") or nested.get("url") or "")
    file_url = file_url or str(nested.get("file_url") or nested.get("cdn_url") or "")
    if not upload_url or not file_url:
        raise RuntimeError(f"Unexpected Luma upload response keys: {sorted(data.keys())}")
    if "images.lumacdn.com" not in file_url:
        raise RuntimeError(f"Luma upload did not return a Luma CDN file URL: {file_url}")
    return {"upload_url": upload_url, "file_url": file_url}


def put_upload(upload_url: str, image: Path) -> None:
    req = urllib.request.Request(
        upload_url,
        data=image.read_bytes(),
        headers={"content-type": "image/png", "user-agent": UA},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            if response.status not in (200, 201, 204):
                raise RuntimeError(f"upload returned HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Luma CDN upload failed HTTP {exc.code}: {body[:800]}") from exc


def upload_image(key: str, image: Path) -> str:
    upload = create_upload_url(key)
    put_upload(upload["upload_url"], image)
    return upload["file_url"]


def insert_top_image(description: str, image_url: str, alt: str) -> str:
    if "images.lumacdn.com" not in image_url:
        raise RuntimeError("description image URL must be hosted on images.lumacdn.com")
    image_md = f"![{alt}]({image_url})"
    pattern = re.compile(r"\A\s*!\[RAP Cohort [23] feature graphic:[^\]]+\]\(https://images\.lumacdn\.com[^)]+\)\s*", re.I)
    if pattern.search(description):
        return pattern.sub(image_md + "\n\n", description, count=1).strip() + "\n"
    return image_md + "\n\n" + description.strip() + "\n"


def comparable_ticket(ticket: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "id",
        "api_id",
        "name",
        "cents",
        "currency",
        "type",
        "is_hidden",
        "require_approval",
        "valid_start_at",
        "valid_end_at",
        "max_capacity",
    ]
    return {key: ticket.get(key) for key in keys}


def comparable_host(host: dict[str, Any]) -> str:
    return str(host.get("id") or host.get("api_id") or host.get("name") or "")


def invariant_snapshot(event: dict[str, Any]) -> dict[str, Any]:
    snap: dict[str, Any] = {}
    for field in INVARIANT_FIELDS:
        value = event.get(field)
        if field == "ticket_types" and isinstance(value, list):
            value = [comparable_ticket(ticket) for ticket in value if isinstance(ticket, dict)]
        if field == "hosts" and isinstance(value, list):
            value = sorted(comparable_host(host) for host in value if isinstance(host, dict))
        snap[field] = value
    return snap


def image_url_present(haystack: str, url: str) -> bool:
    if url in haystack:
        return True
    match = re.search(r"/(api-uploads/.+)$", url)
    return bool(match and match.group(1) in haystack)


def validate_readback(target_name: str, before: dict[str, Any], after: dict[str, Any], image_url: str) -> list[str]:
    changed = [
        key for key in sorted(invariant_snapshot(before))
        if invariant_snapshot(before).get(key) != invariant_snapshot(after).get(key)
    ]
    if changed:
        raise RuntimeError(f"{target_name} unexpected invariant changes: {changed}")
    alt = TARGETS[target_name]["alt"]
    desc = str(after.get("description_md") or "")
    cover = str(after.get("cover_url") or "")
    failures = []
    if not image_url_present(cover, image_url):
        failures.append("cover_url")
    if alt not in desc:
        failures.append("body_alt")
    if not image_url_present(desc, image_url):
        failures.append("body_image_url")
    if failures:
        raise RuntimeError(f"{target_name} readback missing {failures}")
    return changed


def build_payload(target_name: str, event: dict[str, Any], image_url: str) -> dict[str, Any]:
    description = insert_top_image(str(event.get("description_md") or ""), image_url, TARGETS[target_name]["alt"])
    payload = {
        "event_id": event_id(event),
        "cover_url": image_url,
        "description_md": description,
        "suppress_notifications": True,
    }
    if sorted(payload) != ["cover_url", "description_md", "event_id", "suppress_notifications"]:
        raise RuntimeError(f"Unexpected update payload keys: {sorted(payload)}")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply live Luma updates")
    parser.add_argument("--august-image", default="", help="Explicit Cohort 2 PNG winner")
    parser.add_argument("--september-image", default="", help="Explicit Cohort 3 PNG winner")
    parser.add_argument("--august-event-id", default="", help="Override August private draft event id")
    parser.add_argument("--september-event-id", default="", help="Override September private draft event id")
    return parser.parse_args()


def gated_report(run_stamp: str, winners: dict[str, Path], reason: str) -> Path:
    report = {
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "dry_run": True,
        "apply": False,
        "gated": True,
        "reason": reason,
        "selected_images": {key: str(path) for key, path in winners.items()},
        "ratings_file": str(ratings_path()),
        "required": ["one starred August candidate", "one starred September candidate"],
    }
    path = LUMA_DIR / f"luma-gated-report-{run_stamp}.json"
    write_json(path, report)
    return path


def main() -> None:
    args = parse_args()
    run_stamp = stamp()
    winners = resolve_winners(args)
    missing = [name for name in ("august", "september") if name not in winners]
    if missing:
        path = gated_report(run_stamp, winners, f"Missing selected winner(s): {', '.join(missing)}")
        print(json.dumps({"gated": True, "report": str(path), "missing": missing}, indent=2))
        return

    key = load_luma_api_key()
    overrides = {"august": args.august_event_id, "september": args.september_event_id}
    events = discover_targets(key, overrides)
    before_paths: dict[str, str] = {}
    payloads: dict[str, dict[str, Any]] = {}
    uploads: dict[str, str] = {}

    for target_name, event in events.items():
        before_path = LUMA_DIR / f"{target_name}-before-{run_stamp}.json"
        write_json(before_path, event)
        before_paths[target_name] = str(before_path)
        placeholder_url = f"https://images.lumacdn.com/api-uploads/dry-run/{winners[target_name].name}"
        payloads[target_name] = build_payload(target_name, event, placeholder_url)

    base_report: dict[str, Any] = {
        "generated_at": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat(),
        "dry_run": not args.apply,
        "apply": args.apply,
        "gated": False,
        "search_after": SEARCH_AFTER,
        "search_before": SEARCH_BEFORE,
        "selected_images": {key: str(path) for key, path in winners.items()},
        "events": {
            name: {
                "event_id": event_id(event),
                "name": event.get("name"),
                "start_at": event.get("start_at"),
                "timezone": event.get("timezone"),
                "visibility": event.get("visibility"),
                "url": event.get("url"),
                "before_snapshot": before_paths[name],
            }
            for name, event in events.items()
        },
        "payload_keys": {name: sorted(payload.keys()) for name, payload in payloads.items()},
        "suppress_notifications": True,
    }

    if not args.apply:
        path = LUMA_DIR / f"luma-dry-run-report-{run_stamp}.json"
        write_json(path, base_report)
        print(json.dumps({"dry_run": True, "report": str(path), "payload_keys": base_report["payload_keys"]}, indent=2))
        return

    after_paths: dict[str, str] = {}
    responses: dict[str, Any] = {}
    invariants: dict[str, bool] = {}
    for target_name in ("august", "september"):
        event = events[target_name]
        image_url = upload_image(key, winners[target_name])
        uploads[target_name] = image_url
        payload = build_payload(target_name, event, image_url)
        responses[target_name] = luma_json("/event/update", key, method="POST", payload=payload)
        time.sleep(1)
        after_raw = get_event(key, event_id(event))
        after_event = event_payload(after_raw)
        after_path = LUMA_DIR / f"{target_name}-after-{run_stamp}.json"
        write_json(after_path, after_event)
        after_paths[target_name] = str(after_path)
        validate_readback(target_name, event, after_event, image_url)
        invariants[target_name] = True

    final_report = {
        **base_report,
        "dry_run": False,
        "uploaded_urls": uploads,
        "after_snapshots": after_paths,
        "update_response_keys": {name: sorted(response.keys()) for name, response in responses.items()},
        "invariants_unchanged": invariants,
    }
    report_path = LUMA_DIR / f"luma-apply-report-{run_stamp}.json"
    write_json(report_path, final_report)
    print(json.dumps({"updated": True, "report": str(report_path), "uploaded": uploads}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        sys.exit(f"ERROR: {exc}")
