DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS trainers CASCADE;
DROP TABLE IF EXISTS athletes CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
DROP TABLE IF EXISTS additionalInfo CASCADE;
DROP TABLE IF EXISTS plans CASCADE;
DROP TABLE IF EXISTS competitionsAthleteLinks CASCADE;
DROP TABLE IF EXISTS competitions CASCADE;
DROP TYPE IF EXISTS user_role_enum ;
CREATE TYPE user_role_enum AS ENUM ('Админ', 'Тренер', 'Спортсмен');


CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR NOT NULL,
    last_name VARCHAR NOT NULL,
    phone_number VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    role user_role_enum,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE trainers (
    id SERIAL PRIMARY KEY,
    userId INT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE  athletes(
    id SERIAL PRIMARY KEY,
    userId INT NOT NULL,
    trainerId INT,
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (userId) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (trainerId) REFERENCES trainers(id) ON DELETE CASCADE
);

CREATE TABLE plans (
    id SERIAL PRIMARY KEY,
    athleteId INT NOT NULL,
    data text,
    created_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (athleteId) REFERENCES athletes(id)
);

CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    trainerId INT NOT NULL,
    data text,
    planId INT,
    created_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (trainerId) REFERENCES trainers(id),
    FOREIGN KEY (planId) REFERENCES plans(id)
);

CREATE TABLE additionalInfo (
    id SERIAL PRIMARY KEY,
    athleteId INT NOT NULL,
    age INTEGER,
    weight INTEGER,
    height INTEGER,
    created_at TIMESTAMP DEFAULT now(),
    FOREIGN KEY (athleteId) REFERENCES athletes(id)
);

CREATE TABLE competitions (
    id SERIAL PRIMARY KEY,
    title VARCHAR,
    data VARCHAR
);

CREATE TABLE competitionsAthleteLinks (
    competitionId INT,
    athleteId INT,
    PRIMARY KEY (competitionId, athleteId),
    FOREIGN KEY (competitionId) REFERENCES competitions(id),
    FOREIGN KEY (athleteId) REFERENCES athletes(id)
);

CREATE OR REPLACE FUNCTION insert_user_role_handler()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.role = 'Спортсмен' THEN
        INSERT INTO athletes (userId) VALUES (NEW.id);
    ELSIF NEW.role = 'Тренер' THEN
        INSERT INTO trainers (userId) VALUES (NEW.id);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_insert_user
AFTER INSERT ON users
FOR EACH ROW
EXECUTE FUNCTION insert_user_role_handler();

CREATE OR REPLACE FUNCTION insert_additional_info_handler()
RETURNS TRIGGER AS $$
BEGIN

    INSERT INTO additionalInfo (athleteId, age, weight, height)
    VALUES (NEW.id, 0, 0, 0);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER after_insert_athlete
AFTER INSERT ON athletes
FOR EACH ROW
EXECUTE FUNCTION insert_additional_info_handler();