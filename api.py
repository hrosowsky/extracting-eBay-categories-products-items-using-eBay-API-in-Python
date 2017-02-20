import settings
import utilities
import urllib
import uuid
from xml.etree import ElementTree as et

def get_response_finding_api(operation_name, xml_request):
    
    http_headers = {
        'X-EBAY-SOA-SECURITY-APPNAME': settings.APP_ID
        , 'X-EBAY-SOA-OPERATION-NAME': operation_name
        , 'X-EBAY-SOA-GLOBAL-ID': settings.GLOBAL_ID
        , 'Content-type': 'text/xml;charset=utf-8'
    }   
    
    return get_response(settings.URL_FINDING_API, xml_request, http_headers)
    
def get_response_shopping_api(operation_name, xml_request):
    
    http_headers = {
          'X-EBAY-API-APP-ID': settings.APP_ID
        , 'X-EBAY-API-SITE-ID': settings.SITE_ID
        , 'X-EBAY-API-CALL-NAME': operation_name
        , 'X-EBAY-API-VERSION': settings.VERSION
        , 'X-EBAY-API-REQUEST-ENCODING': settings.ENCODING
        , 'Content-type': 'text/xml;charset=utf-8'
    }  
    
    return get_response(settings.URL_SHOPPING_API, xml_request, http_headers)
    
def get_response_trading_api(operation_name, xml_request):
    
    http_headers = {
        'X-EBAY-API-SITEID': settings.SITE_ID
        , 'X-EBAY-API-COMPATIBILITY-LEVEL': settings.COMPATIBILITY_LEVEL
        , 'X-EBAY-API-CALL-NAME': operation_name
    }
    
    return get_response(settings.URL_TRADING_API, xml_request, http_headers)
    
def get_response(url, xml_request, http_headers): 
    
    # Convert to utf-8 encoded string
    request_utf8 = '<?xml version="1.0" encoding="UTF-8"?>'.encode('utf-8') + et.tostring(xml_request, encoding='utf-8', method='xml') 
        
    # Write request to file
    file_name = str(uuid.uuid4())
    utilities.save_xml_to_file('log/' + file_name + ' request.xml', request_utf8.decode('utf-8'))   
    
    print('    Making xml request to eBay api...')
    
    # Make url request and get response
    req = urllib.request.Request(url, request_utf8, http_headers) 
    res = urllib.request.urlopen(req) 
    data = res.read()
    # Hack to remove namespace
    data = data.replace(b' xmlns="urn:ebay:apis:eBLBaseComponents"', b'')
    data = data.replace(b' xmlns="http://www.ebay.com/marketplace/search/v1/services"', b'')
        
    print('    Response received and writing to file.')    
    
    # Write response to file    
    utilities.save_xml_to_file('log/' + file_name + ' response.xml', data)    
    
    xml = et.fromstring(data)
    
    return xml