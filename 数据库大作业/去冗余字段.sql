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
