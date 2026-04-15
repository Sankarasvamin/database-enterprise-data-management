USE transfer_fifa_clean;

SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE transfers;
TRUNCATE TABLE coaches;
TRUNCATE TABLE clubs;
TRUNCATE TABLE players;
TRUNCATE TABLE player_type_dim;
TRUNCATE TABLE position_dim;
TRUNCATE TABLE league_dim;
TRUNCATE TABLE country_dim;

LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/country_dim.csv' INTO TABLE country_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/league_dim.csv' INTO TABLE league_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/position_dim.csv' INTO TABLE position_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/player_type_dim.csv' INTO TABLE player_type_dim CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/players.csv' INTO TABLE players CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/clubs.csv' INTO TABLE clubs CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/coaches.csv' INTO TABLE coaches CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/Users/apple/Desktop/surviveFdu/数据库与企业数据管理/maindata/sql_ready/transfers.csv' INTO TABLE transfers CHARACTER SET utf8mb4 FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '"' LINES TERMINATED BY '\n' IGNORE 1 LINES;

SET FOREIGN_KEY_CHECKS = 1;
