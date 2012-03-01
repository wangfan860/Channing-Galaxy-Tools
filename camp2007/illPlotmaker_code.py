from galaxy import datatypes,model
import sys

import galaxy.util

#Provides Upload tool with access to list of available builds

builds = []
#Read build names and keys from galaxy.util
for dbkey, build_name in galaxy.util.dbnames:
    builds.append((build_name,dbkey,False))

#Return available builds
def get_available_builds(defval='hg18'):
    for i,x in enumerate(builds):
        if x[1] == defval:
           x = list(x)
           x[2] = True
           builds[i] = tuple(x)
    return builds

def exec_after_process(app, inp_data, out_data, param_dict, tool, stdout, stderr):
    """
    """
    job_name = param_dict.get( 'title1', 'Intensity plots' )
    of1 = '%s.html' % job_name.replace(' ','_')
    lookup={}
    lookup['outfile1'] = of1
    for aname in lookup.keys():
       data = out_data[aname]
       newname = lookup[aname]
       data.name = newname
       out_data[aname] = data
