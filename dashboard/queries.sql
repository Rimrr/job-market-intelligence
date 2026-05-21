-- Ces requêtes sont à coller dans Metabase ou Grafana

-- Dashboard 1 : Top 10 compétences demandées
SELECT skill, count FROM gold_top_skills LIMIT 10;

-- Dashboard 2 : Offres par ville (Top 15)
SELECT location, count FROM gold_offers_by_city LIMIT 15;

-- Dashboard 3 : Répartition par source
SELECT source, count FROM gold_offers_by_source;

-- Dashboard 4 : Salaires médians par ville
SELECT location, ROUND(median_salary) AS median_salary, offers_count
FROM gold_salary_by_city
WHERE offers_count > 5
LIMIT 15;

-- Dashboard 5 : Évolution des offres dans le temps
SELECT day, SUM(count) AS total_offers
FROM gold_offers_over_time
GROUP BY day
ORDER BY day;