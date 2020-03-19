import os
import random

from elastic_app_search import Client

API_KEY = os.getenv('APPSEARCH_PRIVATE_KEY')
ENGINE = 'usb'
ENDPOINT = 'appsearch:3002/api/as/v1'


class Appsearch(Client):
    def __init__(self, endpoint=ENDPOINT, api_key=API_KEY):
        super(Appsearch, self).__init__(
            base_endpoint=endpoint,
            api_key=api_key,
            use_https=False
        )


    def get_document(self, engine, id):
        documents = self.get_documents(engine, [id])

        if len(documents) == 1:
            return documents[0]

        return None


    def get(self, engine, query, rand=True):
        results = self.search(engine, query)

        if results['results']:
            if rand:
                result = random.choice(results['results'])
            else:
                result = results['results'][0]

            return result

        return None
