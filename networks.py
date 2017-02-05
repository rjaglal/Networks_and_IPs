import subprocess
import pprint


# Obtains subnet mask prefix length.
# Example takes 255.255.255.0 --> /24
def subnet_mask_to_slash_network(subnet_ip):

    ones = 0

    for num in subnet_ip.split('.'):
        one_zero = str(bin(int(num)))
        ones += one_zero.count('1')

    return ones


# Takes in the ip address and subnet mask and calculates the network address
def cal_network_address(ip_address="0.0.0.0", subnet_mask="0.0.0.0"):

    ip_address_list = ip_address.split('.')
    subnet_mask_list = subnet_mask.split('.')

    network_address_list = []

    for i in range(0, 4):
        logical_and = int(ip_address_list[i]) & int(subnet_mask_list[i])
        network_address_list.append(logical_and)

    network_address = '.'.join(str(x) for x in network_address_list)
    return network_address


# Takes in the ip address and subnet mask and outputs network address with subnet prefix
def find_network_address(ipaddress="0.0.0.0", subnet_mask="0.0.0.0"):

    subnet_number = subnet_mask_to_slash_network(subnet_mask)
    network_address = cal_network_address(ipaddress, subnet_mask)
    network_val = str(network_address) + "/" + str(subnet_number)

    return network_val


# Assume list of hosts from command line
def read_list_of_servers():
    print("Please enter list of servers: ")
    server_names = str(input())
    list_of_servers = server_names.split()
    return list_of_servers


def create_server_dict(servers):
    server_dict = {}

    for i in servers:
        server_dict[i] = {}
    return server_dict


# Parse data from a single server's ifconfig -a
# for interfaces, ip address, broadcast, and subnet mask
# TODO: Improve validation on incoming data
def strip_out_interfaces_and_details(data):
    # Every 9 lines there is a new Interface information
    interface_dict = {}

    data = data.split('\n')

    for i in range(0, len(data), 9):
        # Interface on the "9th" line
        if not data[i]:
            break
        interface = data[i].split()[0]
        # Interface info on "9th + 1" line
        info = data[i + 1].split()

        ip_address = ""
        broadcast = ""
        subnet_mask = ""

        # Extracting information
        for item in info:
            if "addr" in item:
                ip_address = item.split(':')[1]

            if "Bcast" in item:
                broadcast = item.split(':')[1]

            if "Mask" in item:
                subnet_mask = item.split(':')[1]

        interface_dict[interface] = {}
        interface_dict[interface]['ipaddress'] = ip_address
        interface_dict[interface]['broadcast'] = broadcast
        interface_dict[interface]['subnet_mask'] = subnet_mask
        interface_dict[interface]['network'] = find_network_address(ip_address,
                                                                    subnet_mask)

    return interface_dict


# Gathers all networks address with its respective ip address in a list
def get_all_networks_and_its_ips(server_dict):

    network_dict = {}

    for server in server_dict:
        for interface in server_dict[server]:

            network_address = server_dict[server][interface]['network']

            if network_address in network_dict:
                network_dict[network_address].append(server_dict[server][interface]['ipaddress'])
            else:
                network_dict[network_address] = []
                network_dict[network_address].append(server_dict[server][interface]['ipaddress'])

    return network_dict


# Default ssh function to get all interfaces on a single server
def run_ssh_command(server):
    user = 'observer'
    command = "ifconfig -a"

    ssh = subprocess.Popen(["ssh", "%s@%s" % (user, server), command],
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)

    data, error = ssh.communicate()

    return data


# Takes in a list of ip address and arranges the list in ascending order.
def sort_list_of_ips(list_ips):

    # Testing; list_ips = ['172.12.34.243', '172.12.12.334', '172.12.23.32']

    for i in range(len(list_ips)):
        list_ips[i] = "%3s.%3s.%3s.%3s" % tuple(list_ips[i].split("."))
    list_ips.sort()

    for i in range(len(list_ips)):
        list_ips[i] = list_ips[i].replace(" ", "")

    return list_ips

if __name__ == '__main__':

    # Data entry maybe in multiple ways. Obtain the list form stdin
    # Example: "server1.example.com server2.example.com server3.example.com"

    server_list = []
    server_list = read_list_of_servers()

    # Testing
    #server_list = ['server1.example.com', 'server3.example.com', 'server2.example.com']

    main_dict = {}
    main_dict = create_server_dict(server_list)

    # Testing
    #print(main_dict)

    # Data gathering and updating main_dict
    for machine in main_dict:

        machine_data = run_ssh_command(machine)
        main_dict[machine] = strip_out_interfaces_and_details(machine_data)

    # Testing
    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(main_dict)

    # Find all networks and their ip addresses
    network_dict = {}
    network_dict = get_all_networks_and_its_ips(main_dict)

    # Testing
    #print(network_dict)

    for network in network_dict:
        network_dict[network] = sort_list_of_ips(network_dict[network])
        # Prints the name of the network and all ip addresses in ascending order
        print(network + ' - ' + ' '.join(ip for ip in network_dict[network]))
