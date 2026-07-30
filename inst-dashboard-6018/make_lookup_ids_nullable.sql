-- Make difficulty_level_id nullable
ALTER TABLE questions RENAME COLUMN difficulty_level_id TO old_difficulty_level_id;
ALTER TABLE questions ADD COLUMN difficulty_level_id INTEGER;
UPDATE questions SET difficulty_level_id = old_difficulty_level_id;
ALTER TABLE questions DROP COLUMN old_difficulty_level_id;

-- Make cognitive_level_id nullable
ALTER TABLE questions RENAME COLUMN cognitive_level_id TO old_cognitive_level_id;
ALTER TABLE questions ADD COLUMN cognitive_level_id INTEGER;
UPDATE questions SET cognitive_level_id = old_cognitive_level_id;
ALTER TABLE questions DROP COLUMN old_cognitive_level_id;

-- Make learning_outcome_id nullable
ALTER TABLE questions RENAME COLUMN learning_outcome_id TO old_learning_outcome_id;
ALTER TABLE questions ADD COLUMN learning_outcome_id INTEGER;
UPDATE questions SET learning_outcome_id = old_learning_outcome_id;
ALTER TABLE questions DROP COLUMN old_learning_outcome_id;
