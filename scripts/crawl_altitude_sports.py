#!/usr/bin/env python3
import json
import logging
import os

import bs4
import requests

from base import Spider

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


class AltitudeSportsProductPagesSpider(Spider):
    domain = "https://www.altitude-sports.com"

    def product_urls(self):
        searchspring_url = (
            "https://cdmr7g.a.searchspring.io/api/search/search.json?siteId="
            "cdmr7g&userId=YZW0IVC4-ZLJS-IWDZ-6R5B-L1TAINV2KL29&domain=https"
            "://www.altitude-sports.com/collections/all&referer=https://www."
            "altitude-sports.com&resultsFormat=native&method=search&format=j"
            "son&resultsPerPage=48&page=%s"
        )
        n = 1
        while True:
            response = self.get(searchspring_url % n)
            page = response.json()
            for item in page["results"]:
                url = item["url"]
                yield f"{self.domain}{url}", item
            if page["pagination"]["totalPages"] <= n:
                return
            n += 1

    def crawl(self):
        for url, item in self.product_urls():
            response = self.get(url)
            soup = bs4.BeautifulSoup(response.content, "html.parser")
            yield response, soup, item


class AltitudeSportsProduct:
    def __init__(
        self, response: requests.Response, soup: bs4.BeautifulSoup, data: dict
    ):
        self.response = response
        self.soup = soup
        self.data = data

    def json(self):

        tech_specs = {"features": []}
        description = self.soup.find("div", {"class": "description"})
        state = ""
        for child in description.children:
            if child.name == "strong":
                state = child.text
            if child.name == "h2":
                state = child.text
            if child.name == "table":
                table = child
                data = {}
                for tr in table.findAll("tr"):
                    tds = tr.findAll("td")
                    if len(tds) == 2:
                        key = tds[0].text
                        val = tds[1].text
                        data[key] = val
                tech_specs[state] = data

            if child.name == "ul":
                ul = child
                lis = [li.text for li in ul.findAll("li")]
                tech_specs[state] = lis

            if type(child) == bs4.element.NavigableString:
                if state == "Features":
                    tech_specs["features"].append(str(child).lstrip("• "))
                if state == "Details":
                    if ":" in child:
                        key, val = child.split(":", 1)
                        tech_specs[key] = val
        return {
            "manufacturer": self.data.get("manufacturer"),
            "name": self.data.get("name"),
            "price": self.data.get("price"),
            "category_hierarchy": self.data.get("category_hierarchy"),
            "sku": self.data.get("sku"),
            "uid": self.data.get("uid"),
            "review_score": self.data.get("yotpo_score_reviews"),
            "review_total": self.data.get("yotpo_total_reviews"),
            "url": self.response.request.url,
            "tech_specs": tech_specs,
            "img_urls": [self.data.get("imageUrl")],
        }

    def save(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        data = self.json()
        p = "../items/products/altitude_sports"
        filepath = f"{dir_path}/{p}/as_{data['sku']}.json"
        with open(filepath, "w") as f:
            f.write(json.dumps(data))


i = 0
for response, soup, item in AltitudeSportsProductPagesSpider().crawl():
    print(i, response.status_code, response.url)
    product = AltitudeSportsProduct(response, soup, item)
    product.save()
    i += 1
