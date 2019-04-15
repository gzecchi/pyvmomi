# VMware vSphere Python SDK
# Copyright (c) 2019 GiZeta. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Get ESXi CLI VMOMI Instance.
"""
from pyVmomi.VmomiSupport import CreateAndLoadManagedType, F_OPTIONAL
from pyVmomi.ManagedMethodExecutorHelper import MMESoapStubAdapter

class EsxCLI(object):
    _loaded_types = {}

    def __init__(self, host):
        self._host = host
        self._host_api_version = host.summary.config.product.apiVersion

    def _load_type(self, type_info):
        if type_info.name not in self._loaded_types:
            methods = []
            for method in type_info.method:
                params = [(param.name, param.type, param.version, F_OPTIONAL, method.privId) for param in method.paramTypeInfo]
                return_type = (0, method.returnTypeInfo.type, method.returnTypeInfo.type)
                methods.append((method.name, method.wsdlName, method.version, params, return_type, method.privId, list(method.fault)))

            cls = CreateAndLoadManagedType(type_info.name, type_info.wsdlName, type_info.base[0], type_info.version, [], methods)
            self._loaded_types[type_info.name] = cls
        return self._loaded_types[type_info.name]

    def get(self, name):
        type_name = "vim.EsxCLI." + name
        mme = self._host.RetrieveManagedMethodExecuter()
        stub = MMESoapStubAdapter(mme)
        stub.versionId = 'urn:vim25/{}'.format(self._host_api_version)
        dm = self._host.RetrieveDynamicTypeManager()
        type_to_moId = {moi.moType: moi.id for moi in dm.DynamicTypeMgrQueryMoInstances()}
        if type_name in type_to_moId:
            moId = type_to_moId[type_name]
            ti = dm.DynamicTypeMgrQueryTypeInfo()
            for type_info in ti.managedTypeInfo:
                if type_info.name == type_name:
                    cls = self._load_type(type_info)
                    return cls(moId, stub)
        raise Exception("CLI type '{}' not found".format(name))
