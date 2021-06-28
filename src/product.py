import json
import os
from typing import List, Dict


class Product:
    name:str=""
    categories=[]
    description:str=""
    product_code:str=""
    tech_specs={}
    img_urls=[]

    def __init__(
        self,
        name:str="",
        categories:List[str]=list,
        description:str="",
        product_code:str="",
        tech_specs=dict,
        img_urls:List[str]=list,
    ):
        self.name = name
        self.categories = categories
        self.description = description
        self.product_code = product_code
        self.tech_specs = tech_specs
        self.img_urls = img_urls

    def __str__(self):
        return f"<Product: {self.name}>"

    def json(self) -> dict:
        return {
            "name": self.name,
            "categories": self.categories,
            "description": self.description,
            "product_code": self.product_code,
            "tech_specs": self.tech_specs,
            "img_urls": self.img_urls,
        }

    @classmethod
    def load_all(cls) -> List["Product"]:
        file_dir = os.path.dirname(os.path.realpath(__file__))
        for filename in os.listdir(f"{file_dir}/products"):
            with open(f"{file_dir}/products/{filename}") as f:
                data = json.loads(f.read())
                yield Product(
                    name=data.get("name", ""),
                    categories=data.get("categories", []),
                    description=data.get("description", ""),
                    product_code=data.get("product_code", ""),
                    tech_specs=data.get("tech_specs", {}),
                    img_urls=data.get("img_urls", []),
                )
