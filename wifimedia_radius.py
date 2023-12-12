from datetime import datetime, timedelta
import pymysql
import pymysqlpool
from datetime import  datetime
import settings

def create_conn():
    mysql_host = settings.MYSQL_HOST
    mysql_port = settings.MYSQL_PORT
    mysql_user = settings.MYSQL_USER
    mysql_password = settings.MYSQL_PASSWORD
    mysql_db = settings.MYSQL_DB
    return pymysql.connect(host=mysql_host, port=mysql_port,
                           user=mysql_user, password=mysql_password,
                           database=mysql_db, charset='utf8',
                           autocommit=True)


pool = pymysqlpool.Pool(create_instance=create_conn)

def check_profile_radius(user_name):
    conn = pool.get()
    cursor = conn.cursor()
    sql = "select * from profiles where name = '%s'" % (user_name)
    print(sql)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def insert_profile_radius(user_name):
    created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    modified =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = pool.get()
    cursor = conn.cursor()
    sql = "INSERT INTO `profiles` (`name`, `available_to_siblings`, `user_id`, " \
          "`created`,`modified`) " \
          "VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(sql, (user_name, 1, 44, created, modified))
    conn.commit()
    cursor.close()
    conn.close()

def insert_profile_component_radius(group_name):
    created =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    modified =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = pool.get()
    cursor = conn.cursor()
    sql = "INSERT INTO `profile_components` (`name`, `available_to_siblings`, `user_id`, " \
          "`created`,`modified`) " \
          "VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(sql, (group_name, 1, 44, created, modified))
    conn.commit()
    cursor.close()
    conn.close()

def insert_client_radius(user_name, attribute, value, op):
    conn = pool.get()
    cursor = conn.cursor()
    sql = "INSERT INTO `radcheck` (`username`, `attribute`, `value`, " \
          "`op`) " \
          "VALUES (%s,%s,%s,%s)"
    cursor.execute(sql, (user_name, attribute, value, op))
    conn.commit()
    cursor.close()
    conn.close()


def get_client_radius_by_user_name(user_name):
    conn = pool.get()
    cursor = conn.cursor()
    sql = "select * from radcheck where username = '%s'" % (user_name)
    print(sql)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def get_client_radius_by_attr(user_name, attr):
    conn = pool.get()
    cursor = conn.cursor()
    sql = "select * from radcheck where username = '%s' and attribute='%s'" % (user_name, attr)
    print(sql)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result



def add_clients_to_radius_group(username, groupname, priority):
    conn = pool.get()
    cursor = conn.cursor()
    sql_session = "INSERT INTO `radusergroup` (`username`, `groupname`, " \
                  "`priority`) " \
                  "VALUES (%s,%s,%s)"
    cursor.execute(sql_session,
                   (username, groupname, priority))
    conn.commit()
    cursor.close()
    conn.close()


def insert_radius_group(groupname, attribute, value, op):
    conn = pool.get()
    cursor = conn.cursor()
    # sql_session = "INSERT INTO `radgroupcheck` (`groupname`, `attribute`, `value`, " \
    #               "`op`) " \
    #               "VALUES (%s,%s,%s,%s)"
    # cursor.execute(sql_session, (groupname, attribute, value, op))

    sql_attr =  "INSERT INTO `radgroupcheck` (`groupname`, `attribute`, `op`, " \
                  "`value`, `comment`, `created`, `modified`) " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql_attr, (groupname, 'Rd-Total-Time', ':=', '604800', '',  datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    cursor.execute(sql_attr, (groupname, 'Rd-Reset-Type-Time', ':=', 'never', '', datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    cursor.execute(sql_attr, (groupname, 'Rd-Cap-Type-Time', ':=', 'hard', '',  datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    cursor.close()
    conn.close()


def check_user_in_group(user, group):
    conn = pool.get()
    cursor = conn.cursor()
    sql = "select * from radusergroup where username='%s' and groupname = '%s'" % (user, group)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def check_radius_group(groupname):
    conn = pool.get()
    cursor = conn.cursor()
    sql = "select * from radgroupcheck where groupname = '%s'" % (groupname)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def check_group_reply(groupname, attribute):
    conn = pool.get()
    cursor = conn.cursor()
    sql = "select * from radgroupreply where groupname = '%s' and attribute='%s'" % (groupname, attribute)
    cursor.execute(sql)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def add_radius_group_reply(groupname, attribute, value):
    created =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    modified =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = pool.get()
    cursor = conn.cursor()

    sql_session = "INSERT INTO `radgroupreply` (`groupname`, `attribute`, `op`, " \
                  "`value`, `comment`,`created`, `modified`) " \
                  "VALUES (%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(sql_session, (groupname, attribute, ':=', value, '', created, modified))
    conn.commit()
    cursor.close()
    conn.close()


def update_radius_group_reply(groupname, session_timeout, up_bw, down_bw):
    modified =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = pool.get()
    cursor = conn.cursor()
    updateStatement = "UPDATE radgroupreply set value='%s',modified='%s'  where " \
                      "groupname='%s' and attribute='%s'" % (down_bw, modified, groupname, 'WISPr-Bandwidth-Max-Down')

    cursor.execute(updateStatement)
    updateStatement = "UPDATE radgroupreply set value='%s',modified='%s' where " \
                      "groupname='%s' and attribute='%s'" % (up_bw, modified, groupname, 'WISPr-Bandwidth-Max-Up')

    cursor.execute(updateStatement)
    updateStatement = "UPDATE radgroupreply set value='%s',modified='%s' where " \
                      "groupname='%s' and attribute='%s'" % (session_timeout, modified, groupname, 'Session-Timeout')

    cursor.execute(updateStatement)

    conn.commit()
    cursor.close()
    conn.close()
