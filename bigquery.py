from google.cloud import bigquery

client = bigquery.Client()

# Perform a query.
QUERY = (
	'SELECT * FROM bigquery-public-data.covid19_open_data.compatibility_view AS COVID19 '
    'WHERE COVID19.country_region = "Cuba" AND COVID19.province_state LIKE "%Havana%" AND COVID19.confirmed IS NOT NULL LIMIT 1 '
    'LIMIT 1')
query_job = client.query(QUERY)  # API request
rows = query_job.result()  # Waits for query to finish

for row in rows:
    print(row.name)