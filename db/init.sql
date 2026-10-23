-- Runs once on first container start. The app also does this idempotently.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE DATABASE rag_test OWNER rag;
