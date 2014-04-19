#!/usr/bin/env python

import rospy
from  rospkg import rospack
__rospack = rospack.RosPack()

import strands_action_domain
print strands_action_domain.STRANDSDomain().domain #generatePDDL()