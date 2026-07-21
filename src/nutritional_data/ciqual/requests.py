import requests
from constants.constants_variables import constants_variables_getter

CIQUAL_URL = constants_variables_getter('CIQUAL_URL')

def get_results(text_to_search: str) -> dict:

    ciqual_processed_response = {}
    request = {
        "from": 0,
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": text_to_search,
                            "fields": [
                                "nomIndexEng^2",
                                "nomEng"
                            ]
                        }
                    }
                ],
                "should": [
                    {
                        "prefix": {
                            "nomSortEng": {
                                "value": text_to_search,
                                "boost": 2
                            }
                        }
                    }
                ]
            }
        },
        "_source": {
            "excludes": [
                "compos",
                "groupeAfficheEng",
                "nomFr",
                "nomSortEng",
                "nomSortFr",
                "nomIndexFr",
                "nomIndexEng"
            ]
        }
    }

    response = requests.post(CIQUAL_URL, json=request)
    if response.status_code != 200:
        raise Exception(f"Error al obtener los datos de la API ciqual - Elasticsearch: {response.status_code}")

    ciqual_response = response.json()

    if not ciqual_response or not ciqual_response['hits']['total']:
        return ciqual_processed_response

    hits = ciqual_response['hits']['hits']

    for hit in hits:
        source_data = hit['_source']
        ciqual_processed_response[source_data['code']] = source_data['nomEng']

    return ciqual_processed_response