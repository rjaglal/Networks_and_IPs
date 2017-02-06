# Networks_and_IPs

Assumptions:
1. Linux enviroment
2. Python 3.5+
3. User account with public key authentication

Description:
1. Consumes a list of servers via stdin. 
2. Locate all networks on the servers via ssh and running 'ifconfig -a'
3. Output all networks with a list of respective ip addresses.
