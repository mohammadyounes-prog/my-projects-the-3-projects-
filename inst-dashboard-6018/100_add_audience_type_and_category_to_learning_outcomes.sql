-- 100_add_audience_type_and_category_to_learning_outcomes.sql
ALTER TABLE learning_outcomes ADD COLUMN audience_type TEXT;
ALTER TABLE learning_outcomes ADD COLUMN category TEXT;
ALTER TABLE learning_outcomes ADD COLUMN category_ar TEXT;
