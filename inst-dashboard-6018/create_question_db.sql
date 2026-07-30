-- Table for Difficulty Levels
CREATE TABLE difficulty_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE -- e.g., 'Easy', 'Medium', 'Hard', 'Expert'
);

-- Table for Cognitive Levels (formerly Bloom's Taxonomy)
CREATE TABLE cognitive_levels (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE -- e.g., 'Remembering', 'Understanding', 'Applying', 'Analyzing', 'Evaluating', 'Creating'
);

-- Table for Learning Outcomes
CREATE TABLE learning_outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE -- e.g., 'Identify basic facts', 'Describe biological processes'
);

-- Main Questions Table
CREATE TABLE questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique identifier for each question
    author_creator VARCHAR(100),                  -- Name of the question author/creator
    date_created DATE NOT NULL,                   -- Date when the question was created
    question_text TEXT NOT NULL,                  -- The main text of the question
    choice_1 TEXT,                                -- Text for choice 1
    choice_2 TEXT,                                -- Text for choice 2
    choice_3 TEXT,                                -- Text for choice 3
    choice_4 TEXT,                                -- Text for choice 4
    correct_option TEXT NOT NULL,                 -- The text of the correct choice (e.g., 'Paris' or 'x = 5')
    difficulty_level_id INTEGER NOT NULL,         -- Foreign key to difficulty_levels table
    cognitive_level_id INTEGER NOT NULL,          -- Foreign key to cognitive_levels table
    learning_outcome_id INTEGER NOT NULL,         -- Foreign key to learning_outcomes table
    mark INTEGER NOT NULL,                        -- Marks assigned to the question
    time_seconds INTEGER NOT NULL,                -- Recommended time to answer in seconds
    discriminating_factor REAL,                   -- New column for Discriminating Factor (using REAL for floating-point numbers)

    FOREIGN KEY (difficulty_level_id) REFERENCES difficulty_levels(id),
    FOREIGN KEY (cognitive_level_id) REFERENCES cognitive_levels(id),
    FOREIGN KEY (learning_outcome_id) REFERENCES learning_outcomes(id)
);

-- Optional: Index for faster lookups on common filter fields
CREATE INDEX idx_questions_difficulty ON questions (difficulty_level_id);
CREATE INDEX idx_questions_cognitive ON questions (cognitive_level_id);
CREATE INDEX idx_questions_learning_outcome ON questions (learning_outcome_id);
CREATE INDEX idx_questions_author ON questions (author_creator);
CREATE INDEX idx_questions_date_created ON questions (date_created);
