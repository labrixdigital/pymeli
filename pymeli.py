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

def listing_prices(**kwargs):
 return _get(
  resource='/sites/{site_id}/listing_prices'.format(**kwargs),
  parameters={'price':kwargs['price']}
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