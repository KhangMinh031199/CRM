from bs4 import BeautifulSoup
import requests

URL_BASE = "https://www.tripadvisor.com/Hotel_Review-g562819-d289642-Reviews-Hotel_Caserio-Playa_del_Ingles_Maspalomas_Gran_Canaria_Canary_Islands.html"
MAX_PAGES = 30
counter = 0

for i in range(1, MAX_PAGES):
    url = ''
    if i > 1:
        url = "%spage/%d/" % (URL_BASE, i)
    else:
        url = URL_BASE

    req = requests.get(url)
    statusCode = req.status_code
    if statusCode == 200:

        html = BeautifulSoup(req.text, "html.parser")
        resultsoup = html.find_all('P', {'class': 'partial_entry'})
    else:
        break

for review in resultsoup:
    review_list = review.get_text()
    print(review_list)