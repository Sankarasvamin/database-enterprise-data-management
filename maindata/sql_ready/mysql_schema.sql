CREATE DATABASE IF NOT EXISTS transfer_fifa_clean CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE transfer_fifa_clean;

DROP TABLE IF EXISTS transfers;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS clubs;
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
  CONSTRAINT fk_clubs_league_dim FOREIGN KEY (league_dim_id) REFERENCES league_dim(league_dim_id));

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
  CONSTRAINT fk_coaches_nationality_dim FOREIGN KEY (nationality_country_dim_id) REFERENCES country_dim(country_dim_id));

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
