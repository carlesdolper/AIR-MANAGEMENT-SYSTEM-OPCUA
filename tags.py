class Tags:
    def __init__(self, tag_name, nodeid, namespace, scale_factor):
        self.tag_name = tag_name
        self.nodeid = nodeid
        self.namespace = namespace
        self.scale_factor = scale_factor
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

# Crea una lista de nombres de tags
# Define el NodeId inicial
nodeid = 16842752
tag_data = {
    #"BaseUnit_SysDiag": {"nodeid": nodeid + 256 * 0, "namespace": 3, "scale_factor": 1},
    #"BaseUnit_LinkInfo": {"nodeid": nodeid + 256 * 1, "namespace": 3, "scale_factor": 1},
    #"BaseUnit_DiagInfo": {"nodeid": nodeid + 256 * 2, "namespace": 3, "scale_factor": 1},
    #"BaseUnit_RegInfo": {"nodeid": nodeid + 256 * 3, "namespace": 3, "scale_factor": 1},
    "AMS00_PF3A_AccumFlow": {"nodeid": nodeid + 256 * 4, "namespace": 3, "scale_factor": 10},
    "AMS00_PF3A_Flow": {"nodeid": nodeid + 256 * 5, "namespace": 3, "scale_factor": 1},
    "AMS00_PF3A_Temperature": {"nodeid": nodeid + 256 * 6, "namespace": 3, "scale_factor": 0.1},
    "AMS00_PF3A_Pressure": {"nodeid": nodeid + 256 * 7, "namespace": 3, "scale_factor": 0.001},
    #"AMS00_PF3A_Err": {"nodeid": nodeid + 256 * 8, "namespace": 3, "scale_factor": 1},
    #"AMS00_PF3A_Status": {"nodeid": nodeid + 256 * 9, "namespace": 3, "scale_factor": 1},
    "AMS00_ITV_Value": {"nodeid": nodeid + 256 * 10, "namespace": 3, "scale_factor": 0.001},
    #"AMS00_ITV_DiagData": {"nodeid": nodeid + 256 * 11, "namespace": 3, "scale_factor": 1},
    #"AMS00_EX_PQI": {"nodeid": nodeid + 256 * 12, "namespace": 3, "scale_factor": 1},
    #"AMS00_EX_ITV_PQI": {"nodeid": nodeid + 256 * 13, "namespace": 3, "scale_factor": 1},
    #"AMS00_EX_P4_PQI": {"nodeid": nodeid + 256 * 14, "namespace": 3, "scale_factor": 1},
    #"AMS00_EX_DI": {"nodeid": nodeid + 256 * 15, "namespace": 3, "scale_factor": 1},
    #"AMS00_EX_P4_PDin": {"nodeid": nodeid + 256 * 16, "namespace": 3, "scale_factor": 1},
    #"AMS00_Standby": {"nodeid": nodeid + 256 * 17, "namespace": 3, "scale_factor": 1},
    #"AMS00_ForcedStandby": {"nodeid": nodeid + 256 * 18, "namespace": 3, "scale_factor": 1},
    #"AMS00_VP_ITV_NC": {"nodeid": nodeid + 256 * 19, "namespace": 3, "scale_factor": 1},
    #"AMS00_VP_ITV_NO": {"nodeid": nodeid + 256 * 20, "namespace": 3, "scale_factor": 1},
    #"AMS00_P4_DO": {"nodeid": nodeid + 256 * 21, "namespace": 3, "scale_factor": 1},
    #"AMS00_P4_PDout": {"nodeid": nodeid + 256 * 22, "namespace": 3, "scale_factor": 1},
}

tag_list = [Tags(name, data["nodeid"], data["namespace"], data["scale_factor"]) for name, data in tag_data.items()]