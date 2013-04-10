'''Login Module'''
import os
from xml.dom import minidom
import ConfigParser, SendApiRequest
	

'''Login into Ebay'''
def GetLoginPage():
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.ini"))

	loginUrl = config.get("Server", "loginUrl")
	runame = config.get("Runame", "runame")

	#setup request body
	request = "<?xml version='1.0' encoding='utf-8' ?>" +\
		"<GetSessionIDRequest xmlns='urn:ebay:apis:eBLBaseComponents'>" +\
			"<Version>811</Version>" +\
			"<RuName>" + runame + "</RuName>" +\
		"</GetSessionIDRequest>"

	#used to retrieve sessionID
	serverUrl = config.get("Server", "serverURL")
	respXml = SendApiRequest.SendApiRequest(request, serverUrl, "GetSessionID")
	resp = minidom.parseString(respXml)

	sessionID = resp.getElementsByTagName("SessionID")[0].firstChild

	return [loginUrl + "?SignIn&runame=" + runame + "&SessID=" + sessionID.nodeValue, sessionID.nodeValue]

	
'''Get user token'''
def GetToken(username, sessionID):
	config = ConfigParser.ConfigParser()
	config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "config.ini"))


	request = "<?xml version='1.0' encoding='utf-8' ?>" +\
		"<FetchTokenRequest xmlns='urn:ebay:apis:eBLBaseComponents'>" +\
		"<RequesterCredentials><Username>" + username + "</Username></RequesterCredentials>" +\
		"<SessionID>" + sessionID + "</SessionID>" +\
		"</FetchTokenRequest>"

	serverUrl = config.get("Server", "serverURL")
	respXml = SendApiRequest.SendApiRequest(request, serverUrl, "FetchToken")
	resp = minidom.parseString(respXml)
	
	if resp.getElementsByTagName("Ack")[0].firstChild.nodeValue == "Failure":
		return None

	token = resp.getElementsByTagName("eBayAuthToken")[0].firstChild

	return token.nodeValue

