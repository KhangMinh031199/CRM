import bitly_api


# access_token = '46f433d63f43bc0254490887d27b993b0c8653d2'
def shorten_url_bitly(access_token, longurl):
    b = bitly_api.Connection(access_token=access_token)
    print(longurl)
    short_url = b.shorten(longurl)
    return short_url
