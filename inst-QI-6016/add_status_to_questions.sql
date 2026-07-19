-- Add status column to the questions table
ALTER TABLE questions
ADD COLUMN status TEXT DEFAULT 'pending';
