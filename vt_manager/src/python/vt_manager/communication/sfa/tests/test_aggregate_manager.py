from vt_manager.communication.sfa.AggregateManager import AggregateManager
from vt_manager.communication.sfa.tests.example_vm_rspec import rspec as RSPEC
'''
This module run tests over the AM locally without xmlrpc or sfa instances
'''

class Options:

	def __init__(self,callId='fancy-UUID',sliceId=None):
		self.call_id = callId
		self.geni_slice_urn = None
		self.geni_rspec_version = 'OcfVt'

	def get(self,attr,extra=None):
		return getattr(options,attr)

options = Options(123456)
agg = AggregateManager(None)
print 'Aggregate instance:',agg
#xml = agg.ListResources(None,None,options)
#print '------------------ListResources:',xml

#XXX: Last ListResources() test was 02/13/2013 with OK results, the first temptative of OCF rspecs are done(based in PGv2). OCF Rspecs need to be improved and clearify the XRN, HRN and URN concepts in order to offer the correct notation for aggregates, component managers, slices etc. 

xml = agg.CreateSliver(None, None, None, RSPEC, None, options)

#XXX: Last CreateSliver() test was 02/25/2013 with OK results. The test does not get any parametre from VTShell yet, but the RSpec parsing(v1) is OK. The CreateSliver and GetSlice VTShell functions should be implemented working with slice_leaf parametre in order to check the manifest response RSpec.
