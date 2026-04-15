from __future__ import annotations

import csv
import re
from pathlib import Path
from textwrap import wrap
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "maindata"


TABLE_META = {
    "male_players.csv": {
        "section": "male",
        "entity": "player",
        "pk": ("player_id", "fifa_version", "fifa_update"),
    },
    "male_players (legacy).csv": {
        "section": "male",
        "entity": "player_legacy",
        "pk": ("player_id", "fifa_version", "fifa_update"),
    },
    "male_teams.csv": {
        "section": "male",
        "entity": "team",
        "pk": ("team_id", "fifa_version", "fifa_update"),
    },
    "male_coaches.csv": {
        "section": "male",
        "entity": "coach",
        "pk": ("coach_id",),
    },
    "female_players.csv": {
        "section": "female",
        "entity": "player",
        "pk": ("player_id", "fifa_version", "fifa_update"),
    },
    "female_players (legacy).csv": {
        "section": "female",
        "entity": "player_legacy",
        "pk": ("player_id", "fifa_version", "fifa_update"),
    },
    "female_teams.csv": {
        "section": "female",
        "entity": "team",
        "pk": ("team_id", "fifa_version", "fifa_update"),
    },
    "female_coaches.csv": {
        "section": "female",
        "entity": "coach",
        "pk": ("coach_id",),
    },
}


ROLE_COLUMNS = {
    "captain",
    "short_free_kick",
    "long_free_kick",
    "left_short_free_kick",
    "right_short_free_kick",
    "penalties",
    "left_corner",
    "right_corner",
}


REFERENCE_RULES = {
    ("male_players.csv", "club_team_id"): ("实体引用", "male_teams.csv.team_id"),
    ("male_players.csv", "nation_team_id"): ("实体引用", "male_teams.csv.team_id"),
    ("male_players (legacy).csv", "club_team_id"): ("实体引用", "male_teams.csv.team_id"),
    ("male_players (legacy).csv", "nation_team_id"): ("实体引用", "male_teams.csv.team_id"),
    ("female_players.csv", "club_team_id"): ("实体引用", "female_teams.csv.team_id"),
    ("female_players.csv", "nation_team_id"): ("实体引用", "female_teams.csv.team_id"),
    ("female_players (legacy).csv", "club_team_id"): ("实体引用", "female_teams.csv.team_id"),
    ("female_players (legacy).csv", "nation_team_id"): ("实体引用", "female_teams.csv.team_id"),
    ("male_teams.csv", "coach_id"): ("严格FK", "male_coaches.csv.coach_id"),
    ("female_teams.csv", "coach_id"): ("严格FK", "female_coaches.csv.coach_id"),
    ("male_teams.csv", "rival_team"): ("弱自引用", "male_teams.csv.team_id"),
    ("female_teams.csv", "rival_team"): ("弱自引用", "female_teams.csv.team_id"),
}

for table_name in ("male_teams.csv", "female_teams.csv"):
    target = "male_players.csv.player_id" if table_name.startswith("male") else "female_players.csv.player_id"
    for col in ROLE_COLUMNS:
        REFERENCE_RULES[(table_name, col)] = ("实体引用", target)


EXACT_DESCRIPTIONS = {
    "player_id": "Player business identifier.",
    "team_id": "Team business identifier.",
    "coach_id": "Coach business identifier.",
    "player_url": "Relative URL for the player profile page.",
    "team_url": "Relative URL for the team profile page.",
    "coach_url": "Relative URL for the coach profile page.",
    "fifa_version": "Game version number that identifies the yearly edition.",
    "fifa_update": "In-version update sequence number.",
    "fifa_update_date": "Release date of the specific FIFA update.",
    "short_name": "Short display name.",
    "long_name": "Full display name.",
    "team_name": "Displayed team name.",
    "dob": "Date of birth.",
    "nationality_id": "Country identifier; local country table is not present in maindata.",
    "nationality_name": "Country name text.",
    "face_url": "Portrait image URL.",
    "player_positions": "Primary and secondary player positions.",
    "overall": "Overall rating.",
    "potential": "Potential rating.",
    "value_eur": "Estimated market value in EUR.",
    "wage_eur": "Estimated wage in EUR.",
    "age": "Age in years at the snapshot date.",
    "height_cm": "Height in centimeters.",
    "weight_kg": "Weight in kilograms.",
    "league_id": "League identifier; local league table is not present in maindata.",
    "league_name": "League name text.",
    "league_level": "League tier level.",
    "club_team_id": "Referenced club team business ID.",
    "club_name": "Club name text.",
    "club_position": "Player role inside the club lineup.",
    "club_jersey_number": "Club jersey number.",
    "club_loaned_from": "Source club when the player is on loan.",
    "club_joined_date": "Date when the player joined the club.",
    "club_contract_valid_until_year": "Club contract end year.",
    "nation_team_id": "Referenced national team business ID.",
    "nation_position": "Player role inside the national team lineup.",
    "nation_jersey_number": "National team jersey number.",
    "preferred_foot": "Preferred foot.",
    "weak_foot": "Weak-foot rating.",
    "skill_moves": "Skill-move rating.",
    "international_reputation": "International reputation rating.",
    "work_rate": "Attacking and defensive work rate.",
    "body_type": "Body type descriptor.",
    "real_face": "Whether the player has a real face scan.",
    "release_clause_eur": "Release clause amount in EUR.",
    "player_tags": "Tagged special roles or archetypes.",
    "player_traits": "Detailed player traits.",
    "pace": "Aggregate pace rating.",
    "shooting": "Aggregate shooting rating.",
    "passing": "Aggregate passing rating.",
    "dribbling": "Aggregate dribbling rating.",
    "defending": "Aggregate defending rating.",
    "physic": "Aggregate physical rating.",
    "home_stadium": "Home stadium name.",
    "rival_team": "Referenced rival team business ID.",
    "international_prestige": "International prestige score.",
    "domestic_prestige": "Domestic prestige score.",
    "transfer_budget_eur": "Transfer budget in EUR.",
    "club_worth_eur": "Estimated club worth in EUR.",
    "starting_xi_average_age": "Average age of the starting eleven.",
    "whole_team_average_age": "Average age of the full squad.",
    "captain": "Captain player business ID.",
    "short_free_kick": "Assigned short free-kick taker ID.",
    "long_free_kick": "Assigned long free-kick taker ID.",
    "left_short_free_kick": "Assigned left short free-kick taker ID.",
    "right_short_free_kick": "Assigned right short free-kick taker ID.",
    "penalties": "Assigned penalty taker ID.",
    "left_corner": "Assigned left corner taker ID.",
    "right_corner": "Assigned right corner taker ID.",
}


POSITION_CODES = {
    "ls", "st", "rs", "lw", "lf", "cf", "rf", "rw", "lam", "cam", "ram",
    "lm", "lcm", "cm", "rcm", "rm", "lwb", "ldm", "cdm", "rdm", "rwb",
    "lb", "lcb", "cb", "rcb", "rb", "gk",
}


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INT_RE = re.compile(r"^-?\d+$")
DEC_RE = re.compile(r"^-?\d+\.\d+$")
PROJ_RE = re.compile(r"^\d{1,3}([+-]\d{1,2})?$")
URLISH_RE = re.compile(r"^(https?://|/).+")


def wrap_text(text: str, width: int) -> list[str]:
    lines: list[str] = []
    for block in text.split("\n"):
        wrapped = wrap(block, width=width, break_long_words=False, break_on_hyphens=False) or [""]
        lines.extend(wrapped)
    return lines


def read_headers(table_path: Path) -> list[str]:
    with table_path.open("r", encoding="utf-8-sig", newline="") as f:
        return next(csv.reader(f))


def collect_samples(table_path: Path, limit_rows: int = 4000, max_per_column: int = 24) -> dict[str, list[str]]:
    with table_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        samples = {field: [] for field in (reader.fieldnames or [])}
        for idx, row in enumerate(reader):
            if idx >= limit_rows:
                break
            if not row:
                continue
            for field, value in row.items():
                if value is None:
                    continue
                value = value.strip()
                if not value:
                    continue
                if len(samples[field]) < max_per_column:
                    samples[field].append(value)
        return samples


def infer_type(values: list[str]) -> str:
    if not values:
        return "unknown"
    unique_values = set(values)
    if unique_values.issubset({"Yes", "No", "TRUE", "FALSE", "True", "False"}):
        return "boolean_text"
    if all(DATE_RE.match(v) for v in values):
        return "date"
    if all(URLISH_RE.match(v) for v in values):
        return "url_or_path"
    if all(PROJ_RE.match(v) and ("+" in v or "-" in v) for v in values):
        return "position_rating_projection"
    if all(INT_RE.match(v) for v in values):
        return "integer"
    if all(INT_RE.match(v) or DEC_RE.match(v) for v in values):
        return "decimal"
    if len(unique_values) <= 12 and all(len(v) <= 24 for v in values):
        return "coded_text"
    return "text"


def describe_field(field_name: str) -> str:
    if field_name in EXACT_DESCRIPTIONS:
        return EXACT_DESCRIPTIONS[field_name]
    if field_name in POSITION_CODES:
        return f"Projected rating for the {field_name.upper()} position."
    if field_name.startswith("attacking_"):
        return f"Detailed attacking metric: {field_name.removeprefix('attacking_').replace('_', ' ')}."
    if field_name.startswith("skill_"):
        return f"Detailed skill metric: {field_name.removeprefix('skill_').replace('_', ' ')}."
    if field_name.startswith("movement_"):
        return f"Detailed movement metric: {field_name.removeprefix('movement_').replace('_', ' ')}."
    if field_name.startswith("power_"):
        return f"Detailed power metric: {field_name.removeprefix('power_').replace('_', ' ')}."
    if field_name.startswith("mentality_"):
        return f"Detailed mentality metric: {field_name.removeprefix('mentality_').replace('_', ' ')}."
    if field_name.startswith("defending_"):
        return f"Detailed defending metric: {field_name.removeprefix('defending_').replace('_', ' ')}."
    if field_name.startswith("goalkeeping_"):
        return f"Detailed goalkeeping metric: {field_name.removeprefix('goalkeeping_').replace('_', ' ')}."
    if field_name.startswith("def_"):
        return f"Team defensive tactic attribute: {field_name.removeprefix('def_').replace('_', ' ')}."
    if field_name.startswith("off_"):
        return f"Team offensive tactic attribute: {field_name.removeprefix('off_').replace('_', ' ')}."
    if field_name.startswith("build_up_play_"):
        return f"Build-up play setting: {field_name.removeprefix('build_up_play_').replace('_', ' ')}."
    if field_name.startswith("chance_creation_"):
        return f"Chance-creation setting: {field_name.removeprefix('chance_creation_').replace('_', ' ')}."
    if field_name.endswith("_url"):
        return "URL or relative path attribute."
    if field_name.endswith("_id"):
        return "Identifier or referenced identifier field."
    return f"General attribute: {field_name.replace('_', ' ')}."


def classify_role(table_name: str, field_name: str) -> tuple[str, str]:
    pk = TABLE_META[table_name]["pk"]
    if field_name in pk:
        return "PK", ""
    if (table_name, field_name) in REFERENCE_RULES:
        return REFERENCE_RULES[(table_name, field_name)]
    if field_name in {"nationality_id", "league_id"}:
        target = "external dimension not included in maindata"
        return "外部维度引用", target
    if field_name.endswith("_id"):
        return "业务ID/标识字段", ""
    return "普通属性", ""


def build_data_structure_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for table_name in sorted(TABLE_META):
        table_path = DATA_DIR / table_name
        headers = read_headers(table_path)
        samples = collect_samples(table_path)
        for ordinal, field_name in enumerate(headers, start=1):
            field_type = infer_type(samples.get(field_name, []))
            role, ref_target = classify_role(table_name, field_name)
            rows.append(
                [
                    TABLE_META[table_name]["section"],
                    table_name,
                    str(ordinal),
                    field_name,
                    field_type,
                    role,
                    ref_target,
                    describe_field(field_name),
                ]
            )
    return rows


def write_data_structure(rows: list[list[str]]) -> tuple[Path, Path]:
    csv_path = DATA_DIR / "data_structure_table.csv"
    md_path = DATA_DIR / "data_structure_table.md"
    header = [
        "section",
        "table_name",
        "column_order",
        "field_name",
        "inferred_type",
        "key_role",
        "reference_target",
        "description",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    lines = [
        "# Data Structure Table",
        "",
        "Full field-level structure for the 8 CSV tables in `maindata`.",
        "",
        "| section | table_name | column_order | field_name | inferred_type | key_role | reference_target | description |",
        "| --- | --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        safe = [cell.replace("|", "\\|") for cell in row]
        lines.append("| " + " | ".join(safe) + " |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, md_path


def svg_header(width: int, height: int) -> list[str]:
    return [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff" />',
        "<defs>",
        '<marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#000000" /></marker>',
        "</defs>",
    ]


def svg_footer() -> str:
    return "</svg>"


def draw_rect(x: int, y: int, w: int, h: int, title: str, body: list[str], rounded: int = 18, dash: str = "") -> str:
    title_lines = wrap_text(title, 26)
    body_lines: list[str] = []
    for line in body:
        body_lines.extend(wrap_text(line, max(24, int((w - 36) / 10))))
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rounded}" fill="#ffffff" stroke="#000000" stroke-width="2.5"{dash} />',
        f'<line x1="{x}" y1="{y + 46}" x2="{x + w}" y2="{y + 46}" stroke="#000000" stroke-width="2" />',
    ]
    text_y = y + 28
    for idx, line in enumerate(title_lines):
        parts.append(
            f'<text x="{x + 16}" y="{text_y + idx * 22}" font-family="Helvetica, Arial, sans-serif" font-size="22" font-weight="700" fill="#000000">{escape(line)}</text>'
        )
    cursor_y = y + 76
    for line in body_lines:
        parts.append(
            f'<text x="{x + 16}" y="{cursor_y}" font-family="Helvetica, Arial, sans-serif" font-size="18" fill="#000000">{escape(line)}</text>'
        )
        cursor_y += 24
    return "\n".join(parts)


def draw_process(cx: int, cy: int, rx: int, ry: int, title: str, lines: list[str]) -> str:
    text_lines = wrap_text(title, 22)
    for line in lines:
        text_lines.extend(wrap_text(line, 24))
    parts = [
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#ffffff" stroke="#000000" stroke-width="2.5" />'
    ]
    start_y = cy - (len(text_lines) - 1) * 11
    for idx, line in enumerate(text_lines):
        parts.append(
            f'<text x="{cx}" y="{start_y + idx * 22}" text-anchor="middle" font-family="Helvetica, Arial, sans-serif" font-size="18" fill="#000000">{escape(line)}</text>'
        )
    return "\n".join(parts)


def draw_arrow(points: list[tuple[int, int]], label: str, lx: int, ly: int, dash: str = "") -> str:
    points_str = " ".join(f"{x},{y}" for x, y in points)
    label_lines = wrap_text(label, 34)
    parts = [
        f'<polyline fill="none" points="{points_str}" stroke="#000000" stroke-width="3"{dash} marker-end="url(#arrow)" />',
        f'<rect x="{lx - 10}" y="{ly - 24}" width="360" height="{32 + 24 * len(label_lines)}" rx="10" fill="#ffffff" stroke="#000000" stroke-width="1.4" />',
    ]
    for idx, line in enumerate(label_lines):
        parts.append(
            f'<text x="{lx}" y="{ly + idx * 24}" font-family="Helvetica, Arial, sans-serif" font-size="17" fill="#000000">{escape(line)}</text>'
        )
    return "\n".join(parts)


def build_overview_svg() -> str:
    width, height = 2400, 1500
    parts = svg_header(width, height)
    parts.extend(
        [
            '<text x="80" y="80" font-family="Helvetica, Arial, sans-serif" font-size="36" font-weight="700" fill="#000000">maindata overview DFD</text>',
            '<rect x="50" y="110" width="1080" height="720" rx="24" fill="#ffffff" stroke="#000000" stroke-width="2" />',
            '<rect x="1270" y="110" width="1080" height="720" rx="24" fill="#ffffff" stroke="#000000" stroke-width="2" />',
            '<text x="80" y="155" font-family="Helvetica, Arial, sans-serif" font-size="30" font-weight="700" fill="#000000">Male section</text>',
            '<text x="1300" y="155" font-family="Helvetica, Arial, sans-serif" font-size="30" font-weight="700" fill="#000000">Female section</text>',
        ]
    )

    parts.append(draw_rect(90, 210, 300, 170, "male_players.csv", ["Current player snapshots", "PK: player_id + fifa_version + fifa_update"]))
    parts.append(draw_rect(90, 450, 300, 170, "male_players (legacy).csv", ["Legacy player snapshots", "Same player business IDs"], dash=' stroke-dasharray="8 5"'))
    parts.append(draw_rect(480, 320, 320, 190, "male_teams.csv", ["Team snapshots", "Coach FK plus player/team references"]))
    parts.append(draw_rect(860, 350, 220, 130, "male_coaches.csv", ["Coach master data"]))

    parts.append(draw_rect(1310, 210, 300, 170, "female_players.csv", ["Current player snapshots", "PK: player_id + fifa_version + fifa_update"]))
    parts.append(draw_rect(1310, 450, 300, 170, "female_players (legacy).csv", ["Legacy player snapshots", "Same player business IDs"], dash=' stroke-dasharray="8 5"'))
    parts.append(draw_rect(1700, 320, 320, 190, "female_teams.csv", ["Team snapshots", "Coach FK plus player/team references"]))
    parts.append(draw_rect(2080, 350, 220, 130, "female_coaches.csv", ["Coach master data"]))

    parts.append(draw_process(1200, 560, 210, 105, "Cross-table structure analysis", ["ER identification", "Flow extraction", "Field dictionary"]))
    parts.append(draw_rect(670, 1010, 1060, 280, "Analysis outputs", ["1. ER diagram", "2. DFD overview + male + female", "3. Data structure table"]))

    parts.append(draw_arrow([(390, 295), (440, 295), (440, 355), (480, 355)], "club_team_id, nation_team_id", 402, 250, ' stroke-dasharray="10 6"'))
    parts.append(draw_arrow([(390, 535), (440, 535), (440, 450), (480, 450)], "club_team_id, nation_team_id", 402, 490, ' stroke-dasharray="10 6"'))
    parts.append(draw_arrow([(800, 410), (835, 410), (835, 415), (860, 415)], "coach_id (strict FK)", 745, 355))
    parts.append(draw_arrow([(480, 470), (430, 470), (430, 360), (390, 360)], "captain + set-piece role IDs", 360, 382, ' stroke-dasharray="10 6"'))

    parts.append(draw_arrow([(1610, 295), (1660, 295), (1660, 355), (1700, 355)], "club_team_id, nation_team_id", 1622, 250, ' stroke-dasharray="10 6"'))
    parts.append(draw_arrow([(1610, 535), (1660, 535), (1660, 450), (1700, 450)], "club_team_id, nation_team_id", 1622, 490, ' stroke-dasharray="10 6"'))
    parts.append(draw_arrow([(2020, 410), (2055, 410), (2055, 415), (2080, 415)], "coach_id (strict FK)", 1955, 355))
    parts.append(draw_arrow([(1700, 470), (1650, 470), (1650, 360), (1610, 360)], "captain + set-piece role IDs", 1552, 382, ' stroke-dasharray="10 6"'))

    for x, y in [(640, 510), (1850, 510)]:
        parts.append(
            f'<path d="M{x} {y} q 0 55 55 55" fill="none" stroke="#000000" stroke-width="3" stroke-dasharray="5 5" marker-end="url(#arrow)" />'
        )
        parts.append(
            f'<text x="{x - 20}" y="{y + 95}" font-family="Helvetica, Arial, sans-serif" font-size="17" fill="#000000">rival_team self-reference</text>'
        )

    for src_x in (640, 1850):
        parts.append(draw_arrow([(src_x, 610), (src_x, 700), (1200, 700), (1200, 665)], "table metadata + references", 1010, 720))

    parts.append(draw_arrow([(1200, 665), (1200, 930), (1200, 1010)], "normalized structure model", 1230, 870))
    parts.append(svg_footer())
    return "\n".join(parts)


def build_gender_svg(gender: str) -> str:
    is_male = gender == "male"
    title = "male DFD" if is_male else "female DFD"
    players = "male_players.csv" if is_male else "female_players.csv"
    players_legacy = "male_players (legacy).csv" if is_male else "female_players (legacy).csv"
    teams = "male_teams.csv" if is_male else "female_teams.csv"
    coaches = "male_coaches.csv" if is_male else "female_coaches.csv"

    width, height = 2200, 1450
    parts = svg_header(width, height)
    parts.extend(
        [
            f'<text x="80" y="80" font-family="Helvetica, Arial, sans-serif" font-size="36" font-weight="700" fill="#000000">{title}</text>',
            '<rect x="50" y="110" width="2100" height="1280" rx="24" fill="#ffffff" stroke="#000000" stroke-width="2" />',
        ]
    )

    parts.append(draw_rect(90, 180, 430, 190, players, ["Current player snapshots", "Entity ID: player_id"]))
    parts.append(draw_rect(90, 460, 430, 190, players_legacy, ["Legacy player snapshots", "Entity ID: player_id"], dash=' stroke-dasharray="8 5"'))
    parts.append(draw_rect(90, 980, 430, 190, teams, ["Team snapshots", "Entity ID: team_id", "coach_id is strict FK"]))
    parts.append(draw_rect(1690, 1010, 380, 150, coaches, ["Coach reference table", "Unique business key: coach_id"]))

    parts.append(draw_process(890, 275, 250, 95, "Club-team mapping", ["club_team_id", "player -> team"]))
    parts.append(draw_process(890, 555, 250, 95, "National-team mapping", ["nation_team_id", "player -> team"]))
    parts.append(draw_process(900, 1080, 275, 105, "Player role mapping", ["captain and set-piece IDs", "team -> player"]))
    parts.append(draw_process(1450, 1080, 230, 95, "Coach assignment", ["coach_id", "team -> coach"]))
    parts.append(draw_process(890, 780, 235, 90, "Rival-team check", ["rival_team", "team -> team"]))

    parts.append(draw_arrow([(520, 275), (640, 275)], "player snapshots", 548, 244))
    parts.append(draw_arrow([(1140, 275), (1340, 275), (1340, 1015), (520, 1015)], "club_team_id identifies target team", 1165, 234, ' stroke-dasharray="10 6"'))

    parts.append(draw_arrow([(520, 555), (640, 555)], "legacy player snapshots", 548, 524))
    parts.append(draw_arrow([(1140, 555), (1320, 555), (1320, 1035), (520, 1035)], "nation_team_id identifies target team", 1165, 514, ' stroke-dasharray="10 6"'))

    parts.append(draw_arrow([(520, 1070), (625, 1070)], "team snapshots", 545, 1038))
    parts.append(draw_arrow([(1175, 1080), (1260, 1080), (1260, 330), (520, 330)], "captain + set-piece role IDs point to player_id", 1200, 1044, ' stroke-dasharray="10 6"'))

    parts.append(draw_arrow([(520, 1110), (1190, 1110)], "team snapshot rows", 750, 1136))
    parts.append(draw_arrow([(1680, 1080), (1690, 1080)], "strict FK by coach_id", 1535, 1046))

    parts.append(draw_arrow([(520, 940), (660, 940), (660, 780)], "team rows", 545, 904))
    parts.append(draw_arrow([(1125, 780), (1260, 780), (1260, 940), (520, 940)], "rival_team reuses team_id; not perfectly complete", 1140, 742, ' stroke-dasharray="5 5"'))

    parts.append(
        '<rect x="1270" y="180" width="780" height="300" rx="18" fill="#ffffff" stroke="#000000" stroke-width="1.8" />'
    )
    legend_lines = [
        "Reading rule:",
        "1. Players and teams are snapshot tables, so player_id/team_id alone are not row-unique.",
        "2. coach_id is the only strict FK inside this local group.",
        "3. rival_team is a weak self-reference because unmatched IDs exist in the data.",
    ]
    for idx, line in enumerate(legend_lines):
        parts.append(
            f'<text x="1300" y="{220 + idx * 40}" font-family="Helvetica, Arial, sans-serif" font-size="20" fill="#000000">{escape(line)}</text>'
        )

    parts.append(svg_footer())
    return "\n".join(parts)


def write_svg(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def build_mermaid_overview() -> str:
    lines = [
        "flowchart TB",
        "    classDef table fill:#ffffff,stroke:#000000,color:#000000,stroke-width:1.5px;",
        "    classDef process fill:#ffffff,stroke:#000000,color:#000000,stroke-width:1.5px;",
        "    classDef output fill:#ffffff,stroke:#000000,color:#000000,stroke-width:1.5px;",
        "",
        "    subgraph male_section[Male section]",
        '        MP["male_players.csv<br/>Current player snapshots<br/>PK: player_id + fifa_version + fifa_update"]',
        '        MPL["male_players (legacy).csv<br/>Legacy player snapshots<br/>Same player business IDs"]',
        '        MT["male_teams.csv<br/>Team snapshots<br/>Coach FK plus player/team references"]',
        '        MC["male_coaches.csv<br/>Coach master data"]',
        "    end",
        "",
        "    subgraph female_section[Female section]",
        '        FP["female_players.csv<br/>Current player snapshots<br/>PK: player_id + fifa_version + fifa_update"]',
        '        FPL["female_players (legacy).csv<br/>Legacy player snapshots<br/>Same player business IDs"]',
        '        FT["female_teams.csv<br/>Team snapshots<br/>Coach FK plus player/team references"]',
        '        FC["female_coaches.csv<br/>Coach master data"]',
        "    end",
        "",
        '    XA(("Cross-table structure analysis<br/>ER identification<br/>Flow extraction<br/>Field dictionary"))',
        '    OUT["Analysis outputs<br/>1. ER diagram<br/>2. Mermaid DFD overview + male + female<br/>3. Data structure table"]',
        "",
        '    MP -. "club_team_id, nation_team_id" .-> MT',
        '    MPL -. "club_team_id, nation_team_id" .-> MT',
        '    MT -- "coach_id (strict FK)" --> MC',
        '    MT -. "captain + set-piece role IDs" .-> MP',
        '    MT -. "rival_team self-reference" .-> MT',
        "",
        '    FP -. "club_team_id, nation_team_id" .-> FT',
        '    FPL -. "club_team_id, nation_team_id" .-> FT',
        '    FT -- "coach_id (strict FK)" --> FC',
        '    FT -. "captain + set-piece role IDs" .-> FP',
        '    FT -. "rival_team self-reference" .-> FT',
        "",
        '    MT -- "table metadata + references" --> XA',
        '    FT -- "table metadata + references" --> XA',
        '    XA -- "normalized structure model" --> OUT',
        "",
        "    class MP,MPL,MT,MC,FP,FPL,FT,FC table;",
        "    class XA process;",
        "    class OUT output;",
    ]
    return "\n".join(lines) + "\n"


def build_mermaid_gender(gender: str) -> str:
    is_male = gender == "male"
    title = "Male section" if is_male else "Female section"
    prefix = "M" if is_male else "F"
    players = "male_players.csv" if is_male else "female_players.csv"
    legacy = "male_players (legacy).csv" if is_male else "female_players (legacy).csv"
    teams = "male_teams.csv" if is_male else "female_teams.csv"
    coaches = "male_coaches.csv" if is_male else "female_coaches.csv"
    unmatched = "113826" if is_male else "111473"

    lines = [
        "flowchart TB",
        "    classDef table fill:#ffffff,stroke:#000000,color:#000000,stroke-width:1.5px;",
        "    classDef process fill:#ffffff,stroke:#000000,color:#000000,stroke-width:1.5px;",
        "    classDef note fill:#ffffff,stroke:#000000,color:#000000,stroke-width:1.2px;",
        "",
        f"    subgraph {prefix}_section[{title}]",
        f'        {prefix}P["{players}<br/>Current player snapshots<br/>Entity ID: player_id"]',
        f'        {prefix}PL["{legacy}<br/>Legacy player snapshots<br/>Entity ID: player_id"]',
        f'        {prefix}T["{teams}<br/>Team snapshots<br/>Entity ID: team_id<br/>coach_id is strict FK"]',
        f'        {prefix}C["{coaches}<br/>Coach reference table<br/>Unique business key: coach_id"]',
        f'        {prefix}CT(("Club-team mapping<br/>club_team_id<br/>player -> team"))',
        f'        {prefix}NT(("National-team mapping<br/>nation_team_id<br/>player -> team"))',
        f'        {prefix}PR(("Player role mapping<br/>captain and set-piece IDs<br/>team -> player"))',
        f'        {prefix}CA(("Coach assignment<br/>coach_id<br/>team -> coach"))',
        f'        {prefix}RT(("Rival-team check<br/>rival_team<br/>team -> team"))',
        f'        {prefix}N["Reading rule<br/>1. Players and teams are snapshot tables.<br/>2. coach_id is the only strict FK here.<br/>3. rival_team is weak; unmatched ID: {unmatched}."]',
        "    end",
        "",
        f'    {prefix}P -- "player snapshots" --> {prefix}CT',
        f'    {prefix}CT -. "club_team_id identifies target team" .-> {prefix}T',
        f'    {prefix}PL -- "legacy player snapshots" --> {prefix}NT',
        f'    {prefix}NT -. "nation_team_id identifies target team" .-> {prefix}T',
        f'    {prefix}T -- "team snapshots" --> {prefix}PR',
        f'    {prefix}PR -. "captain + set-piece role IDs point to player_id" .-> {prefix}P',
        f'    {prefix}T -- "team snapshot rows" --> {prefix}CA',
        f'    {prefix}CA -- "strict FK by coach_id" --> {prefix}C',
        f'    {prefix}T -- "team rows" --> {prefix}RT',
        f'    {prefix}RT -. "rival_team reuses team_id; not perfectly complete" .-> {prefix}T',
        "",
        f"    class {prefix}P,{prefix}PL,{prefix}T,{prefix}C table;",
        f"    class {prefix}CT,{prefix}NT,{prefix}PR,{prefix}CA,{prefix}RT process;",
        f"    class {prefix}N note;",
    ]
    return "\n".join(lines) + "\n"


def write_mermaid(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def write_mermaid_markdown(overview: str, male: str, female: str) -> Path:
    md_path = DATA_DIR / "all_mermaid.md"
    content = "\n".join(
        [
            "# Mermaid Diagrams",
            "",
            "Typora can render each fenced `mermaid` block below as a separate diagram.",
            "",
            "## DFD Overview",
            "",
            "```mermaid",
            overview.rstrip(),
            "```",
            "",
            "## DFD Male",
            "",
            "```mermaid",
            male.rstrip(),
            "```",
            "",
            "## DFD Female",
            "",
            "```mermaid",
            female.rstrip(),
            "```",
            "",
        ]
    )
    md_path.write_text(content, encoding="utf-8")
    return md_path


def main() -> None:
    rows = build_data_structure_rows()
    csv_path, md_path = write_data_structure(rows)

    overview_path = DATA_DIR / "DFD_overview.svg"
    male_path = DATA_DIR / "DFD_male.svg"
    female_path = DATA_DIR / "DFD_female.svg"
    overview_mmd_path = DATA_DIR / "DFD_overview.mmd"
    male_mmd_path = DATA_DIR / "DFD_male.mmd"
    female_mmd_path = DATA_DIR / "DFD_female.mmd"
    overview_mermaid = build_mermaid_overview()
    male_mermaid = build_mermaid_gender("male")
    female_mermaid = build_mermaid_gender("female")
    write_svg(overview_path, build_overview_svg())
    write_svg(male_path, build_gender_svg("male"))
    write_svg(female_path, build_gender_svg("female"))
    write_mermaid(overview_mmd_path, overview_mermaid)
    write_mermaid(male_mmd_path, male_mermaid)
    write_mermaid(female_mmd_path, female_mermaid)
    mermaid_md_path = write_mermaid_markdown(overview_mermaid, male_mermaid, female_mermaid)

    print(f"Wrote {csv_path}")
    print(f"Wrote {md_path}")
    print(f"Wrote {overview_path}")
    print(f"Wrote {male_path}")
    print(f"Wrote {female_path}")
    print(f"Wrote {overview_mmd_path}")
    print(f"Wrote {male_mmd_path}")
    print(f"Wrote {female_mmd_path}")
    print(f"Wrote {mermaid_md_path}")


if __name__ == "__main__":
    main()
