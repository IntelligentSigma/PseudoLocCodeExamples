#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################################################
##
##	File: concant_properties.py
##	Authors: Clinton De Young, Tyler Peterson and Dave Mamanakis
##	Date: August 16, 2010
##
##	-------------------------------------------------------------------------------
##	Description: Cleans up the properties files that need to be deleted
##
####################################################################################

import sys
import getopt
import os
import re
import shutil
from subprocess import Popen, PIPE
from exceptions import IOError

class Remove_Files(object):
    
    	def __init__(self):
		
		self.sandbox_path = '/home/sandbox/' #Path to the properties files that need to be cleaned up, deleted
		self.old_files = ''
		self.new_files = ''
		self.old_properties_files = []
		self.new_properties_files = []
		
		self.just_do_it()
		
	def just_do_it(self):
			
		cmd = "/usr/bin/find '%s' -iname '*.old' -print -o -iname '*.old' -print" % self.sandbox_path 
		findProcess = Popen(cmd, shell=True, stdout=PIPE) 
		self.old_files = findProcess.communicate()[0]
		self.old_properties_files = self.old_files.split()
		
		for o in self.old_properties_files:
			os.remove(o)
						
if __name__ == '__main__':
	
	Remove_Files()
		
