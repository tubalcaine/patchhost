import requests
import json

# This is here ONLY to suppress self-signed certificate warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# End of warning supression

bf_server = "10.10.220.247:52311"
bf_username = "HCLAdmin"
bf_password = "BigFix!123"

#sourcedAction = '''
#<?xml version="1.0" encoding="UTF-8" ?>
# For those qho attended the webinar, the lines above were what was broken in
# the demo code. When you look below you will note a backslash at the end of the
# triple quote. That prevents a newline from being included in the string. That
# newline was the problem! I literally could not see that I managed to delete the
# backslash at some point. This would also work:
#
#sourcedAction = '''<?xml version="1.0" encoding="UTF-8" ?>
#
# The point is, BigFix wants to see the XML tag **first** and nothing else.
# So here is the code, with explanation! It works properly.

sourcedAction = '''\
<?xml version="1.0" encoding="UTF-8" ?>
<BES xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" >
<SourcedFixletAction>
	<SourceFixlet>
		<Sitename>Enterprise Security</Sitename>
		<FixletID>48001</FixletID>
		<Action>Action1</Action>
	</SourceFixlet>
	<Target>
		<ComputerName>BF2LABROOT</ComputerName>
	</Target>
	<Settings>
	</Settings>
	<Title>Programmatic Action</Title>
</SourcedFixletAction>
</BES>
'''

session = requests.Session()
session.auth = (bf_username, bf_password)
response = session.get("https://" + bf_server + "/api/login", verify=False)

qheader = {
	'Content-Type' : 'application/x-www-form-urlencoded'
}

req = requests.Request('POST'
	, "https://" + bf_server + "/api/actions"
	, headers=qheader
	, data=sourcedAction
)

prepped = session.prepare_request(req)
	
result = session.send(prepped, verify = False)

if (result.status_code == 200):
	print(result.text)  # Again, for webinar attendees:
	# The line above will print out the result on success. Here is what that might look like:
	# <?xml version="1.0" encoding="UTF-8"?>
	#<BESAPI xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="BESAPI.xsd">
    #    <Action Resource="https://10.10.220.247:52311/api/action/64" LastModified="Thu, 15 Oct 2020 18:19:39 +0000">
    #            <Name>Programmatic Action</Name>
    #            <ID>64</ID>
    #    </Action>
	#</BESAPI>
	#
	# The ID is the action ID, which you could use in a GET url for the status, for example:
	#
	# https://10.10.220.247:52311/api/action/64/status
	#
	# Here's what that looks like:
	#<BESAPI xsi:noNamespaceSchemaLocation="BESAPI.xsd">
	#<ActionResults Resource="https://10.10.220.247:52311/api/action/64/status">
	#	<ActionID>64</ActionID>
	#	<Status>Open</Status>
	#	<DateIssued>Thu, 15 Oct 2020 18:19:40 +0000</DateIssued>
	#	<Computer ID="11394379" Name="BF2LABROOT">
	#		<Status>The action failed.</Status>
	#		<State IsError="0">4</State>
	#		<ExitCode>3010</ExitCode>
	#		<ApplyCount>1</ApplyCount>
	#		<RetryCount>1</RetryCount>
	#		<LineNumber>4</LineNumber>
	#		<StartTime>Thu, 15 Oct 2020 18:20:03 +0000</StartTime>
	#		<EndTime>Thu, 15 Oct 2020 18:20:53 +0000</EndTime>
	#	</Computer>
	#</ActionResults>
	#</BESAPI>
else:
	print("Fixlet POST failed.")
	print(result)
	