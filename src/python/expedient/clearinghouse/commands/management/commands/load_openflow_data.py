'''
Created on Oct 7, 2010

@author: jnaous
'''

from django.core.management.base import NoArgsCommand
from expedient.clearinghouse.project.models import Project
try:
    from json import load
except ImportError:
    from simplejson import load

from openflow.plugin.models import OpenFlowAggregate, OpenFlowInterfaceSliver,\
    OpenFlowSliceInfo, FlowSpaceRule, OpenFlowInterface
from optparse import make_option
from django.test import Client
from expedient.common.tests.client import test_get_and_post_form
from django.core.urlresolvers import reverse, resolve
from urlparse import urlsplit, urlunsplit
from expedient.clearinghouse.project.views import create_project_roles
from django.contrib.auth.models import User
from expedient.clearinghouse.slice.models import Slice
from expedient.common.permissions.shortcuts import give_permission_to
from expedient.common.middleware import threadlocals

def assert_redirection(response, expected_url):
    assert(response.code == 302)
    
    url = response['Location']
    
    e_scheme, e_netloc, e_path, e_query, e_fragment = urlsplit(expected_url)
    if not (e_scheme or e_netloc):
        expected_url = urlunsplit(('http', 'testserver', e_path,
            e_query, e_fragment))

    assert(url == expected_url)
    
class Command(NoArgsCommand):
    help = "load serialized data for re-use in database migration."

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--username', action='store', dest='username',
            default="expedient", type="string",
            help='Specifies username to use to login. '
                'Defaults to "expedient"',
        ),
        make_option(
            '--password', action='store', dest='password',
            default="expedient", type="string",
            help='Specifies password to use to login. '
                'Defaults to "expedient"',
        ),
        make_option(
            '--filename', action='store', dest='filename',
            default="db_dump.json", type="string",
            help='Specifies the name of the file that has the dumped'
                'JSON data. Defaults to "db_dump.json"',
        ),
        make_option(
            '--load_aggs', action='store_true', dest='load_aggs',
            help='Load the aggregate information or not? Default is False',
        ),
        make_option(
            '--load_slices', action='store_true', dest='load_slices',
            help='Create the slices or not? Default is False',
        ),
        make_option(
            '--start_slices', action='store_true', dest='start_slices',
            help='Start the slices after creating them? Default is False',
        ),
    )

    def handle_noargs(self, **options):
        
        username = options.get("username")
        password = options.get("password")
        
        filename = options.get("filename")
        do_aggs = options.get("load_aggs")
        do_slices = options.get("load_slices")
        start_slices = options.get("start_slices")
        
        data = load(filename)
        
        client = Client()
        client.login(username=username, password=password)

        user = User.objects.get(username=username)

        if do_aggs:
            for agg_dict in data["aggregates"]:
                resp = test_get_and_post_form(
                    client, reverse("openflow_aggregate_create"),
                    agg_dict,
                )
                
                assert_redirection(
                    resp,
                    reverse("openflow_aggregate_add_links", args=[i+1]))
        
        if do_slices:
            for project_dict in data["projects"]:
                
                project = Project.objects.create(
                    name=project_dict["name"],
                    description=project_dict["description"],
                )
                create_project_roles(project, user)
                
                # add aggregates to project
                for aggregate in OpenFlowAggregate.objects.all():
                    give_permission_to("can_use_aggregate", aggregate, user)
                    give_permission_to("can_use_aggregate", aggregate, project)
                
                # add slices to project
                for slice_dict in project_dict["slices"]:
                    slice = Slice.objects.create(
                        name=slice_dict["name"],
                        description=slice_dict["description"],
                        project=project,
                        owner=user,
                    )
                
                    OpenFlowSliceInfo.objects.create(
                        slice=slice,
                        controller_url=slice_dict["controller_url"],
                        password=slice_dict["password"],
                    )
                    
                    # add aggregates to slices
                    for aggregate in OpenFlowAggregate.objects.all():
                        give_permission_to("can_use_aggregate", aggregate, slice)
                    
                    # add slivers
                    slivers = []
                    for dpid, port in slice_dict["ifaces"]:
                        sliver = OpenFlowInterfaceSliver.objects.get_or_create(
                            slice=slice,
                            resource=OpenFlowInterface.objects.get(
                                port_num=port, switch__datapath_id=dpid),
                        )
                        sliver.append(slivers)
                        
                    # add flowspace
                    for sfs_dict in slice_dict["sfs"]:
                        fs_dict = {}
                        for attr in "dl_src", "dl_dst", "dl_type", "vlan_id", \
                        "nw_src", "nw_dst", "nw_proto", "tp_dst", "tp_src":
                            fs_dict[attr+"_start"] = sfs_dict[attr]
                            fs_dict[attr+"_end"] = sfs_dict[attr]
                        
                        fs = FlowSpaceRule.objects.create(**fs_dict)
                        
                        for sliver in slivers:
                            fs.slivers.add(sliver)
                            
                    if start_slices:
                        tl = threadlocals.get_thread_locals()
                        tl["project"] = project
                        tl["slice"] = slice
                        slice.start(user)
                        