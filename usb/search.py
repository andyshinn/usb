import os

from elastic_app_search import Client

API_KEY = os.getenv('APPSEARCH_PRIVATE_KEY')
ENGINE = 'usb'
ENDPOINT = 'appsearch:3002/api/as/v1'


class Appsearch:
    def __init__(self, base_endpoint=ENDPOINT, api_key=API_KEY, engine=ENGINE):
        self.client = Client(base_endpoint=base_endpoint, api_key=api_key ,use_https=False)
        self.engine = engine


    def get_document(self, id):
        documents = self.client.get_documents(self.engine, [id])

        if len(documents) == 1:
            return documents[0]

        return None


    def index(self, documents):
        return self.client.index_documents(self.engine, documents)


    def query(self, query):
        return self.client.search(self.engine, query)
