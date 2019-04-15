#!/usr/bin/env python
from __future__ import print_function

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import argparse
import atexit
import ssl

def GetArgs():
    """
    Supports the command-line arguments listed below.
    """
    parser = argparse.ArgumentParser(description='Process args for generate CLI Types')
    parser.add_argument('-s', '--host', required=True, action='store', help='Remote host to connect to')
    parser.add_argument('-o', '--port', type=int, default=443, action='store', help='Port to connect on')
    parser.add_argument('-u', '--user', required=True, action='store', help='User name to use when connecting to host')
    parser.add_argument('-p', '--password', required=False, action='store', help='Password to use when connecting to host')
    args = parser.parse_args()
    return args

def generate_cli_data_objects(host):
    dmanager = host.RetrieveDynamicTypeManager()

    data_types = dmanager.DynamicTypeMgrQueryTypeInfo(None).dataTypeInfo
    for data_type in data_types:
        vmodlName = data_type.name
        wsdlName = data_type.wsdlName
        parent = data_type.base[0]
        version = data_type.version
        props = []
        for prop in data_type.property:
            props.append('("{}", "{}", "{}", {})'.format(prop.name, prop.type, prop.version, "F_OPTIONAL"))
        props = "[{}]".format(", ".join(props))
        yield 'CreateDataType("{}", "{}", "{}", "{}", {})'.format(vmodlName, wsdlName, parent, version, props)

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
        obj = [host for host in host_view.view]
        GiZeta = obj[0]
        for i in generate_cli_data_objects(GiZeta):
            print(i)
        
    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start Execution
if __name__ == "__main__":
    main()