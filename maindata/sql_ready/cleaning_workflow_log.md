# Cleaning Workflow Log

This file is the persistent record for the current cleaning workflow. It should be updated after every meaningful cleaning operation.

## Scope

- Only `maindata` is in scope.
- `archive` and `sqlite_sequence` are excluded.
- `Transfer Market Data.csv` is the master source table.
- `Transfer Market Data Outgoing.csv` is excluded from downstream output because it is a byte-for-byte duplicate.

## Naming Standard

- Generated primary keys use `*_key`: `player_key`, `club_key`.
- Source identifiers reused for joins keep the same names across tables: `player_id`, `team_id`, `coach_id`.
- Source-version fields keep the same names across tables: `fifa_version`, `fifa_update`, `fifa_update_date`.
- Directional transfer fields use `origin_*` and `destination_*` prefixes.
- Entity names use stable labels: `player_name`, `club_name`, `team_name`, `league_name`, `country_name`.

## Operation History

### 2026-04-13 1. Transfer-centric base cleaning

- Built `players.csv`, `clubs.csv`, `coaches.csv`, and `transfers.csv` under `maindata/sql_ready`.
- Preserved every transfer record.
- Used FIFA tables only as enrichment sources.

### 2026-04-13 2. Subset compression fix

- Changed `male_players_subset.csv` from full matched snapshot history to one representative record per matched `player_id`.
- Changed `male_teams_subset.csv` from full matched snapshot history to one representative record per matched `team_id`.
- Reduced unnecessary bulk while keeping joinable matched entities.

### 2026-04-13 3. Join-friendly header normalization

- Renamed repeated concepts to consistent names across cleaned tables.
- Standardized join columns to `player_id`, `team_id`, and `coach_id` where they refer to the same source entities.
- Standardized transfer direction fields to `origin_*` and `destination_*`.

### 2026-04-13 4. Dimension list tables

- Added `country_dim.csv`, `league_dim.csv`, `position_dim.csv`, and `player_type_dim.csv`.
- Added `*_dim_id` reference columns into cleaned core tables while keeping readable text columns.
- Updated MySQL schema and load scripts to include these dimensions.

### 2026-04-13 5. Coursework simplified database package

- Created `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业` as a standalone coursework package.
- Built a referentially closed simplified dataset by randomly sampling `600` transfer rows and backfilling the related `players`, `clubs`, and `coaches`.
- Kept the four dimension tables complete because `country_dim` and `league_dim` exceed a 100-row cutoff and act as hard lookup tables.
- Added a copied schema document, sampled CSV files, and a Markdown file containing `CREATE TABLE` and `INSERT` SQL for the simplified database.

### 2026-04-13 6. SQL type tightening

- Audited the cleaned CSV outputs for columns that were stored as numeric values but declared as `VARCHAR` in SQL.
- Changed `transfers.player_market_value` and `transfers.cost` to `BIGINT UNSIGNED`.
- Changed transfer coordinates to `DECIMAL(10,7)` and `week_of_transfer` to `TINYINT UNSIGNED`.
- Tightened additional numeric columns in `players` and `clubs`, including `age`, `fifa_version`, `fifa_update`, `overall`, `potential`, `team_overall`, and transfer-count columns.
- Regenerated the coursework package SQL so its `CREATE TABLE` and `INSERT` statements follow the corrected numeric types.

### 2026-04-13 7. Empty-table ALTER script for coursework database

- Added an `ALTER TABLE` script for the case where the coursework database was already created from the old loose schema but still contains no data.
- Saved the executable patch script as `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/现有空表结构修正.sql`.
- Saved a Markdown explanation copy as `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/现有空表结构修正_SQL.md`.

### 2026-04-13 8. Plain SQL export for coursework database

- Added `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/简化数据库.sql` as the executable SQL export of the simplified coursework package.
- Kept the Markdown version `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/简化数据库_SQL.md` for documentation, but the `.sql` file is now the direct import target.

### 2026-04-13 9. Redundant-name column removal script

- Added `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/去冗余字段.sql` to remove denormalized name columns that duplicate id-based references.
- Added `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/去冗余字段_SQL.md` as the documented version of the same script.
- The script keeps keys and `*_dim_id` columns, and drops name columns that can be reconstructed by joins.

### 2026-04-13 10. Transfer-country redundancy fix

- Refined the coursework redundancy-removal script so that `transfers` also drops `origin_country_dim_id`, `origin_league_dim_id`, `destination_country_dim_id`, and `destination_league_dim_id`.
- This aligns `transfers` with a stricter normalized design where club geography and league attributes are obtained through `origin_club_key` and `destination_club_key` joining to `clubs`.

### 2026-04-13 11. Coursework database documentation refresh

- Rewrote `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/简化数据库说明.md` to describe the final normalized database after applying both `简化数据库.sql` and `去冗余字段.sql`.
- Added per-table sections covering table purpose, row counts, key structure, final columns, and what each table stores.

### 2026-04-14 12. Coursework database data-flow diagrams

- Added `/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/数据流图.md`.
- The file contains 9 Mermaid diagrams: 1 overall first-level data flow diagram and 8 second-level table-specific diagrams.
- The diagrams are based on the final normalized database structure after applying both `简化数据库.sql` and `去冗余字段.sql`.

## Current Output Summary

```json
{
  "raw_transfer_rows": 19139,
  "deduplicated_transfer_rows": 19139,
  "duplicate_transfer_file_same_as_master": true,
  "players_dimension_rows": 19022,
  "clubs_dimension_rows": 6749,
  "coaches_dimension_rows": 530,
  "transfers_fact_rows": 19139,
  "country_dim_rows": 176,
  "league_dim_rows": 535,
  "position_dim_rows": 16,
  "player_type_dim_rows": 4,
  "matched_transfer_player_rows": 4863,
  "matched_transfer_player_ratio": 0.2557,
  "matched_transfer_club_rows": 532,
  "matched_transfer_club_ratio": 0.0788,
  "ambiguous_player_name_keys": 259,
  "male_players_subset_rows": 4740,
  "male_players_legacy_subset_rows": 0,
  "male_teams_subset_rows": 532,
  "male_coaches_subset_rows": 530,
  "mysql_schema": "/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/mysql_schema.sql",
  "mysql_load_script": "/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/mysql_load_data.sql"
}
```
