-- India Data Jobs Analysis: SQL queries
-- Database: SQLite (data/processed/jobs.db)
-- Tables: jobs (one row per job), job_skills (one row per job-skill pair)

-- Q1. Top 10 cities by number of data jobs
SELECT city, COUNT(*) AS total_jobs
FROM jobs
WHERE city != 'India (unspecified)'
GROUP BY city
ORDER BY total_jobs DESC
LIMIT 10;

-- Q2. Average salary by role (in lakhs per year)
SELECT role,
       COUNT(salary_avg_lakh) AS jobs_with_salary,
       ROUND(AVG(salary_avg_lakh), 1) AS avg_salary_lakh
FROM jobs
WHERE role != 'Other'
GROUP BY role
ORDER BY avg_salary_lakh DESC;

-- Q3. Top 10 skills for Data Analyst jobs (JOIN)
SELECT s.skill, COUNT(*) AS jobs
FROM job_skills AS s
JOIN jobs AS j ON s.job_id = j.job_id
WHERE j.role = 'Data Analyst'
GROUP BY s.skill
ORDER BY jobs DESC
LIMIT 10;

-- Q4. Entry-level vs senior-level jobs by role (CASE WHEN)
SELECT role,
       COUNT(*) AS total_jobs,
       SUM(CASE WHEN seniority IN ('Intern', 'Junior') THEN 1 ELSE 0 END) AS entry_level,
       SUM(CASE WHEN seniority IN ('Senior', 'Lead / Principal') THEN 1 ELSE 0 END) AS senior_level
FROM jobs
WHERE role != 'Other'
GROUP BY role
ORDER BY senior_level DESC;

-- Q5. Average salary by city, only cities with 15+ salaried jobs (HAVING)
SELECT city,
       COUNT(salary_avg_lakh) AS jobs_with_salary,
       ROUND(AVG(salary_avg_lakh), 1) AS avg_salary_lakh
FROM jobs
WHERE city != 'India (unspecified)'
GROUP BY city
HAVING COUNT(salary_avg_lakh) >= 15
ORDER BY avg_salary_lakh DESC;