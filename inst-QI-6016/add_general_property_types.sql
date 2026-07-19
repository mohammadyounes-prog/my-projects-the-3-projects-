-- add_general_property_types.sql
INSERT INTO property_types (name, api_name, audience_type) VALUES
('Difficulty Level', 'difficulty_levels', 'general'),
('Cognitive Level', 'cognitive_levels', 'general'),
('Learning Outcome', 'learning_outcomes', 'general'),
('Question Type', 'question_types', 'general');
