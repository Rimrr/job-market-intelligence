from scrapers.base_scraper import BaseScraper, JobOffer
from datetime import datetime

class WuzzufScraper(BaseScraper):
    BASE_URL = "https://wuzzuf.net/search/jobs/?q=data+engineer&start={page}"

    def scrape(self, pages=3) -> list:
        offers = []
        for page in range(pages):
            try:
                soup = self.get(self.BASE_URL.format(page=page))
                cards = soup.find_all("div", class_="css-1gatmva")
                for card in cards:
                    try:
                        title_tag = card.find("h2", class_="css-m604qf")
                        company_tag = card.find("a", class_="css-17s97q8")
                        loc_tag = card.find("span", class_="css-5wys0k")
                        link_tag = title_tag.find("a") if title_tag else None

                        title = title_tag.get_text(strip=True) if title_tag else "N/A"
                        company = company_tag.get_text(strip=True) if company_tag else "N/A"
                        location = loc_tag.get_text(strip=True) if loc_tag else "N/A"
                        link = "https://wuzzuf.net" + link_tag["href"] if link_tag else ""

                        offers.append(JobOffer(
                            title=title,
                            company=company,
                            location=location,
                            description="",
                            source="wuzzuf",
                            url=link,
                            published_at=datetime.now().isoformat()
                        ))
                    except Exception as e:
                        print(f"[Wuzzuf] Erreur card: {e}")
            except Exception as e:
                print(f"[Wuzzuf] Erreur page {page}: {e}")
        print(f"[Wuzzuf] {len(offers)} offres collectées")
        return offers