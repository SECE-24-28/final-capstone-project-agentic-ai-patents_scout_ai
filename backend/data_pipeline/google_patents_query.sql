-- Google Patents BigQuery Consolidated Query for 12,000 Patents (1,000 per domain)
-- Run this query in Google BigQuery Console and export the results to data/raw_patents/raw_patents.csv

-- 1. Artificial Intelligence
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Artificial Intelligence' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'G06N') OR STARTS_WITH(c.code, 'G06V'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 2. Healthcare
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Healthcare' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'G16H') OR STARTS_WITH(c.code, 'A61B') OR STARTS_WITH(c.code, 'A61M'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 3. Biotechnology
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Biotechnology' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'C12N') OR STARTS_WITH(c.code, 'C12Q') OR STARTS_WITH(c.code, 'G16B'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 4. Agriculture
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Agriculture' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'A01B') OR STARTS_WITH(c.code, 'A01C') OR STARTS_WITH(c.code, 'A01G'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 5. Renewable Energy
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Renewable Energy' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'H02S') OR STARTS_WITH(c.code, 'F03D') OR STARTS_WITH(c.code, 'Y02E'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 6. Cybersecurity
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Cybersecurity' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'H04L63') OR STARTS_WITH(c.code, 'H04L9'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 7. Robotics
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Robotics' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'B25J') OR STARTS_WITH(c.code, 'G05D1'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 8. Internet of Things (IoT)
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Internet of Things (IoT)' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'G16Y') OR STARTS_WITH(c.code, 'H04W'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 9. Smart Cities
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Smart Cities' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'G08G') OR STARTS_WITH(c.code, 'Y02A30') OR STARTS_WITH(c.code, 'G06Q50/30'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 10. Education Technology
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Education Technology' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'G09B'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 11. FinTech
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'FinTech' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'G06Q20') OR STARTS_WITH(c.code, 'G06Q40'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
)

UNION ALL

-- 12. Sustainability
(
  SELECT 
    p.publication_number AS patent_number,
    (SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1) AS title,
    (SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1) AS abstract,
    COALESCE((SELECT assignee.name FROM UNNEST(p.assignee_harmonized) AS assignee LIMIT 1), 'Unknown Assignee') AS assignee,
    CAST(DIV(p.publication_date, 10000) AS INT64) AS year,
    'Sustainability' AS domain
  FROM `patents-public-data.patents.publications` AS p
  WHERE p.country_code = 'US'
    AND EXISTS (SELECT 1 FROM UNNEST(p.cpc) AS c WHERE STARTS_WITH(c.code, 'Y02W') OR STARTS_WITH(c.code, 'C02F') OR STARTS_WITH(c.code, 'C08L'))
    AND EXISTS (SELECT 1 FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en')
    AND EXISTS (SELECT 1 FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en')
    AND LENGTH((SELECT title.text FROM UNNEST(p.title_localized) AS title WHERE title.language = 'en' LIMIT 1)) >= 10
    AND LENGTH((SELECT abs.text FROM UNNEST(p.abstract_localized) AS abs WHERE abs.language = 'en' LIMIT 1)) >= 50
    AND p.publication_date >= 20180101
  LIMIT 1000
);
