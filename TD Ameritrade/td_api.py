import time, urllib, requests, pandas as pd, yaml, re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse
from selenium.webdriver.chrome.service import Service

with open('C:/Users/samla/OneDrive/Documents/GitHub/slasker1/td_api_yml.yml', 'r') as f:
    doc = yaml.safe_load(f)

for word, val in doc.items():
    doc[word] = re.sub("[']+", "", str(val))


chrome_options = Options()
chrome_options.add_argument("--headless")

pd.set_option('display.max_columns', None)

# Define the Components for Authentication
username = doc['USER']
password = doc['WORD']
api_key = doc['TD_KEY']
client_code = api_key + '@AMER.OAUTHAP'
Acct_ID = doc['ACCT_ID']
Q1 = doc['Q1']
Q1_ANS = doc['Q1_ANS']
Q2 = doc['Q2']
Q2_ANS = doc['Q2_ANS']
Q3 = doc['Q3']
Q3_ANS = doc['Q3_ANS']
Q4 = doc['Q4']
Q4_ANS = doc['Q4_ANS']
# Define path to Web Driver
def auth():
    # Open a new browser
    s = Service(r'C:/Users/samla/OneDrive/Documents/GitHub/slasker1/chromedriver.exe')
    driver = webdriver.Chrome(service=s, options=chrome_options)
    # Define the components of request
    method = 'GET'
    url = 'https://auth.tdameritrade.com/auth?'
    # Define Payload, MAKE SURE TO HAVE THE CORRECT REDIRECT URI
    payload_auth = {'response_type': 'code', 'redirect_uri': 'http://localhost', 'client_id': client_code}
    built_url = requests.Request(method, url, params=payload_auth).prepare()
    # Go to the URL
    my_url = built_url.url
    driver.get(my_url)
    # Fill Out the Form
    payload_fill = {'username': username, 'password': password}
    driver.find_element('id','username0').send_keys(payload_fill['username'])
    driver.find_element('id','password1').send_keys(payload_fill['password'])
    driver.find_element('id','accept').click()
    time.sleep(1)
    # Get the Text Message Box
    driver.find_elements(By.XPATH,'/html/body/form/main/details/summary')[0].click()
    # Get the Answer Box
    driver.find_element(By.NAME,"init_secretquestion").click()
    # Answer the Security Questions.
    secret_question = driver.find_elements(By.XPATH, '//*[@id="authform"]/main/div[2]/p[2]')[0].text
    print(secret_question)
    if secret_question == Q1:
        driver.find_element(By.ID,'secretquestion0').send_keys(Q1_ANS)
    elif secret_question == Q2:
        driver.find_element(By.ID,'secretquestion0').send_keys(Q2_ANS)
    elif secret_question == Q3:
        driver.find_element(By.ID,'secretquestion0').send_keys(Q3_ANS)
    elif secret_question == Q4:
        driver.find_element(By.ID,'secretquestion0').send_keys(Q4_ANS)
    # Submit results
    driver.find_element(By.ID,'accept').click()
    # Sleep and click Accept Terms.
    time.sleep(1)

    #I do trust the device option button
    option = driver.find_elements(By.CLASS_NAME,"radio")[0]
    option.click()

    #Trust device Save button
    time.sleep(1)
    driver.find_element(By.ID,'accept').click()

    #ALLOW AUTHORIZATION FINAL BUTTON
    driver.find_element(By.ID,'accept').click()
    time.sleep(1)

    new_url = driver.current_url
    #print(new_url)
    parse_url = urllib.parse.unquote(new_url.split('code=')[1])

    driver.close()
    #print(parse_url)
    endpoint_url = r"https://api.tdameritrade.com/v1/oauth2/token"

    headers = {'Content-Type':"application/x-www-form-urlencoded"}

    payload_auth = {'grant_type':'authorization_code',
                    'access_type':'offline',
                    'code':parse_url,
                    'client_id':api_key,
                    'redirect_uri':'http://localhost'}

    authReply = requests.post(endpoint_url, headers = headers, data=payload_auth)

    decoded_content = authReply.json()
    #print(decoded_content)
    access_token = decoded_content['access_token']
    #print(access_token)
    print("Logged in and got access token successfully!")
    return access_token

def options(symbol,
            contractType='ALL',
            strikeCount=-1,
            includeQuotes=False,
            strategy='SINGLE',
            interval=None,
            strike=None,
            range='ALL',
            fromDate=None,
            toDate=None,
            volatility=None,
            underlyingPrice=None,
            interestRate=None,
            daysToExpiration=None,
            expMonth='ALL',
            optionType='ALL'):
    # THE QUOTES ENDPOINT
    # define an endpoint with a stock of your choice, MUST BE UPPER
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/chains"
    # define the payload
    payload = {'apikey': client_code,
               'symbol':symbol,
                'contractType':contractType,
                'strikeCount':strikeCount,
                'includeQuotes':includeQuotes,
                'strategy':strategy,
                'interval':interval,
                'strike':strike,
                'range':range,
                'fromDate':fromDate,
                'toDate':toDate,
                'volatility':volatility,
                'underlyingPrice':underlyingPrice,
                'interestRate':interestRate,
                'daysToExpiration':daysToExpiration,
                'expMonth':expMonth,
                'optionType':optionType}
    # make a request
    content = requests.get(url=endpoint, params=payload)
    # convert it dictionary object
    data = content.json()

    print(data)

    return data

def get_price(ticker):
    # THE QUOTES ENDPOINT
    # define an endpoint with a stock of your choice, MUST BE UPPER
    endpoint = r"https://api.tdameritrade.com/v1/marketdata/quotes"
    # define the payload
    payload = {'apikey': client_code,
               'symbol': ticker}
    # make a request
    content = requests.get(url=endpoint, params=payload)
    # convert it dictionary object
    data = content.json()

    price = data[ticker]['mark']

    return price

def trade(instruction, ticker, quantity, access_token):
    #access_token = auth()

    # Create Saved Order
    O_headers = {'Authorization': "Bearer {}".format(access_token),
                  "Content-Type": "application/json"}

    #test saved orders
    O_endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/savedorders".format(Acct_ID)
    #real order
    #O_endpoint = r"https://api.tdameritrade.com/v1/accounts/{}/orders".format(Acct_ID)

    # define the payload, in JSON format
    O_payload = {'orderType':'MARKET',
               'session':'NORMAL',
               'duration':'DAY',
               'orderStrategyType':'SINGLE',
               'orderLegCollection':[{'instruction':instruction,'quantity':quantity,'instrument':{'symbol':ticker,'assetType':'EQUITY'}}]}


    # make a post, NOTE WE'VE CHANGED DATA TO JSON AND ARE USING POST
    O_content = requests.post(url = O_endpoint, json = O_payload, headers = O_headers)

    # show the status code, we want 200

    price = get_price(ticker)

    #return O_content.status_code, price
    print(O_content.status_code)
    return price

#print(trade('Buy','AAPL',2))

def get_account_info(access_token):
    #access_token = auth()

    headers = {'Authorization': "Bearer {}".format(access_token)}

    accounts_endpoint = r"https://api.tdameritrade.com/v1/accounts/" + str(Acct_ID)

    payload = {'fields': 'positions'}

    # make a request
    content = requests.get(url = accounts_endpoint, headers = headers , params=payload)

    # convert it dictionary object
    data = content.json()

    initial_account_value = data["securitiesAccount"]["initialBalances"]["accountValue"]
    cash_available_to_trade = data["securitiesAccount"]["currentBalances"]["cashBalance"]
    total_equity = data["securitiesAccount"]["currentBalances"]["liquidationValue"]

    print("Today's Starting Value = " + str(initial_account_value))

    print("Cash = " + str(cash_available_to_trade))

    print("Current Liquidation Value = " + str(total_equity))

    try:
        positions = data["securitiesAccount"]["positions"]
        my_positions = pd.DataFrame(eval(str(positions)))
        my_positions = pd.concat([my_positions.drop(['instrument'], axis=1),
                                       my_positions['instrument'].apply(pd.Series)], axis=1)
    except:
        my_positions = pd.DataFrame([])
        print('You currently have no positions...')

    return my_positions, cash_available_to_trade, total_equity

get_account_info(auth())