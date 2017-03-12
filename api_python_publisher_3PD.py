'''
This is an example intended to show how to access the Lotame DMP Administrative ReST API.
We mostly use simple classes available in the Python 2.7x distro for simplicity, with the
exception of the Requests package to make ReST requests (in particular DETETE and PUT)
easier.  You can install it with "pip install requests" or "easy_install requests"

There may be more efficient ways to parse the JSON, especially using other
libraries, but that is not the focus of the example.

This example also does not include any error handling - You should
make sure that you do include error handling with any code, but especially
when working with an external API!
'''

# Set up the libs we need
import requests
import sys
import csv
import os
import json
from ConfigParser import SafeConfigParser   # used to get information from a config file
from datetime import datetime

reload(sys)
sys.setdefaultencoding('utf-8')
'''
Now let's get what we need from our config file, including the username and password

We are assuming we have a config file called config.config in the same directory
where this python script is run, where the config file looks like:

[api_samples]
authentication_url = https://crowdcontrol.lotame.com/auth/v1/tickets
api_url = https://api.lotame.com/2/
username = USERNAME_FOR_API_CALLS
password = PASSWORD

'''
# Set up our Parser and get the values - usernames and password should never be in code!
parser = SafeConfigParser()
parser.read('config.cfg')
username = parser.get('api_samples', 'username')
password = parser.get('api_samples', 'password')
authentication_url = parser.get('api_samples', 'authentication_url')
base_api_url = parser.get('api_samples', 'api_url')

# OK, all set with our parameters, let's get ready to make our call to get a Ticket Granting Ticket
# Add the username and password to the payload (requests encodes for us, no need to urlencode)
payload = {'username': username,
           'password': password}

# We want to set some headers since we are going to post some url encoded params.
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }

# Now, let's make our Ticket Granting Ticket request.  We get the location from the response header
tg_ticket_location = requests.post(authentication_url, data=payload).headers['location']

# Let's take a look at what a Ticket Granting Ticket looks like:
# print ('Ticket Granting Ticket - %s \n') % (tg_ticket_location[tg_ticket_location.rfind('/') + 1:])

# Now we have our Ticket Granting Ticket, we can get a service ticket for the service we want to call
# The first service call will be to get information on behavior id 5990.
# service_call = base_api_url + 'behaviors/5990'

# Add the service call to the payload and get the ticket
#payload = {'service': service_call}
#service_ticket = requests.post( tg_ticket_location, data=payload ).text

# Let's take a look at the service ticket
#print ('Here is our Service Ticket - %s \n') % ( service_ticket )

'''
Now let's make our call to the service ... remember we need to be quick about it because
we only have 10 seconds to do it before the Service Ticket expires.

A couple of things to note:

JSON is the default response, and it is what we want, so we don't need to specify
like {'Accept':'application/json'}, but we will anyway because it is a good practice.

We don't need to pass any parameters to this call, so we just add the parameter
notation and then 'ticket=[The Service Ticet]'
'''

headers = {'Accept':'application/json'}

#behavior_info = requests.get( ('%s?ticket=%s') % (service_call, service_ticket), headers=headers)

# Let's print out our JSON to see what it looks like
# requests support JSON on it's own, so not other package needed for this
# print ('Behavior Information: \n %s \n') % (behavior_info.json() )

'''
Now let's get the names and IDs of some audiences

We can reuse our Ticket Granting Ticket for a 3 hour period ( we haven't passed that yet),
so let's use it to get a service ticket for the audiences service call.

Note that here we do have a parameter that is part of the call.  That needs to be included
in the Service Ticket request.

We plan to make a call to the audience service to get the first 10 audiences in the system
ascending by audience id.  We don't need to pass the sort order, because it defaults to ascending
'''

# Set up our call and get our new Service Ticket, we plan to sort by id


# Please insert audiences ID below:

#audienceids = ['242509','242508','243787','243791','243789','243786','243790','243788','245165','243625','243626','257995']
dirs = os.path.join( os.path.dirname(__file__),'../reports/')
f = open(dirs+datetime.now().date().isoformat()+'_3PD.csv',  'w+')
title_str = ('publisherName,3PDContribution,audienceId,audienceName')
print >> f,(title_str)
for a in open("audience.csv"):
    audience_id = a.strip()
    service_call = base_api_url + 'reports/audiences/' + audience_id + '/publisher?stat_interval=LAST_MONTH&page_count=999&page_num=1&sort_attr=audienceName&inc_network=false&sort_order=ASC'
    payload = {'service': service_call}

# Let's get the new Service Ticket, we can print it again to see it is a new ticket
    service_ticket = requests.post( tg_ticket_location, data=payload ).text
#print ('Here is our new Service Ticket - %s \n') % ( service_ticket )

# Use the new ticket to query the service, remember we did have a parameter this time,
# so we need to & 'ticket=[The Service Ticket]' to the parameter list
    audience_list = requests.get( ('%s&ticket=%s') % (service_call, service_ticket)).json()
#print audience_list
# create an array to hold the audiences, pull ou the details we want, and print it out

    audiences = []
    for ln in audience_list['stats']:
        audiences.append({'audienceId': ln['audienceId'], 'audienceName': ln['audienceName'], 'Client Name': ln['publisherName'], '3PD % Contribution': ln['percentOfAudience']})

        for ii in range( 0, len(audiences) ):
            data = audiences[ii]
            data_str = json.dumps(data)
            result = data_str.replace("\"","")
            result1 = result.replace("3PD % Contribution:","")
            result2 = result1.replace("{Client Name: ","")
            result3 = result2.replace("audienceName: ","")
            result4 = result3.replace("audienceId: ","")
            result5 = result4.replace("}","")

        print >> f,(result5)


    service_call = base_api_url + 'reports/audiences/' + audience_id + '/behaviors/contributing?stat_interval=LAST_MONTH&page_count=999&page_num=1&sort_attr=percentOfAudience&sort_order=DESC'
    payload = {'service': service_call}
    
    # Let's get the new Service Ticket, we can print it again to see it is a new ticket
    service_ticket = requests.post( tg_ticket_location, data=payload ).text
    #print ('Here is our new Service Ticket - %s \n') % ( service_ticket )
    
    # Use the new ticket to query the service, remember we did have a parameter this time,
    # so we need to & 'ticket=[The Service Ticket]' to the parameter list
    audience_list = requests.get( ('%s&ticket=%s') % (service_call, service_ticket)).json()
    #print audience_list
    # create an array to hold the audiences, pull ou the details we want, and print it out
    
    audiences = []
    for ln in audience_list['stats']:
        audiences.append({'audienceId': ln['audienceId'], 'audienceName': ln['audienceName'], 'Client Name': ln['source'], '3PD % Contribution': ln['percentOfAudience']})
        
        for ii in range( 0, len(audiences) ):
            data = audiences[ii]
            data_str = json.dumps(data)
            result = data_str.replace("\"","")
            result1 = result.replace("3PD % Contribution:","")
            result2 = result1.replace("{Client Name: ","")
            result3 = result2.replace("audienceName: ","")
            result4 = result3.replace("audienceId: ","")
            result5 = result4.replace("}","")
        
        print >> f,(result5)


# Once we are done with the Ticket Granting Ticket we should clean it up'
remove_tgt = requests.delete( tg_ticket_location )
print ( 'Status for closing TGT - %s') % (remove_tgt.status_code)
print ('YAY! Gotcha!!--/reports/'+datetime.now().date().isoformat()+'_3PD.csv')
