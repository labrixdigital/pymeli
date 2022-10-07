import requests
import json
from os import environ

BASE_URL = 'https://api.mercadolibre.com'
USER_NAME = environ['MELI_USER']

def refresh_token():
 token = _get_token()
 credentials = _get_credentials()

 #Request refresh token
 url = BASE_URL + '/oauth/token'
 data = {
  'grant_type':'refresh_token',
  'client_id':credentials['client_id'],
  'client_secret':credentials['client_secret'],
  'refresh_token':token['refresh_token']
 }
 response = requests.post(
  url=url,
  data=data
 )

 #Save the new token
 if response.status_code == 200:
  with open('tokens/{}.json'.format(USER_NAME), 'w+') as f:
   f.write(response.text)

 return json.loads(response.text)

def me():
 return _get(resource='/users/me')

def sites():
 return _get(resource='/sites')

def listing_types(**kwargs):
 return _get(
  resource='/sites/{site_id}/listing_types'.format(**kwargs)
 )

def listing_type(**kwargs):
 return _get(
  resource='/sites/{site_id}/listing_types/{listing_type}'.format(**kwargs)
 )

def listing_prices(**kwargs):
 parameters = {}
 if 'price' in kwargs:
  parameters['price'] = kwargs['price']
 if 'category_id' in kwargs:
  parameters['category_id'] = kwargs['category_id']
 return _get(
  resource='/sites/{site_id}/listing_prices'.format(**kwargs),
  parameters=parameters
 )

def categories(**kwargs):
 return _get(
  resource='/sites/{site_id}/categories'.format(**kwargs)
 )

def category(**kwargs):
 return _get(
  resource='/categories/{category_id}'.format(**kwargs)
 )

def category_search(**kwargs):
 #Check if searching for a query
 parameters = {'category':kwargs['category_id']}
 if 'query' in kwargs:
  parameters['q'] = kwargs['query']
 #Paginate
 response = _get(
  resource='/sites/{site_id}/search'.format(**kwargs),
  parameters=parameters
 )
 results = response['results']
 total = response['paging']['total']
 for offset in range(50,total,50):
  results += _get(
   resource='/sites/{site_id}/search'.format(**kwargs),
   parameters={
    **parameters,
    'limit':'50',
    'offset':offset
   }
  )['results']
 return results

def item(**kwargs):
 return _get(
  resource='/items/{item_id}'.format(**kwargs)
 )

def item_description(**kwargs):
 return _get(
  resource='/items/{item_id}/description'.format(**kwargs)
 )

def user_items(**kwargs):
 #If no user, then get the ID for me
 if 'user_id' not in kwargs:
  user_id = me()['id']
 else:
  user_id = kwargs['user_id']

 response = _get(
  resource='/users/{user_id}/items/search'.format(user_id=user_id),
  parameters={'limit':'100','offset':'0','search_type':'scan'}
 )
 total = response['paging']['total']
 scroll_id = response['scroll_id']
 results = response['results']
 
 for _ in range(100,total,100):
  results += _get(
   resource='/users/{user_id}/items/search'.format(user_id=user_id),
   parameters={
    'limit':'100',
    'scroll_id':scroll_id,
    'search_type':'scan'
   }
  )['results']

 return results

def publish_item(**kwargs):
 response = _post(
   headers = {'Content-Type':'application/json'},
   resource = '/items',
   data = kwargs['item']
  )
 return response

def update_item(**kwargs):
 response = _put(
   headers = {'Content-Type':'application/json'},
   resource='/items/{item_id}'.format(**kwargs),
   data = kwargs['updates']
  )
 return response

def upload_item_description(**kwargs):
 response = _post(
   headers = {'Content-Type':'application/json'},
   resource='/items/{item_id}/description'.format(**kwargs),
   data = {'plain_text':kwargs['description']}
  )
 return response

def update_item_description(**kwargs):
 response = _put(
   headers = {'Content-Type':'application/json'},
   resource='/items/{item_id}/description'.format(**kwargs),
   data = {'plain_text':kwargs['description']}
  )
 return response

def upload_image(**kwargs):
 response = _post(
   headers = {'multipart':'form-data'},
   resource = '/pictures/items/upload',
   image = kwargs['image']
  )
 return response

def update_available_quantity(**kwargs):
 response = _put(
   headers = {'Content-Type':'application/json'},
   resource='/items/{item_id}'.format(**kwargs),
   data = {'available_quantity':kwargs['available_quantity']}
  )
 return response

def pause_item(**kwargs):
 response = _put(
   headers = {'Content-Type':'application/json'},
   resource='/items/{item_id}'.format(**kwargs),
   data = {'status':'paused'}
  )
 return response

def activate_item(**kwargs):
 response = _put(
   headers = {'Content-Type':'application/json'},
   resource='/items/{item_id}'.format(**kwargs),
   data = {'status':'active'}
  )
 return response

def set_free_shipping(**kwargs):
 payload = {
  "shipping": {
        "mode": "me2",
        "free_methods":
        [
            {
                "id": 501245,
                "rule":
                {
                    "default": True,
                    "free_mode": "country",
                    "free_shipping_flag": True,
                    "value": None
                }
            }
        ],
        "local_pick_up": False,
        "free_shipping": True,
        "logistic_type": "drop_off"
    }
 }
 response = _put(
   headers = {'Content-Type':'application/json'},
   resource='/items/{item_id}'.format(**kwargs),
   data = payload
  )
 return response


###############################################################################
def _get_token():
 #Read file with token details
 with open('tokens/{}.json'.format(USER_NAME), 'r') as f:
  token = json.load(f)
 return token

def _get_credentials():
 #Read file with credential details
 with open('credentials.json', 'r') as f:
  credentials = json.load(f)
 return credentials

def _get_authorization_header():
 #Get token
 token = _get_token()
 header = {"Authorization": "Bearer {}".format(
  token['access_token'])}
 return header

def _get(**kwargs):
 headers = _get_authorization_header()
 url = BASE_URL + kwargs['resource']
 if 'parameters' not in kwargs:
  parameters = {}
 else:
  parameters = kwargs['parameters']

 response = requests.get(url=url, headers=headers, params=parameters)
 response.raise_for_status()
 return json.loads(response.text)

def _post(**kwargs):
 #Most basic request
 request = {
  'url': BASE_URL + kwargs['resource'],
  'headers': _get_authorization_header()
 }
 #Enhance if additional headers
 if 'headers' in kwargs:
  request['headers'] = {**request['headers'], **kwargs['headers']}
 #Enhance if data
 if 'data' in kwargs:
  request['data'] = json.dumps(kwargs['data'])
 #Enhance if image
 elif 'image' in kwargs:
  from requests_toolbelt import MultipartEncoder
  request['data'] = MultipartEncoder(
   fields={'file': ('i.jpeg',kwargs['image'],'image/jpeg')})
  request['headers'] = {
   **request['headers'], 'Content-type': request['data'].content_type}
 #Issue request
 response = requests.post(**request)

 return json.loads(response.text)

def _put(**kwargs):
 #Most basic request
 request = {
  'url': BASE_URL + kwargs['resource'],
  'headers': _get_authorization_header()
 }
 #Enhance if additional headers
 if 'headers' in kwargs:
  request['headers'] = {**request['headers'], **kwargs['headers']}
 #Enhance if data
 if 'data' in kwargs:
  request['data'] = json.dumps(kwargs['data'])
 #Issue request
 response = requests.put(**request)

 return json.loads(response.text)



