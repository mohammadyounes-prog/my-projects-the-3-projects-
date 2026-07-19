-- 007_add_question_property_types.sql
INSERT INTO property_types (name, api_name, audience_type) VALUES
('Difficulty Level', 'difficulty_levels', 'question'),
('Cognitive Level', 'cognitive_levels', 'question'),
('Learning Outcome', 'learning_outcomes', 'question'),
('Question Type', 'question_types', 'question');
