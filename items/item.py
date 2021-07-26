import json
import os
from typing import List, Optional

from quantulum3 import parser


class Item:
    name: str = ""
    categories = []
    description: str = ""
    product_code: str = ""
    tech_specs = {}
    img_urls = []

    def __init__(
        self,
        name: str = "",
        categories: List[str] = list,
        description: str = "",
        product_code: str = "",
        tech_specs=dict,
        img_urls: List[str] = list,
    ):
        self.name = name
        self.categories = categories
        self.description = description
        self.product_code = product_code
        self.tech_specs = tech_specs
        self.img_urls = img_urls

    def __str__(self):
        return f"<Item: {self.name}>"

    def json(self) -> dict:
        return {
            "name": self.name,
            "categories": self.categories,
            "description": self.description,
            "product_code": self.product_code,
            "tech_specs": self.tech_specs,
            "img_urls": self.img_urls,
        }

    @property
    def weight(self) -> Optional[float]:
        weight_strs = self.tech_specs.get("Weight", [])
        raw_weights = [parser.parse(s)[0] for s in weight_strs]
        weights_grams = []
        for w in raw_weights:
            if w.unit.name == "gram":
                weights_grams.append(w.value)
            if w.unit.name == "kilogram":
                weights_grams.append(w.value * 1000)
        if len(weights_grams) == 0:
            return None
        max_weight = max(weights_grams)
        return max_weight

    @classmethod
    def load_rei(cls, category=None) -> List["Item"]:
        file_dir = os.path.dirname(os.path.realpath(__file__))

        for filename in os.listdir(f"{file_dir}/products/rei"):
            with open(f"{file_dir}/products/rei/{filename}") as f:
                data = json.loads(f.read())
                product = Item(
                    name=data.get("name", ""),
                    categories=data.get("categories", ""),
                    product_code=data.get("sku", ""),
                    tech_specs=data.get("tech_specs", {}),
                    img_urls=data.get("img_urls", []),
                )
                if category and category not in product.categories:
                    continue
                yield product

    @classmethod
    def load_altitude_sports(cls, category=None) -> List["Item"]:
        file_dir = os.path.dirname(os.path.realpath(__file__))

        for filename in os.listdir(f"{file_dir}/products/altitude_sports"):
            with open(f"{file_dir}/products/altitude_sports/{filename}") as f:
                data = json.loads(f.read())
                categories = data.get("category_hierarchy", [])
                if categories is None:
                    categories = []
                product = Item(
                    name=data.get("name", ""),
                    categories=categories,
                    product_code=data.get("sku", ""),
                    tech_specs=data.get("tech_specs", {}),
                    img_urls=data.get("img_urls", []),
                )
                if category and category not in product.categories:
                    continue
                yield product

    @classmethod
    def load_mec(cls, category=None) -> List["Item"]:
        file_dir = os.path.dirname(os.path.realpath(__file__))
        for filename in os.listdir(f"{file_dir}/products/mec"):
            with open(f"{file_dir}/products/mec/{filename}") as f:
                data = json.loads(f.read())
                product = Item(
                    name=data.get("name", ""),
                    categories=data.get("categories", []),
                    description=data.get("description", ""),
                    product_code=data.get("product_code", ""),
                    tech_specs=data.get("tech_specs", {}),
                    img_urls=data.get("img_urls", []),
                )
                if category and category not in product.categories:
                    continue
                yield product
