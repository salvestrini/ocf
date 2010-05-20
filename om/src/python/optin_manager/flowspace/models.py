from django.db import models
from django.contrib import auth
from optin_manager.flowspace.utils import int_to_mac, int_to_dotted_ip

class FlowSpace(models.Model):
    mac_src_s           = models.IntegerField("Start Source MAC address", null=True, default=0x000000000000)
    mac_src_e           = models.IntegerField("End Source MAC address", null=True, default=0xFFFFFFFFFFFF)
    mac_dst_s           = models.IntegerField("Start Destination MAC address" , null=True, default=0x000000000000)
    mac_dst_e           = models.IntegerField("End Destination MAC address" , null=True, default=0xFFFFFFFFFFFF)
    eth_type_s          = models.IntegerField("Start Ethernet Type" , null=True, default=0x0000)
    eth_type_e          = models.IntegerField("End Ethernet Type" , null=True, default=0xFFFF)
    vlan_id_s           = models.IntegerField("Start Vlan ID" , null=True, default=0x000)
    vlan_id_e           = models.IntegerField("End Vlan ID" , null=True, default=0xFFF)
    ip_src_s            = models.IntegerField("Start Source IP Address" , null=True, default=0x00000000)
    ip_src_e            = models.IntegerField("End Source IP Address" , null=True, default=0xFFFFFFFF)
    ip_dst_s            = models.IntegerField("Start Destination IP Address" , null=True, default=0x00000000)
    ip_dst_e            = models.IntegerField("End Destination IP Address" , null=True, default=0xFFFFFFFF)
    ip_proto_s          = models.IntegerField("Start IP Protocol Number" , null=True, default=0x00)
    ip_proto_e          = models.IntegerField("End IP Protocol Number" , null=True, default=0xFF)
    tp_src_s            = models.IntegerField("Start Source Transport Port" , null=True, default=0x0000)
    tp_src_e            = models.IntegerField("End Source Transport Port" , null=True, default=0xFFFF)
    tp_dst_s            = models.IntegerField("Start Destination Transport Port" , null=True, default=0x0000)
    tp_dst_e            = models.IntegerField("End Destination Transport Port" , null=True, default=0xFFFF)
    
    def stringify(self):
        return "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s"%(
                    self.mac_src_s,self.mac_src_e,
                    self.mac_dst_s,self.mac_dst_e,
                    self.vlan_id_s,self.vlan_id_e,
                    self.ip_src_s,self.ip_src_e,
                    self.ip_dst_s,self.ip_dst_e,
                    self.ip_proto_s,self.ip_proto_e,
                    self.tp_src_s,self.tp_src_e,
                    self.tp_dst_s,self.tp_dst_e,
                    )                      
          
    def __unicode__(self):
        expression = ""
        if (self.mac_src_s > 0 and self.mac_src_e < 0xFFFFFFFFFFFF):
            expression = expression + ("MAC Source Addr: %s-%s , " % (int_to_mac(self.mac_src_s), int_to_mac(self.mac_src_e)))
        if (self.mac_dst_s > 0 and self.mac_dst_e < 0xFFFFFFFFFFFF): 
            expression = expression + ("MAC Destination Addr: %s-%s , " % (int_to_mac(self.mac_dst_s), int_to_mac(self.mac_dst_e))) 
        if (self.vlan_id_s > 0 and self.vlan_id_e < 0xFFF): 
            expression = expression + ("VALN id: %d-%d , " % (self.vlan_id_s,self.vlan_id_e)) 
        if (self.ip_src_s > 0 and self.ip_src_e < 0xFFFFFFFF):    
            expression = expression + ("IP Source Addr: %s-%s , " % (int_to_dotted_ip(self.ip_src_s), int_to_dotted_ip(self.ip_src_e)))
        if (self.ip_dst_s > 0 and self.ip_dst_e < 0xFFFFFFFF):    
            expression = expression + ("IP Destination Addr: %s-%s , " % (int_to_dotted_ip(self.ip_dst_s), int_to_dotted_ip(self.ip_dst_e)))
        if (self.ip_proto_s > 0 and self.ip_proto_e < 0xFF):    
            expression = expression + ("IP Protocol Number: %s-%s , " % (self.ip_proto_s, self.ip_proto_e)) 
        if (self.tp_src_s > 0 and self.tp_src_e < 0xFFFF):    
            expression = expression + ("Transport Source Port: %s-%s , " % (self.tp_src_s, self.tp_src_e))
        if (self.tp_dst_s > 0 and self.tp_dst_e < 0xFFFF):    
            expression = expression + ("Transport Destination Port: %s-%s , " % (self.tp_dst_s, self.tp_dst_e))
        if expression == "":
            expression = "*"
        return expression
                     
#        return ("MAC Source Addr: %s-%s , MAC Destination Addr: %s-%s # IP Source Addr: %s-%s , \
#            IP Destination Addr: %s-%s # TP Source Port: %d-%d , TP Destination Port: %d-%d" % 
#        (int_to_mac(self.mac_src_s), int_to_mac(self.mac_src_e), int_to_mac(self.mac_dst_s), int_to_mac(self.mac_dst_e),
#         int_to_dotted_ip(self.ip_src_s), int_to_dotted_ip(self.ip_src_e), int_to_dotted_ip(self.ip_dst_s), int_to_dotted_ip(self.ip_dst_e),
#          self.tp_src_s, self.tp_src_e, self.tp_dst_s, self.tp_dst_e) )   
        
    class Meta:
        abstract = True

 
class UserFlowSpace(FlowSpace):
    '''
    Holds information about the verified flowspace for each user
    '''
    user            = models.ForeignKey(auth.models.User)        

class AdminFlowSpace(FlowSpace):
    '''
    Holds information about the verified flowspace for each admin
    This is the flowspace that can be delegated to each user
    '''
    user           = models.ForeignKey(auth.models.User)
   
class RequestedAdminFlowSpace(FlowSpace):
    '''
    Admin FLowSpace requests, waiting for higher level admin approval
    '''
    user            = models.ForeignKey(auth.models.User, related_name = "admin_fs_requester")
    admin           = models.ForeignKey(auth.models.User, related_name = "admin_fs_approver")
    req_priority    = models.IntegerField()

class RequestedUserFlowSpace(FlowSpace):
    '''
    User FLowSpace requests, waiting for admin approval
    '''
    user            = models.ForeignKey(auth.models.User, related_name = "user_fs_requester")
    admin           = models.ForeignKey(auth.models.User, related_name = "user_fs_approver")
    
'''
Experiment, ExperimentFlowSpace stores information about each experiment
'''    
class Experiment(models.Model):
    ''' 
    Holds information about the topology and flowspace request of an experiment
    '''
    slice_id            = models.CharField(max_length = 1024)
    project_name        = models.CharField(max_length = 1024)
    project_desc        = models.CharField(blank=True, max_length = 1024)
    slice_name          = models.CharField(max_length = 1024)
    slice_desc          = models.CharField(blank=True, max_length = 1024)
    controller_url      = models.CharField(max_length = 1024)
    owner_email         = models.CharField(blank=True, max_length = 1024)
    owner_password      = models.CharField(blank=True, max_length = 2048)
    
    # TODO: takeout the replacement when Rob fixes the . escaping in FV
    def get_fv_slice_name(self):
        s = "%s ID: %s" % (self.slice_name, self.slice_id)
        return s.replace(".", "_")
    
    def __unicode__(self):
        return "experiment: %s:%s" % (self.project_name,self.slice_name)

class ExperimentFLowSpace(FlowSpace):
    dpid          = models.CharField(max_length = 30)
    direction     = models.IntegerField(default = 2)  #0:ingress 1:egress 2:bi-directional
    port_number_s = models.IntegerField("Start of Port Range", blank=True, default=0)
    port_number_e = models.IntegerField("End of Port Range", blank=True, default=0xFFFF)
    exp           = models.ForeignKey(Experiment)
    def __unicode__(self):
        fs_desc = super(ExperimentFLowSpace, self).__unicode__()
        return "dpid; %s , FS: %s"%(self.dpid,fs_desc)   
    
'''
UserOpts, OptsFlowSpace stores information about each opt-in
'''   
class UserOpts(models.Model):
    '''
    Holds information about all opt-ins
    '''
    user            = models.ForeignKey(auth.models.User)
    priority        = models.IntegerField()
    experiment      = models.ForeignKey(Experiment)
    nice            = models.BooleanField(default = True)
    
    def __unicode__(self):
        return "user: %s  opted into: %s"%(self.user, self.experiment)   
    
class OptsFlowSpace(FlowSpace):
    dpid          = models.CharField(max_length = 30)
    direction     = models.IntegerField(default = 2)  #0:ingress 1:egress 2:bi-directional
    port_number_s = models.IntegerField("Start of Port Range", default = 0)
    port_number_e = models.IntegerField("End of Port Range", default=0xFFFF)
    opt           = models.ForeignKey(UserOpts)
    def __unicode__(self):
        fs_desc = super(OptsFlowSpace, self).__unicode__()
        return "dpid; %s , FS: %s"%(self.dpid,fs_desc)

    
class MatchStruct(models.Model):
    match       = models.CharField(max_length = 2000)
    #TODO unique should be true
    fv_id       = models.CharField(unique = False, max_length = 40)
    priority    = models.IntegerField()
    optfs       = models.ForeignKey(OptsFlowSpace)
    def __unicode__(self):
        return "%s: %s"%(self.fv_id, self.match)

   