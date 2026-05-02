-- Supabase SQL Migration for Predictions Table
-- Run this in the Supabase SQL Editor

-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
  id bigserial PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  prediction text NOT NULL,
  confidence float8 NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
  probabilities jsonb NOT NULL DEFAULT '{}'::jsonb,
  image_url text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_user_created ON predictions(user_id, created_at DESC);

-- Enable Row-Level Security
ALTER TABLE predictions ENABLE ROW LEVEL SECURITY;

-- Create RLS policy: Users can only see their own predictions
CREATE POLICY "Users can read own predictions" ON predictions
  FOR SELECT USING (auth.uid() = user_id);

-- Create RLS policy: Users can only insert their own predictions
CREATE POLICY "Users can insert own predictions" ON predictions
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Create RLS policy: Users can update their own predictions
CREATE POLICY "Users can update own predictions" ON predictions
  FOR UPDATE USING (auth.uid() = user_id);

-- Create RLS policy: Users can delete their own predictions
CREATE POLICY "Users can delete own predictions" ON predictions
  FOR DELETE USING (auth.uid() = user_id);
