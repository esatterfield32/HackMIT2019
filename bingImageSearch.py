import requests
import matplotlib.pyplot as plt
from PIL import Image
from io import BytesIO

def findImage(queryWord):
    subscription_key = "79c7b41f532146e69b1ccd9e6f71e585"
    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
    search_term = queryWord

    headers = {"Ocp-Apim-Subscription-Key" : subscription_key}
    params  = {"q": search_term, "license": "public", "imageType": "photo"}

    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    pictureSource = search_results["value"][0]["contentUrl"]

    return pictureSource