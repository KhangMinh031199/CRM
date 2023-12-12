from datetime import datetime
from bson.objectid import ObjectId
from raven import Client
from raven.transport.http import HTTPTransport
from apscheduler.schedulers.blocking import BlockingScheduler
import api_radius

reload(sys)

sys.setdefaultencoding('utf-8')
logging.basicConfig()

sched = BlockingScheduler(
    {
        'apscheduler.jobstores.redis': {
            'type': 'redis'
        },
        'apscheduler.timezone': 'UTC',
    }
)

sentry = Client(
    'http://9399211fa32c46a69c3b40d5a41c99ed:9989ba328bc748aeb4d8dd52b3fa8234@sentry.nextify.vn/2',
    transport=HTTPTransport
)


@sched.scheduled_job('interval', minutes=15)
def run():
    clients = api_radius.get_expire_radius_client(time.time())
    for client in clients:
        client_mac = client.get('client_mac')
        api_radius.update_client_radius_status(client_mac, 'Reject')
        print client
        
sched.start()

