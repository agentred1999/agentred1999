#!/usr/bin/env python3
"""
generate_stats.py — draws self-hosted, matrix-themed GitHub stats SVGs.

Stdlib only. No third-party dependencies, so nothing to break in CI.

Env vars required:
  GITHUB_TOKEN   provided automatically by Actions (secrets.GITHUB_TOKEN)
  GH_LOGIN       provided automatically by Actions (github.repository_owner)

Outputs (written to repo root):
  hero.svg    total contributions + weekly sparkline
  streak.svg  current + longest streak, with date ranges
  langs.svg   top languages by bytes and by repo count
  year.svg    365-day grid, one char per day, monochrome ramp
"""

import json
import os
import sys
import urllib.request
import datetime as dt

# ---------------------------------------------------------------------------
# theme
# ---------------------------------------------------------------------------

BG = "#0d1117"
GREEN = "#00FF41"
GREEN_DIM = "#0a5c1c"
GREEN_MID = "#12a83a"
GRID_LINE = "#1a2b1a"
TEXT_MUTED = "#3fae55"
FONT = "'Fira Code', 'JetBrains Mono', 'Consolas', monospace"

RAMP = " .:-=+*#%@"  # blank -> dense, used for year.svg cell fill intensity via opacity steps

# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------

API_URL = "https://api.github.com/graphql"


def gh_graphql(query: str, variables: dict) -> dict:
    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "matrix-stats-generator",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    if "errors" in payload:
        raise RuntimeError(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def utc_window():
    """Pin the contribution window to whole UTC days so two runs on the
    same calendar day always bucket identically."""
    today = dt.datetime.now(dt.timezone.utc).replace(
        hour=23, minute=59, second=59, microsecond=0
    )
    start = (today - dt.timedelta(days=364)).replace(hour=0, minute=0, second=0)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    return start.strftime(fmt), today.strftime(fmt)


CONTRIB_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount }
        }
      }
    }
  }
}
"""

LANGS_QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    repositories(first: 100, after: $cursor, privacy: PUBLIC, isFork: false,
                  ownerAffiliations: [OWNER]) {
      pageInfo { hasNextPage endCursor }
      nodes {
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch_contributions(login):
    frm, to = utc_window()
    data = gh_graphql(CONTRIB_QUERY, {"login": login, "from": frm, "to": to})
    cal = data["user"]["contributionsCollection"]["contributionCalendar"]
    days = []
    for week in cal["weeks"]:
        for d in week["contributionDays"]:
            days.append((d["date"], d["contributionCount"]))
    days.sort(key=lambda x: x[0])
    return cal["totalContributions"], days


def fetch_languages(login):
    totals = {}          # name -> total bytes
    repo_counts = {}      # name -> number of repos it appears in
    colors = {}
    cursor = None
    while True:
        data = gh_graphql(LANGS_QUERY, {"login": login, "cursor": cursor})
        repos = data["user"]["repositories"]
        for repo in repos["nodes"]:
            seen_in_this_repo = set()
            for edge in repo["languages"]["edges"]:
                name = edge["node"]["name"]
                colors[name] = edge["node"]["color"] or GREEN
                totals[name] = totals.get(name, 0) + edge["size"]
                seen_in_this_repo.add(name)
            for name in seen_in_this_repo:
                repo_counts[name] = repo_counts.get(name, 0) + 1
        if not repos["pageInfo"]["hasNextPage"]:
            break
        cursor = repos["pageInfo"]["endCursor"]
    return totals, repo_counts, colors


# ---------------------------------------------------------------------------
# derived stats
# ---------------------------------------------------------------------------

def compute_streaks(days):
    """days: list of (date_str, count) ascending. Returns current + longest
    streak lengths and their date ranges."""
    longest = cur = 0
    longest_range = cur_range = None
    run_start = None

    for date_str, count in days:
        if count > 0:
            if run_start is None:
                run_start = date_str
            cur += 1
            cur_range = (run_start, date_str)
            if cur > longest:
                longest = cur
                longest_range = cur_range
        else:
            cur = 0
            run_start = None

    # "current" streak only counts if it runs up to today or yesterday
    today = dt.date.today()
    last_active_date = dt.date.fromisoformat(days[-1][0]) if days else today
    gap = (today - last_active_date).days
    if gap > 1:
        cur = 0
        cur_range = None

    return {
        "current": cur,
        "current_range": cur_range,
        "longest": longest,
        "longest_range": longest_range,
    }


def weekly_sparkline(days, weeks=12):
    """Aggregate the trailing N weeks (7-day buckets) into totals."""
    buckets = []
    chunk = []
    for date_str, count in days:
        chunk.append(count)
        if len(chunk) == 7:
            buckets.append(sum(chunk))
            chunk = []
    if chunk:
        buckets.append(sum(chunk))
    return buckets[-weeks:]


def fmt_date(iso):
    return dt.date.fromisoformat(iso).strftime("%b %d, %Y")


# ---------------------------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------------------------

def svg_shell(width, height, body, title):
    return f'''<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}"
     xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{title}">
  <title>{title}</title>
  <style>
    .bg  {{ fill: {BG}; }}
    .lbl {{ fill: {TEXT_MUTED}; font: 12px {FONT}; }}
    .val {{ fill: {GREEN}; font: bold 15px {FONT}; }}
    .hd  {{ fill: {GREEN}; font: bold 13px {FONT}; letter-spacing: 1px; }}
  </style>
  <rect class="bg" width="{width}" height="{height}" rx="6"/>
{body}
</svg>'''


def sparkline_path(values, x0, y0, w, h):
    if not values:
        return ""
    vmax = max(values) or 1
    n = len(values)
    step = w / max(n - 1, 1)
    pts = []
    for i, v in enumerate(values):
        x = x0 + i * step
        y = y0 + h - (v / vmax) * h
        pts.append((x, y))
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2" fill="{GREEN}"/>' for x, y in pts
    )
    return f'<path d="{d}" fill="none" stroke="{GREEN}" stroke-width="1.5"/>{dots}'


# ---------------------------------------------------------------------------
# hero.svg
# ---------------------------------------------------------------------------

def build_hero(total, days):
    spark = weekly_sparkline(days, weeks=12)
    w, h = 460, 160
    body = f'''  <text x="20" y="34" class="hd">CONTRIBUTIONS // LAST 365 DAYS</text>
  <text x="20" y="70" class="val" font-size="34">{total:,}</text>
  <text x="20" y="90" class="lbl">total commits, PRs, reviews &amp; issues</text>
  <text x="20" y="118" class="lbl">last 12 weeks</text>
  {sparkline_path(spark, 20, 125, w - 40, 20)}
'''
    return svg_shell(w, h, body, "GitHub contribution summary")


# ---------------------------------------------------------------------------
# streak.svg
# ---------------------------------------------------------------------------

def build_streak(streaks):
    w, h = 460, 140
    cur = streaks["current"]
    lon = streaks["longest"]
    cur_range = streaks["current_range"]
    lon_range = streaks["longest_range"]

    cur_sub = (
        f"{fmt_date(cur_range[0])} → {fmt_date(cur_range[1])}"
        if cur_range else "no active streak"
    )
    lon_sub = (
        f"{fmt_date(lon_range[0])} → {fmt_date(lon_range[1])}"
        if lon_range else "—"
    )

    body = f'''  <text x="20" y="30" class="hd">STREAK</text>

  <text x="20" y="65" class="val" font-size="28">{cur}</text>
  <text x="90" y="60" class="lbl">day current streak</text>
  <text x="90" y="76" class="lbl" fill="{GREEN_MID}">{cur_sub}</text>

  <line x1="20" y1="92" x2="440" y2="92" stroke="{GRID_LINE}"/>

  <text x="20" y="120" class="val" font-size="28">{lon}</text>
  <text x="90" y="115" class="lbl">day longest streak</text>
  <text x="90" y="131" class="lbl" fill="{GREEN_MID}">{lon_sub}</text>
'''
    return svg_shell(w, h, body, "GitHub contribution streaks")


# ---------------------------------------------------------------------------
# langs.svg
# ---------------------------------------------------------------------------

def build_langs(totals, repo_counts, top_n=6):
    w = 460
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    grand_total = sum(totals.values()) or 1
    row_h = 26
    h = 50 + row_h * len(ranked)

    rows = []
    y = 60
    bar_x, bar_w = 150, 250
    for name, size in ranked:
        pct = size / grand_total
        rows.append(
            f'  <text x="20" y="{y}" class="lbl" fill="{GREEN}">{name}</text>'
        )
        rows.append(
            f'  <rect x="{bar_x}" y="{y-11}" width="{bar_w}" height="10" '
            f'fill="{GRID_LINE}" rx="2"/>'
        )
        rows.append(
            f'  <rect x="{bar_x}" y="{y-11}" width="{bar_w * pct:.1f}" height="10" '
            f'fill="{GREEN}" rx="2"/>'
        )
        rows.append(
            f'  <text x="{bar_x + bar_w + 10}" y="{y}" class="lbl">'
            f'{pct*100:.1f}%</text>'
        )
        rows.append(
            f'  <text x="{bar_x + bar_w + 55}" y="{y}" class="lbl" '
            f'fill="{TEXT_MUTED}">{repo_counts.get(name, 0)} repos</text>'
        )
        y += row_h

    body = f'  <text x="20" y="30" class="hd">TOP LANGUAGES</text>\n' + "\n".join(rows)
    return svg_shell(w, h, body, "Top languages by bytes and repo count")


# ---------------------------------------------------------------------------
# year.svg — one char per day, using the monochrome ramp
# ---------------------------------------------------------------------------

def build_year(days):
    cell = 11
    gap = 2
    cols = (len(days) // 7) + 1
    w = 40 + cols * (cell + gap)
    h = 40 + 7 * (cell + gap) + 20

    counts = [c for _, c in days]
    vmax = max(counts) if counts else 1
    vmax = max(vmax, 1)

    cells = []
    # lay out by week columns, Sunday-first rows, matching GitHub's own grid
    col = row = 0
    first_weekday = dt.date.fromisoformat(days[0][0]).weekday() if days else 0
    # Python weekday(): Monday=0 ... Sunday=6; GitHub grid is Sunday-first
    row = (first_weekday + 1) % 7

    for date_str, count in days:
        intensity = 0 if count == 0 else min(4, 1 + int((count / vmax) * 3))
        opacity = [0.08, 0.35, 0.55, 0.75, 1.0][intensity]
        x = 30 + col * (cell + gap)
        y = 30 + row * (cell + gap)
        cells.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
            f'fill="{GREEN}" opacity="{opacity}"><title>{date_str}: {count}</title></rect>'
        )
        row += 1
        if row == 7:
            row = 0
            col += 1

    body = f'  <text x="20" y="18" class="hd">THE LAST 365 DAYS</text>\n' + "\n".join(
        f"  {c}" for c in cells
    )
    return svg_shell(w, h, body, "365-day contribution grid")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"wrote {path}")


def main():
    login = os.environ["GH_LOGIN"]

    total, days = fetch_contributions(login)
    streaks = compute_streaks(days)
    totals, repo_counts, _colors = fetch_languages(login)

    write("hero.svg", build_hero(total, days))
    write("streak.svg", build_streak(streaks))
    write("langs.svg", build_langs(totals, repo_counts))
    write("year.svg", build_year(days))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        print(f"generate_stats.py failed: {exc}", file=sys.stderr)
        sys.exit(1)
