#Josh Tanner, Hao Nguyen
import urllib, json, random, sqlite3, os, math
import ConfigParser

#App information
config = ConfigParser.ConfigParser()
config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)), "configLive.ini"))

devID = config.get("Keys", "Developer")
appID = config.get("Keys", "Application")
certID = config.get("Keys", "Certificate")
findingUrl = config.get("Server", "findingURL")
shoppingUrl = config.get("Server", "shoppingURL")


categories = {'antiques':'20081', 'art':'550', 'baby':'2984','books':'267','business & industrial':'12576','cameras & photo':'625',
 'cell phones & accessories':'15032', 'clothing, shoes & accessories':'15032', 'coins & paper money':'1116',
 'collectibles':'1', 'computers/tablets & networking':'58058', 'consumer electronics': '293', 'crafts': '14439',
 'dolls & bears':'237', 'dvds & movies': '11232', 'entertainment memorabilia':'45100', 'everything else':'99',
 'gift cards & coupons':'172008', 'health & beauty':'26395', 'home & garden':'11700', 'jewelry & watches': '281',
 'music':'11233', 'musical instruments & gear':'619', 'pet supplies':'1281', 'pottery & glass':'870',
 'real estate':'10542', 'speciality services':'316', 'sporting goods':'382', 'sports mem, cards & fan shop':'64482',
 'stamps':'260', 'tickets':'1305', 'toys & hobbies':'220', 'travel':'3252', 'video games & consoles': '1249'}


picked = {'everything else': 1, 'art': 1, 'pet supplies': 1, 'cell phones & accessories': 1, 'books': 1, 'gift cards & coupons': 1,
          'sporting goods': 1, 'cameras & photo': 1, 'video games & consoles': 1, 'dolls & bears': 1, 'business & industrial': 1,
          'collectibles': 1, 'travel': 1, 'antiques': 1, 'dvds & movies': 1, 'stamps': 1, 'musical instruments & gear': 1, 'music': 1, 
          'clothing, shoes & accessories': 1, 'real estate': 1, 'sports mem, cards & fan shop': 1, 'home & garden': 1, 'coins & paper money': 1,
          'health & beauty': 1, 'baby': 1, 'tickets': 1, 'consumer electronics': 1, 'computers/tablets & networking': 1, 'toys & hobbies': 1,
          'entertainment memorabilia': 1, 'crafts': 1, 'jewelry & watches': 1, 'pottery & glass': 1, 'speciality services': 1}

# sub categories are not useful
file = None
def init_database():
    global file
    build = not os.path.exists('LivePurchases.sqlite')
    file = sqlite3.connect('LivePurchases.sqlite')
    file.row_factory = sqlite3.Row #so info is returned as dicts
    if build:
        cur = file.cursor()
        cur.execute("CREATE TABLE purchases (ID TEXT, url TEXT, category TEXT, UNIQUE(ID))")
        cur.execute("CREATE TABLE categories (category TEXT, picked INT, unique(category))")
        cur.executemany("INSERT INTO categories VALUES (?,?)", picked.items())
        file.commit()
    else:
        cur = file.cursor()
        cur.execute("SELECT * FROM CATEGORIES")
        populate = cur.fetchall()
        for item in populate:
            picked[item[0]] = item[1]

def getParent(categoryID):
    url = shoppingUrl +\
        "?callname=GetCategoryInfo&" +\
        "version=677&" +\
        "appid="+appID+"&" +\
        "responseencoding=JSON&" +\
        "categoryID="+categoryID+"&" 

    resp = urllib.urlopen(url)
    r = resp.read()
    val = json.loads(r)
    parent = val['CategoryArray']['Category'][0]['CategoryParentID']
    if parent == '-1': actualParent = categoryID
    else: actualParent = getParent(parent)
    return actualParent

def save(item):
    global file
    cur = file.cursor()
    parent = getParent(item['primaryCategory'][0]['categoryId'][0])
    cur.execute("INSERT OR IGNORE INTO purchases VALUES (?, ?, ?)", (item['itemId'][0],item['viewItemURL'][0], parent))
    file.commit()

def purchases():
    '''Returns a list of lists. The first list represents all the database entries. If you want the most recent purchase,
    simply look at the end of the list. The lists in each list slot are purchases in the form ['itemId', 'url', 'category']'''
    global file
    cur = file.cursor()
    cur.execute("SELECT * FROM purchases")
    all = cur.fetchall()
    return all


def search(minPrice, maxPrice, feedbackMinimum, topSellersOnly = False, evenDistribution = True, returnIDs = False):
    '''Takes an item name and searches for it, returning a TUPLE formed as such ([list of itemIDs],
    [list of actual items]). Takes (INT minPrice, INT maxPrice, INT feedbackMinimum, BOOL topSellersOnly)
    Given that this method only produces a list, it is strongly suggested to use Find instead'''

    searchCount = 0
    r = []
    while len(r) == 0:
        searchCount = searchCount + 1
        if searchCount == 15:
            return None #This means the search failed; it shouldn't take more than 10 tries

        if evenDistribution:
            #categoryString = random.choice(categories.keys())
            #Weighted random ala http://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
            #Note it's inverted though; numbers get smaller as they're picked more, so I have the value dividing 100 (could be dividing any number)
            total = sum(100.0/i for i in picked.itervalues())
            ra = random.uniform(0, total)
            upto = 0
            for c, w in picked.iteritems():
                if upto + 100.0/w > ra:
                    categoryString = c
                    break
                upto += 100.0/w
        else:
            categoryString = random.choice(categories.keys())
        picked[categoryString] = picked[categoryString]+1
        global file
        cur = file.cursor()
        cur.execute("UPDATE categories SET picked=? WHERE category=?", (picked[categoryString], categoryString))
        file.commit()
        category = categories[categoryString]
        actualMaxPrice = str(int(float(maxPrice))) + ".00"
        actualMinPrice = str(int(float(minPrice))) + ".00"
        actualFeedbackMinimum = str(int(float(feedbackMinimum)))
        if topSellersOnly: actualTopSellersOnly = 'true'
        else: actualTopSellersOnly = 'false'

        #"outputSelector=SellerInfo&"+\ to get more detailed seller info

        url = findingUrl +\
            "?OPERATION-NAME=findItemsByCategory&" +\
            "SERVICE-VERSION=1.9.0&" +\
            "SECURITY-APPNAME="+appID +"&"\
            "RESPONSE-DATA-FORMAT=JSON&" +\
            "REST-PAYLOAD&" +\
            "outputSelector(0)=PictureURLSuperSize&"+\
            "categoryId="+category+"&" +\
            "itemFilter(0).name=AvailableTo&"+\
            "itemFilter(0).value=US&"+\
            "itemFilter(1).name=MaxPrice&" +\
            "itemFilter(1).value="+actualMaxPrice+"&" +\
            "itemFilter(1).paramName=Currency&" +\
            "itemFilter(1).paramValue=USD&" +\
            "itemFilter(2).name=TopRatedSellerOnly&" +\
            "itemFilter(2).value="+actualTopSellersOnly+"&" +\
            "itemFilter(3).name=FeedbackScoreMin"+\
            "itemFilter(3).value="+actualFeedbackMinimum+"&"+\
            "itemFilter(4).name=FreeShippingOnly&"+\
            "itemFilter(4).value=true&"+\
            "itemFilter(5).name=ListingType&"+\
            "itemFilter(5).value=AuctionWithBIN&"+\
            "itemFilter(6).name=MinPrice&"+\
            "itemFilter(6).value="+actualMinPrice+"&"\

        resp = urllib.urlopen(url)
        re = resp.read()
        val = json.loads(re)
        results = val['findItemsByCategoryResponse'][0]['searchResult'][0]
        del results['@count']
        if returnIDs:
            r2 = []
            for item in results:
                for i in results[item]:
                    r2.append(i)
                    format = str(i['itemId']).strip('[').strip(']').strip('u').strip("'")
                    r.append(format)
            final = (r, r2)
        else:
            for item in results:
                for i in results[item]:
                    r.append(i)
            final = r
    return final

def find(maxPrice, feedbackMinimum, enforceMinPrice = True, evenDistribution = True, topSellersOnly = False):
    m = float(maxPrice)
    if enforceMinPrice:
        minPrice = int((math.log(m, 6)/5.5)*m)
    else: minPrice = 0
    item = {}
    results = search(minPrice, maxPrice, feedbackMinimum, topSellersOnly, evenDistribution, False)
    if results == None:
        item['state']='fail'
        return item
    index = random.randint(0, len(results)-1) #Length of list is out of bounds, has to be length - 1
    picked = results[index]
    save(picked) #this keeps a record so the buyer doesn't have to
    item['state']='good'
    item['URL']=picked['viewItemURL'][0]
    item['imageURL']=picked.get('pictureURLSuperSize', ['Could not get supersize image'])[0]
    item['price']=picked['listingInfo'][0]['buyItNowPrice'][0]['__value__']
    item['ID']=picked['itemId'][0]
    item['base']=picked

    return item



