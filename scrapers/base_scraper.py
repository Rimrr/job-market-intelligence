import requests
from bs4 import BeautifulSoup
import time, random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class JobOffer:
    title: str
    company: str
    location: str
    description: str
    source: str
    url: str
    published_at: str
    salary: Optional[str] = None
    skills: list = field(default_factory=list)
    scraped_at: str = field(default_factory=lambda: datetime.now().isoformat())

class BaseScraper:
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/120.0"
        ),
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
    }

    def get(self, url: str) -> BeautifulSoup:
        time.sleep(random.uniform(2, 4))
        resp = requests.get(url, headers=self.HEADERS, timeout=15)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")

    def scrape(self) -> list:
        raise NotImplementedError