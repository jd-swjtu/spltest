import requests
import urllib
import json

#Disable the worning of certificate
requests.packages.urllib3.disable_warnings()

class RestException(Exception):
    pass

class RestHelper(object):
    def __init__(self, baseUrl, timeout=90):
        self.url = baseUrl
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, uri, **kwargs):
        return self.request(uri, 'GET', **kwargs)
    
    def post(self, uri, **kwargs):
        return self.request(uri, 'POST', **kwargs)
    
    def put(self, uri, **kwargs):
        return self.request(uri, 'PUT', **kwargs)

    def delete(self, uri, **kwargs):
        return self.request(uri, 'DELETE', **kwargs)
    
    def request(self, uri, method, headers=None, payload=None,
            content_type='application/json', raw=False, **kwargs):
        url = self.url.rstrip('/') + '/' + uri.lstrip('/')
        if not headers:
            headers = {'Accept': 'application/json'}
        
        if content_type and 'Content-Type' not in headers:
            headers['Content-Type'] = content_type
        response = self.session.request(method, url, headers=headers, data=payload,
            timeout=self.timeout, verify=False, **kwargs)
        if raw:
            return response
        return self.process_response(response)
    
    def process_response(self, response):
        if response.status_code in [requests.codes.ok, requests.codes.no_content]:
            return response.json()

        raise RestException('API response status code: %s' % response.status_code)

    def get_movies(self, cat='batman', count=None, **kwargs):
        params = {"q": cat}
        if count != None:
            params['count'] = count

        uri = 'movies?%s' % urllib.urlencode(params)
        return self.get(uri, **kwargs)['results']
    
    def add_movies(self, name, description, **kwargs):
        uri = 'movies'
        info = {"name": name, "description": description}
        return self.post(uri, payload=json.dumps(info), **kwargs)


if __name__ == '__main__':
    rest = RestHelper('https://splunk.mocklab.io')
    print rest.get_movies()
    print rest.add_movies('Harry Polt', 'Fantancy Movies')