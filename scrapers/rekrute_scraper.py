from scrapers.base_scraper import BaseScraper, JobOffer
from datetime import datetime

class RekruteScraper(BaseScraper):
    BASE_URL = "https://www.rekrute.com"

    def scrape(self, pages=3) -> list:
        offers = []
        for page in range(1, pages + 1):
            try:
                soup = self.get(self.BASE_URL.format(page=page))
                cards = soup.find_all("li", class_="post-id")
                for card in cards:
                    try:
                        title = card.find("a", class_="titreJob")
                        company = card.find("a", class_="nameEts")
                        loc = card.find("li", class_="location")
                        link = title["href"] if title else ""
                        offers.append(JobOffer(
                            title=title.get_text(strip=True) if title else "N/A",
                            company=company.get_text(strip=True) if company else "N/A",
                            location=loc.get_text(strip=True) if loc else "N/A",
                            description="",
                            source="rekrute",
                            url=link,
                            published_at=datetime.now().isoformat()
                        ))
                    except Exception as e:
                        print(f"[Rekrute] Erreur card: {e}")
            except Exception as e:
                print(f"[Rekrute] Erreur page {page}: {e}")
        print(f"[Rekrute] {len(offers)} offres collectées")
        return offers