-- ============================================
-- DATA WAREHOUSE — Job Market Intelligence
-- ============================================

-- Table de faits : offres d'emploi
CREATE TABLE IF NOT EXISTS fact_job_offers (
    id           SERIAL PRIMARY KEY,
    title        TEXT NOT NULL,
    company      TEXT,
    location     TEXT,
    salary_min   INTEGER,
    salary_max   INTEGER,
    language     VARCHAR(10),
    source       TEXT NOT NULL,
    url          TEXT UNIQUE NOT NULL,
    published_at TIMESTAMP,
    scraped_at   TIMESTAMP DEFAULT NOW()
);

-- Dimension : compétences
CREATE TABLE IF NOT EXISTS dim_skills (
    id   SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Liaison offres <-> compétences
CREATE TABLE IF NOT EXISTS offer_skills (
    offer_id INTEGER REFERENCES fact_job_offers(id) ON DELETE CASCADE,
    skill_id INTEGER REFERENCES dim_skills(id) ON DELETE CASCADE,
    PRIMARY KEY (offer_id, skill_id)
);

-- ============================================
-- VUES GOLD (analytiques)
-- ============================================

-- Top compétences
CREATE OR REPLACE VIEW gold_top_skills AS
SELECT s.name AS skill, COUNT(*) AS count
FROM offer_skills os
JOIN dim_skills s ON os.skill_id = s.id
GROUP BY s.name
ORDER BY count DESC;

-- Offres par ville
CREATE OR REPLACE VIEW gold_offers_by_city AS
SELECT location, COUNT(*) AS count
FROM fact_job_offers
GROUP BY location
ORDER BY count DESC;

-- Salaires médians par ville
CREATE OR REPLACE VIEW gold_salary_by_city AS
SELECT
    location,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY salary_min
    ) AS median_salary,
    COUNT(*) AS offers_count
FROM fact_job_offers
WHERE salary_min IS NOT NULL
GROUP BY location
ORDER BY median_salary DESC;

-- Offres par source
CREATE OR REPLACE VIEW gold_offers_by_source AS
SELECT source, COUNT(*) AS count
FROM fact_job_offers
GROUP BY source;

-- Évolution temporelle
CREATE OR REPLACE VIEW gold_offers_over_time AS
SELECT
    DATE(published_at) AS day,
    source,
    COUNT(*) AS count
FROM fact_job_offers
GROUP BY day, source
ORDER BY day;