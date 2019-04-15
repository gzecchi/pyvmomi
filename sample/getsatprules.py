#!/usr/bin/env python

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
from pyVmomi.EsxCLI import EsxCLI
import argparse
import atexit
import ssl

def GetArgs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description='Process args for powering on a Virtual Machine')
    parser.add_argument('-s', '--host', required=True, action='store', help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store', help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store', help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store', help='Password to use when connecting to host')
    args = parser.parse_args()
    return args

def print_host_info(host_machine):
    """
    Print information for a particular host machine 
    """
    print(host_machine.config.network.dnsConfig.hostName)
    print(host_machine.config.product.version)
    for option in host_machine.config.option:
        print(option.key,option.value)

def main():
    args = GetArgs()
    if args.password:
        password = args.password
    else:
        password = getpass.getpass(prompt='Enter password for host %s and user %s: ' % (args.host,args.user))
    
    try:
        context = None
        if hasattr(ssl, '_create_unverified_context'):
            context = ssl._create_unverified_context()
        service_instance = SmartConnect(host=args.host,
                          user=args.user,
                          pwd=password,
                          port=int(args.port),
                          sslContext=context)
        if not service_instance:
            print("Cannot connect to specified host using specified username and password")
            sys.exit()

        atexit.register(Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        container = content.rootFolder
        viewType = [ vim.HostSystem ]
        recursive = True
        host_view = content.viewManager.CreateContainerView(container, viewType, recursive)
        cli = EsxCLI(host_view.view[0])
        # List SATP rules
        rule_cli = cli.get("storage.nmp.satp.rule")
        print(rule_cli.List())

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()