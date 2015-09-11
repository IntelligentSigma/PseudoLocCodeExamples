#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################################################
##
##	File: concant_properties.py
##	Authors: Clinton De Young, Tyler Peterson and Dave Mamanakis
##	Date: November 2, 2010
##
##	-------------------------------------------------------------------------------
##	Description: Renames the properties files from *.properties to *.new
##
####################################################################################

import sys
import getopt
import os
import re
import shutil
from subprocess import Popen, PIPE
from exceptions import IOError

class Rename_Files(object):

	def __init__(self):

		self.sandbox_path = '/home/sandbox/Backup_of_l10n/' #The path to your code repository
		self.old_files = ''
		self.new_files = ''
		self.old_properties_files = []
		self.new_properties_files = []

		self.just_do_it()

	def just_do_it(self):

		cmd = "/usr/bin/find '%s' -iname '*.properties' -print -o -iname '*.properties' -print" % self.sandbox_path 
		findProcess = Popen(cmd, shell=True, stdout=PIPE) 
		self.old_files = findProcess.communicate()[0]
		self.old_properties_files = self.old_files.split()

		cmd = "/usr/bin/find '%s' -iname '*.new' -print -o -iname '*.new' -print" % self.sandbox_path 
		findProcess = Popen(cmd, shell=True, stdout=PIPE) 
		self.new_files = findProcess.communicate()[0]
		self.new_properties_files = self.new_files.split()

		for n in self.new_properties_files:

			for o in self.old_properties_files:

				if o in n:
					os.rename(n, o)


if __name__ == '__main__':

	Rename_Files()
