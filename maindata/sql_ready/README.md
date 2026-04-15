# SQL Ready Output

This folder contains a transfer-centric cleaned dataset prepared from `maindata` only.

## Design rule

- `Transfer Market Data.csv` is the master fact table.
- `Transfer Market Data Outgoing.csv` is ignored because it is byte-for-byte identical.
- Every transfer record is preserved.
- `male_players.csv`, `male_players (legacy).csv`, `male_teams.csv`, and `male_coaches.csv` are used only as enrichment sources.
- Unused rows from the large FIFA total tables are not copied into the SQL-ready output.

## Files

- `players.csv`: one row per transfer-player key generated from normalized name + position + age.
- `clubs.csv`: one row per transfer club generated from normalized club name + league + country.
- `coaches.csv`: matched FIFA coaches for matched clubs only.
- `transfers.csv`: deduplicated transfer records referencing generated player and club keys.
- `country_dim.csv`: country dictionary table.
- `league_dim.csv`: league dictionary table keyed by league + country.
- `position_dim.csv`: position dictionary table.
- `player_type_dim.csv`: player-type dictionary table.
- `male_players_subset.csv`: only matched FIFA player rows kept from the large total table.
- `male_players_legacy_subset.csv`: only matched FIFA player rows kept from the legacy table.
- `male_teams_subset.csv`: only matched FIFA team rows kept.
- `male_coaches_subset.csv`: only coaches referenced by matched teams kept.
- `mysql_schema.sql`: create-table script.
- `mysql_load_data.sql`: `LOAD DATA LOCAL INFILE` script for MySQL.
- `summary.json`: preprocessing counts and match coverage.

## Summary

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
