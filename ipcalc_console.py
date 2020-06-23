SUBNET_NUMBER = 0
HOSTS = 1
SUBNET_IP = 2
SUBNET_MASK = 3
SUBNET_BROADCAST = 4

import general_input as g_i

################IP&Mask functions###############

def str_to_int(st, lbound = 0, ubound = 0xffffffff):
    try:
        retval = int(st)
    except:
        return None
    return None if (retval < lbound) or (retval > ubound) else retval

def not32(int32):
    #inverse 32-bit value
    return int32 ^ 0xffffffff if int32 != None else None

def ip_str_to_int(net_ip):
    arr_ip = net_ip.split('.')
    print(arr_ip)
    if len(arr_ip) != 4:
        return None
    octs = [str_to_int(arr_ip[0], 0, 255), str_to_int(arr_ip[1], 0, 255), str_to_int(arr_ip[2], 0, 255), str_to_int(arr_ip[3], 0, 255)]
    for oct_item in octs:
        if oct_item == None:
            return None
    return int(arr_ip[3]) | int(arr_ip[2]) << 8 | (int(arr_ip[1]) << 16) | (int(arr_ip[0]) << 24)

def ip_int_to_str(ip):
    return (str(ip >> 24) + '.' + str((ip >> 16) & 0xFF)+ '.' \
            + str((ip >> 8) & 0xFF) + '.' + str(ip & 0xFF)) if ip != None else None

################End of IP&Mask functions###############

################Mask functions###############

def wildcard_mask(mask):
    return not32(mask) if mask != None else None 

def pref_to_mask(prefix):
    return (2 ** prefix - 1) << (32 - prefix) if prefix != None else None

def is_mask_invalid(mask):
    # check non-prefix mask format (1...1 at left, 0...0 at right)
    inverted_mask = not32(mask)
    return inverted_mask & (inverted_mask + 1) != 0 if inverted_mask != None else False

def mask_str_to_int(mask):
    mask_int = ip_str_to_int(mask)
    if mask_int == None:
        mask_int = pref_to_mask(str_to_int(mask, 0, 32))
    elif is_mask_invalid(mask_int): 
        return None
    return mask_int

def mask_by_hosts(hosts):
    hosts+=1
    hosts |= hosts >> 1
    hosts |= hosts >> 2
    hosts |= hosts >> 4
    hosts |= hosts >> 8
    hosts |= hosts >> 16
    return not32(hosts)

def pref_by_mask(mask):
# https://blogs.msdn.microsoft.com/jeuge/2005/06/08/bit-fiddling-3/
    mask_count = mask - ((mask >> 1) & 0xdb6db6db) - ((mask >> 2) & 0x49249249)
    return ((mask_count + (mask_count >> 3)) & 0xc71c71c7) % 63

################End of Mask functions###############

################IP functions###############

def net_addr(ip, net_mask):
    return ip & net_mask if (ip != None) and (net_mask != None) else None

def broadcast(ip, net_mask):
    return ip | wildcard_mask(net_mask) if (ip != None) and (net_mask != None) else None

################End of IP functions###############

################Subnets allocation functions###############

def subnets_allocation(subnet_list, subnets_number, ip, net_mask):
    subnet_list.sort(key = lambda x: x[HOSTS])
    ip = net_addr(ip, net_mask)
    subnet_list[0][SUBNET_IP] = ip
    subnet_list[0][SUBNET_MASK] = mask_by_hosts(subnet_list[0][HOSTS])
    subnet_list[0][SUBNET_BROADCAST] = broadcast(subnet_list[0][SUBNET_IP], subnet_list[0][SUBNET_MASK])
    prev_ip = ip

    for i in range(1, subnets_number, 1):
        subnet_list[i][SUBNET_MASK] = mask_by_hosts(subnet_list[i][HOSTS])
        base_ip = ip + not32(subnet_list[i][SUBNET_MASK]) + 1
        if base_ip > prev_ip:
            subnet_list[i][SUBNET_IP] = base_ip
            prev_ip = base_ip
            subnet_list[i][SUBNET_BROADCAST] = broadcast(subnet_list[i][SUBNET_IP], subnet_list[i][SUBNET_MASK])
        else:
            subnet_list[i][SUBNET_IP] = ((prev_ip >> (32 - pref_by_mask(subnet_list[i][SUBNET_MASK]))) + 1) << (32 - pref_by_mask(subnet_list[i][SUBNET_MASK]))
            prev_ip = subnet_list[i][SUBNET_IP]
            subnet_list[i][SUBNET_BROADCAST] = broadcast(subnet_list[i][SUBNET_IP], subnet_list[i][SUBNET_MASK])

    subnet_list.sort(key = lambda x: x[SUBNET_NUMBER])

################End of Subnets allocation functions###############    
        
def main():

    ip = g_i.universal_input("Enter ISP dedicated network ip address\n", "Invalid IP format\n", ip_str_to_int)   
         
    net_mask = g_i.universal_input("Enter network mask for ISP dedicated ip address \n", "Invalid Mask format\n", mask_str_to_int)
    
    net_pref = pref_by_mask(net_mask)

    max_subnets = 1 << (30 - net_pref)
    
    subnets = g_i.universal_input("Enter number of subnets \n", "Invalid number of subnets. " + \
                              "Number of subnets with at least 1 host must be specified by integer value in the range of 1 to " + str(max_subnets), \
                            lambda st: str_to_int(st, 1, max_subnets)) #ограничиваем число подсетей, которое можно создать: минимум 1, максимум max_subnets
      
    max_sub_hosts = (1 << (pref_by_mask(mask_by_hosts(subnets - 2)) - net_pref)) - 2

    subnet_list = []
    for i in range (subnets):
        subnet_list.append([i+1, g_i.universal_input("Enter number of devices in subnet " + str(i + 1) + "\n", \
                                           "Invalid number of hosts. Number of hosts must be specified by integer value in the range of 1 to "\
                                           + str(max_sub_hosts),
                                           lambda st: str_to_int(st, 1, max_sub_hosts)), 0, 0, 0])
    print(subnet_list)
    
    subnets_allocation(subnet_list, subnets, ip, net_mask)

    print(subnet_list)
    print('\ninteger network IP value =',ip)
    print('\nstring network IP value =',ip_int_to_str(net_addr(ip, net_mask)))
    print('\nstring network broadcast address =',ip_int_to_str(broadcast(ip, net_mask)))

    

    for i in range (subnets):
        
        print ("\nFor subnet %s, " %subnet_list[i][SUBNET_NUMBER] + "subnet ip is %s, " %ip_int_to_str(subnet_list[i][SUBNET_IP])\
               + "mask is %s, " %ip_int_to_str(subnet_list[i][SUBNET_MASK]))
    
       
main ()
