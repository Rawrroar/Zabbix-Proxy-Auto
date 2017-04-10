#!/usr/bin/env python

from pyzabbix import ZabbixAPI

myusername = input("Username: ")
mypassword = input("Password: ")

# Create ZabbixAPI class instance
zapi = ZabbixAPI(url='http://zabbix.com', user=myusername, password=mypassword)

done = False


# Collect configuration information
while not done:
    proxyName = input("Please enter school number and name, eg 1234-Test High School: ")
    ipDisc = input("Please enter an IP range in the following format: 192.168.0.1/24 : ")
    print("Please review the following: \nProxy Name= ",proxyName, "\n Subnet= ",ipDisc)
    user_input = input(" is this correct? Y/N: ")
    if user_input.upper() == "Y":
        done = True

# Create Proxy
zabbixproxy = zapi.proxy.create(host=proxyName, status='5')

# Get proxy ID
proxyidget = zapi.do_request('proxy.get',
                          {
                              'filter': {'host': proxyName},
                              'output': 'proxyid'
                          })
proxyID = [host['proxyid'] for host in proxyidget['result']]

#Convert the JSON output from list to string, this is so there are no [] at the beggining and end of proxy_hostid kpv in the discovery rule creation
proxyiddata = ''.join(proxyID)


# Create Discovery Rule
zabbixdrule = zapi.do_request('drule.create',
                          {
                              'name': proxyName + ' Discovery Rule',
                              'iprange': '127.0.0.1,' + ipDisc,
                              'proxy_hostid': proxyiddata,
                              'dchecks': [
                                {
                                    'type': '11',
                                    'snmp_community': 'public',
                                    'key_': 'SNMPv2-MIB::sysName.0',
                                    'uniq': '1',
                                    'ports': '161'
                                },
                                {
                                    'type': '9',
                                    'key_': 'system.uname',
                                    'uniq': '0',
                                    'ports': '10050'
                                }
                              ]
                          })

# Create Host Group
zabbixhostgroup = zapi.hostgroup.create(name=proxyName + ' Host Group')

# Get the host group ID
hostgroupidget = zapi.do_request('hostgroup.get',
                          {
                              'filter': {'name': proxyName + ' Host Group'},
                              'output': 'groupid'
                          })
hostgroupID = [host['groupid'] for host in hostgroupidget['result']]


#Convert the JSON output from list to string, this is so there are no [] at the beggining and end of groupid kpv in the action rule creation
zabbixgroupid = ''.join(hostgroupID)


# Create action rule based on discovery
zabbixactrule = zapi.do_request('action.create',
                          {
                              'name': proxyName + ' Action Rule',
                              'eventsource': 1,
                              'status': 0,
                              'esc_period': 0,
                              'filter': {
                                  'evaltype': 0,
                                  'conditions': [
                                    {
                                        'conditiontype': '21',
                                        'value': '1'
                                    },
                                    {
                                        'conditiontype': '10',
                                        'value': '2'
                                    },
                                    {
                                        'conditiontype': '10',
                                        'value': '0'
                                    },
                                    {
                                        'conditiontype': '20',
                                        'value': proxyiddata
                                    },
                              ]
                          },
                          'operations': [
                              {
                                  'esc_step_from': 1,
                                  'esc_period': 0,
                                  'opgroup': [
                                      {
                                          'groupid': zabbixgroupid
                                      }
                                  ],
                                  'operationtype': 4,
                                  'esc_step_to': 1
                            }
                          ]
                      })


print("Complete")






