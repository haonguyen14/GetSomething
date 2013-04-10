# Create your views here.
from django.shortcuts import render
import Login
import FindItemsLive as FindItems

def index(request):
	if 'token' in request.session:
		request.session['state'] = 'login'
	elif not 'state' in request.session:
		request.session['state'] = 'unknown'
		
	if request.session['state'] != 'login':
		info = Login.GetLoginPage()
		sessionID = info[1]
		request.session['sessionID'] = sessionID
		
		loginPage = info[0]
	else:
		sessionID = ''
		loginPage = ''
		
	if 'output' in request.GET:
		output = request.GET['output']
	else:
		output = ''
		
	if 'imgUrl' in request.GET:
		imgUrl = request.GET['imgUrl']
	else:
		imgUrl = ''
		
	return render(request, 'index.html', {'state':'login', 'loginPage':'', 'output': output, 'imgUrl':imgUrl})
	
def BuyItem(request):
	maxPrice = request.GET['maxPrice']
	feedback = request.GET['feedback']
	if request.GET['weighted'] == 'true':
		weighted = True
	else:
		weighted = False
			
	if request.GET['minPrice'] == 'true':
		minPrice = True
	else:
		minPrice = False

	FindItems.init_database()
	item = FindItems.find(maxPrice, feedback, minPrice, weighted)
	output = item['URL']
	imgUrl = item['imageURL']	
	
	return render(request, 'index.html', {'state':'login', 'loginPage':'', 'output': output, 'imgUrl':imgUrl, "minPrice":minPrice, "weighted":weighted})
	
	
def GetToken(request):
	if 'username' in request.GET and 'sessionID' in request.session:
		username = request.GET['username']
		sessionID = request.session['sessionID']
		request.session['token'] = Login.GetToken(username, sessionID)
		
	return index(request)
