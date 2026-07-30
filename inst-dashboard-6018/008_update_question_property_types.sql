-- 008_update_question_property_types.sql

-- Update existing property types from 'general' to 'question'
UPDATE property_types
SET audience_type = 'question'
WHERE api_name IN ('difficulty_levels', 'cognitive_levels', 'learning_outcomes')
  AND audience_type = 'general';

-- Insert 'question_types' as a new property type for 'question' audience
INSERT INTO property_types (name, api_name, audience_type) VALUES
('Question Type', 'question_types', 'question');
