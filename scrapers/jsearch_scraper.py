import requests
from scrapers.base_scraper import JobOffer
from datetime import datetime

class JSearchScraper:
    """
    Scraper via JSearch API (RapidAPI)
    Donne acces aux offres Indeed + LinkedIn sans blocage
    """
    URL = "https://jsearch.p.rapidapi.com/search"
    
    def __init__(self, api_key: str):
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }

    def scrape(self, query="data engineer", location="Morocco", pages=3) -> list:
        offers = []
        for page in range(1, pages + 1):
            try:
                params = {
                    "query": f"{query} in {location}",
                    "page": str(page),
                    "num_pages": "1",
                    "date_posted": "month"
                }
                resp = requests.get(
                    self.URL,
                    headers=self.headers,
                    params=params,
                    timeout=15
                )
                resp.raise_for_status()
                data = resp.json()

                for job in data.get("data", []):
                    # Extraction du salaire
                    sal_min = job.get("job_min_salary")
                    sal_max = job.get("job_max_salary")

                    offers.append(JobOffer(
                        title       = job.get("job_title", "N/A"),
                        company     = job.get("employer_name", "N/A"),
                        location    = job.get("job_city") or job.get("job_country", "N/A"),
                        salary      = f"{sal_min}-{sal_max}" if sal_min else None,
                        description = job.get("job_description", ""),
                        source      = job.get("job_publisher", "indeed").lower(),
                        url         = job.get("job_apply_link", ""),
                        published_at= job.get("job_posted_at_datetime_utc",
                                              datetime.now().isoformat())
                    ))
            except Exception as e:
                print(f"[JSearch] Erreur page {page}: {e}")

        print(f"[JSearch] {len(offers)} offres collectees (Indeed + LinkedIn)")
        return offers