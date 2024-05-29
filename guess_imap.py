import dns.resolver
from imapclient import IMAPClient
from imapclient.exceptions import LoginError

def get_mx_record(domain):
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        mx_record = str(answers[0].exchange).rstrip('.')
        return mx_record
    except Exception as e:
        print(f"Failed to get MX record for {domain}: {e}")
        return None

def extract_server_domain(mx_record):
    parts = mx_record.split('.')
    return '.'.join(parts[-2:])

def check_imap_access(email, password, server):
    try:
        with IMAPClient(server, port=993, ssl=True, timeout=3) as client:
            client.login(email, password)
            return True
    except (LoginError, Exception):
        return False

def try_imap_servers(email, password, server_domain):
    subdomains = ["imap.", "mail."]
    for subdomain in subdomains:
        server = f"{subdomain}{server_domain}"
        if check_imap_access(email, password, server):
            print(f"Successful connection to {server}")
            return server
    return None

def check_email_access(email, password):
    domain = email.split('@')[-1]
    mx_record = get_mx_record(domain)
    if mx_record:
        server_domain = extract_server_domain(mx_record)
        server = try_imap_servers(email, password, server_domain)
        if server:
            return (1, f"{server}:993:{email}:{password}")
    return (0, None)

# Example usage:
email = "email@domain.com"
password = "password"
status, result = check_email_access(email, password)
print(f"Status: {status}, Result: {result}")
