from typing import List, Dict


class Product:
    name:str=""
    categories:List[str]=[]
    description:str=""
    product_code:str=""
    tech_specs:Dict[str:List[str]]={}
    img_urls:List[str]

    @classmethod
    def list_by_category_path(cls, path) -> List["Product"]:
        products = [Product()]
        return products

    @classmethod
    def list_by_name_search(cls, name) -> List["Product"]:
        products = [Product()]
        return products
