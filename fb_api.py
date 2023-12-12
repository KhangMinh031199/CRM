import time
import arrow
from bson.objectid import ObjectId
import api
import json
from datetime import datetime
import requests
import settings
from mongo_connect import *
import hashlib
import base64
import storage_api
import dateutil.parser

MONGODB = mongodb_create()
DATABASE = MONGODB[settings.MONGODB_NAME]
fb_ads_accounts = DATABASE['fb_ads_accounts']
fb_users = DATABASE['fb_users']
fb_ads = DATABASE['fb_ads']

user_id = '2224333911121725'
access_token = 'EAAIr5W1gE2YBAB5nrpqMLpbvR2Iko0Nm2ZCOMt0WQHA8mM7vBpVIILgrfkQZBk0cEBQZBy1CZCs5uji5w6IzWpCZBtR5dSbj7EDetzeB41wBluO5cnA3XZCuUzlToKnhIjonyFCYRo3An9XLkdZAsebEtwdYs33uYj1OO9Oa3tQNQZDZD'
APP_ID = 611214335939430
APP_SECRET = 'ae4f0c5a72fd43da8ed2de7bcd8e9255'


# facebook_sources
def get_facebook_sources(merchant_id, user_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    return DATABASE.facebook_setting.find_one({'merchant_id': ObjectId(merchant_id), 'fb_user_id': user_id})


def create_facebook_sources(merchant_id, user_id, access_token, long_access_token):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    data = {
        'fb_user_id': user_id,
        'merchant_id': ObjectId(merchant_id),
        'status_login': True,
        'access_token': access_token,
        'long_access_token': long_access_token
    }
    DATABASE.facebook_setting.update_many({'fb_user_id': user_id}, {'$set': {'status_login': False}})
    DATABASE.facebook_setting.insert(data)


def update_facebook_sources(merchant_id, user_id, access_token, long_access_token):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    DATABASE.facebook_setting.update_many({'fb_user_id': user_id}, {'$set': {'status_login': False}})
    DATABASE.facebook_setting.update_one({'merchant_id': merchant_id, 'fb_user_id': user_id},
                                         {'$set': {
                                             'access_token': access_token,
                                             'long_access_token': long_access_token,
                                             'status_login': True
                                         }})


# access_token
def fb_long_lived_user_access_token(app_id, app_secret, user_access_token):
    url = 'https://graph.facebook.com/v5.0/oauth/access_token?grant_type=fb_exchange_token' \
          '&client_id={}&client_secret={}&fb_exchange_token={}'.format(app_id, app_secret, user_access_token)
    result = requests.get(url=url)
    if result.status_code != 200:
        return False
    else:
        access_token = json.loads(result.text).get('access_token')  # type: object
        return access_token


# facebook_users
def get_user_info_by_user_id(user_id):
    return DATABASE.fb_users.find_one({'fb_user_id': user_id})


def create_fb_user_db(user_info):
    return DATABASE.fb_users.insert(user_info)


def update_fb_user_db(user_id, user_info):
    return DATABASE.fb_users.update_one({'fb_user_id': user_id}, {'$set': user_info})


# facebook_ads
def get_ads_info_by_id(ads_id):
    return DATABASE.fb_ads.find_one({'ads_id': ads_id})


def create_fb_ads_db(ads_info):
    return DATABASE.fb_ads.insert(ads_info)


def update_fb_ads_db(ads_id, ads_info, plus=None):
    if not plus:
        return DATABASE.fb_ads.update_one({'ads_id': ads_id}, {'$set': ads_info})
    else:
        impressions_age = ads_info.get('impressions').get('age')
        impressions_gender = ads_info.get('impressions').get('gender')
        clicks_age = ads_info.get('clicks').get('age')
        clicks_gender = ads_info.get('clicks').get('gender')
        post_engagement_age = ads_info.get('post_engagement').get('age')
        post_engagement_gender = ads_info.get('post_engagement').get('gender')
        return DATABASE.fb_ads.update_one({
            'ads_id': ads_id
        }, {'$set': {
            'impressions.age': impressions_age,
            'impressions.gender': impressions_gender,
            'clicks.age': clicks_age,
            'clicks.gender': clicks_gender,
            'post_engagement.age': post_engagement_age,
            'post_engagement.gender': post_engagement_gender,
        }})


def percent_of_goal(donation, goal):
    return int(round(float(donation) / float(goal) * 100)) if goal != 0 else 0


def ads_detail(user_id, ads_account_id, ads_data):
    """
        create or update ads detail, impressions, clicks, post_engagement, ctr, frequency by device and platform
    """
    ads_detail = {'fb_user_id': user_id, 'fb_ads_account_id': ads_account_id}
    ads_id = ads_data.get('id')
    ads_detail['ads_id'] = ads_id
    ads_detail['campaign_id'] = ads_data.get('campaign_id')
    ads_detail['adset_id'] = ads_data.get('adset_id')
    ads_created_time = ads_data.get('created_time')
    if ads_created_time:
        ads_detail['created_time'] = ads_created_time
        try:
            ads_created_time_ts = time.mktime(dateutil.parser.parse(ads_created_time).timetuple())
            ads_detail['created_time_ts'] = ads_created_time_ts
        except:
            ads_detail['created_time_ts'] = None
    else:
        ads_detail['created_time'] = None
        ads_detail['created_time_ts'] = None
    ads_detail['name'] = ads_data.get('name')
    ads_detail['status'] = ads_data.get('status')
    ads_updated_time = ads_data.get('updated_time')
    if ads_updated_time:
        ads_detail['updated_time'] = ads_updated_time
        try:
            ads_updated_time_ts = time.mktime(dateutil.parser.parse(ads_updated_time).timetuple())
            ads_detail['updated_time_ts'] = ads_updated_time_ts
        except:
            ads_detail['updated_time_ts'] = None
    else:
        ads_detail['updated_time'] = None
        ads_detail['updated_time_ts'] = None
    # creative
    creative = ads_data.get('creative')
    if creative:
        creative_id = creative.get('id')
        ads_detail['creative'] = {}
        ads_detail['creative']['id'] = creative_id
        ads_detail['creative']['body'] = creative.get('body')
        ads_detail['creative']['name'] = creative.get('name')
        ads_detail['creative']['title'] = creative.get('title')
        try:
            creative_thumbnail_url = creative.get('thumbnail_url')
            creative_picture_reading = requests.get(url=creative_thumbnail_url)
            creative_thumbnail = creative_picture_reading.content
            creative_picture_origin_name = 'creative_thumbnail_{}.jpg'.format(creative_id)
            creative_picture_name = \
                hashlib.md5(creative_thumbnail).hexdigest() + '.' + \
                creative_picture_origin_name.rsplit('.', 1)[1]
            creative_picture_data = {
                'file_name': creative_picture_name,
                'file_data': base64.b64encode(creative_thumbnail),
                'origin_name': creative_picture_origin_name
            }
            storage_api.save_file(creative_picture_data)
            ads_detail['creative']['thumbnail'] = creative_picture_name
        except:
            ads_detail['creative']['thumbnail'] = None
        creative_object_story_id = creative.get('object_story_id')
        if creative_object_story_id:
            page_post = creative_object_story_id.split('_')
            permalink_url = 'https://www.facebook.com/{}/posts/{}'.format(page_post[0],
                                                                          page_post[1])
            ads_detail['creative']['permalink_url'] = permalink_url
        else:
            ads_detail['creative']['permalink_url'] = None
    else:
        ads_detail['creative'] = None
    # tracking_specs
    tracking_specs = ads_data.get('tracking_specs')
    if tracking_specs:
        ads_detail['tracking_specs'] = [
            {str(key).replace('.', '_'): value for (key, value) in item.items()} for item in
            tracking_specs]
    else:
        ads_detail['tracking_specs'] = None
    # insights
    insights = ads_data.get('insights')
    if insights:
        insight = insight_conversation(insights)
        ads_detail.update(insight)
    return ads_detail


def update_ads_detail(access_token):
    """
        create or update ads detail, impressions, clicks, post_engagement, ctr, frequency by age and gender
    """
    query = """
        adaccounts{
            ads{
                insights.fields(clicks,impressions,actions).breakdowns(age,gender).date_preset(lifetime).time_increment(1)
            }
        }
    """
    url = 'https://graph.facebook.com/v5.0/me?fields={}&access_token={}'.format(query, access_token)
    ads_insights_detail = requests.get(url=url)
    if ads_insights_detail.status_code == 200:
        reading_ads_insights_detail = json.loads(ads_insights_detail.text).get('adaccounts')
        adaccounts_data = reading_ads_insights_detail.get('data')
        if adaccounts_data:
            for account in adaccounts_data:
                ads = account.get('ads')
                if ads:
                    ads_data = ads.get('data')
                    for ad in ads_data:
                        ads_id = ad.get('id')
                        # insights
                        insights = ad.get('insights')
                        if insights:
                            insight = insight_conversation(insights, plus=True)
                            update_fb_ads_db(ads_id, insight, plus=True)


def insight_conversation(insights, plus=None):
    insights_data = insights.get('data')
    dates = list(dict.fromkeys([insight.get('date_stop') for insight in insights_data]))
    dates = sorted(dates, key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
    total_impressions = sum(int(insight.get('impressions')) for insight in insights_data)
    total_clicks = sum(int(insight.get('clicks')) for insight in insights_data)
    total_post_engagement = sum(sum(int(action.get('value')) for action in insight.get('actions') if action.get('action_type') == 'post_engagement') for insight in insights_data if insight.get('actions'))

    if not plus:
        total_reach = sum(int(insight.get('reach')) for insight in insights_data)
        completed_time = dates[-1]
        completed_time_ts = time.mktime(dateutil.parser.parse(completed_time).timetuple())
        ads_detail = {
            'impressions': {
                'device': [],
                'date': []
            },
            'clicks': {
                'device': [],
                'date': []
            },
            'post_engagement': {
                'device': [],
                'date': []
            },
            'reach': {},
            'ctr': {},
            'frequency': {},
            'completed_time': completed_time,
            'completed_time_ts': completed_time_ts
        }
        # impressions
        impressions_desktop = sum(
            int(insight.get('impressions')) for insight in insights_data if 'desktop' in insight.get('device_platform'))
        impressions_desktop_percent = percent_of_goal(impressions_desktop, total_impressions)

        impressions_mobile = sum(
            int(insight.get('impressions')) for insight in insights_data if 'mobile' in insight.get('device_platform'))
        impressions_mobile_percent = percent_of_goal(impressions_mobile, total_impressions)

        impressions_tablet = sum(
            int(insight.get('impressions')) for insight in insights_data if 'tablet' in insight.get('device_platform'))
        impressions_tablet_percent = 100 - impressions_mobile_percent - impressions_desktop_percent \
            if 0 < impressions_mobile_percent + impressions_desktop_percent < 100 else 0

        impressions_facebook = sum(
            int(insight.get('impressions')) for insight in insights_data if insight.get('publisher_platform') == 'facebook')
        impressions_instagram = sum(
            int(insight.get('impressions')) for insight in insights_data if insight.get('publisher_platform') == 'instagram')
        ads_detail['impressions']['device'] = [
            {
                'device': 'destop',
                'value': impressions_desktop,
                'percent': impressions_desktop_percent
            },
            {
                'device': 'mobile',
                'value': impressions_mobile,
                'percent': impressions_mobile_percent
            },
            {
                'device': 'tablet',
                'value': impressions_tablet,
                'percent': impressions_tablet_percent
            }
        ]
        ads_detail['impressions']['facebook'] = impressions_facebook
        ads_detail['impressions']['instagram'] = impressions_instagram
        ads_detail['impressions']['total'] = total_impressions
        for date in dates:
            ads_in_date = {'date': datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')}
            impressions_date = sum(
                int(insight.get('impressions')) for insight in insights_data if insight.get('date_stop') == date)
            ads_in_date['value'] = impressions_date
            ads_detail['impressions']['date'].append(ads_in_date)

        # clicks
        clicks_desktop = sum(
            int(insight.get('clicks')) for insight in insights_data if 'desktop' in insight.get('device_platform'))
        clicks_desktop_percent = percent_of_goal(clicks_desktop, total_clicks)

        clicks_mobile = sum(
            int(insight.get('clicks')) for insight in insights_data if 'mobile' in insight.get('device_platform'))
        clicks_mobile_percent = percent_of_goal(clicks_mobile, total_clicks)

        clicks_tablet = sum(
            int(insight.get('clicks')) for insight in insights_data if 'tablet' in insight.get('device_platform'))
        clicks_tablet_percent = 100 - clicks_desktop_percent - clicks_mobile_percent \
            if 0 < clicks_desktop_percent + clicks_mobile_percent < 100 else 0

        clicks_facebook = sum(
            int(insight.get('clicks')) for insight in insights_data if insight.get('publisher_platform') == 'facebook')
        clicks_instagram = sum(
            int(insight.get('clicks')) for insight in insights_data if insight.get('publisher_platform') == 'instagram')
        ads_detail['clicks']['device'] = [
            {
                'device': 'destop',
                'value': clicks_desktop,
                'percent': clicks_desktop_percent
            },
            {
                'device': 'mobile',
                'value': clicks_mobile,
                'percent': clicks_mobile_percent
            },
            {
                'device': 'tablet',
                'value': clicks_tablet,
                'percent': clicks_tablet_percent
            }
        ]
        ads_detail['clicks']['facebook'] = clicks_facebook
        ads_detail['clicks']['instagram'] = clicks_instagram
        ads_detail['clicks']['total'] = total_clicks
        for date in dates:
            ads_in_date = {'date': datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')}
            clicks_date = sum(
                int(insight.get('clicks')) for insight in insights_data if insight.get('date_stop') == date)
            ads_in_date['value'] = clicks_date
            ads_detail['clicks']['date'].append(ads_in_date)
        # post_engagement
        post_engagement_desktop = sum(sum(int(action.get('value')) for action in insight.get('actions') if action.get('action_type') == 'post_engagement') for insight in insights_data if insight.get('actions') and 'desktop' in insight.get('device_platform'))
        post_engagement_desktop_percent = percent_of_goal(post_engagement_desktop, total_post_engagement)

        post_engagement_mobile = sum(sum(int(action.get('value')) for action in insight.get('actions') if action.get('action_type') == 'post_engagement') for insight in insights_data if insight.get('actions') and 'mobile' in insight.get('device_platform'))
        post_engagement_mobile_percent = percent_of_goal(post_engagement_mobile, total_post_engagement)

        post_engagement_tablet = sum(sum(int(action.get('value')) for action in insight.get('actions') if action.get('action_type') == 'post_engagement') for insight in insights_data if insight.get('actions') and 'tablet' in insight.get('device_platform'))
        post_engagement_tablet_percent = 100 - post_engagement_desktop_percent - post_engagement_mobile_percent \
            if 0 < post_engagement_desktop_percent + post_engagement_mobile_percent < 100 else 0

        post_engagement_facebook = sum(sum(int(action.get('value')) for action in insight.get('actions') if
                                         action.get('action_type') == 'post_engagement') for insight in insights_data if
                                     insight.get('actions') and insight.get('publisher_platform') == 'facebook')
        post_engagement_instagram = sum(sum(int(action.get('value')) for action in insight.get('actions') if
                                         action.get('action_type') == 'post_engagement') for insight in insights_data if
                                     insight.get('actions') and insight.get('publisher_platform') == 'instagram')
        ads_detail['post_engagement']['device'] = [
            {
                'device': 'destop',
                'value': post_engagement_desktop,
                'percent': post_engagement_desktop_percent
            },
            {
                'device': 'mobile',
                'value': post_engagement_mobile,
                'percent': post_engagement_mobile_percent
            },
            {
                'device': 'tablet',
                'value': post_engagement_tablet,
                'percent': post_engagement_tablet_percent
            }
        ]
        ads_detail['post_engagement']['facebook'] = post_engagement_facebook
        ads_detail['post_engagement']['instagram'] = post_engagement_instagram
        ads_detail['post_engagement']['total'] = total_post_engagement
        for date in dates:
            ads_in_date = {'date': datetime.strptime(date, '%Y-%m-%d').strftime('%d-%m-%Y')}
            post_engagement_date = sum(sum(int(action.get('value')) for action in insight.get('actions') if
                                         action.get('action_type') == 'post_engagement') for insight in insights_data if
                                     insight.get('actions') and insight.get('date_stop') == date)
            ads_in_date['value'] = post_engagement_date
            ads_detail['post_engagement']['date'].append(ads_in_date)
        # reach
        reach_facebook = sum(
            int(insight.get('reach')) for insight in insights_data if insight.get('publisher_platform') == 'facebook')
        reach_instagram = sum(
            int(insight.get('reach')) for insight in insights_data if insight.get('publisher_platform') == 'instagram')
        # ctr
        ctr_facebook = float(clicks_facebook) / float(impressions_facebook) * 100 if impressions_facebook != 0 else 0
        ctr_instagram = float(clicks_instagram) / float(impressions_instagram) * 100 if impressions_instagram != 0 else 0
        # frequency
        frequency_facebook = float(impressions_facebook) / float(reach_facebook) if reach_facebook != 0 else 0
        frequency_instagram = float(impressions_instagram) / float(reach_instagram) if reach_instagram != 0 else 0

        ads_detail['reach']['facebook'] = reach_facebook
        ads_detail['reach']['instagram'] = reach_instagram
        ads_detail['reach']['total'] = total_reach
        ads_detail['ctr']['facebook'] = ctr_facebook
        ads_detail['ctr']['instagram'] = ctr_instagram
        ads_detail['frequency']['facebook'] = frequency_facebook
        ads_detail['frequency']['instagram'] = frequency_instagram

        return ads_detail
    else:
        ages = list(dict.fromkeys([insight.get('age') for insight in insights_data]))
        ads_detail = {
            'impressions': {
                'age': [],
                'gender': []
            },
            'clicks': {
                'age': [],
                'gender': []
            },
            'post_engagement': {
                'age': [],
                'gender': []
            }
        }
        # impressions
        impressions_male = sum(
            int(insight.get('impressions')) for insight in insights_data if insight.get('gender') == 'male')
        impressions_male_percent = percent_of_goal(impressions_male, total_impressions)

        impressions_female = sum(
            int(insight.get('impressions')) for insight in insights_data if insight.get('gender') == 'female')
        impressions_female_percent = percent_of_goal(impressions_female, total_impressions)

        impressions_unknown = sum(
            int(insight.get('impressions')) for insight in insights_data if insight.get('gender') == 'unknown')
        impressions_unknown_percent = 100 - impressions_male_percent - impressions_female_percent \
            if 0 < impressions_male_percent + impressions_female_percent < 100 else 0

        ads_detail['impressions']['gender'] = [
            {
                'gender': 'male',
                'value': impressions_male,
                'percent': impressions_male_percent
            },
            {
                'gender': 'female',
                'value': impressions_female,
                'percent': impressions_female_percent
            },
            {
                'gender': 'unknown',
                'value': impressions_unknown,
                'percent': impressions_unknown_percent
            }
        ]
        for age in ages:
            impressions_age_detail = {'age': age}
            impressions_age = sum(
                int(insight.get('impressions')) for insight in insights_data if insight.get('age') == age)
            impressions_age_detail['value'] = impressions_age
            impressions_age_detail['percent'] = percent_of_goal(impressions_age, total_impressions)
            ads_detail['impressions']['age'].append(impressions_age_detail)

        # clicks
        clicks_male = sum(
            int(insight.get('clicks')) for insight in insights_data if insight.get('gender') == 'male')
        clicks_male_percent = percent_of_goal(clicks_male, total_clicks)

        clicks_female = sum(
            int(insight.get('clicks')) for insight in insights_data if insight.get('gender') == 'female')
        clicks_female_percent = percent_of_goal(clicks_female, total_clicks)

        clicks_unknown = sum(
            int(insight.get('clicks')) for insight in insights_data if insight.get('gender') == 'unknown')
        clicks_unknown_percent = 100 - clicks_male_percent - clicks_female_percent \
            if 0 < clicks_male_percent + clicks_female_percent < 100 else 0

        ads_detail['clicks']['gender'] = [
            {
                'gender': 'male',
                'value': clicks_male,
                'percent': clicks_male_percent
            },
            {
                'gender': 'female',
                'value': clicks_female,
                'percent': clicks_female_percent
            },
            {
                'gender': 'unknown',
                'value': clicks_unknown,
                'percent': clicks_unknown_percent
            }
        ]
        for age in ages:
            clicks_age_detail = {'age': age}
            clicks_age = sum(
                int(insight.get('clicks')) for insight in insights_data if insight.get('age') == age)
            clicks_age_detail['value'] = clicks_age
            clicks_age_detail['percent'] = percent_of_goal(clicks_age, total_clicks)
            ads_detail['clicks']['age'].append(clicks_age_detail)
        # post_engagement
        post_engagement_male = sum(sum(int(action.get('value')) for action in insight.get('actions') if
                                          action.get('action_type') == 'post_engagement') for insight in insights_data
                                      if insight.get('actions') and insight.get('gender') == 'male')
        post_engagement_male_percent = percent_of_goal(post_engagement_male, total_post_engagement)

        post_engagement_female = sum(sum(int(action.get('value')) for action in insight.get('actions') if
                                         action.get('action_type') == 'post_engagement') for insight in insights_data if
                                     insight.get('actions') and insight.get('gender') == 'female')
        post_engagement_female_percent = percent_of_goal(post_engagement_female, total_post_engagement)

        post_engagement_unknown = sum(sum(int(action.get('value')) for action in insight.get('actions') if
                                         action.get('action_type') == 'post_engagement') for insight in insights_data if
                                     insight.get('actions') and insight.get('gender') == 'unknown')
        post_engagement_unknown_percent = 100 - post_engagement_male_percent - post_engagement_female_percent \
            if 0 < post_engagement_male_percent + post_engagement_female_percent < 100 else 0

        ads_detail['post_engagement']['gender'] = [
            {
                'gender': 'male',
                'value': post_engagement_male,
                'percent': post_engagement_male_percent
            },
            {
                'gender': 'female',
                'value': post_engagement_female,
                'percent': post_engagement_female_percent
            },
            {
                'gender': 'unknown',
                'value': post_engagement_unknown,
                'percent': post_engagement_unknown_percent
            }
        ]
        for age in ages:
            post_engagement_age_detail = {'age': age}
            post_engagement_age = sum(sum(int(action.get('value')) for action in insight.get('actions') if
                                          action.get('action_type') == 'post_engagement') for insight in insights_data
                                      if insight.get('actions') and insight.get('age') == age)
            post_engagement_age_detail['value'] = post_engagement_age
            post_engagement_age_detail['percent'] = percent_of_goal(post_engagement_age, total_post_engagement)
            ads_detail['post_engagement']['age'].append(post_engagement_age_detail)

        return ads_detail


def logout_info_setting_fb(merchant_id):
    if not isinstance(merchant_id, ObjectId):
        merchant_id = ObjectId(merchant_id)
    DATABASE.facebook_setting.update_many({'merchant_id': merchant_id}, {'$set': {'status_login': False}})


def facebook_login(merchant_id, user_id, access_token, APP_ID=APP_ID, APP_SECRET=APP_SECRET):
    # collection facebook_setting
    long_access_token = fb_long_lived_user_access_token(APP_ID, APP_SECRET, access_token)
    facebook_sources = get_facebook_sources(merchant_id, user_id)
    if not facebook_sources:
        create_facebook_sources(merchant_id, user_id, access_token, long_access_token)
    else:
        update_facebook_sources(merchant_id, user_id, access_token, long_access_token)

    query = """
        email,
        gender,
        name,
        picture.type(large){
            url
        },
        adaccounts{
            account_status,
            created_time,
            name,
            owner,
            ads{
                adset_id,
                campaign_id,
                created_time,
                name,
                status,
                updated_time,
                tracking_specs,
                creative.thumbnail_width(200).thumbnail_height(200){
                    body,
                       name,
                    thumbnail_url,
                    object_story_id,
                    title
                },
                insights.fields(clicks,impressions,actions,reach).breakdowns(publisher_platform, device_platform).date_preset(lifetime).time_increment(1)
            }
        }
    """
    url = 'https://graph.facebook.com/v5.0/{}?fields={}&access_token={}'.format(user_id, query, access_token)
    reading = requests.get(url=url)
    if reading.status_code != 200:
        return False
    else:
        user_reading = json.loads(reading.text)
        fb_user_info = {'fb_user_id': user_id}
        user_email = user_reading.get('email')
        fb_user_info['email'] = user_email if user_email else None
        user_gender = user_reading.get('gender')
        fb_user_info['gender'] = user_gender if user_gender else None
        user_name = user_reading.get('name')
        fb_user_info['name'] = user_name if user_name else None

        try:
            user_profile_picture = user_reading.get('picture').get('data').get('url')
            picture_reading = requests.get(url=user_profile_picture)
            user_profile_photo = picture_reading.content
            profile_photo_origin_name = 'profile_photo_{}.jpg'.format(user_id)
            profile_photo_name = \
                hashlib.md5(user_profile_photo).hexdigest() + '.' + \
                profile_photo_origin_name.rsplit('.', 1)[1]
            profile_photo_data = {
                'file_name': profile_photo_name,
                'file_data': base64.b64encode(user_profile_photo),
                'origin_name': profile_photo_origin_name
            }
            storage_api.save_file(profile_photo_data)
            fb_user_info['photo_profile'] = profile_photo_name
        except:
            fb_user_info['photo_profile'] = None

        # adaccounts
        adaccounts = user_reading.get('adaccounts')
        fb_user_info['adaccounts'] = []
        if adaccounts:
            ads_accounts = adaccounts.get('data')
            for account in ads_accounts:
                user_ads_account = {'name': account.get('name'), 'fb_ads_account_id': account.get('id')}
                fb_user_info['adaccounts'].append(user_ads_account)
                ads_account_id = account.get('id')
                ads = account.get('ads')
                if ads:
                    ads_data = ads.get('data')
                    for ads in ads_data:
                        ads_id = ads.get('id')
                        fb_ads_detail = ads_detail(user_id, ads_account_id, ads)
                        facebook_ads = get_ads_info_by_id(ads_id)
                        if not facebook_ads:
                            create_fb_ads_db(fb_ads_detail)
                        else:
                            update_fb_ads_db(ads_id, fb_ads_detail)

        update_ads_detail(long_access_token)

        facebook_user = get_user_info_by_user_id(user_id)
        if not facebook_user:
            create_fb_user_db(fb_user_info)
        else:
            update_fb_user_db(user_id, fb_user_info)

# # collection fb_users
# facebook_user = get_user_info_by_user_id(user_id)
# merchant_id = '5a616f383fd79c2db9147c6a'
# print facebook_login(merchant_id, user_id, access_token)
