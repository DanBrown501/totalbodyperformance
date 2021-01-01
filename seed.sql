-- in terminal:
-- psql < seed.sql
-- psql capstone

DROP DATABASE IF EXISTS  TotalBodyPerformance;

CREATE DATABASE TotalBodyPerformance;

\c TotalBodyPerformance

CREATE TABLE Users
(
  id SERIAL PRIMARY KEY,
  username VARCHAR,
  password VARCHAR,
  email VARCHAR,
  first_name VARCHAR,
  last_name VARCHAR,
  img_url VARCHAR
);

CREATE TABLE Exercise_Categories
(
  id SERIAL PRIMARY KEY,
  name VARCHAR
);

CREATE TABLE Exercises
(
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  description VARCHAR,
  category_id INTEGER REFERENCES Exercise_Categories
);


CREATE TABLE User_Exercises
(
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES Users,
  exercise_id INTEGER REFERENCES Exercises
);

CREATE TABLE Exercise_Comments
(
  id SERIAL PRIMARY KEY,
  content VARCHAR,
  user_id INTEGER REFERENCES Users,
  exercise_id INTEGER REFERENCES Exercises
);


