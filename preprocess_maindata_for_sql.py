from __future__ import annotations

import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "maindata"
OUTPUT_DIR = SOURCE_DIR / "sql_ready"

TRANSFER_FILE = SOURCE_DIR / "Transfer Market Data.csv"
TRANSFER_DUP_FILE = SOURCE_DIR / "Transfer Market Data Outgoing.csv"
PLAYERS_FILE = SOURCE_DIR / "male_players.csv"
PLAYERS_LEGACY_FILE = SOURCE_DIR / "male_players (legacy).csv"
TEAMS_FILE = SOURCE_DIR / "male_teams.csv"
COACHES_FILE = SOURCE_DIR / "male_coaches.csv"


def norm_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "")
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def clean_text(value: str) -> str:
    return (value or "").strip()


def make_key(*parts: str) -> str:
    joined = "|".join(parts)
    return hashlib.sha1(joined.encode("utf-8")).hexdigest()


def safe_int(value: str) -> int:
    try:
        return int(float(clean_text(value)))
    except Exception:
        return -1


def date_sort_key(value: str) -> str:
    value = clean_text(value)
    if not value:
        return ""
    return value[:10]


def is_better_player_candidate(new: dict[str, str], current: dict[str, str] | None) -> bool:
    if current is None:
        return True
    new_key = (
        date_sort_key(new["fifa_update_date"]),
        safe_int(new["fifa_version"]),
        safe_int(new["fifa_update"]),
        safe_int(new["overall"]),
        new["source_priority"],
    )
    cur_key = (
        date_sort_key(current["fifa_update_date"]),
        safe_int(current["fifa_version"]),
        safe_int(current["fifa_update"]),
        safe_int(current["overall"]),
        current["source_priority"],
    )
    return new_key > cur_key


def is_better_team_candidate(new: dict[str, str], current: dict[str, str] | None) -> bool:
    if current is None:
        return True
    new_key = (
        date_sort_key(new["fifa_update_date"]),
        safe_int(new["fifa_version"]),
        safe_int(new["fifa_update"]),
        safe_int(new["overall"]),
    )
    cur_key = (
        date_sort_key(current["fifa_update_date"]),
        safe_int(current["fifa_version"]),
        safe_int(current["fifa_update"]),
        safe_int(current["overall"]),
    )
    return new_key > cur_key


@dataclass
class TransferPreparation:
    player_rows: dict[str, dict[str, str]]
    club_rows: dict[str, dict[str, str]]
    transfer_rows: list[dict[str, str]]
    normalized_player_to_keys: dict[str, set[str]]
    normalized_club_to_keys: dict[str, set[str]]
    transfer_player_names: set[str]
    transfer_club_names: set[str]
    raw_transfer_rows: int
    dedup_transfer_rows: int
    duplicate_transfer_file_same: bool


def detect_duplicate_transfer_file() -> bool:
    if not TRANSFER_DUP_FILE.exists():
        return False
    h1 = hashlib.md5()
    with TRANSFER_FILE.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h1.update(chunk)
    h2 = hashlib.md5()
    with TRANSFER_DUP_FILE.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h2.update(chunk)
    return h1.hexdigest() == h2.hexdigest()


def prepare_transfer_core() -> TransferPreparation:
    player_rows: dict[str, dict[str, str]] = {}
    club_rows: dict[str, dict[str, str]] = {}
    transfer_rows: list[dict[str, str]] = []
    normalized_player_to_keys: dict[str, set[str]] = defaultdict(set)
    normalized_club_to_keys: dict[str, set[str]] = defaultdict(set)
    transfer_player_names: set[str] = set()
    transfer_club_names: set[str] = set()
    seen_rows: set[tuple[str, ...]] = set()
    raw_rows = 0

    with TRANSFER_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for raw_row in reader:
            row = {k: clean_text(v) for k, v in raw_row.items()}
            raw_rows += 1
            key_tuple = tuple(row.get(col, "") for col in reader.fieldnames or [])
            if key_tuple in seen_rows:
                continue
            seen_rows.add(key_tuple)

            normalized_name = norm_text(row["name"])
            normalized_position = norm_text(row["position"])
            normalized_age = clean_text(row["age"])
            player_key = make_key(normalized_name, normalized_position, normalized_age)

            origin_name = clean_text(row["origin_club"])
            origin_league = clean_text(row["league_origin_club"])
            origin_country = clean_text(row["country_origin_club"])
            normalized_origin = norm_text(origin_name)
            origin_key = make_key(normalized_origin, norm_text(origin_league), norm_text(origin_country))

            destination_name = clean_text(row["new_club"])
            destination_league = clean_text(row["league_new_club"])
            destination_country = clean_text(row["country_new_club"])
            normalized_destination = norm_text(destination_name)
            destination_key = make_key(normalized_destination, norm_text(destination_league), norm_text(destination_country))

            transfer_player_names.add(normalized_name)
            transfer_club_names.add(normalized_origin)
            transfer_club_names.add(normalized_destination)
            normalized_player_to_keys[normalized_name].add(player_key)
            normalized_club_to_keys[normalized_origin].add(origin_key)
            normalized_club_to_keys[normalized_destination].add(destination_key)

            player_entry = player_rows.setdefault(
                player_key,
                {
                    "player_key": player_key,
                    "player_name": row["name"],
                    "player_name_normalized": normalized_name,
                    "position": row["position"],
                    "age": row["age"],
                    "transfer_record_count": "0",
                    "first_transfer_date": row["date_of_transfer"][:10],
                    "last_transfer_date": row["date_of_transfer"][:10],
                    "player_match_status": "unmatched",
                    "player_name_match_key": "",
                    "player_id": "",
                    "fifa_version": "",
                    "fifa_update": "",
                    "short_name": "",
                    "long_name": "",
                    "overall": "",
                    "potential": "",
                    "team_id": "",
                    "team_name": "",
                    "team_league_name": "",
                    "nationality_name": "",
                    "fifa_update_date": "",
                    "player_source_table": "",
                },
            )
            player_entry["transfer_record_count"] = str(int(player_entry["transfer_record_count"]) + 1)
            transfer_date = row["date_of_transfer"][:10]
            if transfer_date and (not player_entry["first_transfer_date"] or transfer_date < player_entry["first_transfer_date"]):
                player_entry["first_transfer_date"] = transfer_date
            if transfer_date and transfer_date > player_entry["last_transfer_date"]:
                player_entry["last_transfer_date"] = transfer_date

            for club_key, club_name, league_name, country_name, role in (
                (origin_key, origin_name, origin_league, origin_country, "origin"),
                (destination_key, destination_name, destination_league, destination_country, "destination"),
            ):
                club_entry = club_rows.setdefault(
                    club_key,
                    {
                        "club_key": club_key,
                        "club_name": club_name,
                        "club_name_normalized": norm_text(club_name),
                        "league_name": league_name,
                        "country_name": country_name,
                        "origin_transfer_count": "0",
                        "destination_transfer_count": "0",
                        "team_match_status": "unmatched",
                        "team_id": "",
                        "fifa_version": "",
                        "fifa_update": "",
                        "team_name": "",
                        "team_league_name": "",
                        "coach_id": "",
                        "team_overall": "",
                        "fifa_update_date": "",
                    },
                )
                count_field = "origin_transfer_count" if role == "origin" else "destination_transfer_count"
                club_entry[count_field] = str(int(club_entry[count_field]) + 1)

            transfer_rows.append(
                {
                    "transfer_id": str(len(transfer_rows) + 1),
                    "player_key": player_key,
                    "origin_club_key": origin_key,
                    "destination_club_key": destination_key,
                    "player_name": row["name"],
                    "position": row["position"],
                    "age": row["age"],
                    "origin_club_name": origin_name,
                    "origin_league_name": origin_league,
                    "origin_country_name": origin_country,
                    "destination_club_name": destination_name,
                    "destination_league_name": destination_league,
                    "destination_country_name": destination_country,
                    "player_market_value": row["player_market_value"],
                    "cost": row["cost"],
                    "date_of_transfer": row["date_of_transfer"][:10],
                    "destination_latitude": row["latitude_to"],
                    "destination_longitude": row["longitude_to"],
                    "destination_region": row["to"],
                    "origin_latitude": row["latitude_from"],
                    "origin_longitude": row["longitude_from"],
                    "origin_region": row["from"],
                    "week_of_transfer": row["week_of_transfer"],
                    "player_type": row["Player Type"],
                }
            )

    return TransferPreparation(
        player_rows=player_rows,
        club_rows=club_rows,
        transfer_rows=transfer_rows,
        normalized_player_to_keys=normalized_player_to_keys,
        normalized_club_to_keys=normalized_club_to_keys,
        transfer_player_names=transfer_player_names,
        transfer_club_names=transfer_club_names,
        raw_transfer_rows=raw_rows,
        dedup_transfer_rows=len(transfer_rows),
        duplicate_transfer_file_same=detect_duplicate_transfer_file(),
    )


def enrich_players(prep: TransferPreparation) -> tuple[dict[str, dict[str, str]], set[str], dict[str, set[str]]]:
    best_by_name: dict[str, dict[str, str]] = {}
    matched_ids_by_name: dict[str, set[str]] = defaultdict(set)

    def scan_file(path: Path, source_priority: str) -> None:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                row = {k: clean_text(v) for k, v in row.items()}
                for name_key in {norm_text(row["short_name"]), norm_text(row["long_name"])}:
                    if not name_key or name_key not in prep.transfer_player_names:
                        continue
                    candidate = {
                        "match_name_key": name_key,
                        "player_id": row["player_id"],
                        "short_name": row["short_name"],
                        "long_name": row["long_name"],
                        "overall": row["overall"],
                        "potential": row["potential"],
                        "club_team_id": row["club_team_id"],
                        "club_name": row["club_name"],
                        "league_name": row["league_name"],
                        "nationality_name": row["nationality_name"],
                        "fifa_version": row["fifa_version"],
                        "fifa_update": row["fifa_update"],
                        "fifa_update_date": row["fifa_update_date"],
                        "source_table": path.name,
                        "source_priority": source_priority,
                    }
                    matched_ids_by_name[name_key].add(row["player_id"])
                    if is_better_player_candidate(candidate, best_by_name.get(name_key)):
                        best_by_name[name_key] = candidate

    scan_file(PLAYERS_FILE, "2")
    scan_file(PLAYERS_LEGACY_FILE, "1")

    matched_player_ids: set[str] = set()
    for name_key, player_keys in prep.normalized_player_to_keys.items():
        candidate = best_by_name.get(name_key)
        status = "unmatched"
        if candidate:
            matched_player_ids.add(candidate["player_id"])
            ambiguous = len(matched_ids_by_name.get(name_key, set())) > 1
            status = "matched_ambiguous_name" if ambiguous else "matched_unique_name"
            for player_key in player_keys:
                target = prep.player_rows[player_key]
                target["player_match_status"] = status
                target["player_name_match_key"] = name_key
                target["player_id"] = candidate["player_id"]
                target["fifa_version"] = candidate["fifa_version"]
                target["fifa_update"] = candidate["fifa_update"]
                target["short_name"] = candidate["short_name"]
                target["long_name"] = candidate["long_name"]
                target["overall"] = candidate["overall"]
                target["potential"] = candidate["potential"]
                target["team_id"] = candidate["club_team_id"]
                target["team_name"] = candidate["club_name"]
                target["team_league_name"] = candidate["league_name"]
                target["nationality_name"] = candidate["nationality_name"]
                target["fifa_update_date"] = candidate["fifa_update_date"]
                target["player_source_table"] = candidate["source_table"]
        else:
            for player_key in player_keys:
                prep.player_rows[player_key]["player_match_status"] = status

    return best_by_name, matched_player_ids, matched_ids_by_name


def enrich_teams(prep: TransferPreparation) -> tuple[dict[str, dict[str, str]], set[str], set[str]]:
    best_by_name: dict[str, dict[str, str]] = {}
    matched_team_ids: set[str] = set()
    matched_coach_ids: set[str] = set()

    with TEAMS_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row = {k: clean_text(v) for k, v in row.items()}
            name_key = norm_text(row["team_name"])
            if not name_key or name_key not in prep.transfer_club_names:
                continue
            candidate = {
                "team_id": row["team_id"],
                "team_name": row["team_name"],
                "league_name": row["league_name"],
                "coach_id": row["coach_id"],
                "overall": row["overall"],
                "fifa_version": row["fifa_version"],
                "fifa_update": row["fifa_update"],
                "fifa_update_date": row["fifa_update_date"],
            }
            if is_better_team_candidate(candidate, best_by_name.get(name_key)):
                best_by_name[name_key] = candidate

    for name_key, club_keys in prep.normalized_club_to_keys.items():
        candidate = best_by_name.get(name_key)
        if not candidate:
            continue
        matched_team_ids.add(candidate["team_id"])
        if candidate["coach_id"]:
            matched_coach_ids.add(candidate["coach_id"])
        for club_key in club_keys:
            target = prep.club_rows[club_key]
            target["team_match_status"] = "matched"
            target["team_id"] = candidate["team_id"]
            target["fifa_version"] = candidate["fifa_version"]
            target["fifa_update"] = candidate["fifa_update"]
            target["team_name"] = candidate["team_name"]
            target["team_league_name"] = candidate["league_name"]
            target["coach_id"] = candidate["coach_id"]
            target["team_overall"] = candidate["overall"]
            target["fifa_update_date"] = candidate["fifa_update_date"]

    return best_by_name, matched_team_ids, matched_coach_ids


def write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, str]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})
            count += 1
    return count


def write_selected_player_rows(source_path: Path, selected_rows: set[tuple[str, str, str, str]], destination: Path) -> int:
    count = 0
    with source_path.open("r", encoding="utf-8-sig", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.DictReader(src)
        fieldnames = reader.fieldnames or []
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            key = (
                clean_text(row.get("player_id", "")),
                clean_text(row.get("fifa_version", "")),
                clean_text(row.get("fifa_update", "")),
                clean_text(row.get("fifa_update_date", "")),
            )
            if key in selected_rows:
                writer.writerow(row)
                count += 1
    return count


def write_selected_team_rows(selected_rows: set[tuple[str, str, str, str]], destination: Path) -> tuple[int, set[str]]:
    count = 0
    coach_ids: set[str] = set()
    with TEAMS_FILE.open("r", encoding="utf-8-sig", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.DictReader(src)
        fieldnames = reader.fieldnames or []
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            key = (
                clean_text(row.get("team_id", "")),
                clean_text(row.get("fifa_version", "")),
                clean_text(row.get("fifa_update", "")),
                clean_text(row.get("fifa_update_date", "")),
            )
            if key in selected_rows:
                writer.writerow(row)
                count += 1
                coach_id = clean_text(row.get("coach_id", ""))
                if coach_id:
                    coach_ids.add(coach_id)
    return count, coach_ids


def write_coach_subset(coach_ids: set[str], destination: Path) -> int:
    count = 0
    with COACHES_FILE.open("r", encoding="utf-8-sig", newline="") as src, destination.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.DictReader(src)
        fieldnames = reader.fieldnames or []
        writer = csv.DictWriter(dst, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            if clean_text(row.get("coach_id", "")) in coach_ids:
                writer.writerow(row)
                count += 1
    return count


def build_dimensions(
    player_rows: Iterable[dict[str, str]],
    club_rows: Iterable[dict[str, str]],
    coach_rows: Iterable[dict[str, str]],
    transfer_rows: Iterable[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], list[dict[str, str]], dict[str, str], dict[tuple[str, str], str], dict[str, str], dict[str, str]]:
    country_display: dict[str, str] = {}
    position_display: dict[str, str] = {}
    player_type_display: dict[str, str] = {}
    league_display: dict[tuple[str, str], tuple[str, str]] = {}

    def collect_country(name: str) -> None:
        normalized = norm_text(name)
        if normalized and normalized not in country_display:
            country_display[normalized] = clean_text(name)

    def collect_position(name: str) -> None:
        normalized = norm_text(name)
        if normalized and normalized not in position_display:
            position_display[normalized] = clean_text(name)

    def collect_player_type(name: str) -> None:
        normalized = norm_text(name)
        if normalized and normalized not in player_type_display:
            player_type_display[normalized] = clean_text(name)

    def collect_league(league_name: str, country_name: str) -> None:
        league_norm = norm_text(league_name)
        country_norm = norm_text(country_name)
        if not league_norm or not country_norm:
            return
        league_display.setdefault((league_norm, country_norm), (clean_text(league_name), clean_text(country_name)))

    for row in player_rows:
        collect_position(row.get("position", ""))
        collect_country(row.get("nationality_name", ""))
    for row in club_rows:
        collect_country(row.get("country_name", ""))
        collect_league(row.get("league_name", ""), row.get("country_name", ""))
        collect_league(row.get("team_league_name", ""), row.get("country_name", ""))
    for row in coach_rows:
        collect_country(row.get("nationality_name", ""))
    for row in transfer_rows:
        collect_position(row.get("position", ""))
        collect_player_type(row.get("player_type", ""))
        collect_country(row.get("origin_country_name", ""))
        collect_country(row.get("destination_country_name", ""))
        collect_league(row.get("origin_league_name", ""), row.get("origin_country_name", ""))
        collect_league(row.get("destination_league_name", ""), row.get("destination_country_name", ""))

    country_rows: list[dict[str, str]] = []
    country_id_map: dict[str, str] = {}
    for idx, normalized in enumerate(sorted(country_display), start=1):
        country_id = str(idx)
        country_id_map[normalized] = country_id
        country_rows.append(
            {
                "country_dim_id": country_id,
                "country_name": country_display[normalized],
                "country_name_normalized": normalized,
            }
        )

    league_rows: list[dict[str, str]] = []
    league_id_map: dict[tuple[str, str], str] = {}
    for idx, key in enumerate(sorted(league_display), start=1):
        league_id = str(idx)
        league_name, country_name = league_display[key]
        league_id_map[key] = league_id
        league_rows.append(
            {
                "league_dim_id": league_id,
                "league_name": league_name,
                "league_name_normalized": key[0],
                "country_dim_id": country_id_map[key[1]],
                "country_name": country_name,
            }
        )

    position_rows: list[dict[str, str]] = []
    position_id_map: dict[str, str] = {}
    for idx, normalized in enumerate(sorted(position_display), start=1):
        position_id = str(idx)
        position_id_map[normalized] = position_id
        position_rows.append(
            {
                "position_dim_id": position_id,
                "position_name": position_display[normalized],
                "position_name_normalized": normalized,
            }
        )

    player_type_rows: list[dict[str, str]] = []
    player_type_id_map: dict[str, str] = {}
    for idx, normalized in enumerate(sorted(player_type_display), start=1):
        player_type_id = str(idx)
        player_type_id_map[normalized] = player_type_id
        player_type_rows.append(
            {
                "player_type_dim_id": player_type_id,
                "player_type": player_type_display[normalized],
                "player_type_normalized": normalized,
            }
        )

    return (
        country_rows,
        league_rows,
        position_rows,
        player_type_rows,
        country_id_map,
        league_id_map,
        position_id_map,
        player_type_id_map,
    )


def attach_dimension_ids(
    player_rows: Iterable[dict[str, str]],
    club_rows: Iterable[dict[str, str]],
    coach_rows: Iterable[dict[str, str]],
    transfer_rows: Iterable[dict[str, str]],
    country_id_map: dict[str, str],
    league_id_map: dict[tuple[str, str], str],
    position_id_map: dict[str, str],
    player_type_id_map: dict[str, str],
) -> None:
    team_country_by_team_id: dict[str, str] = {}
    team_league_dim_by_team_id: dict[str, str] = {}

    for row in club_rows:
        country_norm = norm_text(row.get("country_name", ""))
        league_key = (norm_text(row.get("league_name", "")), country_norm)
        row["country_dim_id"] = country_id_map.get(country_norm, "")
        row["league_dim_id"] = league_id_map.get(league_key, "")
        team_country_by_team_id[row.get("team_id", "")] = row["country_dim_id"]
        team_league_dim_by_team_id[row.get("team_id", "")] = row["league_dim_id"]

    for row in player_rows:
        row["position_dim_id"] = position_id_map.get(norm_text(row.get("position", "")), "")
        row["nationality_country_dim_id"] = country_id_map.get(norm_text(row.get("nationality_name", "")), "")
        row["team_country_dim_id"] = team_country_by_team_id.get(row.get("team_id", ""), "")
        row["team_league_dim_id"] = team_league_dim_by_team_id.get(row.get("team_id", ""), "")

    for row in coach_rows:
        row["nationality_country_dim_id"] = country_id_map.get(norm_text(row.get("nationality_name", "")), "")

    for row in transfer_rows:
        row["position_dim_id"] = position_id_map.get(norm_text(row.get("position", "")), "")
        row["player_type_dim_id"] = player_type_id_map.get(norm_text(row.get("player_type", "")), "")
        origin_country_norm = norm_text(row.get("origin_country_name", ""))
        destination_country_norm = norm_text(row.get("destination_country_name", ""))
        row["origin_country_dim_id"] = country_id_map.get(origin_country_norm, "")
        row["destination_country_dim_id"] = country_id_map.get(destination_country_norm, "")
        row["origin_league_dim_id"] = league_id_map.get((norm_text(row.get("origin_league_name", "")), origin_country_norm), "")
        row["destination_league_dim_id"] = league_id_map.get((norm_text(row.get("destination_league_name", "")), destination_country_norm), "")


def write_mysql_schema() -> Path:
    path = OUTPUT_DIR / "mysql_schema.sql"
    path.write_text(
        "\n".join(
            [
                "CREATE DATABASE IF NOT EXISTS transfer_fifa_clean CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
                "USE transfer_fifa_clean;",
                "",
                "DROP TABLE IF EXISTS transfers;",
                "DROP TABLE IF EXISTS players;",
                "DROP TABLE IF EXISTS clubs;",
                "DROP TABLE IF EXISTS coaches;",
                "DROP TABLE IF EXISTS league_dim;",
                "DROP TABLE IF EXISTS country_dim;",
                "DROP TABLE IF EXISTS position_dim;",
                "DROP TABLE IF EXISTS player_type_dim;",
                "",
                "CREATE TABLE country_dim (",
                "  country_dim_id INT PRIMARY KEY,",
                "  country_name VARCHAR(255) NOT NULL,",
                "  country_name_normalized VARCHAR(255) NOT NULL",
                ");",
                "",
                "CREATE TABLE league_dim (",
                "  league_dim_id INT PRIMARY KEY,",
                "  league_name VARCHAR(255) NOT NULL,",
                "  league_name_normalized VARCHAR(255) NOT NULL,",
                "  country_dim_id INT NOT NULL,",
                "  country_name VARCHAR(255) NOT NULL,",
                "  CONSTRAINT fk_league_country FOREIGN KEY (country_dim_id) REFERENCES country_dim(country_dim_id)",
                ");",
                "",
                "CREATE TABLE position_dim (",
                "  position_dim_id INT PRIMARY KEY,",
                "  position_name VARCHAR(255) NOT NULL,",
                "  position_name_normalized VARCHAR(255) NOT NULL",
                ");",
                "",
                "CREATE TABLE player_type_dim (",
                "  player_type_dim_id INT PRIMARY KEY,",
                "  player_type VARCHAR(255) NOT NULL,",
                "  player_type_normalized VARCHAR(255) NOT NULL",
                ");",
                "",
                "CREATE TABLE players (",
                "  player_key CHAR(40) PRIMARY KEY,",
                "  player_name VARCHAR(255) NOT NULL,",
                "  player_name_normalized VARCHAR(255) NOT NULL,",
                "  position_dim_id INT NULL,",
                "  position VARCHAR(128),",
                "  age VARCHAR(32),",
                "  transfer_record_count INT NOT NULL,",
                "  first_transfer_date DATE NULL,",
                "  last_transfer_date DATE NULL,",
                "  player_match_status VARCHAR(64) NOT NULL,",
                "  player_name_match_key VARCHAR(255),",
                "  player_id BIGINT NULL,",
                "  fifa_version VARCHAR(16),",
                "  fifa_update VARCHAR(16),",
                "  short_name VARCHAR(255),",
                "  long_name VARCHAR(255),",
                "  overall VARCHAR(16),",
                "  potential VARCHAR(16),",
                "  team_id BIGINT NULL,",
                "  team_name VARCHAR(255),",
                "  team_country_dim_id INT NULL,",
                "  team_league_dim_id INT NULL,",
                "  team_league_name VARCHAR(255),",
                "  nationality_country_dim_id INT NULL,",
                "  nationality_name VARCHAR(255),",
                "  fifa_update_date DATE NULL,",
                "  player_source_table VARCHAR(128),",
                "  CONSTRAINT fk_players_position_dim FOREIGN KEY (position_dim_id) REFERENCES position_dim(position_dim_id),",
                "  CONSTRAINT fk_players_team_country_dim FOREIGN KEY (team_country_dim_id) REFERENCES country_dim(country_dim_id),",
                "  CONSTRAINT fk_players_team_league_dim FOREIGN KEY (team_league_dim_id) REFERENCES league_dim(league_dim_id),",
                "  CONSTRAINT fk_players_nationality_dim FOREIGN KEY (nationality_country_dim_id) REFERENCES country_dim(country_dim_id)",
                ");",
                "",
                "CREATE TABLE clubs (",
                "  club_key CHAR(40) PRIMARY KEY,",
                "  club_name VARCHAR(255) NOT NULL,",
                "  club_name_normalized VARCHAR(255) NOT NULL,",
                "  country_dim_id INT NULL,",
                "  league_name VARCHAR(255),",
                "  league_dim_id INT NULL,",
                "  country_name VARCHAR(255),",
                "  origin_transfer_count INT NOT NULL,",
                "  destination_transfer_count INT NOT NULL,",
                "  team_match_status VARCHAR(64) NOT NULL,",
                "  team_id BIGINT NULL,",
                "  fifa_version VARCHAR(16),",
                "  fifa_update VARCHAR(16),",
                "  team_name VARCHAR(255),",
                "  team_league_name VARCHAR(255),",
                "  coach_id BIGINT NULL,",
                "  team_overall VARCHAR(16),",
                "  fifa_update_date DATE NULL,",
                "  CONSTRAINT fk_clubs_country_dim FOREIGN KEY (country_dim_id) REFERENCES country_dim(country_dim_id),",
                "  CONSTRAINT fk_clubs_league_dim FOREIGN KEY (league_dim_id) REFERENCES league_dim(league_dim_id)"
                ");",
                "",
                "CREATE TABLE coaches (",
                "  coach_id BIGINT PRIMARY KEY,",
                "  coach_url VARCHAR(255),",
                "  short_name VARCHAR(255),",
                "  long_name VARCHAR(255),",
                "  dob DATE NULL,",
                "  nationality_country_dim_id INT NULL,",
                "  nationality_id BIGINT NULL,",
                "  nationality_name VARCHAR(255),",
                "  face_url VARCHAR(512),",
                "  CONSTRAINT fk_coaches_nationality_dim FOREIGN KEY (nationality_country_dim_id) REFERENCES country_dim(country_dim_id)"
                ");",
                "",
                "CREATE TABLE transfers (",
                "  transfer_id BIGINT PRIMARY KEY,",
                "  player_key CHAR(40) NOT NULL,",
                "  origin_club_key CHAR(40) NOT NULL,",
                "  destination_club_key CHAR(40) NOT NULL,",
                "  player_name VARCHAR(255) NOT NULL,",
                "  position_dim_id INT NULL,",
                "  position VARCHAR(128),",
                "  age VARCHAR(32),",
                "  origin_club_name VARCHAR(255),",
                "  origin_country_dim_id INT NULL,",
                "  origin_league_name VARCHAR(255),",
                "  origin_league_dim_id INT NULL,",
                "  origin_country_name VARCHAR(255),",
                "  destination_club_name VARCHAR(255),",
                "  destination_country_dim_id INT NULL,",
                "  destination_league_name VARCHAR(255),",
                "  destination_league_dim_id INT NULL,",
                "  destination_country_name VARCHAR(255),",
                "  player_market_value VARCHAR(64),",
                "  cost VARCHAR(64),",
                "  date_of_transfer DATE NULL,",
                "  destination_latitude VARCHAR(64),",
                "  destination_longitude VARCHAR(64),",
                "  destination_region VARCHAR(255),",
                "  origin_latitude VARCHAR(64),",
                "  origin_longitude VARCHAR(64),",
                "  origin_region VARCHAR(255),",
                "  week_of_transfer VARCHAR(64),",
                "  player_type_dim_id INT NULL,",
                "  player_type VARCHAR(128),",
                "  CONSTRAINT fk_transfers_player FOREIGN KEY (player_key) REFERENCES players(player_key),",
                "  CONSTRAINT fk_transfers_origin FOREIGN KEY (origin_club_key) REFERENCES clubs(club_key),",
                "  CONSTRAINT fk_transfers_destination FOREIGN KEY (destination_club_key) REFERENCES clubs(club_key),",
                "  CONSTRAINT fk_transfers_position_dim FOREIGN KEY (position_dim_id) REFERENCES position_dim(position_dim_id),",
                "  CONSTRAINT fk_transfers_origin_country_dim FOREIGN KEY (origin_country_dim_id) REFERENCES country_dim(country_dim_id),",
                "  CONSTRAINT fk_transfers_destination_country_dim FOREIGN KEY (destination_country_dim_id) REFERENCES country_dim(country_dim_id),",
                "  CONSTRAINT fk_transfers_origin_league_dim FOREIGN KEY (origin_league_dim_id) REFERENCES league_dim(league_dim_id),",
                "  CONSTRAINT fk_transfers_destination_league_dim FOREIGN KEY (destination_league_dim_id) REFERENCES league_dim(league_dim_id),",
                "  CONSTRAINT fk_transfers_player_type_dim FOREIGN KEY (player_type_dim_id) REFERENCES player_type_dim(player_type_dim_id)",
                ");",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_mysql_load_sql() -> Path:
    path = OUTPUT_DIR / "mysql_load_data.sql"
    country_dim_path = (OUTPUT_DIR / "country_dim.csv").resolve()
    league_dim_path = (OUTPUT_DIR / "league_dim.csv").resolve()
    position_dim_path = (OUTPUT_DIR / "position_dim.csv").resolve()
    player_type_dim_path = (OUTPUT_DIR / "player_type_dim.csv").resolve()
    players_path = (OUTPUT_DIR / "players.csv").resolve()
    clubs_path = (OUTPUT_DIR / "clubs.csv").resolve()
    coaches_path = (OUTPUT_DIR / "coaches.csv").resolve()
    transfers_path = (OUTPUT_DIR / "transfers.csv").resolve()
    path.write_text(
        "\n".join(
            [
                "USE transfer_fifa_clean;",
                "",
                "SET FOREIGN_KEY_CHECKS = 0;",
                "TRUNCATE TABLE transfers;",
                "TRUNCATE TABLE coaches;",
                "TRUNCATE TABLE clubs;",
                "TRUNCATE TABLE players;",
                "TRUNCATE TABLE player_type_dim;",
                "TRUNCATE TABLE position_dim;",
                "TRUNCATE TABLE league_dim;",
                "TRUNCATE TABLE country_dim;",
                "",
                f"LOAD DATA LOCAL INFILE '{country_dim_path}' INTO TABLE country_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                f"LOAD DATA LOCAL INFILE '{league_dim_path}' INTO TABLE league_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                f"LOAD DATA LOCAL INFILE '{position_dim_path}' INTO TABLE position_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                f"LOAD DATA LOCAL INFILE '{player_type_dim_path}' INTO TABLE player_type_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                f"LOAD DATA LOCAL INFILE '{players_path}' INTO TABLE players CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                f"LOAD DATA LOCAL INFILE '{clubs_path}' INTO TABLE clubs CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                f"LOAD DATA LOCAL INFILE '{coaches_path}' INTO TABLE coaches CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                f"LOAD DATA LOCAL INFILE '{transfers_path}' INTO TABLE transfers CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '\"' ESCAPED BY '\"' LINES TERMINATED BY '\\n' IGNORE 1 LINES;",
                "",
                "SET FOREIGN_KEY_CHECKS = 1;",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_import_readme(summary: dict[str, object]) -> Path:
    path = OUTPUT_DIR / "README.md"
    path.write_text(
        "\n".join(
            [
                "# SQL Ready Output",
                "",
                "This folder contains a transfer-centric cleaned dataset prepared from `maindata` only.",
                "",
                "## Design rule",
                "",
                "- `Transfer Market Data.csv` is the master fact table.",
                "- `Transfer Market Data Outgoing.csv` is ignored because it is byte-for-byte identical.",
                "- Every transfer record is preserved.",
                "- `male_players.csv`, `male_players (legacy).csv`, `male_teams.csv`, and `male_coaches.csv` are used only as enrichment sources.",
                "- Unused rows from the large FIFA total tables are not copied into the SQL-ready output.",
                "",
                "## Files",
                "",
                "- `players.csv`: one row per transfer-player key generated from normalized name + position + age.",
                "- `clubs.csv`: one row per transfer club generated from normalized club name + league + country.",
                "- `coaches.csv`: matched FIFA coaches for matched clubs only.",
                "- `transfers.csv`: deduplicated transfer records referencing generated player and club keys.",
                "- `country_dim.csv`: country dictionary table.",
                "- `league_dim.csv`: league dictionary table keyed by league + country.",
                "- `position_dim.csv`: position dictionary table.",
                "- `player_type_dim.csv`: player-type dictionary table.",
                "- `male_players_subset.csv`: only matched FIFA player rows kept from the large total table.",
                "- `male_players_legacy_subset.csv`: only matched FIFA player rows kept from the legacy table.",
                "- `male_teams_subset.csv`: only matched FIFA team rows kept.",
                "- `male_coaches_subset.csv`: only coaches referenced by matched teams kept.",
                "- `mysql_schema.sql`: create-table script.",
                "- `mysql_load_data.sql`: `LOAD DATA LOCAL INFILE` script for MySQL.",
                "- `summary.json`: preprocessing counts and match coverage.",
                "",
                "## Summary",
                "",
                "```json",
                json.dumps(summary, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def write_workflow_log(summary: dict[str, object]) -> Path:
    path = OUTPUT_DIR / "cleaning_workflow_log.md"
    path.write_text(
        "\n".join(
            [
                "# Cleaning Workflow Log",
                "",
                "This file is the persistent record for the current cleaning workflow. It should be updated after every meaningful cleaning operation.",
                "",
                "## Scope",
                "",
                "- Only `maindata` is in scope.",
                "- `archive` and `sqlite_sequence` are excluded.",
                "- `Transfer Market Data.csv` is the master source table.",
                "- `Transfer Market Data Outgoing.csv` is excluded from downstream output because it is a byte-for-byte duplicate.",
                "",
                "## Naming Standard",
                "",
                "- Generated primary keys use `*_key`: `player_key`, `club_key`.",
                "- Source identifiers reused for joins keep the same names across tables: `player_id`, `team_id`, `coach_id`.",
                "- Source-version fields keep the same names across tables: `fifa_version`, `fifa_update`, `fifa_update_date`.",
                "- Directional transfer fields use `origin_*` and `destination_*` prefixes.",
                "- Entity names use stable labels: `player_name`, `club_name`, `team_name`, `league_name`, `country_name`.",
                "",
                "## Operation History",
                "",
                "### 2026-04-13 1. Transfer-centric base cleaning",
                "",
                "- Built `players.csv`, `clubs.csv`, `coaches.csv`, and `transfers.csv` under `maindata/sql_ready`.",
                "- Preserved every transfer record.",
                "- Used FIFA tables only as enrichment sources.",
                "",
                "### 2026-04-13 2. Subset compression fix",
                "",
                "- Changed `male_players_subset.csv` from full matched snapshot history to one representative record per matched `player_id`.",
                "- Changed `male_teams_subset.csv` from full matched snapshot history to one representative record per matched `team_id`.",
                "- Reduced unnecessary bulk while keeping joinable matched entities.",
                "",
                "### 2026-04-13 3. Join-friendly header normalization",
                "",
                "- Renamed repeated concepts to consistent names across cleaned tables.",
                "- Standardized join columns to `player_id`, `team_id`, and `coach_id` where they refer to the same source entities.",
                "- Standardized transfer direction fields to `origin_*` and `destination_*`.",
                "",
                "### 2026-04-13 4. Dimension list tables",
                "",
                "- Added `country_dim.csv`, `league_dim.csv`, `position_dim.csv`, and `player_type_dim.csv`.",
                "- Added `*_dim_id` reference columns into cleaned core tables while keeping readable text columns.",
                "- Updated MySQL schema and load scripts to include these dimensions.",
                "",
                "## Current Output Summary",
                "",
                "```json",
                json.dumps(summary, ensure_ascii=False, indent=2),
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    prep = prepare_transfer_core()

    best_player_candidates, matched_player_ids, matched_ids_by_name = enrich_players(prep)
    best_team_candidates, matched_team_ids, matched_coach_ids = enrich_teams(prep)

    players_fieldnames = [
        "player_key",
        "player_name",
        "player_name_normalized",
        "position_dim_id",
        "position",
        "age",
        "transfer_record_count",
        "first_transfer_date",
        "last_transfer_date",
        "player_match_status",
        "player_name_match_key",
        "player_id",
        "fifa_version",
        "fifa_update",
        "short_name",
        "long_name",
        "overall",
        "potential",
        "team_id",
        "team_name",
        "team_country_dim_id",
        "team_league_dim_id",
        "team_league_name",
        "nationality_country_dim_id",
        "nationality_name",
        "fifa_update_date",
        "player_source_table",
    ]
    clubs_fieldnames = [
        "club_key",
        "club_name",
        "club_name_normalized",
        "country_dim_id",
        "league_name",
        "league_dim_id",
        "country_name",
        "origin_transfer_count",
        "destination_transfer_count",
        "team_match_status",
        "team_id",
        "fifa_version",
        "fifa_update",
        "team_name",
        "team_league_name",
        "coach_id",
        "team_overall",
        "fifa_update_date",
    ]
    coaches_fieldnames = [
        "coach_id",
        "coach_url",
        "short_name",
        "long_name",
        "dob",
        "nationality_country_dim_id",
        "nationality_id",
        "nationality_name",
        "face_url",
    ]
    transfers_fieldnames = [
        "transfer_id",
        "player_key",
        "origin_club_key",
        "destination_club_key",
        "player_name",
        "position_dim_id",
        "position",
        "age",
        "origin_club_name",
        "origin_country_dim_id",
        "origin_league_name",
        "origin_league_dim_id",
        "origin_country_name",
        "destination_club_name",
        "destination_country_dim_id",
        "destination_league_name",
        "destination_league_dim_id",
        "destination_country_name",
        "player_market_value",
        "cost",
        "date_of_transfer",
        "destination_latitude",
        "destination_longitude",
        "destination_region",
        "origin_latitude",
        "origin_longitude",
        "origin_region",
        "week_of_transfer",
        "player_type_dim_id",
        "player_type",
    ]

    coach_rows: list[dict[str, str]] = []
    with COACHES_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if clean_text(row.get("coach_id", "")) in matched_coach_ids:
                coach_rows.append({k: clean_text(v) for k, v in row.items()})

    (
        country_rows,
        league_rows,
        position_rows,
        player_type_rows,
        country_id_map,
        league_id_map,
        position_id_map,
        player_type_id_map,
    ) = build_dimensions(prep.player_rows.values(), prep.club_rows.values(), coach_rows, prep.transfer_rows)
    attach_dimension_ids(
        prep.player_rows.values(),
        prep.club_rows.values(),
        coach_rows,
        prep.transfer_rows,
        country_id_map,
        league_id_map,
        position_id_map,
        player_type_id_map,
    )

    country_dim_count = write_csv(
        OUTPUT_DIR / "country_dim.csv",
        ["country_dim_id", "country_name", "country_name_normalized"],
        country_rows,
    )
    league_dim_count = write_csv(
        OUTPUT_DIR / "league_dim.csv",
        ["league_dim_id", "league_name", "league_name_normalized", "country_dim_id", "country_name"],
        league_rows,
    )
    position_dim_count = write_csv(
        OUTPUT_DIR / "position_dim.csv",
        ["position_dim_id", "position_name", "position_name_normalized"],
        position_rows,
    )
    player_type_dim_count = write_csv(
        OUTPUT_DIR / "player_type_dim.csv",
        ["player_type_dim_id", "player_type", "player_type_normalized"],
        player_type_rows,
    )

    selected_current_player_rows = {
        (
            candidate["player_id"],
            candidate["fifa_version"],
            candidate["fifa_update"],
            candidate["fifa_update_date"],
        )
        for candidate in best_player_candidates.values()
        if candidate["source_table"] == PLAYERS_FILE.name
    }
    selected_legacy_player_rows = {
        (
            candidate["player_id"],
            candidate["fifa_version"],
            candidate["fifa_update"],
            candidate["fifa_update_date"],
        )
        for candidate in best_player_candidates.values()
        if candidate["source_table"] == PLAYERS_LEGACY_FILE.name
    }
    selected_team_rows = {
        (
            candidate["team_id"],
            candidate["fifa_version"],
            candidate["fifa_update"],
            candidate["fifa_update_date"],
        )
        for candidate in best_team_candidates.values()
    }

    players_subset_count = write_selected_player_rows(PLAYERS_FILE, selected_current_player_rows, OUTPUT_DIR / "male_players_subset.csv")
    players_legacy_subset_count = write_selected_player_rows(PLAYERS_LEGACY_FILE, selected_legacy_player_rows, OUTPUT_DIR / "male_players_legacy_subset.csv")
    teams_subset_count, coach_ids_from_subset = write_selected_team_rows(selected_team_rows, OUTPUT_DIR / "male_teams_subset.csv")
    coaches_subset_count = write_coach_subset(coach_ids_from_subset, OUTPUT_DIR / "male_coaches_subset.csv")
    players_count = write_csv(OUTPUT_DIR / "players.csv", players_fieldnames, prep.player_rows.values())
    clubs_count = write_csv(OUTPUT_DIR / "clubs.csv", clubs_fieldnames, prep.club_rows.values())
    transfers_count = write_csv(OUTPUT_DIR / "transfers.csv", transfers_fieldnames, prep.transfer_rows)
    coaches_count = write_csv(OUTPUT_DIR / "coaches.csv", coaches_fieldnames, coach_rows)

    schema_path = write_mysql_schema()
    load_sql_path = write_mysql_load_sql()

    matched_player_rows = sum(1 for row in prep.player_rows.values() if row["player_match_status"] != "unmatched")
    matched_club_rows = sum(1 for row in prep.club_rows.values() if row["team_match_status"] == "matched")
    ambiguous_name_keys = sum(1 for ids in matched_ids_by_name.values() if len(ids) > 1)

    summary = {
        "raw_transfer_rows": prep.raw_transfer_rows,
        "deduplicated_transfer_rows": prep.dedup_transfer_rows,
        "duplicate_transfer_file_same_as_master": prep.duplicate_transfer_file_same,
        "players_dimension_rows": players_count,
        "clubs_dimension_rows": clubs_count,
        "coaches_dimension_rows": coaches_count,
        "transfers_fact_rows": transfers_count,
        "country_dim_rows": country_dim_count,
        "league_dim_rows": league_dim_count,
        "position_dim_rows": position_dim_count,
        "player_type_dim_rows": player_type_dim_count,
        "matched_transfer_player_rows": matched_player_rows,
        "matched_transfer_player_ratio": round(matched_player_rows / players_count, 4) if players_count else 0,
        "matched_transfer_club_rows": matched_club_rows,
        "matched_transfer_club_ratio": round(matched_club_rows / clubs_count, 4) if clubs_count else 0,
        "ambiguous_player_name_keys": ambiguous_name_keys,
        "male_players_subset_rows": players_subset_count,
        "male_players_legacy_subset_rows": players_legacy_subset_count,
        "male_teams_subset_rows": teams_subset_count,
        "male_coaches_subset_rows": coaches_subset_count,
        "mysql_schema": str(schema_path),
        "mysql_load_script": str(load_sql_path),
    }

    (OUTPUT_DIR / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    readme_path = write_import_readme(summary)
    workflow_log_path = write_workflow_log(summary)

    print(f"Wrote {OUTPUT_DIR / 'players.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'clubs.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'coaches.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'transfers.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'country_dim.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'league_dim.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'position_dim.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'player_type_dim.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'male_players_subset.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'male_players_legacy_subset.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'male_teams_subset.csv'}")
    print(f"Wrote {OUTPUT_DIR / 'male_coaches_subset.csv'}")
    print(f"Wrote {schema_path}")
    print(f"Wrote {load_sql_path}")
    print(f"Wrote {OUTPUT_DIR / 'summary.json'}")
    print(f"Wrote {readme_path}")
    print(f"Wrote {workflow_log_path}")


if __name__ == "__main__":
    main()
