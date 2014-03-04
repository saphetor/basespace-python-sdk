
from pprint import pprint
import urllib2
import shutil
import urllib
import pycurl
import httplib
import cStringIO
import json
import os

from BaseSpacePy.api.APIClient import APIClient
from BaseSpacePy.api.BaseSpaceException import *
from BaseSpacePy.model import *


class BaseAPI(object):
    '''
    Parent class for BaseSpaceAPI and BillingAPI classes
    '''
    def __init__(self, AccessToken, apiServer, timeout=10):
        '''
        :param AccessToken: the current access token
        :param apiServer: the api server URL with api version
        :param timeout: (optional) the timeout in seconds for each request made, default 10 
        '''
        self.apiClient = APIClient(AccessToken, apiServer, timeout=timeout)

    def __singleRequest__(self, myModel, resourcePath, method, queryParams, headerParams, postData=None, verbose=False, forcePost=False):
        '''
        Call a REST API and deserialize response into an object.
        
        :param myModel: a Response object that includes a 'Response' swaggerType key with a value for the model type to return
        :param resourcePath: the api url path to call (without server and version)
        :param method: the REST method type, eg. GET
        :param queryParams: a dictionary of query parameters
        :param headerParams: a dictionary of header parameters
        :param postData: (optional) data to POST, default None
        :param version: (optional) print detailed output, default False
        :param forcePost: (optional) use a POST call with pycurl instead of urllib, default False (used only when POSTing with no post data?)
        :param verbose: (optional) prints verbose output, default False
        
        :returns: an instance of the Response model from the provided myModel
        '''
        if verbose: 
            print '    # Path: ' + str(resourcePath)
            print '    # QPars: ' + str(queryParams)
            print '    # Hdrs: ' + str(headerParams)
            print '    # forcePost: ' + str(forcePost)             
        response = self.apiClient.callAPI(resourcePath, method, queryParams, postData, headerParams, forcePost=forcePost)
        if verbose: 
            print '    # Response: '            
            pprint(response)
        if not response: 
            raise ServerResponseException('No response returned')                
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise ServerResponseException(str(response['ResponseStatus']['ErrorCode'] + ": " + response['ResponseStatus']['Message']))
        elif response['ResponseStatus'].has_key('Message'):
            raise ServerResponseException(str(response['ResponseStatus']['Message']))
                 
        responseObject = self.apiClient.deserialize(response, myModel)
        return responseObject.Response

    def __listRequest__(self, myModel, resourcePath, method, queryParams, headerParams, verbose=False):
        '''
        Call a REST API that returns a list and deserialize response into a list of objects of the provided model.

        :param myModel: a Model type to return a list of
        :param resourcePath: the api url path to call (without server and version)
        :param method: the REST method type, eg. GET
        :param queryParams: a dictionary of query parameters
        :param headerParams: a dictionary of header parameters
        :param verbose: (optional) prints verbose output, default False
        
        :returns: a list of instances of the provided model
        '''                
        if verbose: 
            print '    # Path: ' + str(resourcePath)
            print '    # QPars: ' + str(queryParams)
            print '    # Hdrs: ' + str(headerParams)
        response = self.apiClient.callAPI(resourcePath, method, queryParams, None, headerParams)
        if verbose:
            print '    # Response: '             
            pprint(response)
        if not response: 
            raise ServerResponseException('No response returned')
        if response['ResponseStatus'].has_key('ErrorCode'):
            raise ServerResponseException(str(response['ResponseStatus']['ErrorCode'] + ": " + response['ResponseStatus']['Message']))
        elif response['ResponseStatus'].has_key('Message'):
            raise ServerResponseException(str(response['ResponseStatus']['Message']))
        
        respObj = self.apiClient.deserialize(response, ListResponse.ListResponse)
        return [self.apiClient.deserialize(c, myModel) for c in respObj._convertToObjectList()]

    def __makeCurlRequest__(self, data, url):
        '''
        Make a curl POST request
        
        :param data: data to post (eg. list of tuples of form (key, value))
        :param url: url to post data to
        :returns: dictionary of api server response
        '''
        post = urllib.urlencode(data)
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL,url)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.POSTFIELDS, post)
        c.setopt(c.WRITEFUNCTION, response.write)
        c.perform()
        c.close()
        obj = json.loads(response.getvalue())
        if obj.has_key('error'):
            raise Exception("BaseSpace exception: " + obj['error'] + " - " + obj['error_description'])
        return obj      

    def getTimeout(self):
        '''
        Returns the timeout in seconds for each request made
        '''
        return self.apiClient.timeout

    def setTimeout(self, time):
        '''
        Specify the timeout in seconds for each request made
        
        :param time: timeout in seconds
        '''        
        self.apiClient.timeout = time
        
    def getAccessToken(self):
        '''
        Returns the current access token. 
        '''        
        return self.apiClient.apiKey        

    def setAccessToken(self, token):
        '''
        Sets the current access token.
                
        :param token: an access token
        '''
        self.apiClient.apiKey = token            

    def getServerUri(self):
        '''
        Returns the server uri used by this instance
        '''
        return self.apiClient.apiServer

    def setServerUri(self, apiServer):
        '''
        Sets the server uri used by this instance
        
        :param apiServer: the api server url with version
        '''
        self.apiClient.apiServer = apiServer 
