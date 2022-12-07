import json
import requests

class Meli():
 def __init__(self, *, credentials, token):
  """Constructor for Meli class
  Parameters:
  - credentials: The file where your client (application) credentials are
   stored or the dictionary containing them (client_id and client_secret)
  - token: The file where the token from the user grant is stored or a dictionary
   containing the access_token and refresh_token
  """
  if type(credentials) == str:
   with open(credentiasl, 'r') as f:
    self.credentials = json.load(f)
   self.credentials = credentials

  if type(token) == str:
   with open(token, 'r') as f:
    self.token = json.load(f)
   self.token = token
 
 def refresh_token():
  """Refresh the current token. It saves it in memory for future use and also
  returns an object containing the new token for persistent storage
  Return:
  - token: A dictionary containing the access_token and refresh_token
  """
  url = 'https://api.mercadolibre.com/oauth/token'
  data = {
   'grant_type':'refresh_token',
   'client_id':self.credentials['client_id'],
   'client_secret':self.credentials['client_secret'],
   'refresh_token':self.token['refresh_token']
  }
  response = requests.post(
   url=url,
   data=data
  )
  response.raise_for_status()
  return json.loads(response.text)
 
 def me():
  return self._get(resource='/users/me')

 def sites():
  return self._get(resource='/sites')

 def listing_types(**kwargs):
  return self._get(
   resource='/sites/{site_id}/listing_types'.format(**kwargs)
  )

 def listing_type(**kwargs):
  return self._get(
   resource='/sites/{site_id}/listing_types/{listing_type}'.format(**kwargs)
  )

 def listing_prices(**kwargs):
  parameters = {}
  if 'price' in kwargs:
   parameters['price'] = kwargs['price']
  if 'category_id' in kwargs:
   parameters['category_id'] = kwargs['category_id']
  return self._get(
   resource='/sites/{site_id}/listing_prices'.format(**kwargs),
   parameters=parameters
  )

 def categories(**kwargs):
  return self._get(
   resource='/sites/{site_id}/categories'.format(**kwargs)
  )

 def category(**kwargs):
  return self._get(
   resource='/categories/{category_id}'.format(**kwargs)
  )

 def category_search(**kwargs):
  #Check if searching for a query
  parameters = {'category':kwargs['category_id']}
  if 'query' in kwargs:
   parameters['q'] = kwargs['query']
  #Paginate
  response = self._get(
   resource='/sites/{site_id}/search'.format(**kwargs),
   parameters=parameters
  )
  results = response['results']
  total = response['paging']['total']
  for offset in range(50,total,50):
   results += self._get(
    resource='/sites/{site_id}/search'.format(**kwargs),
    parameters={
     **parameters,
     'limit':'50',
     'offset':offset
    }
   )['results']
  return results

 def item(**kwargs):
  return self._get(
   resource='/items/{item_id}'.format(**kwargs)
  )

 def item_description(**kwargs):
  return self._get(
   resource='/items/{item_id}/description'.format(**kwargs)
  )

 def user_items(**kwargs):
  #If no user, then get the ID for me
  if 'user_id' not in kwargs:
   user_id = me()['id']
  else:
   user_id = kwargs['user_id']

  response = self._get(
   resource='/users/{user_id}/items/search'.format(user_id=user_id),
   parameters={'limit':'100','offset':'0','search_type':'scan'}
  )
  total = response['paging']['total']
  scroll_id = response['scroll_id']
  results = response['results']
  
  for _ in range(100,total,100):
   results += self._get(
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
 ##############################################################################
 ########### INTERNAL FUNCTIONS NOT TO BE IMPLEMENTED PUBLICALLY###############
 ##############################################################################
 def _get_authorization_header():
  #Get token
  return {"Authorization": "Bearer {}".format(
   self.token['access_token'])}

 def _get(**kwargs):
  headers = _get_authorization_header()
  url = 'https://api.mercadolibre.com' + kwargs['resource']
  if 'parameters' not in kwargs:
   parameters = {}
  else:
   parameters = kwargs['parameters']
  #Issue request
  response = requests.get(url=url, headers=headers, params=parameters)
  response.raise_for_status()
  return json.loads(response.text)

 def _post(**kwargs):
  #Most basic request
  request = {
   'url': 'https://api.mercadolibre.com' + kwargs['resource'],
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
  response.raise_for_status()
  return json.loads(response.text)

 def _put(**kwargs):
  #Most basic request
  request = {
   'url': 'https://api.mercadolibre.com' + kwargs['resource'],
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
  response.raise_for_status()
  return json.loads(response.text)


