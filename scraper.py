import requests
import re
from bs4 import BeautifulSoup
import json

url = "https://hotpoint.co.ke/catalogue/category/tvs/"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/153.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)

source = response.text

pattern = r'\\"@type\\":\\"ListItem\\",\\"position\\":(\d+),\\"name\\":\\"(.*?)\\",\\"url\\":\\"(.*?)\\"'

products = re.findall(pattern, source)

products = [p for p in products if "Home" not in p[1]]

print("Products found:", len(products))

scraped_products = []

for position, name, product_url in products:

    try:
        product_response = requests.get(
            product_url,
            headers=headers
        )

        product_soup = BeautifulSoup(
            product_response.text,
            "html.parser"
        )

        scripts = product_soup.find_all(
            "script",
            type="application/ld+json"
        )

        for script in scripts:

            try:
                data = json.loads(script.string)

                if isinstance(data, list):

                    for item in data:

                        if (
                            isinstance(item, dict)
                            and item.get("@type") == "Product"
                        ):

                            offers = item.get("offers", {})

                            scraped_products.append({
                                "name": item.get("name"),
                                "price": offers.get("price"),
                                "currency": offers.get("priceCurrency"),
                                "availability": offers.get("availability"),
                                "url": product_url
                            })

                            break

            except (json.JSONDecodeError, TypeError):
                continue

        print("Scraped:", position, "-", name)

    except requests.RequestException as e:
        print("Failed:", position, "-", e)

print("\nTotal products scraped:", len(scraped_products))

for product in scraped_products:
    print(product)
    import pandas as pd

df = pd.DataFrame(scraped_products)

df["price"] = pd.to_numeric(df["price"])

df["availability"] = df["availability"].str.replace(
    "https://schema.org/", "", regex=False
)

df.to_csv("hotpoint_products.csv", index=False)

df.to_excel("hotpoint_products.xlsx", index=False)

print("\nFiles created successfully.")
print(df.head())