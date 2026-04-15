# 现有空表结构修正 SQL

适用前提：

- 你已经按旧版模糊 schema 建好了表
- 当前还没有插入任何数据
- 数据库名为 `transfer_fifa_coursework_simplified`

在这个前提下，不需要重建数据库，也不需要做数据迁移，直接执行下面这份结构修正 SQL 即可。

对应可执行文件：

- `现有空表结构修正.sql`

```sql
USE transfer_fifa_coursework_simplified;

SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE players
  MODIFY COLUMN age TINYINT UNSIGNED NULL,
  MODIFY COLUMN transfer_record_count SMALLINT UNSIGNED NOT NULL,
  MODIFY COLUMN fifa_version SMALLINT UNSIGNED NULL,
  MODIFY COLUMN fifa_update SMALLINT UNSIGNED NULL,
  MODIFY COLUMN overall TINYINT UNSIGNED NULL,
  MODIFY COLUMN potential TINYINT UNSIGNED NULL;

ALTER TABLE clubs
  MODIFY COLUMN origin_transfer_count INT UNSIGNED NOT NULL,
  MODIFY COLUMN destination_transfer_count INT UNSIGNED NOT NULL,
  MODIFY COLUMN fifa_version SMALLINT UNSIGNED NULL,
  MODIFY COLUMN fifa_update SMALLINT UNSIGNED NULL,
  MODIFY COLUMN team_overall TINYINT UNSIGNED NULL;

ALTER TABLE transfers
  MODIFY COLUMN age TINYINT UNSIGNED NULL,
  MODIFY COLUMN player_market_value BIGINT UNSIGNED NULL,
  MODIFY COLUMN cost BIGINT UNSIGNED NULL,
  MODIFY COLUMN destination_latitude DECIMAL(10,7) NULL,
  MODIFY COLUMN destination_longitude DECIMAL(10,7) NULL,
  MODIFY COLUMN origin_latitude DECIMAL(10,7) NULL,
  MODIFY COLUMN origin_longitude DECIMAL(10,7) NULL,
  MODIFY COLUMN week_of_transfer TINYINT UNSIGNED NULL;

SET FOREIGN_KEY_CHECKS = 1;
```

本次核心修正点：

- `transfers.player_market_value` 从文本改为 `BIGINT UNSIGNED`
- `transfers.cost` 从文本改为 `BIGINT UNSIGNED`
- 经纬度字段从文本改为 `DECIMAL(10,7)`
- 多个年龄、评分、版本号、周次字段从文本改为整数类型

如果你准备直接重建而不是修补旧表，也可以直接使用：

- `简化数据库_SQL.md` 中最新的 `CREATE TABLE`
