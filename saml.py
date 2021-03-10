from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import requests
import time
import json
from browsermobproxy import Server
import os
from datetime import date

browsermob_binary_path = "./bmproxy/bin/browsermob-proxy"

# Kills existing bm-proxy connections
os.system("killall java")

initVal = input('Is this the first run?\n')

def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver

def hdrFinder(dct):
    for i in range(len(dct)):
        for hdr in dct[i]['request']['headers']:
            if "dea-CSRFToken" in hdr['name']:
                csrf = str(hdr['value'])
                # print(csrf)
                return csrf

headers = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'dea-CSRFToken': '17b02bad-30fe-4d29-8646-7e02c720e5ff',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4273.0 Safari/537.36',
    'Content-Type': 'application/json; charset=UTF-8',
    'Origin': 'https://reserve.rit.edu',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://reserve.rit.edu/RoomRequest.aspx?data=ity3Dem%2byxxGFZTQvNr97yLU%2byk57qiz',
    'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

data = '{"templateId":2,"filterData":{"filters":[{"filterName":"Locations","value":"6","displayValue":"Wallace Library Study Rooms (005SR)","filterType":8},{"filterName":"SetupTypes","value":"45","displayValue":"Physical Distance Capacity","filterType":7},{"filterName":"Features","value":"","displayValue":"(none)","filterType":7},{"filterName":"Capacity","value":1,"filterType":2},{"filterName":"StartDate","value":"REPLACE_ME 00:00:00","displayValue":null,"filterType":3},{"filterName":"EndDate","value":"REPLACE_ME 23:59:59","filterType":3,"displayValue":null},{"filterName":"TimeZone","value":61,"displayValue":"Mountain Time","filterType":2},{"filterName":"Rooms","value":"302,303,304,305,306,317,318,319,322,323,324,325,326,337,338,339,340,341,342,343,344,345","displayValue":null,"filterType":7}]}}'
options = Options()
options.headless = False

if initVal == "y" or initVal == "Y":
    server = Server(browsermob_binary_path)
    server.start()
    proxy = server.create_proxy()
    proxy.new_har('capture', options={'captureHeaders': True})

    print(proxy.proxy)
    options.add_argument('--proxy-server=%s' % proxy.proxy)
    options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome('./chromedriver', options=options)

else:
    driver = create_driver_session('14927ed67f0662b2097553358846cee0', 'http://127.0.0.1:58807')
    server = Server(browsermob_binary_path)
    server.start()
    proxy = server.create_proxy()
    proxy.new_har('capture', options={'captureHeaders': True})
    print(proxy.proxy)


executor_url = driver.command_executor._url
session_id = driver.session_id

print(executor_url, session_id)

driver.get('https://mycourses.rit.edu/Shibboleth.sso/Login?entityID=https://shibboleth.main.ad.rit.edu/idp/shibboleth&target=https%3A%2F%2Fmycourses.rit.edu%2Fd2l%2FshibbolethSSO%2Flogin.d2l')

time.sleep(2)

if driver.current_url != "https://mycourses.rit.edu/d2l/home":
    # Use Vault
    driver.find_element_by_id('username').send_keys("")
    driver.find_element_by_id('password').send_keys("")
    time.sleep(1)
    l = driver.find_element_by_name("_eventId_proceed")
    l.click()

    time.sleep(4)

    if driver.current_url == "https://shibboleth.main.ad.rit.edu/idp/profile/SAML2/Redirect/SSO?execution=e1s2":
        iframe = driver.find_element_by_xpath("//iframe[@id='duo_iframe']")
        driver.switch_to.frame(iframe)

        try:
            driver.find_element_by_name("dampen_choice").click()
        except Exception as e:
            print(e)

        try:
            driver.find_element_by_xpath(".//*[contains(text(), 'Send Me a Push')]").click()
        except Exception as e:
            print(e)
        driver.switch_to.default_content()
        time.sleep(10)

driver.get('https://reserve.rit.edu/Default.aspx')

try:
    if driver.find_element_by_xpath(".//*[contains(text(), 'RIT Login')]"):
        driver.find_element_by_xpath(".//*[contains(text(), 'RIT Login')]").click()
        window_name = driver.window_handles[1]
        driver.switch_to.window(window_name=window_name)
        time.sleep(2)
        driver.close()

        window_name = driver.window_handles[0]
        driver.switch_to.window(window_name=window_name)

except Exception as e:
    pass

driver.get('https://reserve.rit.edu/Default.aspx')

time.sleep(2)

driver.find_element_by_id('rit-create-reservation-btn').click()
driver.get('https://reserve.rit.edu/RoomRequest.aspx?data=ity3Dem%2byxxGFZTQvNr97yLU%2byk57qiz')
driver.find_element_by_xpath(".//button[contains(text(), 'Search')]").click()

session = requests.Session()
cookies = driver.get_cookies()

for cookie in cookies: 
    session.cookies.set(cookie['name'], cookie['value'])

harDict = proxy.har['log']['entries']
dea = hdrFinder(harDict)

headers['dea-CSRFToken'] = dea

# Accepted Format: 2021-02-26
today = date.today()
d1 = today.strftime("%Y-%m-%d")
data = data.replace("REPLACE_ME",str(d1))

response = session.post('https://reserve.rit.edu/ServerApi.aspx/GetBrowseLocationsBookingsForRoomRequest', headers=headers, data=data)
with open('init.json', 'w') as wrt:
    wrt.write(str(response.content))

server.stop()
os.system("killall java")