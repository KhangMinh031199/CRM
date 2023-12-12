import settings
import requests

page_id = "1929006573784334"
page_token = "EAAIr5W1gE2YBAGokaQQFDw2ls2B16oFtyqRjcP1HgcxBeFHXQXpythg8H4QKwkeSFy8fYxxaISbBklTo1s4ngOeZBCqPr4ZB8Rh0YiOOUPZAGseLUzmZCWLvc8ihOPSllTUVAHrPlg3Bmw1C8eAkoxZBR4POaKyF81MtDfyJJwQZDZD"

facebook_page_conversion_url = '/%s/conversations?fields=senders&access_token=%s' % (page_id, page_token)

r = requests.get(settings.FACBOOK_GRAPH_API + facebook_page_conversion_url)
print r.json()