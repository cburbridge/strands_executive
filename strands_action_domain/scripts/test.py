#!/usr/bin/env python

import rospy
from  rospkg import rospack
__rospack = rospack.RosPack()

import strands_action_domain

strands_domain =  strands_action_domain.STRANDSDomain()
print strands_domain.domain #generatePDDL()

# For example
#task =  strands_domain.domain.get_action("launch").create_executive_task({'param1': 'scitos_bringup.launch',})
# schedule / execute task...

