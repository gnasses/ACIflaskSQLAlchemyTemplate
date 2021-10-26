import acitoolkit.acitoolkit as aci
import sys
import re
from prettytable import PrettyTable

apic_ip = '10.10.20.14'
apic_username = 'admin'
apic_password = 'C1sco12345'
apic_url = 'https://' + apic_ip


session = aci.Session(apic_url, apic_username, apic_password)
resp = session.login()

if not resp.ok:
    print("ERROR: Could not login into APIC: %s" % apic_ip)
    sys.exit(0)
else:
    print("SUCCESS: Logged into APIC: %s" % apic_ip)

endpoints = aci.Endpoint.get(session)
table_data = []


for endpoint in endpoints:
    if endpoint.if_dn:
        for dn in endpoint.if_dn:
            match = re.match('protpaths-(\d+)-(\d+)', dn.split('/')[2])
            if match:
                if match.group(1) and match.group(2):
                    interface = "Nodes: " + match.group(1) + "-" + match.group(2) + " " + endpoint.if_name
    else:
        interface = endpoint.if_name

    table_row = { "MAC": endpoint.mac, "IP": endpoint.ip, "INT": interface}
    table_data.append(table_row)


table = PrettyTable()
table.field_names = ['IP Address','MAC Address',"Interface"]
for row in table_data:
#    table.add_row([row['IP'],row['MAC'],row['INT']])
    print(row['MAC'])
#print(table)