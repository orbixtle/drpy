import requests
from imapclient import IMAPClient
import xml.etree.ElementTree as ET
from imapclient.exceptions import LoginError

def get_autoconfig(email_domain):
    url = f"https://autoconfig.thunderbird.net/v1.1/{email_domain}"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.text)
            imap_settings = {}
            for server in root.findall(".//incomingServer[@type='imap']"):
                imap_settings['hostname'] = server.find('hostname').text
                imap_settings['port'] = int(server.find('port').text)
                imap_settings['socketType'] = server.find('socketType').text
                imap_settings['authentication'] = server.find('authentication').text
                imap_settings['username'] = server.find('username').text
                return imap_settings
        except ET.ParseError:
            print(f"Error: Response content is not valid XML:\n{response.text}")
    else:
        print(f"Error: Received status code {response.status_code} from auto-config server.")
    raise Exception("Auto-config not available for this domain.")

email = "email@domain.com"
password = "password"
domain = email.split('@')[1]

imap_settings = get_autoconfig(domain)

server = imap_settings['hostname']
port = imap_settings['port']
ssl = imap_settings['socketType'] == 'SSL'

try:
    with IMAPClient(server, port=port, ssl=ssl) as client:
        client.login(email, password)
        print("Connected and authenticated successfully.")
except LoginError as e:
    print(f"Login failed: {e}")
