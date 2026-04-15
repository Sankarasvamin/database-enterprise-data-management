from __future__ import annotations

from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "maindata"
SVG_WIDTH = 2300
SVG_HEIGHT = 1750


TABLES = {
    "male_players": {
        "file": "male_players.csv",
        "title": "male_players.csv",
        "rows": 10_003_590,
        "pk": ["player_id", "fifa_version", "fifa_update"],
        "entity_id": "player_id",
        "distinct_ids": 56_880,
        "category": "male",
        "style": "current",
        "box": (90, 150, 670, 220),
        "notes": [
            "Historical snapshot table",
            "Entity ID player_id is not unique by itself",
        ],
    },
    "male_players_legacy": {
        "file": "male_players (legacy).csv",
        "title": "male_players (legacy).csv",
        "rows": 161_583,
        "pk": ["player_id", "fifa_version", "fifa_update"],
        "entity_id": "player_id",
        "distinct_ids": 49_699,
        "category": "male",
        "style": "legacy",
        "box": (90, 430, 670, 220),
        "notes": [
            "Historical snapshot table",
            "Same entity domain as player snapshots",
        ],
    },
    "male_teams": {
        "file": "male_teams.csv",
        "title": "male_teams.csv",
        "rows": 385_055,
        "pk": ["team_id", "fifa_version", "fifa_update"],
        "entity_id": "team_id",
        "distinct_ids": 1_112,
        "category": "male",
        "style": "team",
        "box": (900, 210, 640, 260),
        "notes": [
            "Historical snapshot table",
            "Strict FK to coaches; other refs use repeated team/player IDs",
        ],
    },
    "male_coaches": {
        "file": "male_coaches.csv",
        "title": "male_coaches.csv",
        "rows": 1_155,
        "pk": ["coach_id"],
        "entity_id": "coach_id",
        "distinct_ids": 1_155,
        "category": "male",
        "style": "coach",
        "box": (1770, 260, 400, 170),
        "notes": [
            "Single-column key is unique",
            "Target of strict FK from male_teams",
        ],
    },
    "female_players": {
        "file": "female_players.csv",
        "title": "female_players.csv",
        "rows": 181_361,
        "pk": ["player_id", "fifa_version", "fifa_update"],
        "entity_id": "player_id",
        "distinct_ids": 1_635,
        "category": "female",
        "style": "current",
        "box": (90, 980, 670, 220),
        "notes": [
            "Historical snapshot table",
            "Entity ID player_id is not unique by itself",
        ],
    },
    "female_players_legacy": {
        "file": "female_players (legacy).csv",
        "title": "female_players (legacy).csv",
        "rows": 3_196,
        "pk": ["player_id", "fifa_version", "fifa_update"],
        "entity_id": "player_id",
        "distinct_ids": 1_266,
        "category": "female",
        "style": "legacy",
        "box": (90, 1260, 670, 220),
        "notes": [
            "Historical snapshot table",
            "Same entity domain as player snapshots",
        ],
    },
    "female_teams": {
        "file": "female_teams.csv",
        "title": "female_teams.csv",
        "rows": 7_941,
        "pk": ["team_id", "fifa_version", "fifa_update"],
        "entity_id": "team_id",
        "distinct_ids": 52,
        "category": "female",
        "style": "team",
        "box": (900, 1040, 640, 260),
        "notes": [
            "Historical snapshot table",
            "Strict FK to coaches; other refs use repeated team/player IDs",
        ],
    },
    "female_coaches": {
        "file": "female_coaches.csv",
        "title": "female_coaches.csv",
        "rows": 52,
        "pk": ["coach_id"],
        "entity_id": "coach_id",
        "distinct_ids": 52,
        "category": "female",
        "style": "coach",
        "box": (1770, 1090, 400, 170),
        "notes": [
            "Single-column key is unique",
            "Target of strict FK from female_teams",
        ],
    },
}


RELATIONSHIPS = [
    {
        "src": "male_players",
        "dst": "male_teams",
        "kind": "entity",
        "label": "club_team_id / nation_team_id -> team_id\nEntity-ID reference\n100% rows, 100% distinct IDs",
        "points": [(760, 260), (840, 260), (840, 300), (900, 300)],
        "label_pos": (785, 165),
    },
    {
        "src": "male_players_legacy",
        "dst": "male_teams",
        "kind": "entity",
        "label": "club_team_id / nation_team_id -> team_id\nEntity-ID reference\n100% rows, 100% distinct IDs",
        "points": [(760, 540), (840, 540), (840, 430), (900, 430)],
        "label_pos": (785, 505),
    },
    {
        "src": "male_teams",
        "dst": "male_coaches",
        "kind": "strict",
        "label": "coach_id -> coach_id\nStrict FK to unique key\n100% rows, 100% distinct IDs",
        "points": [(1540, 340), (1650, 340), (1650, 345), (1770, 345)],
        "label_pos": (1548, 225),
    },
    {
        "src": "male_teams",
        "dst": "male_players",
        "kind": "entity",
        "label": "captain + set-piece role columns -> player_id\nEntity-ID reference\n100% rows, 100% distinct IDs",
        "points": [(900, 390), (830, 390), (830, 330), (760, 330)],
        "label_pos": (785, 355),
    },
    {
        "src": "male_teams",
        "dst": "male_teams",
        "kind": "weak",
        "label": "rival_team -> team_id\nWeak self-reference\n99.88% distinct IDs matched; invalid: 113826",
        "points": [(1200, 210), (1200, 125), (1440, 125), (1440, 210)],
        "label_pos": (1160, 55),
    },
    {
        "src": "female_players",
        "dst": "female_teams",
        "kind": "entity",
        "label": "club_team_id / nation_team_id -> team_id\nEntity-ID reference\n100% rows, 100% distinct IDs",
        "points": [(760, 1090), (840, 1090), (840, 1130), (900, 1130)],
        "label_pos": (785, 995),
    },
    {
        "src": "female_players_legacy",
        "dst": "female_teams",
        "kind": "entity",
        "label": "club_team_id / nation_team_id -> team_id\nEntity-ID reference\n100% rows, 100% distinct IDs",
        "points": [(760, 1370), (840, 1370), (840, 1260), (900, 1260)],
        "label_pos": (785, 1335),
    },
    {
        "src": "female_teams",
        "dst": "female_coaches",
        "kind": "strict",
        "label": "coach_id -> coach_id\nStrict FK to unique key\n100% rows, 100% distinct IDs",
        "points": [(1540, 1170), (1650, 1170), (1650, 1175), (1770, 1175)],
        "label_pos": (1548, 1055),
    },
    {
        "src": "female_teams",
        "dst": "female_players",
        "kind": "entity",
        "label": "captain + set-piece role columns -> player_id\nEntity-ID reference\n100% rows, 100% distinct IDs",
        "points": [(900, 1220), (830, 1220), (830, 1160), (760, 1160)],
        "label_pos": (785, 1185),
    },
    {
        "src": "female_teams",
        "dst": "female_teams",
        "kind": "weak",
        "label": "rival_team -> team_id\nWeak self-reference\n97.44% distinct IDs matched; invalid: 111473",
        "points": [(1200, 1040), (1200, 955), (1440, 955), (1440, 1040)],
        "label_pos": (1160, 885),
    },
]


COLORS = {
    "bg": "#ffffff",
    "male_cluster": "#ffffff",
    "female_cluster": "#ffffff",
    "current": ("#ffffff", "#000000"),
    "legacy": ("#ffffff", "#000000"),
    "team": ("#ffffff", "#000000"),
    "coach": ("#ffffff", "#000000"),
    "text": "#000000",
    "muted": "#000000",
    "strict": "#000000",
    "entity": "#000000",
    "weak": "#000000",
    "note_fill": "#ffffff",
    "note_stroke": "#000000",
}


def fmt_int(value: int) -> str:
    return f"{value:,}"


def wrap_svg_text(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for block in text.split("\n"):
        if not block:
            lines.append("")
            continue
        wrapped = wrap(block, width=width, break_long_words=False, break_on_hyphens=False)
        lines.extend(wrapped or [""])
    return lines


def render_box(table_id: str, meta: dict[str, object]) -> str:
    x, y, w, h = meta["box"]
    fill, stroke = COLORS[meta["style"]]
    dashed = ' stroke-dasharray="8 5"' if meta["style"] == "legacy" else ""
    title = escape(meta["title"])
    pk = ", ".join(meta["pk"])
    lines = [
        f"Rows: {fmt_int(meta['rows'])}",
        f"PK: ({pk})",
        f"Entity ID: {meta['entity_id']} ({fmt_int(meta['distinct_ids'])} distinct)",
    ]
    lines.extend(meta["notes"])
    wrapped_lines: list[str] = []
    for line in lines:
        wrapped_lines.extend(wrap_svg_text(line, width=max(24, int((w - 40) / 11))))

    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="{fill}" stroke="{stroke}" stroke-width="2.5"{dashed} />',
        f'<line x1="{x}" y1="{y + 42}" x2="{x + w}" y2="{y + 42}" stroke="{stroke}" stroke-width="2" />',
        f'<text x="{x + 18}" y="{y + 28}" font-family="Helvetica, Arial, sans-serif" font-size="21" font-weight="700" fill="{COLORS["text"]}">{title}</text>',
    ]

    cursor_y = y + 70
    for line in wrapped_lines:
        parts.append(
            f'<text x="{x + 18}" y="{cursor_y}" font-family="Helvetica, Arial, sans-serif" font-size="17" fill="{COLORS["text"]}">{escape(line)}</text>'
        )
        cursor_y += 26

    return "\n".join(parts)


def render_edge(rel: dict[str, object]) -> str:
    color = COLORS[rel["kind"]]
    points = " ".join(f"{x},{y}" for x, y in rel["points"])
    marker = {
        "strict": "arrowStrict",
        "entity": "arrowEntity",
        "weak": "arrowWeak",
    }[rel["kind"]]
    dash = ""
    if rel["kind"] == "entity":
        dash = ' stroke-dasharray="10 6"'
    elif rel["kind"] == "weak":
        dash = ' stroke-dasharray="5 5"'

    lx, ly = rel["label_pos"]
    label_lines = wrap_svg_text(rel["label"], width=52)
    label_height = 26 + 24 * len(label_lines)
    label_width = 470

    parts = [
        f'<polyline fill="none" points="{points}" stroke="{color}" stroke-width="3.5"{dash} marker-end="url(#{marker})" />',
        f'<rect x="{lx - 10}" y="{ly - 20}" width="{label_width}" height="{label_height}" rx="12" fill="{COLORS["note_fill"]}" stroke="{color}" stroke-width="1.4" opacity="0.96" />',
    ]
    for idx, line in enumerate(label_lines):
        parts.append(
            f'<text x="{lx}" y="{ly + idx * 24}" font-family="Helvetica, Arial, sans-serif" font-size="17" fill="{COLORS["text"]}">{escape(line)}</text>'
        )
    return "\n".join(parts)


def build_svg() -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}">',
        f'<rect x="0" y="0" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" fill="{COLORS["bg"]}" />',
        "<defs>",
        f'<marker id="arrowStrict" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="{COLORS["strict"]}" /></marker>',
        f'<marker id="arrowEntity" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="{COLORS["entity"]}" /></marker>',
        f'<marker id="arrowWeak" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="{COLORS["weak"]}" /></marker>',
        "</defs>",
        '<rect x="40" y="40" width="2220" height="770" rx="28" fill="#ffffff" stroke="#000000" stroke-width="2" />',
        '<rect x="40" y="900" width="2220" height="770" rx="28" fill="#ffffff" stroke="#000000" stroke-width="2" />',
        '<text x="80" y="95" font-family="Helvetica, Arial, sans-serif" font-size="34" font-weight="700" fill="#000000">Male section</text>',
        '<text x="80" y="955" font-family="Helvetica, Arial, sans-serif" font-size="34" font-weight="700" fill="#000000">Female section</text>',
        '<text x="1680" y="95" font-family="Helvetica, Arial, sans-serif" font-size="28" font-weight="700" fill="#000000">Line style</text>',
        '<rect x="1660" y="115" width="560" height="140" rx="18" fill="#ffffff" stroke="#000000" stroke-width="1.8" />',
        '<line x1="1690" y1="155" x2="1780" y2="155" stroke="#000000" stroke-width="3.5" marker-end="url(#arrowStrict)" />',
        '<line x1="1690" y1="195" x2="1780" y2="195" stroke="#000000" stroke-width="3.5" stroke-dasharray="10 6" marker-end="url(#arrowEntity)" />',
        '<line x1="1690" y1="235" x2="1780" y2="235" stroke="#000000" stroke-width="3.5" stroke-dasharray="5 5" marker-end="url(#arrowWeak)" />',
        '<text x="1800" y="160" font-family="Helvetica, Arial, sans-serif" font-size="18" fill="#000000">Strict FK to unique target key</text>',
        '<text x="1800" y="200" font-family="Helvetica, Arial, sans-serif" font-size="18" fill="#000000">Entity-ID reference across snapshot rows</text>',
        '<text x="1800" y="240" font-family="Helvetica, Arial, sans-serif" font-size="18" fill="#000000">Weak self-reference with unmatched IDs</text>',
        '<rect x="90" y="825" width="2130" height="52" rx="12" fill="#ffffff" stroke="#000000" stroke-width="1.5" />',
        '<text x="115" y="858" font-family="Helvetica, Arial, sans-serif" font-size="19" fill="#000000">league_id and nationality_id are not drawn as FK edges because maindata has no league or country dimension table. Current and legacy files share entity IDs but do not form direct FK links.</text>',
    ]

    for table_id, meta in TABLES.items():
        parts.append(render_box(table_id, meta))

    for rel in RELATIONSHIPS:
        parts.append(render_edge(rel))

    parts.append("</svg>")
    return "\n".join(parts)


def build_markdown() -> str:
    lines = [
        "# ER Analysis For `maindata`",
        "",
        "This report summarizes the eight CSV tables in `maindata` and the foreign-key analysis that is reflected in the ER diagram.",
        "",
        "## Key interpretation rule",
        "",
        "- `male_players.csv`, `male_players (legacy).csv`, `female_players.csv`, `female_players (legacy).csv`, `male_teams.csv`, and `female_teams.csv` are snapshot tables.",
        "- In those snapshot tables, `player_id` and `team_id` are business entity IDs, not unique row IDs.",
        "- The minimal row-level key for those tables is `(id, fifa_version, fifa_update)`.",
        "- Because of that, references to `player_id` or `team_id` alone are shown as entity-level references in the ER diagram rather than strict relational foreign keys.",
        "",
        "## Table summary",
        "",
        "| Table | Rows | Row-level PK | Entity ID | Distinct entity IDs |",
        "| --- | ---: | --- | --- | ---: |",
    ]

    table_order = [
        "male_players",
        "male_players_legacy",
        "male_teams",
        "male_coaches",
        "female_players",
        "female_players_legacy",
        "female_teams",
        "female_coaches",
    ]
    for key in table_order:
        table = TABLES[key]
        lines.append(
            f"| `{table['file']}` | {fmt_int(table['rows'])} | `({', '.join(table['pk'])})` | `{table['entity_id']}` | {fmt_int(table['distinct_ids'])} |"
        )

    lines.extend(
        [
            "",
            "## Relationship analysis",
            "",
            "| Source | Target | Columns | Type in ER | Evidence |",
            "| --- | --- | --- | --- | --- |",
            "| `male_teams.csv` | `male_coaches.csv` | `coach_id -> coach_id` | Strict FK | 100% row match and 100% distinct-ID match; target key is unique. |",
            "| `female_teams.csv` | `female_coaches.csv` | `coach_id -> coach_id` | Strict FK | 100% row match and 100% distinct-ID match; target key is unique. |",
            "| `male_players.csv` | `male_teams.csv` | `club_team_id`, `nation_team_id` -> `team_id` | Entity-ID reference | 100% row match and 100% distinct-ID match, but `team_id` is not unique in `male_teams.csv`. |",
            "| `male_players (legacy).csv` | `male_teams.csv` | `club_team_id`, `nation_team_id` -> `team_id` | Entity-ID reference | 100% row match and 100% distinct-ID match, but `team_id` is not unique in `male_teams.csv`. |",
            "| `female_players.csv` | `female_teams.csv` | `club_team_id`, `nation_team_id` -> `team_id` | Entity-ID reference | 100% row match and 100% distinct-ID match, but `team_id` is not unique in `female_teams.csv`. |",
            "| `female_players (legacy).csv` | `female_teams.csv` | `club_team_id`, `nation_team_id` -> `team_id` | Entity-ID reference | 100% row match and 100% distinct-ID match, but `team_id` is not unique in `female_teams.csv`. |",
            "| `male_teams.csv` | `male_players.csv` | `captain`, `short_free_kick`, `long_free_kick`, `left_short_free_kick`, `right_short_free_kick`, `penalties`, `left_corner`, `right_corner` -> `player_id` | Entity-ID reference | 100% row match and 100% distinct-ID match, but `player_id` is not unique in `male_players.csv`. |",
            "| `female_teams.csv` | `female_players.csv` | `captain`, `short_free_kick`, `long_free_kick`, `left_short_free_kick`, `right_short_free_kick`, `penalties`, `left_corner`, `right_corner` -> `player_id` | Entity-ID reference | 100% row match and 100% distinct-ID match, but `player_id` is not unique in `female_players.csv`. |",
            "| `male_teams.csv` | `male_teams.csv` | `rival_team -> team_id` | Weak self-reference | Almost complete coverage, but one unmatched distinct ID remains: `113826`. |",
            "| `female_teams.csv` | `female_teams.csv` | `rival_team -> team_id` | Weak self-reference | Coverage is high but not perfect; one unmatched distinct ID remains: `111473`. |",
            "",
            "## Relationships deliberately not drawn as foreign keys",
            "",
            "- `league_id` is present in players and teams, but `maindata` has no league dimension table.",
            "- `nationality_id` is present in players, teams, and coaches, but `maindata` has no country dimension table.",
            "- Current and legacy CSV pairs share the same business entity space, but there is no direct FK between the separate files.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    svg_path = OUT_DIR / "ER_diagram.svg"
    md_path = OUT_DIR / "ER_analysis.md"
    svg_path.write_text(build_svg(), encoding="utf-8")
    md_path.write_text(build_markdown(), encoding="utf-8")
    print(f"Wrote {svg_path}")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()
