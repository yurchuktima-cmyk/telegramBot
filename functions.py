import requests
headers = {
    "User-Agent": "Mozilla/5.0"
}
def save_image(url):
    immeg = requests.get(url, timeout=15, headers=headers)
    immeg.raise_for_status()
    with open("file.jpg", "wb") as file:
        file.write(immeg.content)
    return "file.jpg"
