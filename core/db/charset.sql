# charset for saving emoji's

SET NAMES utf8mb4;
# For each database:
ALTER DATABASE dwm_sentiment CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin;
# For each table:
ALTER TABLE posts CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
# For each column:
ALTER TABLE posts CHANGE text text text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
# (Don’t blindly copy-paste this! The exact statement depends on the column type, maximum length, and other properties. The above line is just an example for a `VARCHAR` column.)


# check charset
SELECT default_character_set_name FROM information_schema.SCHEMATA S WHERE schema_name = 'dwm_sentiment';
