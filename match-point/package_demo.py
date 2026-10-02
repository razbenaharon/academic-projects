"""Losslessly package the original standalone HTML for GitHub (stdlib only)."""

import argparse
import json
from pathlib import Path
import re


def package(source: str) -> str:
    match_start = re.search(r"const allMatches\s*=\s*", source).end()
    fixtures, _ = json.JSONDecoder().raw_decode(source[match_start:])
    dates = [fixture["date"] for fixture in fixtures]
    first_date, last_date = min(dates), max(dates)
    start = re.search(r"const allRecs\s*=\s*", source).end()
    recommendations, length = json.JSONDecoder().raw_decode(source[start:])
    fields = list(next(iter(recommendations.values()))[0])
    values = [[] for _ in fields]
    lookups = [{} for _ in fields]
    matches = {}
    for match, rows in recommendations.items():
        matches[match] = []
        for row in rows:
            if list(row) != fields:
                raise ValueError("Recommendation fields differ; update the packager.")
            indices = []
            for i, field in enumerate(fields):
                value = row[field]
                key = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
                if key not in lookups[i]:
                    lookups[i][key] = len(values[i])
                    values[i].append(value)
                indices.append(lookups[i][key])
            matches[match].append(indices)

    # Check every record before writing, including order, numbers and availability.
    for match, rows in matches.items():
        restored = [
            {field: values[i][row[i]] for i, field in enumerate(fields)}
            for row in rows
        ]
        if restored != recommendations[match]:
            raise ValueError(f"Lossless verification failed for {match}")

    packed = json.dumps(
        {"fields": fields, "values": values, "matches": matches},
        ensure_ascii=False, separators=(",", ":"),
    ).replace("<", "\\u003c")
    replacement = """(() => {
        // Dictionary encoding preserves every original recommendation.
        const packed = PACKED;
        return Object.fromEntries(Object.entries(packed.matches).map(([id, rows]) =>
            [id, rows.map(row => Object.fromEntries(packed.fields.map((field, i) =>
                [field, packed.values[i][row[i]]])))]));
    })()""".replace("PACKED", packed)
    result = source[:start] + replacement + source[start + length:]
    result = result.replace(
        '<div class="card" id="step1">',
        '<div class="card" role="note">Historical course demo: fixtures span '
        f'{first_date} to {last_date}. Prices, availability and stadium guides '
        'are saved project data. Booking is simulated; no reservation or email '
        'is sent.</div>\n\n<div class="card" id="step1">',
        1,
    )
    result = result.replace("Booking Confirmed!", "Demo Booking!")
    result = result.replace(
        "Thank you for choosing MatchPoint. Your booking has been received.",
        "This is a demonstration. No reservation has been made.",
    )
    result = result.replace("Confirmation sent to your email", "Demo only — no email sent")
    print(f"Verified {len(matches):,} match groups / "
          f"{sum(map(len, matches.values())):,} recommendation records")
    return "\n".join(line.rstrip() for line in result.splitlines()) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.source.resolve() == args.output.resolve():
        parser.error("Use a separate output path to preserve the original.")
    source = args.source.read_text(encoding="utf-8")
    args.output.write_text(package(source), encoding="utf-8", newline="\n")
    print(f"HTML: {args.source.stat().st_size:,} -> {args.output.stat().st_size:,} bytes")
