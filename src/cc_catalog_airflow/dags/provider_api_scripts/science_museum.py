import logging
from common.requester import DelayedRequester
from common.storage.image import ImageStore

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s:  %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LIMIT = 100
DELAY = 5.0
RETRIES = 3
PROVIDER = "sciencemuseum"
ENDPOINT = "https://collection.sciencemuseumgroup.org.uk/search/"

delay_request = DelayedRequester(delay=DELAY)
image_store = ImageStore(provider=PROVIDER)

HEADERS = {
    "Accept":"application/json"
}

DEFAULT_QUERY_PARAM = {
    "has_image" : 1,
	"image_license" : "CC",
	"page[size]" : LIMIT,
	"page[number]" : 1
}


def main():
    logger.info("Begin: Science Museum script")
    page_number = 1
    condition = True
    while condition:
        query_param = _get_query_param(
            page_number=page_number
            )
        batch_data = _get_batch_objects(
            query_param=query_param
        )
        if batch_data:
            image_count = _handle_object_data(batch_data)      
            page_number += 1
        else:
            condition = False
    logger.info(f"Total pages crawled {page_number}")
    
        
def _get_query_param(
        page_number=1,
        default_query_param=DEFAULT_QUERY_PARAM
        ):
    query_param = default_query_param.copy()
    query_param["page[number]"] = page_number
    return query_param


def _get_batch_objects(
        endpoint=ENDPOINT,
        headers=HEADERS,
        retries=RETRIES,
        query_param=None
        ):
    for retry in range(retries):
        response = delay_request.get(
            endpoint,
            query_param,
            headers=headers
        )
        try:
            response_json = response.json()
            if "data" in response_json.keys():
                data = response_json.get("data")
                break
            else:
                data = None 
        except Exception as e:
            logger.error(f"Failed to due to {e}")
            data = None
    return data


def _handle_object_data(batch_data)
    pass            

