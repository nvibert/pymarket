#!/usr/bin/env python3

# The shebang above is to tell the shell which interpreter to use. This make the file executable without "python3" in front of it (otherwise I had to use python3 pyvmc.py)
# I also had to change the permissions of the file to make it run. "chmod +x pyVMC.py" did the trick.
# I also added "export PATH="MY/PYVMC/DIRECTORY":$PATH" (otherwise I had to use ./pyvmc.y)

# PyMarket

"""

Welcome to PyMarket ! 

You can install python 3.8 from https://www.python.org/downloads/windows/ (Windows) or https://www.python.org/downloads/mac-osx/ (MacOs).

You can install the dependent python packages locally with:
pip3 install requests or pip3 install requests -t . --upgrade
pip3 install configparser or pip3 install configparser -t . --upgrade
pip3 install PTable or pip3 install PTable -t . --upgrade

"""

import requests                         # need this for Get/Post/Delete
import configparser                     # parsing config file
import sys
import json
from prettytable import PrettyTable

config = configparser.ConfigParser()
config.read("./config.ini")
strProdURL      = config.get("vmcConfig", "strProdURL")
strCSPProdURL   = config.get("vmcConfig", "strCSPProdURL")
Refresh_Token   = config.get("vmcConfig", "refresh_Token")
ORG_ID          = config.get("vmcConfig", "org_id")
SDDC_ID         = config.get("vmcConfig", "sddc_id")


def getAccessToken(myKey):
    """ Gets the Access Token using the Refresh Token """
    params = {'refreshToken': myKey}
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    response = requests.post('https://gtw.marketplace.cloud.vmware.com/api/v1/user/login', json=params, headers=headers)
    jsonResponse = response.json()
    access_token = jsonResponse['access_token']
    return access_token

def getSDDCCreds(tenantid, sessiontoken, sddc_id):
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + tenantid + "/sddcs/" + sddc_id
    response = requests.get(myURL, headers=myHeader)
    jsonResponse = response.json()
    sddc = jsonResponse['resource_config']
    sddc_username = sddc['cloud_username']
    sddc_password = sddc['cloud_password']
    sddc_url = sddc['vc_url']
    return [sddc_username,sddc_password,sddc_url]

def getSDDCName(sddc_id, sessiontoken):
    myHeader = {'csp-auth-token': sessiontoken}
    myURL = strProdURL + "/vmc/api/orgs/" + ORG_ID + "/sddcs/" + sddc_id
    response = requests.get(myURL, headers=myHeader)
    mySDDC = response.json()
    sddc_name = mySDDC['name']
    return sddc_name
    
def subscribe(productid,version,token,org,sddc,user,password,vc_url,sddc_name,cl_name):
    myHeader = {'csp-auth-token': token, 'content-type': 'application/json', 'accept': 'application/json'}
    body = {
    "deployParams": {
    "consumercsporgid" : org,
    "selected_datastore": {
      "datastore": "datastore-48",
      "name":"WorkloadDatastore",
      "type":"VSAN"
    },
    "selectedSddc": {
      "sddc_id": sddc,
      "name":sddc_name,
      "provider":"AWS",
      #"region":"US West (Oregon)",
      "cloud_username": user,
      "sddc_type":"1NODE",
      "vc_url":vc_url
    },
    "deploymentPlatform": "VMC",
    "productversion": version,
    "productsList": [
      {
        "productid": product_id,
        "appversion": version,
        "eulaaccepted": True,
        "autoupdate": False,
        "maxversions": "0"
      }
    ],
    "cloud_username": user,
    "cloud_password": password,
    "eulaAccepted": True,
    "contentlibname": cl_name + "---" + version
  }
}   
    myURL = "https://gtw.marketplace.cloud.vmware.com/api/v1/subscriptions/vmc"
    response = requests.post(myURL, json=body, headers=myHeader)
    jsonResponse = response.json()
    jR = jsonResponse['response']
    message = jR['message']
    lastJSONResponse = f'API Call Status {response.status_code}, text:{response.text}'
    if response.status_code == 200:
        print()
    elif response.status_code == 201:
        jR = jsonResponse['response']
        message = jR['message']
        print(message + ": the product image has been added to the Content Library " + cl_name + "---" + version + ".")
    else:
        jsonResponse = ""
        lastJSONResponse = f'API Call Status {response.status_code}, text:{response.text}'
        print(lastJSONResponse)

def getProduct(token,id):
    myHeader = {'content-type': 'application/json', 'accept': 'application/json'}
    myURL = "https://gtw.marketplace.cloud.vmware.com/api/v1/products/" + id
    response = requests.get(myURL, headers=myHeader)
    try:
        jsonResponse = response.json()
        jR = jsonResponse['response']
        jRd = jR['data']
        d_n = jRd['displayname']
        return(d_n)
    except:
        print("Incorrect product id.")
    return

def searchProducts(token,name):
    params = {
    "textsearch":name,
    }
    myHeader = {'content-type': 'application/json', 'accept': 'application/json'}
    myURL = "https://gtw.marketplace.cloud.vmware.com/api/v1/products/search"
    response = requests.get(myURL, headers=myHeader, params=params)
    jsonResponse = response.json()
    ed = jsonResponse['response']
    ed_data_list = ed['dataList']
    table = PrettyTable(['Product Name', 'ID', 'Solution Type', 'Latest version'])
    for i in ed_data_list:
        try:
            latest_version = i['allversiondetailsList'][0]
        except:
            latest_version = {'versionnumber':"N/A"}
        table.add_row([i['displayname'],i['productid'],i['solutiontype'], latest_version['versionnumber']])  
    print(table)
    return

# --------------------------------------------
# ---------------- Main ----------------------
# --------------------------------------------

if len(sys.argv) > 1:
    intent_name = sys.argv[1].lower()
else:
    intent_name = ""

st = getAccessToken(Refresh_Token)


if intent_name == "get-token":
    print(st)
elif intent_name == "get-credentials":
    print(getSDDCCreds(ORG_ID,st,SDDC_ID))
elif intent_name == "get-sddc-name":
    print(getSDDCName(SDDC_ID,st))
elif intent_name == "search-product":
    product = sys.argv[2]
    searchProducts(st,product)
elif intent_name == "subscribe":
    product_id = sys.argv[2]
    version = sys.argv[3]
    sddc_creds=getSDDCCreds(ORG_ID,st,SDDC_ID)
    user = sddc_creds[0]
    password = sddc_creds[1]
    vc_url = sddc_creds[2]
    sddc_name = getSDDCName(SDDC_ID,st)
    cl_name = getProduct(st,product_id)
    subscribe(product_id,version,st,ORG_ID,SDDC_ID,user,password,vc_url,sddc_name,cl_name)
else:
    print("\nWelcome to PyMarket !")
    print("\nTo search for a product:")
    print("\tsearch-product [product_name]")
    print("\nTo subscribe to a product:")
    print("\tsubscribe [product-id] [version]")
