#!/usr/bin/env python3
import json
import logging
import os
import re
from typing import List

import requests
import requests_cache
from requests_cache import CachedSession
import bs4

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class Spider:
    name = "base scraper"
    cache_dir = "../data"
    start_urls = []
    to_visit_urls = []
    visited_urls = {}
    use_cache = True
    session = None
    url_regex = ""
    domain = ""
    strip_params = True

    def __init__(self):
        self.to_visit_urls = self.start_urls
        dir_path = os.path.dirname(os.path.realpath(__file__))
        requests_cache.install_cache(backend="filesystem", cache_name=f"{dir_path}/cache/")
        self.session = CachedSession()

    def crawl(self):
        while len(self.to_visit_urls) > 0:
            url = self.to_visit_urls.pop()
            if self.visited_urls.get(url, False):
                logger.debug(f"skilling url, already visited: {url}")
                continue
            response = self.get(url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            next_urls = self.next_urls(soup)
            logger.debug(f"adding {len(next_urls)} urls to visit")
            self.to_visit_urls += next_urls
            yield response, soup
            self.visited_urls[url] = True

    def get(self, url: str) -> requests.Response:
        response = self.session.get(url)
        return response

    def next_urls(self, soup: bs4.BeautifulSoup) -> List[str]:
        anchors = soup.findAll('a', href=re.compile(self.url_regex))
        urls = []
        for a in anchors:
            href = a["href"]
            if not href.startswith(self.domain):
                href = f"{self.domain}{href}"
                if self.strip_params and "?" in href:
                    href = href.split("?")[0]
                urls.append(href)
        return urls


class MECListPagesSpider(Spider):
    name = "mec-list-pages"
    domain = "https://www.mec.ca"
    start_urls = ['https://www.mec.ca/en/products/c/100']
    url_regex = r'\/en\/products\/c\/100\?page\=[0-9]*'
    strip_params = False


class MECProductPagesSpider(Spider):
    name = "mec-product-pages"
    domain = "https://www.mec.ca"
    url_regex = r'\/en\/product\/.*'

    def product_urls(self):
        for response, soup in MECListPagesSpider().crawl():
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
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            yield response, soup


class MECProduct:
    def __init__(self, response: requests.Response, soup: bs4.BeautifulSoup):
        self.response = response
        self.soup = soup

    def json(self):
        def _clean(s: str) -> str:
            return s.strip("\n ")

        tech_specs = {}
        try:
            tech_specs_table = self.soup.find("div", {"id": "pdp-tech-specs"}).find("table").find("tbody")
            for tr in tech_specs_table.findChildren("tr"):
                key = _clean(tr.find("th").text)
                td = tr.find("td")
                if len(td.findAll("ul")) > 0:
                    ul = td.find("ul")
                    values = [_clean(li.text) for li in ul.findAll("li")]
                else:
                    values = [_clean(td.text)]
                tech_specs[key] = values
        except:
            pass

        divs = self.soup.findAll("div", {"class": "carousel__media"})
        img_urls = []
        for div in divs:
            try:
                img_url = div.find("img")["data-high-res-src"]
            except:
                continue
            img_urls.append(img_url)

        categories = []
        for li in self.soup.findAll("li", {"class": "breadcrumbs__item"}):
            categories.append(_clean(li.text))
        return {
            "name": _clean(self.soup.find("h1", {"class": "product__name"}).text),
            "categories": categories,
            # "price": _clean(self.soup.find("div", {"class": "product-price"}).text),
            "description": _clean(self.soup.find("div", {"id": "pdp-description"}).text),
            "product_code": self.response.url.split("/")[5],
            "tech_specs": tech_specs,
            "img_urls": img_urls,
        }

    def save(self):
        # import pprint
        # pprint.pprint(self.json())
        dir_path = os.path.dirname(os.path.realpath(__file__))
        data = self.json()
        filepath = f"{dir_path}/../src/products/{data['product_code']}.json"
        with open(filepath, "w") as f:
            f.write(json.dumps(data))


i = 0
for response, soup in MECProductPagesSpider().crawl():
    print(i, response.status_code, response.url)
    product = MECProduct(response, soup)
    product.save()
    i += 1
