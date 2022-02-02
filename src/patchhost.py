import requests
import json
import argparse
import sys

# This is here ONLY to suppress self-signed certificate warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# End of warning supression
# This is here ONLY to suppress self-signed certoficate warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# End of warning supression

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--bfserver"
	, help="address and port of BigFix server"
	, nargs='?'
	, default="10.10.220.60:52311" 
	)
parser.add_argument("-u", "--bfuser"
	, help="BigFix REST API Username"
	, nargs='?'
	, default="IEMAdmin" 
	)
parser.add_argument("-p", "--bfpass"
	, help="BigFix REST API Password"
	, default="BigFix!123"
	)
parser.add_argument("-e", "--endpoint"
	, help="BigFix endpoint name"
	, required=True
	)

args = parser.parse_args()


sourcedAction = '''\

'''

query = f'''\
(id of it, name of it, (id of it, name of it) of site of it, content id of default action of it) \
	of relevant fixlets \
	whose (exists name whose (it as lowercase contains "patch") of site of it and \
	fixlet flag of it and \
	exists default action of it) \
	of bes computers whose (name of it as lowercase = "{args.endpoint}" as lowercase)\
'''

print(query)

session = requests.Session();
session.auth = (args.bfuser, args.bfpass)
response = session.get(f"https://{args.bfserver}/api/login", verify=False);

qheader = {
	'Content-Type' : 'application/x-www-form-urlencoded'
}

qquery = {
	"relevance" : query,
	"output"    : "json"
}

req = requests.Request('POST'
	, f"https://{args.bfserver}/api/query"
	, headers=qheader
	, data=qquery
)

prepped = session.prepare_request(req)

result = session.send(prepped, verify = False)

if result.status_code != 200:
	print(f"The query:\n{query}\n\nReturned an unsuccessful status of {result.status_code}\n")
	print(f"Result: {result}")
	print(f"Reason: {result.reason}")
	print(f"Error:  {result.text}")
	sys.exit(1)

qheader = {
	'Content-Type' : 'application/x-www-form-urlencoded'
}

fixlets = json.loads(result.text)

for fixlet in fixlets['result']:
	sourcedAction = f'''\
<?xml version="1.0" encoding="UTF-8" ?>
<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >
<SourcedFixletAction>
	<SourceFixlet>
		<Sitename>{fixlet[2][1]}</Sitename>
		<FixletID>{fixlet[0]}</FixletID>
		<Action>{fixlet[3]}</Action>
	</SourceFixlet>
	<Target>
		<ComputerName>{args.endpoint}</ComputerName>
	</Target>
	<Settings>
	</Settings>
	<Title>patchhost - ({fixlet[0]}) {fixlet[1]}</Title>
</SourcedFixletAction>
</BES>'''

	req = requests.Request('POST'
		, f"https://{args.bfserver}/api/actions"
		, headers=qheader
		, data=sourcedAction
	)

	prepped = session.prepare_request(req)
	
	result = session.send(prepped, verify = False)

	if (result.status_code == 200):
		print(result.text)  
	else:
		print("Fixlet POST failed.")
		print(f"Result: {result}")
		print(f"Reason: {result.reason}")
		print(f"Error:  {result.text}")
		sys.exit(1)


print("\nSuccessful termination")
