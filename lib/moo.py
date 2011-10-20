import httplib 
import json
import urllib2
import lib.oauth as oauth
import lib.MultipartPostHandler as MultipartPostHandler

class MOOClient(oauth.OAuthClient):

    server = 'secure.moo.com'
    oauth_port = 443
    service_port = 80
    request_token_url = 'https://secure.moo.com/oauth/request_token.php'
    access_token_url = 'https://secure.moo.com/oauth/access_token.php'
    authorization_url = 'https://secure.moo.com/oauth/authorize.php'
    service_url =  'http://www.moo.com/api/service/'
    access_token = None

    def __init__(self, consumer_key, consumer_secret):
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.oauth_connection = httplib.HTTPSConnection("%s:%d" % (self.server, self.oauth_port))
        self.service_connection = httplib.HTTPConnection("%s:%d" % (self.server, self.service_port))


    def __del__(self):
        self.oauth_connection.close()
        self.service_connection.close()


    def fetch_access_token(self, oauth_request):
        self.oauth_connection.request(oauth_request.http_method, self.access_token_url, headers=oauth_request.to_header()) 
        response = self.oauth_connection.getresponse()
        r = response.read()
        print(r)
        return oauth.OAuthToken.from_string(r)

    def is_authorized(self):
        authorized = False;
        if self.access_token is not None:
            authorized = True
        return authorized


    def get_request_token(self, callback):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(\
            self.consumer, callback=callback, http_url=self.request_token_url)
        oauth_request.sign_request(oauth.OAuthSignatureMethod_PLAINTEXT(), self.consumer, None)
        self.oauth_connection.request(oauth_request.http_method, self.request_token_url, headers=oauth_request.to_header())
        response = self.oauth_connection.getresponse()
        return oauth.OAuthToken.from_string(response.read())
        


    def get_authorization_url(self, request_token):
        return "%s?oauth_token=%s" % (self.authorization_url, request_token.key)


    def get_access_token(self, request_token, verification_code):
        oauth_request = oauth.OAuthRequest.from_consumer_and_token( \
            self.consumer, token=request_token, http_url=self.access_token_url, 
            parameters={'oauth_verifier': verification_code})
        oauth_request.sign_request(oauth.OAuthSignatureMethod_PLAINTEXT(), self.consumer, request_token)
        return self.fetch_access_token(oauth_request)

    @staticmethod
    def upload_image(image_file_path):
        #import pdb; pdb.set_trace()
        params = { 'imageFile' : file(image_file_path, 'rb'), 'method':'moo.image.uploadImage' }
        opener = urllib2.build_opener(MultipartPostHandler.MultipartPostHandler)
        resp = json.loads(opener.open("http://www.moo.com/api/service/", params).read())
        return resp['imageBasketItem']


    def get_template(self, access_token, template_name):
        params={}
        params['method']= 'moo.template.getTemplate' 
        params['templateCode']= template_name
        
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_method='GET', \
            token=access_token, http_url=self.service_url, parameters=params)
        
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, access_token)
        self.service_connection.request('GET', oauth_request.to_url())
        response = self.service_connection.getresponse()
        return response.read()
        
    def create_empty_pack(self, access_token, product_name):
        params={}
        params['method'] = 'moo.pack.createPack' 
        params['product'] = product_name
        
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(self.consumer, http_method='POST', \
            token=access_token, http_url=self.service_url, parameters=params)
        
        oauth_request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), self.consumer, access_token)
        self.service_connection.request('POST', oauth_request.to_url())
        response = self.service_connection.getresponse()
        return response.read()