import os
import httplib
import ConfigParser
from urlparse import urlparse

'''send XML HTTP request to the specified server'''
'''return XML response'''
def SendApiRequest(requestBody, url, verb):
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.ini"))


	devID = config.get("Keys", "Developer")
	appID = config.get("Keys", "Application")
	certID = config.get("Keys", "Certificate")

	header = {"X-EBAY-API-COMPATIBILITY-LEVEL": "811",
		"X-EBAY-API-DEV-NAME": devID,
		"X-EBAY-API-APP-NAME": appID,
		"X-EBAY-API-CERT-NAME": certID,
		"X-EBAY-API-CALL-NAME": verb,
		"X-EBAY-API-SITEID": "0",
		"Content-Type": "text/xml"
		}

	url = urlparse(url)
	if url.scheme == "https":
		conn = httplib.HTTPSConnection(url.netloc)
	else:
		conn = httplib.HTTPConnection(url.netloc)

	conn.request("POST", url.path, requestBody, header)
	resp = conn.getresponse()

	return resp.read()
