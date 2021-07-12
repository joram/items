import src

for product in src.Product.load_rei():
    weight = product.tech_specs.get("Weight", [""])[0]
    fill = product.tech_specs.get("Fill", [""])[0]
    print(",".join([product.name, weight, fill]))
