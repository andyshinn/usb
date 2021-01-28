import os
import random
from typing import Union, List

from meilisearch import Client

from usb.document import Document

MEILI_API_KEY = os.getenv("MEILI_API_KEY_PRIVATE", None)
MEILI_ENDPOINT = "http://{}:7700".format(os.getenv("SERVICE_NAME_MEILISEARCH", "meilisearch"))


class Meilisearch(Client):
    def __init__(self, url=MEILI_ENDPOINT, api_key=MEILI_API_KEY):
        super(Meilisearch, self).__init__(url, api_key)

    def get_document(self, index, document_id) -> Union[Document, None]:
        document: dict = self.index(index).get_document(document_id)

        if not document:
            return None

        return Document(**document_without_id(document))

    def get(self, index_name: str, query: str, rand=True) -> Union[Document, None]:
        results = self.index(index_name).search(query, dict(limit=20))

        if len(results["hits"]) > 0:
            if rand:
                result: dict = random.choice(results["hits"])
            else:
                result = results["hits"][0]

            return Document(**document_without_id(result))

        return None

    def search(self, index_name: str, query: str, options=None) -> Union[List[Document], None]:
        if options is None:
            options = {"limit": 10}

        index = self.index(index_name)
        results = index.search(query, options)

        if not results.get("hits", None):
            return None

        return list(map(lambda result: Document(**document_without_id(result)), results.get("hits")))


def document_without_id(result: dict):
    return {k: v for (k, v) in result.items() if k != "id"}
