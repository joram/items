#!/usr/bin/env python3
import json
import logging
import os

import bs4
import requests

from scripts.base import Spider

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class REIListPagesSpider(Spider):
    name = "rei-list-pages"
    domain = "https://www.rei.com"
    start_urls = ["https://www.rei.com/c/sleeping-bags-and-accessories"]
    # url_regex = r"\/c\/sleeping-bags-and-accessories.*"
    url_regex = r"\/c\/.*"
    strip_params = False


class REIProductPagesSpider(Spider):
    name = "rei-product-pages"
    domain = "https://www.rei.com"
    url_regex = r"\/product\/.*/.*"

    def product_urls(self):
        for response, soup in REIListPagesSpider().crawl():
            logger.info(f"{response.status_code}, {response.url}")
            next_urls = self.next_urls(soup)
            for url in next_urls:
                if self.visited_urls.get(url):
                    continue
                yield url
                self.visited_urls[url] = True

    def crawl(self):
        for url in self.product_urls():
            response = self.get(url)
            soup = bs4.BeautifulSoup(response.content, "html.parser")
            yield response, soup


class REIProduct:
    def __init__(self, response: requests.Response, soup: bs4.BeautifulSoup):
        self.response = response
        self.soup = soup

    def json(self):
        def _clean(s: str) -> str:
            return s.strip("\n ")

        try:
            script = self.soup.find(
                "script", {"data-client-store": "page-meta-data"}
            )  # qaignore: E501
            metadata = json.loads(script.text)
            script = self.soup.find(
                "script", {"data-client-store": "product-details"}
            )  # qaignore: E501
            details = json.loads(script.text)
        except Exception:
            metadata = {}
            details = {}
        tech_specs = {}
        for spec in details.get("specs", []):
            tech_specs[spec["name"]] = spec["values"]

        return {
            "name": metadata["pageName"].lstrip("rei:product details:"),
            "categories": metadata.get("CATEGORIES", "").split("|"),
            "product_code": self.response.request.url.split("/")[4],
            "tech_specs": tech_specs,
        }

    def save(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        data = self.json()
        p = "../src/products/rei"
        filepath = f"{dir_path}/{p}/{data['product_code']}.json"
        with open(filepath, "w") as f:
            f.write(json.dumps(data))


i = 0
for response, soup in REIProductPagesSpider().crawl():
    print(i, response.status_code, response.url)
    try:
        product = REIProduct(response, soup)
        product.save()
    except Exception:
        pass
    i += 1
