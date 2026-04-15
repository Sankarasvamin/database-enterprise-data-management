# Cleaned Tables Schema

本文档只描述 `maindata/sql_ready` 中清洗后的业务数据表，不包含原始源表，也不包含 SQL 脚本、说明文件和统计 JSON。

## 总览

| table_name | rows | columns | role |
| --- | ---: | ---: | --- |
| `country_dim.csv` | 176 | 3 | 国家清单维表 |
| `league_dim.csv` | 535 | 5 | 联赛清单维表，按联赛名 + 国家唯一 |
| `position_dim.csv` | 16 | 3 | 位置清单维表 |
| `player_type_dim.csv` | 4 | 3 | 球员类型清单维表 |
| `players.csv` | 19,022 | 27 | 转会球员维表，保证所有有转会记录的球员都被保留 |
| `clubs.csv` | 6,749 | 18 | 转会俱乐部维表，覆盖转出与转入俱乐部 |
| `coaches.csv` | 530 | 9 | 能通过匹配球队补充到的教练维表 |
| `transfers.csv` | 19,139 | 30 | 转会事实表，是最终入库的主事实表 |
| `male_players_subset.csv` | 4,740 | 110 | 按 `players.csv` 中已匹配 FIFA 球员压缩后的代表性球员子集 |
| `male_players_legacy_subset.csv` | 0 | 110 | 当前匹配结果未选择 legacy 代表记录，因此为空 |
| `male_teams_subset.csv` | 532 | 54 | 按 `clubs.csv` 中已匹配 FIFA 球队压缩后的代表性球队子集 |
| `male_coaches_subset.csv` | 530 | 8 | 与压缩后球队子集实际关联的教练子集 |

## 清单维表

### `country_dim.csv`

- 用途：国家名称清单
- 主键建议：`country_dim_id`
- 说明：供 `players`、`clubs`、`coaches`、`transfers` 中的国家字段做 id 对照

表头：

```text
country_dim_id, country_name, country_name_normalized
```

### `league_dim.csv`

- 用途：联赛名称清单
- 主键建议：`league_dim_id`
- 说明：按 `league_name + country_dim_id` 唯一，用于减少联赛名称重复

表头：

```text
league_dim_id, league_name, league_name_normalized, country_dim_id, country_name
```

### `position_dim.csv`

- 用途：位置名称清单
- 主键建议：`position_dim_id`

表头：

```text
position_dim_id, position_name, position_name_normalized
```

### `player_type_dim.csv`

- 用途：转会球员类型清单
- 主键建议：`player_type_dim_id`

表头：

```text
player_type_dim_id, player_type, player_type_normalized
```

## 核心 SQL 表

### `players.csv`

- 用途：转会球员维表
- 主键建议：`player_key`
- 说明：以转会记录为主生成，FIFA 信息只是补充字段，不保证每个球员都能匹配到 FIFA；`position_dim_id`、`nationality_country_dim_id` 等字段可直接和清单维表 join

表头：

```text
player_key, player_name, player_name_normalized, position_dim_id, position, age, transfer_record_count, first_transfer_date, last_transfer_date, player_match_status, player_name_match_key, player_id, fifa_version, fifa_update, short_name, long_name, overall, potential, team_id, team_name, team_country_dim_id, team_league_dim_id, team_league_name, nationality_country_dim_id, nationality_name, fifa_update_date, player_source_table
```

### `clubs.csv`

- 用途：转会俱乐部维表
- 主键建议：`club_key`
- 说明：俱乐部唯一键由标准化名称 + 联赛 + 国家组合生成；`country_dim_id` 和 `league_dim_id` 可直接对照清单维表

表头：

```text
club_key, club_name, club_name_normalized, country_dim_id, league_name, league_dim_id, country_name, origin_transfer_count, destination_transfer_count, team_match_status, team_id, fifa_version, fifa_update, team_name, team_league_name, coach_id, team_overall, fifa_update_date
```

### `coaches.csv`

- 用途：匹配球队后保留下来的教练维表
- 主键建议：`coach_id`
- 说明：只包含在匹配球队中实际被引用到的教练；国籍也可通过 `nationality_country_dim_id` 对照国家维表

表头：

```text
coach_id, coach_url, short_name, long_name, dob, nationality_country_dim_id, nationality_id, nationality_name, face_url
```

### `transfers.csv`

- 用途：转会事实表
- 主键建议：`transfer_id`
- 外键建议：`player_key -> players.player_key`，`origin_club_key -> clubs.club_key`，`destination_club_key -> clubs.club_key`
- 说明：该表保留全部转会记录，是最终上传 SQL 时的中心事实表；同时通过 `position_dim_id`、`origin_country_dim_id`、`origin_league_dim_id`、`destination_country_dim_id`、`destination_league_dim_id`、`player_type_dim_id` 引用清单维表

表头：

```text
transfer_id, player_key, origin_club_key, destination_club_key, player_name, position_dim_id, position, age, origin_club_name, origin_country_dim_id, origin_league_name, origin_league_dim_id, origin_country_name, destination_club_name, destination_country_dim_id, destination_league_name, destination_league_dim_id, destination_country_name, player_market_value, cost, date_of_transfer, destination_latitude, destination_longitude, destination_region, origin_latitude, origin_longitude, origin_region, week_of_transfer, player_type_dim_id, player_type
```

## FIFA 补充子集表

### `male_players_subset.csv`

- 用途：从 `male_players.csv` 中裁出的匹配球员代表子集
- 主键语义：快照表，建议行级键 `(player_id, fifa_version, fifa_update)`
- 说明：每个已匹配 `player_id` 只保留 1 条代表记录，不再保留全部历史快照

表头：

```text
player_id, player_url, fifa_version, fifa_update, fifa_update_date, short_name, long_name, player_positions, overall, potential, value_eur, wage_eur, age, dob, height_cm, weight_kg, league_id, league_name, league_level, club_team_id, club_name, club_position, club_jersey_number, club_loaned_from, club_joined_date, club_contract_valid_until_year, nationality_id, nationality_name, nation_team_id, nation_position, nation_jersey_number, preferred_foot, weak_foot, skill_moves, international_reputation, work_rate, body_type, real_face, release_clause_eur, player_tags, player_traits, pace, shooting, passing, dribbling, defending, physic, attacking_crossing, attacking_finishing, attacking_heading_accuracy, attacking_short_passing, attacking_volleys, skill_dribbling, skill_curve, skill_fk_accuracy, skill_long_passing, skill_ball_control, movement_acceleration, movement_sprint_speed, movement_agility, movement_reactions, movement_balance, power_shot_power, power_jumping, power_stamina, power_strength, power_long_shots, mentality_aggression, mentality_interceptions, mentality_positioning, mentality_vision, mentality_penalties, mentality_composure, defending_marking_awareness, defending_standing_tackle, defending_sliding_tackle, goalkeeping_diving, goalkeeping_handling, goalkeeping_kicking, goalkeeping_positioning, goalkeeping_reflexes, goalkeeping_speed, ls, st, rs, lw, lf, cf, rf, rw, lam, cam, ram, lm, lcm, cm, rcm, rm, lwb, ldm, cdm, rdm, rwb, lb, lcb, cb, rcb, rb, gk, player_face_url
```

### `male_players_legacy_subset.csv`

- 用途：从 `male_players (legacy).csv` 中裁出的匹配球员历史子集
- 主键语义：快照表，建议行级键 `(player_id, fifa_version, fifa_update)`
- 说明：结构与 `male_players_subset.csv` 相同；当前最佳匹配全部落在当前表，因此此表目前为空

表头：

```text
player_id, player_url, fifa_version, fifa_update, fifa_update_date, short_name, long_name, player_positions, overall, potential, value_eur, wage_eur, age, dob, height_cm, weight_kg, league_id, league_name, league_level, club_team_id, club_name, club_position, club_jersey_number, club_loaned_from, club_joined_date, club_contract_valid_until_year, nationality_id, nationality_name, nation_team_id, nation_position, nation_jersey_number, preferred_foot, weak_foot, skill_moves, international_reputation, work_rate, body_type, real_face, release_clause_eur, player_tags, player_traits, pace, shooting, passing, dribbling, defending, physic, attacking_crossing, attacking_finishing, attacking_heading_accuracy, attacking_short_passing, attacking_volleys, skill_dribbling, skill_curve, skill_fk_accuracy, skill_long_passing, skill_ball_control, movement_acceleration, movement_sprint_speed, movement_agility, movement_reactions, movement_balance, power_shot_power, power_jumping, power_stamina, power_strength, power_long_shots, mentality_aggression, mentality_interceptions, mentality_positioning, mentality_vision, mentality_penalties, mentality_composure, defending_marking_awareness, defending_standing_tackle, defending_sliding_tackle, goalkeeping_diving, goalkeeping_handling, goalkeeping_kicking, goalkeeping_positioning, goalkeeping_reflexes, goalkeeping_speed, ls, st, rs, lw, lf, cf, rf, rw, lam, cam, ram, lm, lcm, cm, rcm, rm, lwb, ldm, cdm, rdm, rwb, lb, lcb, cb, rcb, rb, gk, player_face_url
```

### `male_teams_subset.csv`

- 用途：从 `male_teams.csv` 中裁出的匹配球队代表子集
- 主键语义：快照表，建议行级键 `(team_id, fifa_version, fifa_update)`
- 说明：每个已匹配 `team_id` 只保留 1 条代表记录，不再保留全部球队快照

表头：

```text
team_id, team_url, fifa_version, fifa_update, fifa_update_date, team_name, league_id, league_name, league_level, nationality_id, nationality_name, overall, attack, midfield, defence, coach_id, home_stadium, rival_team, international_prestige, domestic_prestige, transfer_budget_eur, club_worth_eur, starting_xi_average_age, whole_team_average_age, captain, short_free_kick, long_free_kick, left_short_free_kick, right_short_free_kick, penalties, left_corner, right_corner, def_style, def_team_width, def_team_depth, def_defence_pressure, def_defence_aggression, def_defence_width, def_defence_defender_line, off_style, off_build_up_play, off_chance_creation, off_team_width, off_players_in_box, off_corners, off_free_kicks, build_up_play_speed, build_up_play_dribbling, build_up_play_passing, build_up_play_positioning, chance_creation_passing, chance_creation_crossing, chance_creation_shooting, chance_creation_positioning
```

### `male_coaches_subset.csv`

- 用途：从 `male_coaches.csv` 中裁出的匹配教练子集
- 主键建议：`coach_id`
- 说明：与 `coaches.csv` 同结构，但来源是 FIFA 原始总表中的子集

表头：

```text
coach_id, coach_url, short_name, long_name, dob, nationality_id, nationality_name, face_url
```

## 备注

- 最终上传 SQL 时，优先使用核心四张表：`players.csv`、`clubs.csv`、`coaches.csv`、`transfers.csv`
- 如果目标是减少文本量并规范 join，推荐同时上传四张清单维表：`country_dim.csv`、`league_dim.csv`、`position_dim.csv`、`player_type_dim.csv`
- 四张 `*_subset.csv` 更适合作为补充审计表或二级分析表，不建议替代核心维表/事实表
- `transfers.csv` 是完备性最高的主表，因为它保留了全部转会记录
- 为了方便后续 join，跨表复用的源实体字段已统一为 `player_id`、`team_id`、`coach_id`
