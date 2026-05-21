from scrapers.base_scraper import BaseScraper, JobOffer
from datetime import datetime

class IndeedScraper(BaseScraper):
    BASE_URL = (
        "https://fr.indeed.com/jobs"
        "?q={keyword}&l={location}&start={start}"
    )

    def __init__(self, keyword="data engineer", location="France"):
        self.keyword = keyword
        self.location = location

    def scrape(self, pages=3) -> list:
        offers = []
        for page in range(pages):
            url = self.BASE_URL.format(
                keyword=self.keyword.replace(" ", "+"),
                location=self.location,
                start=page * 10
            )
            try:
                soup = self.get(url)
                cards = soup.find_all("div", class_="job_seen_beacon")
                for card in cards:
                    try:
                        title = card.find(
                            "h2", class_="jobTitle"
                        ).get_text(strip=True)
                        company = card.find(
                            "span", {"data-testid": "company-name"}
                        ).get_text(strip=True)
                        loc = card.find(
                            "div", {"data-testid": "text-location"}
                        ).get_text(strip=True)
                        salary_tag = card.find(
                            "div", {"data-testid": "attribute_snippet_testid"}
                        )
                        salary = (
                            salary_tag.get_text(strip=True)
                            if salary_tag else None
                        )
                        link_tag = card.find("a", class_="jcs-JobTitle")
                        link = (
                            "https://fr.indeed.com" + link_tag["href"]
                            if link_tag else ""
                        )
                        offers.append(JobOffer(
                            title=title,
                            company=company,
                            location=loc,
                            salary=salary,
                            description="",
                            source="indeed",
                            url=link,
                            published_at=datetime.now().isoformat()
                        ))
                    except Exception as e:
                        print(f"[Indeed] Erreur card: {e}")
            except Exception as e:
                print(f"[Indeed] Erreur page {page}: {e}")
        print(f"[Indeed] {len(offers)} offres collectées")
        return offers