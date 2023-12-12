import api


visits = api.DATABASE.visit_log.find()
for visit in visits:
    user_id = visit.get('user_id')
    user = api.get_user_info(user_id=user_id)
    if user:
        api.DATABASE.visit_log.update({'_id': visit['_id']},
                                      {'$set':{
                                          'phone': user['phone']
                                      }})
