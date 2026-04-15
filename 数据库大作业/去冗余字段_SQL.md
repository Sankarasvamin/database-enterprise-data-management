# 去冗余字段 SQL

适用场景：

- 你先执行 [简化数据库.sql](/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/数据库大作业/简化数据库.sql) 完成建库和插数
- 然后希望删掉那些可以通过外键 join 还原出来的冗余字段

执行顺序：

1. `简化数据库.sql`
2. `去冗余字段.sql`

```sql
USE transfer_fifa_coursework_simplified;

SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE league_dim
  DROP COLUMN country_name;

ALTER TABLE players
  DROP COLUMN position,
  DROP COLUMN team_league_name,
  DROP COLUMN nationality_name;

ALTER TABLE clubs
  DROP COLUMN league_name,
  DROP COLUMN country_name,
  DROP COLUMN team_league_name;

ALTER TABLE coaches
  DROP COLUMN nationality_name;

ALTER TABLE transfers
  DROP COLUMN player_name,
  DROP COLUMN position,
  DROP COLUMN origin_club_name,
  DROP COLUMN origin_country_dim_id,
  DROP COLUMN origin_league_name,
  DROP COLUMN origin_league_dim_id,
  DROP COLUMN origin_country_name,
  DROP COLUMN destination_club_name,
  DROP COLUMN destination_country_dim_id,
  DROP COLUMN destination_league_name,
  DROP COLUMN destination_league_dim_id,
  DROP COLUMN destination_country_name,
  DROP COLUMN player_type;

SET FOREIGN_KEY_CHECKS = 1;
```

删除逻辑说明：

- 保留真正必要的主键、外键和维表键
- 删除可通过 join 还原出来的冗余列，不限于名称列
- 例如：
  - `transfers.origin_club_key -> clubs.club_key -> clubs.country_dim_id`，所以 `transfers.origin_country_dim_id` 删除
  - `transfers.destination_club_key -> clubs.club_key -> clubs.league_dim_id`，所以 `transfers.destination_league_dim_id` 删除
  - `players.position_dim_id` 保留，`players.position` 删除

这次修正后，`transfers` 中与俱乐部属性重复的国家和联赛信息都不再保留，查询时应通过 `clubs` 表取回。
