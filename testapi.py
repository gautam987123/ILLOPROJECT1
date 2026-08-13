import requests

url = "http://127.0.0.1:5000/predict"

data = {
    "location": "JP Nagar",
    "area_type": "Plot Area",
    "bhk": 2,
    "sqft": 1200,
    "bath": 2,
    "balcony": 1,
    "years": 10,
    "listed_price": 80
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Response:")
print(response.json())