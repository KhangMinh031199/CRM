import settings
from elasticsearch import Elasticsearch


es = Elasticsearch(
    [settings.ELASTICSEARCH_SERVER],
    http_auth=(settings.ELASTICSEARCH_USER, settings.ELASTICSEARCH_PASSWORD),
    scheme="http",
    port=9200,
    timeout=3000,
    max_retries=10,
    retry_on_timeout=True
)


def create_or_update_index(index_name, doc_type, body_index, index_id):
    if es.exists(index=index_name, id=index_id):
        es.update(index=index_name, doc_type=doc_type, body=body_index, id=index_id)
    else:
        es.index(index=index_name, doc_type=doc_type, body=body_index, id=index_id)


def remove_index(index_name, index_id):
    es.delete(index=index_name, id=index_id)