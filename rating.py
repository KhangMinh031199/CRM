#! coding: utf-8
import requests
import settings
import api
import hashlib
import time
from bson.objectid import ObjectId


def facebook_rating_sync(page_id, access_token_page):
    url = settings.FACBOOK_GRAPH_API + '/{}/ratings?fields=created_time,recommendation_type,rating,review_text,{}&access_token={}'.format(
        page_id, "reviewer{picture,name}", access_token_page)
    result = requests.get(url=url)
    resp = result.json()
    for res in resp['data']:
        print(res)


#
# facebook_rating_sync('1929006573784334', 'EAAIr5W1gE2YBAEZAHmaxYquFFI1Wy6K4R88fzWQo7Mf2aDWZAUaLq1ddjZBTEmtJRaQH3MjtONEQXNx70yOYdZCcNERWwu7onidrDAq4R5hC1Peorvrf21Q9Ax14LJ98TppfR5s1I8XbPWaaAXx9QRO1ZAbQKBnRzpvzE00bMAAZDZD')


def init_survey(merchant, shop_id_select, top_domain):
    survey_1 = {
        'question': 'Bạn biết tới chúng tôi qua kênh nào?',
        'survey_type': 'multi_select',
        'answers': [
            {'id': 0, 'value': 'Mạng xã hội'},
            {'id': 1, 'value': 'Bạn bè'},
            {'id': 2, 'value': 'Nhân viên nhà hàng'},
            {'id': 3, 'value': 'Website nhà hàng'},
            {'id': 4, 'value': 'SMS'},
            {'id': 5, 'value': 'Khác'},
        ],
        'connect_button': 'Gửi khảo sát',
        'photo_name': None
    }

    survey_2 = {
        'question': 'Bạn có sẵn lòng giới thiệu chúng tôi tới bạn bè và đồng nghiệp?',
        'survey_type': 'one_select',
        'answers': [
            {'id': 0, 'value': 'Có'},
            {'id': 1, 'value': 'Không'},
        ],
        'connect_button': 'Gửi khảo sát',
        'photo_name': None
    }
    survey_3 = {
        'question': 'Bạn đánh giá thế nào về chất lượng phục vụ của chúng tôi?',
        'survey_type': 'rating',
        'min_point': '1',
        'max_point': '5',
        'connect_button': 'Gửi khảo sát',
        'photo_name': None
    }
    survey_4 = {
        'question': 'Bạn đánh giá thế nào về sản phẩm của chúng tôi?',
        'survey_type': 'rating',
        'min_point': '1',
        'max_point': '5',
        'connect_button': 'Gửi khảo sát',
        'photo_name': None
    }
    survey_5 = {
        'question': 'Bạn là khách du lịch hay địa phương?',
        'survey_type': 'one_select',
        'answers': [
            {'id': 0, 'value': 'Khách địa phương'},
            {'id': 1, 'value': 'Khách du lịch'},
        ],
        'connect_button': 'Gửi khảo sát',
        'photo_name': None
    }

    surveys = [survey_1, survey_2, survey_3, survey_4, survey_5]
    for sur in surveys:
        survey_type = sur.get('survey_type')
        question = sur.get('question')
        answers = sur.get('answers')
        min_point = sur.get('min_point')
        max_point = sur.get('max_point')
        photo_name = sur.get('photo_name')
        connect_button = sur.get('connect_button')
        survey_id= api.new_survey_splash_page(shop_id=shop_id_select, survey_type=survey_type,
                                   question=question, answers=answers, comment='',
                                   min_point=min_point, max_point=max_point, active=True,
                                   auto_popup='', photo_name=photo_name,
                                   connect_button=connect_button, connect_button_color='#f57a33', active_comment=True)
        survey_item = api.get_survey_item(survey_id)
        slug = survey_item.get('slug')
        unique_string = str(shop_id_select) + str(survey_id) + str(time.time())
        unique_id = slug + '_' + hashlib.md5(str(unique_string).encode('utf-8')).hexdigest()
        long_url = "https://survey." + top_domain + "/" + unique_id
        api.update_survey_splash_page(shop_id_select, survey_id, unique_id=unique_id)
        bitly_token = merchant.get('bitly_access_token', '')
        if bitly_token and len(bitly_token) > 0:
            try:
                api.update_bitly_url(shop_id_select, survey_id, bitly_token, long_url)
            except:
                pass


