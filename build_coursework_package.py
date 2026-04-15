from __future__ import annotations

import csv
import random
from pathlib import Path


ROOT = Path("/Users/apple/Desktop/surviveFdu/数据库与企业数据管理")
SOURCE_DIR = ROOT / "maindata" / "sql_ready"
TARGET_DIR = ROOT / "数据库大作业"

RANDOM_SEED = 20260413
BASE_TRANSFER_SAMPLE_SIZE = 600
DATABASE_NAME = "transfer_fifa_coursework_simplified"

CORE_TABLES = [
    "players.csv",
    "clubs.csv",
    "coaches.csv",
    "transfers.csv",
]

DIMENSION_TABLES = [
    "country_dim.csv",
    "league_dim.csv",
    "position_dim.csv",
    "player_type_dim.csv",
]


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def write_csv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)


NUMERIC_COLUMNS: dict[str, set[str]] = {
    "country_dim.csv": {"country_dim_id"},
    "league_dim.csv": {"league_dim_id", "country_dim_id"},
    "position_dim.csv": {"position_dim_id"},
    "player_type_dim.csv": {"player_type_dim_id"},
    "coaches.csv": {"coach_id", "nationality_country_dim_id", "nationality_id"},
    "players.csv": {
        "position_dim_id",
        "age",
        "transfer_record_count",
        "player_id",
        "fifa_version",
        "fifa_update",
        "overall",
        "potential",
        "team_id",
        "team_country_dim_id",
        "team_league_dim_id",
        "nationality_country_dim_id",
    },
    "clubs.csv": {
        "country_dim_id",
        "league_dim_id",
        "origin_transfer_count",
        "destination_transfer_count",
        "team_id",
        "fifa_version",
        "fifa_update",
        "coach_id",
        "team_overall",
    },
    "transfers.csv": {
        "transfer_id",
        "position_dim_id",
        "age",
        "origin_country_dim_id",
        "origin_league_dim_id",
        "destination_country_dim_id",
        "destination_league_dim_id",
        "player_market_value",
        "cost",
        "destination_latitude",
        "destination_longitude",
        "origin_latitude",
        "origin_longitude",
        "week_of_transfer",
        "player_type_dim_id",
    },
}

DATE_COLUMNS: dict[str, set[str]] = {
    "coaches.csv": {"dob"},
    "players.csv": {"first_transfer_date", "last_transfer_date", "fifa_update_date"},
    "clubs.csv": {"fifa_update_date"},
    "transfers.csv": {"date_of_transfer"},
}


def sql_literal(value: str) -> str:
    if value == "":
        return "NULL"
    escaped = value.replace("\\", "\\\\").replace("'", "''")
    return f"'{escaped}'"


def format_value_for_column(csv_name: str, column: str, value: str) -> str:
    if value == "":
        return "NULL"
    if column in NUMERIC_COLUMNS.get(csv_name, set()):
        return value
    if column in DATE_COLUMNS.get(csv_name, set()):
        return f"'{value}'"
    return sql_literal(value)


def format_insert_block(csv_name: str, table_name: str, header: list[str], rows: list[dict[str, str]]) -> str:
    if not rows:
        return f"-- {table_name} has no rows in the simplified package.\n"
    column_list = ", ".join(header)
    chunks: list[str] = []
    batch_size = 200
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        value_lines = []
        for row in batch:
            values = ", ".join(
                format_value_for_column(csv_name, column, row[column]) for column in header
            )
            value_lines.append(f"  ({values})")
        chunk = (
            f"INSERT INTO {table_name} ({column_list}) VALUES\n"
            + ",\n".join(value_lines)
            + ";\n"
        )
        chunks.append(chunk)
    return "\n".join(chunks)


def build_create_table_sql() -> str:
    return f"""CREATE DATABASE IF NOT EXISTS {DATABASE_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE {DATABASE_NAME};

DROP TABLE IF EXISTS transfers;
DROP TABLE IF EXISTS clubs;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS coaches;
DROP TABLE IF EXISTS league_dim;
DROP TABLE IF EXISTS country_dim;
DROP TABLE IF EXISTS position_dim;
DROP TABLE IF EXISTS player_type_dim;

CREATE TABLE country_dim (
  country_dim_id INT PRIMARY KEY,
  country_name VARCHAR(255) NOT NULL,
  country_name_normalized VARCHAR(255) NOT NULL
);

CREATE TABLE league_dim (
  league_dim_id INT PRIMARY KEY,
  league_name VARCHAR(255) NOT NULL,
  league_name_normalized VARCHAR(255) NOT NULL,
  country_dim_id INT NOT NULL,
  country_name VARCHAR(255) NOT NULL,
  CONSTRAINT fk_league_country FOREIGN KEY (country_dim_id) REFERENCES country_dim(country_dim_id)
);

CREATE TABLE position_dim (
  position_dim_id INT PRIMARY KEY,
  position_name VARCHAR(255) NOT NULL,
  position_name_normalized VARCHAR(255) NOT NULL
);

CREATE TABLE player_type_dim (
  player_type_dim_id INT PRIMARY KEY,
  player_type VARCHAR(255) NOT NULL,
  player_type_normalized VARCHAR(255) NOT NULL
);

CREATE TABLE coaches (
  coach_id BIGINT PRIMARY KEY,
  coach_url VARCHAR(255),
  short_name VARCHAR(255),
  long_name VARCHAR(255),
  dob DATE NULL,
  nationality_country_dim_id INT NULL,
  nationality_id BIGINT NULL,
  nationality_name VARCHAR(255),
  face_url VARCHAR(512),
  CONSTRAINT fk_coaches_nationality_dim FOREIGN KEY (nationality_country_dim_id) REFERENCES country_dim(country_dim_id)
);

CREATE TABLE players (
  player_key CHAR(40) PRIMARY KEY,
  player_name VARCHAR(255) NOT NULL,
  player_name_normalized VARCHAR(255) NOT NULL,
  position_dim_id INT NULL,
  position VARCHAR(128),
  age TINYINT UNSIGNED NULL,
  transfer_record_count SMALLINT UNSIGNED NOT NULL,
  first_transfer_date DATE NULL,
  last_transfer_date DATE NULL,
  player_match_status VARCHAR(64) NOT NULL,
  player_name_match_key VARCHAR(255),
  player_id BIGINT NULL,
  fifa_version SMALLINT UNSIGNED NULL,
  fifa_update SMALLINT UNSIGNED NULL,
  short_name VARCHAR(255),
  long_name VARCHAR(255),
  overall TINYINT UNSIGNED NULL,
  potential TINYINT UNSIGNED NULL,
  team_id BIGINT NULL,
  team_name VARCHAR(255),
  team_country_dim_id INT NULL,
  team_league_dim_id INT NULL,
  team_league_name VARCHAR(255),
  nationality_country_dim_id INT NULL,
  nationality_name VARCHAR(255),
  fifa_update_date DATE NULL,
  player_source_table VARCHAR(128),
  CONSTRAINT fk_players_position_dim FOREIGN KEY (position_dim_id) REFERENCES position_dim(position_dim_id),
  CONSTRAINT fk_players_team_country_dim FOREIGN KEY (team_country_dim_id) REFERENCES country_dim(country_dim_id),
  CONSTRAINT fk_players_team_league_dim FOREIGN KEY (team_league_dim_id) REFERENCES league_dim(league_dim_id),
  CONSTRAINT fk_players_nationality_dim FOREIGN KEY (nationality_country_dim_id) REFERENCES country_dim(country_dim_id)
);

CREATE TABLE clubs (
  club_key CHAR(40) PRIMARY KEY,
  club_name VARCHAR(255) NOT NULL,
  club_name_normalized VARCHAR(255) NOT NULL,
  country_dim_id INT NULL,
  league_name VARCHAR(255),
  league_dim_id INT NULL,
  country_name VARCHAR(255),
  origin_transfer_count INT UNSIGNED NOT NULL,
  destination_transfer_count INT UNSIGNED NOT NULL,
  team_match_status VARCHAR(64) NOT NULL,
  team_id BIGINT NULL,
  fifa_version SMALLINT UNSIGNED NULL,
  fifa_update SMALLINT UNSIGNED NULL,
  team_name VARCHAR(255),
  team_league_name VARCHAR(255),
  coach_id BIGINT NULL,
  team_overall TINYINT UNSIGNED NULL,
  fifa_update_date DATE NULL,
  CONSTRAINT fk_clubs_country_dim FOREIGN KEY (country_dim_id) REFERENCES country_dim(country_dim_id),
  CONSTRAINT fk_clubs_league_dim FOREIGN KEY (league_dim_id) REFERENCES league_dim(league_dim_id),
  CONSTRAINT fk_clubs_coach FOREIGN KEY (coach_id) REFERENCES coaches(coach_id)
);

CREATE TABLE transfers (
  transfer_id BIGINT PRIMARY KEY,
  player_key CHAR(40) NOT NULL,
  origin_club_key CHAR(40) NOT NULL,
  destination_club_key CHAR(40) NOT NULL,
  player_name VARCHAR(255) NOT NULL,
  position_dim_id INT NULL,
  position VARCHAR(128),
  age TINYINT UNSIGNED NULL,
  origin_club_name VARCHAR(255),
  origin_country_dim_id INT NULL,
  origin_league_name VARCHAR(255),
  origin_league_dim_id INT NULL,
  origin_country_name VARCHAR(255),
  destination_club_name VARCHAR(255),
  destination_country_dim_id INT NULL,
  destination_league_name VARCHAR(255),
  destination_league_dim_id INT NULL,
  destination_country_name VARCHAR(255),
  player_market_value BIGINT UNSIGNED NULL,
  cost BIGINT UNSIGNED NULL,
  date_of_transfer DATE NULL,
  destination_latitude DECIMAL(10,7) NULL,
  destination_longitude DECIMAL(10,7) NULL,
  destination_region VARCHAR(255),
  origin_latitude DECIMAL(10,7) NULL,
  origin_longitude DECIMAL(10,7) NULL,
  origin_region VARCHAR(255),
  week_of_transfer TINYINT UNSIGNED NULL,
  player_type_dim_id INT NULL,
  player_type VARCHAR(128),
  CONSTRAINT fk_transfers_player FOREIGN KEY (player_key) REFERENCES players(player_key),
  CONSTRAINT fk_transfers_origin FOREIGN KEY (origin_club_key) REFERENCES clubs(club_key),
  CONSTRAINT fk_transfers_destination FOREIGN KEY (destination_club_key) REFERENCES clubs(club_key),
  CONSTRAINT fk_transfers_position_dim FOREIGN KEY (position_dim_id) REFERENCES position_dim(position_dim_id),
  CONSTRAINT fk_transfers_origin_country_dim FOREIGN KEY (origin_country_dim_id) REFERENCES country_dim(country_dim_id),
  CONSTRAINT fk_transfers_destination_country_dim FOREIGN KEY (destination_country_dim_id) REFERENCES country_dim(country_dim_id),
  CONSTRAINT fk_transfers_origin_league_dim FOREIGN KEY (origin_league_dim_id) REFERENCES league_dim(league_dim_id),
  CONSTRAINT fk_transfers_destination_league_dim FOREIGN KEY (destination_league_dim_id) REFERENCES league_dim(league_dim_id),
  CONSTRAINT fk_transfers_player_type_dim FOREIGN KEY (player_type_dim_id) REFERENCES player_type_dim(player_type_dim_id)
);
"""


def sample_rows(
    rows: list[dict[str, str]],
    key_name: str,
    required_keys: set[str],
    minimum_size: int,
    rng: random.Random,
) -> list[dict[str, str]]:
    row_by_key = {row[key_name]: row for row in rows}
    selected_keys = {key for key in required_keys if key in row_by_key}
    extra_candidates = [row[key_name] for row in rows if row[key_name] not in selected_keys]
    needed = max(0, min(minimum_size, len(rows)) - len(selected_keys))
    if needed > 0:
        selected_keys.update(rng.sample(extra_candidates, needed))
    selected = [row for row in rows if row[key_name] in selected_keys]
    return selected


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RANDOM_SEED)

    headers: dict[str, list[str]] = {}
    tables: dict[str, list[dict[str, str]]] = {}
    for name in CORE_TABLES + DIMENSION_TABLES:
        header, rows = read_csv(SOURCE_DIR / name)
        headers[name] = header
        tables[name] = rows

    transfer_rows = tables["transfers.csv"]
    transfer_sample_size = min(BASE_TRANSFER_SAMPLE_SIZE, len(transfer_rows))
    sampled_transfers = rng.sample(transfer_rows, transfer_sample_size)

    player_keys = {row["player_key"] for row in sampled_transfers}
    club_keys = {
        row["origin_club_key"] for row in sampled_transfers
    } | {row["destination_club_key"] for row in sampled_transfers}

    sampled_players = [row for row in tables["players.csv"] if row["player_key"] in player_keys]
    sampled_clubs = [row for row in tables["clubs.csv"] if row["club_key"] in club_keys]

    required_coach_ids = {row["coach_id"] for row in sampled_clubs if row["coach_id"]}
    sampled_coaches = sample_rows(
        rows=tables["coaches.csv"],
        key_name="coach_id",
        required_keys=required_coach_ids,
        minimum_size=100,
        rng=rng,
    )

    sampled_country_dim = tables["country_dim.csv"]
    sampled_league_dim = tables["league_dim.csv"]
    sampled_position_dim = tables["position_dim.csv"]
    sampled_player_type_dim = tables["player_type_dim.csv"]

    outputs = {
        "country_dim.csv": sampled_country_dim,
        "league_dim.csv": sampled_league_dim,
        "position_dim.csv": sampled_position_dim,
        "player_type_dim.csv": sampled_player_type_dim,
        "coaches.csv": sampled_coaches,
        "players.csv": sampled_players,
        "clubs.csv": sampled_clubs,
        "transfers.csv": sampled_transfers,
    }

    for name, rows in outputs.items():
        write_csv(TARGET_DIR / name, headers[name], rows)

    schema_copy = (SOURCE_DIR / "cleaned_tables_schema.md").read_text(encoding="utf-8")
    (TARGET_DIR / "cleaned_tables_schema.md").write_text(schema_copy, encoding="utf-8")

    summary_md = f"""# 简化数据库说明

## 数据来源

- 来源目录：`maindata/sql_ready`
- 输出目录：`数据库大作业`
- 随机种子：`{RANDOM_SEED}`
- 抽样方式：以 `transfers.csv` 为中心随机抽取 `{transfer_sample_size}` 条记录，再保留其关联的 `players`、`clubs`、`coaches`

## 为什么不是每张表独立随机取 100 行

- 独立抽样会直接破坏外键对应关系，例如 `transfers.player_key` 找不到 `players.player_key`
- 维表中存在硬性小表与清单表，例如 `country_dim` 共 `{len(sampled_country_dim)}` 行、`league_dim` 共 `{len(sampled_league_dim)}` 行，直接裁成 100 行会丢失大量合法引用
- 因此本简化库保留了完整维表，并对事实表做可闭合抽样

## 当前简化库包含的表

| table_name | rows | note |
| --- | ---: | --- |
| `country_dim.csv` | {len(sampled_country_dim)} | 完整国家清单维表 |
| `league_dim.csv` | {len(sampled_league_dim)} | 完整联赛清单维表 |
| `position_dim.csv` | {len(sampled_position_dim)} | 完整位置清单维表 |
| `player_type_dim.csv` | {len(sampled_player_type_dim)} | 完整球员类型维表 |
| `coaches.csv` | {len(sampled_coaches)} | 保留被引用教练，并补足到至少 100 行 |
| `players.csv` | {len(sampled_players)} | 由抽样转会反推得到的关联球员 |
| `clubs.csv` | {len(sampled_clubs)} | 由抽样转会反推得到的关联俱乐部 |
| `transfers.csv` | {len(sampled_transfers)} | 简化库主事实表 |

## 外键闭合性

- `transfers.player_key -> players.player_key`
- `transfers.origin_club_key -> clubs.club_key`
- `transfers.destination_club_key -> clubs.club_key`
- `clubs.coach_id -> coaches.coach_id`
- `players`、`clubs`、`coaches`、`transfers` 中的 `*_dim_id` 都可以在对应维表中找到
"""
    (TARGET_DIR / "简化数据库说明.md").write_text(summary_md, encoding="utf-8")

    create_sql = build_create_table_sql()
    insert_sections = []
    sql_insert_blocks = []
    for table_name in [
        "country_dim.csv",
        "league_dim.csv",
        "position_dim.csv",
        "player_type_dim.csv",
        "coaches.csv",
        "players.csv",
        "clubs.csv",
        "transfers.csv",
    ]:
        insert_sql = format_insert_block(
            table_name,
            table_name.replace(".csv", ""),
            headers[table_name],
            outputs[table_name],
        )
        insert_sections.append(
            f"## {table_name}\n\n```sql\n"
            + insert_sql
            + "```\n"
        )
        sql_insert_blocks.append(insert_sql)

    sql_md = (
        "# 简化数据库 SQL\n\n"
        "本文档提供 `数据库大作业` 目录下简化数据库的建表语句与插数语句。\n\n"
        "## CREATE TABLE\n\n```sql\n"
        + create_sql
        + "```\n\n## INSERT DATA\n\n"
        + "\n".join(insert_sections)
    )
    (TARGET_DIR / "简化数据库_SQL.md").write_text(sql_md, encoding="utf-8")

    sql_file = create_sql + "\n" + "\n".join(sql_insert_blocks)
    (TARGET_DIR / "简化数据库.sql").write_text(sql_file, encoding="utf-8")


if __name__ == "__main__":
    main()
