#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################################################
##
##	File: concant_properties.py
##	Authors: Clinton De Young, Tyler Peterson and Dave Mamanakis
##	Date: August 16, 2010
##
##	-------------------------------------------------------------------------------
##	Description: Take Old Properties Files, Compare HTML, Extract any 
##                   missing IDs, create new Properties Files with HTML
##                   inside.
##
####################################################################################

import sys
import getopt
import os
import re
import shutil
from HTMLParser import HTMLParser
from Properties import Properties
from pprint import pformat
from exceptions import IOError
from random import randint
from subprocess import Popen, PIPE

class Get_User_Input(object):
	'''
	The Get_User_Input class grabs command line arguments from the user and
	makes them available
	'''
	
	__path = "" # This is the path we are looking for
	
	def __init__(self):
		'''
		The INIT part of the DEF sets up the options and variables
		'''
		
		# Try to get the Command Line Arguments (i.e. the PATH) or send an error
		try:
			options, arguments = getopt.getopt(sys.argv[1:], 'hp:t:l:', ['help', 'path='])

		except getopt.GetoptError, e:
			print "A dark buzzard has fouled our breakfast bowl with the following droppings:\n"
			print e
			sys.exit(1)
			
		# Check the command line arguments for validity
		if len(options) == 0:
			print "You have not specified any command line arguments and I cannot read\nyour mind.  You may try using one or more of these:\n"
			self.__usage()
			sys.exit(1)

		for o,a in options:
			if o in ('-h', '--help'):
				self.__usage()
				sys.exit(0)

			if o in ('-p', '--path'):
				self.__path = a
				
		if not os.path.exists(self.__path):
			print "\nYou have selected an invalid path François.  Please try again.\n"
			self.__usage()
			sys.exit(1)
			
	def __usage(self):
		'''
		if we request Help, or detect an error, print the following for
		the pleebs to read
		'''
		
		print '----------------------------------------------------------------------'
		print 'USAGE:\n'
		print '-h, --help\tPrint this help message.\n'
		print '-p, --path\tSpecify the Path to the Properties files and HTML files.\n'
		
		print 'Example: concant_properties.py -p /home/billy/sandbox/code/ \n'
		print '----------------------------------------------------------------------'
		
	def get_path(self):
		'''
		get_path returns the path entered by the user as the location of
		the files to manipulate
		'''
		
		return self.__path
	
class Pull_Files(object):
	'''
	The Pull_Files class recursively parses the specfied path and returns
	all properties files in the web client. Then returns all the HTML files
	of the same name.
	'''
	
	def __init__(self, sandbox_path):
		'''
		Initialize and prepare for this section's run
		'''
		
		self.__sandbox_path = sandbox_path # This is the location of the files to manipulate
		self.__prop_files = [] # This is a list for the Properties Files
		self.__html_files = [] # This is a list for the HTML Files
				
		# The following generates the Property Files List
		self.__generate_prop_file_list()
		
		# The following generates the HTML Files List based on the list of Property Files
		self.__generate_html_file_list(self.__prop_files)
		
	def __generate_prop_file_list(self):
		'''
		__generate_prop_file_list will get a recursive list of the 
		Properties files from the directory specified in the path.
		'''
		
		# Because the Properties files are all located in a single directory (for this exercise) we build a directory tree and find the files
		### There is a faster way to do this, and the next iteration (if there is one) will reflect that method
		tree = os.walk(self.__sandbox_path)
		is_prop = re.compile("l10n[/\\\]\w+\.properties$") # This identifies the Properties Files in the code repository
		
		# Walk the tree to find the Properties files and create a useful path location to that file.
		for item in tree:
			
			for full_file_name in item[2]:
				fullpath = os.path.join(item[0], full_file_name)
				
				if is_prop.search(fullpath):
					file_name, extension = full_file_name.split('.', 1)
					
					self.__prop_files.append(fullpath)
					
	def __generate_html_file_list(self, prop_files):
		'''
		__generate_html_file_list will get a recursive list of the HTML
		files with the same name as the properties files.
		'''
		
		# The faster method mentioned in __generate_prop_file_list will look more like this
		cmd = "/usr/bin/find '%s' -iname '*.htm' -print -o -iname '*.html' -print -o -iname '*.ssi' -print" % self.__sandbox_path 
		#cmd = "/usr/bin/find '%s' -iname '*.ssi' -print" % self.__sandbox_path
		findProcess = Popen(cmd, shell=True, stdout=PIPE) 
		htmfiles = findProcess.communicate()[0]
		self.__html_files = htmfiles.split()
	
	def get_html(self):
		'''
		get_html will return the list of the HTML Files
		'''
		
		return self.__html_files
	
	def get_properties(self):
		'''
		get_properties will return the list of the Properties Files
		'''
		
		return self.__prop_files
	
class Pull_And_Concant_Strings(object):		
	'''
	The Pull_And_Concant_Strings class recursively parses the specfied path 
	and returns all properties files in the web client. Then returns all the 
	HTML files of the same name.
	'''
	
	def __init__(self, html_files, properties_files):
		'''
		Initialize and prepare for running this part of the script
		'''
		
		self.__prop_files = properties_files # We pass in the Properties Files List
		self.__html_files = html_files # We pass in the HTML Files List
		self.__tran_id_list = [] # We create a list for the Translation IDs
		self.__tran_id_prop_list = [] # We create a list for the Translation IDs from the Properties Files
		counter = 0 # Counter for counting purposes
		temp = '' # A temp holder for the name of the new files to be created
		self.__ignore = [
			'_fr',
			'_de',
			'_es',
			'_pt',
			'_ja',
			'_zh',
			'_ko',
			'_it',
			'_ru',
		] # We set this list for all the current languages we use in the product
		
		# We will now start the process of generating the new files
		self.generate_files()
		
	def generate_files(self):
		'''
		generate_files will do just that. We create several lists of 
		Necessary files, the ones we want to use and the ones we want
		to create.
		We send the HTML and Properties files in to be compared, and to 
		verify we have all the ID's in the Properties Files that aren't
		labeled "no translate".
		We also compare the Properties Files for the Languages to the 
		English Properties Files, in case something is missing, then
		we replace it.
		We take the Old Stuff, and concantinate the Old Properties 
		together, based on the HTML, and put all that into the NEW
		Properties Files.
		'''

		# Extract the first Properties File from the list, and get 2 things, Language Code (if any) and the Base Property File Name
		### Note, we also create the Default Property File Name (English) and the new Property File ".NEW" as well
		### Note, the main body of parsing code is also explained below
		for p_file in self.__prop_files:
			left_side, right_side = p_file.split('l10n/', 1)
			file_name, extension = right_side.split('.', 1)

			# Some of the Properties Files have odd names XXX_XXX_XXX_en.properties, so we have to parse that out...
			if "_" in file_name: 
				file_side, lang_code = file_name.split('_', 1)
				
				if "_" in lang_code:
					file_side, a_lang_code = lang_code.split('_', 1)
					lang_code = a_lang_code
					
					if "_" in lang_code:
						file_side, b_lang_code = lang_code.split('_', 1)
						lang_code = b_lang_code 
						
				lang_code = "_" + lang_code # This is the Language Code as found in the List, (_en is NOT in the list)
				
			else:
				lang_code = "_en"
			
			# We don't have _en in the list, so we only do this for any foreign language files
			if lang_code in self.__ignore:
				file_name = file_name[0:-3]
				default_property = left_side + "l10n/" + file_name + "." + extension
				temp = left_side + "l10n/" + file_name + lang_code + "." + extension + ".new"
				
			else: # This is for the English Property Files
				default_property = p_file
				temp = p_file + ".new"
		
			is_html = re.compile(r'\b' + file_name + '.htm') # The searcher for the currently needed HTML File
			is_ssi = re.compile(r'\b' + file_name + '.ssi') # The searcher for the currently needed SSI File
			
			# Take the first HTML file in the list and move forward
			for h_file in self.__html_files:
				
				# If the HTML File is the one for the Property File...
				if is_html.search(h_file) or is_ssi.search(h_file):
					props = Properties() # Initialize the language Properties Files via this program (creates a Dictionary)
					props.load(open(p_file))
					default_props = Properties() # Initialize the English Properties Files via this program (creates a Dictionary)
					
					try: # If the Default Properties Files does not exist, throw the error, but don't fail, continue
						default_props.load(open(default_property))
						
					except IOError:
						### Logging
						LOGGING = open('/home/sandbox/SCRIPT_RUN.LOG', 'a') #Log file location
						LOG_ME = "Missing the Default English property file:\t%s\n\n" % default_property
						print LOG_ME
						LOGGING.write(LOG_ME)
						LOGGING.close()
						continue

					MHP = My_Html_Parser(); # Initialize the HTML Parser to read the HTML
					MHP.my_init(props, temp, default_props) # Send in the Language Property File, the Temp File Name and Location and the English Property File
					read_html = open(h_file, "r") # Open the HTML File
					
					### Logging Info
					LOGGING = open('/home/sandbox/SCRIPT_RUN.LOG', 'a') #Log file location
					LOG_ME = "The current HTML File is:\n"
					print LOG_ME
					LOGGING.write(LOG_ME)
					LOG_ME = "\t\t" + h_file + "\n"
					print LOG_ME
					LOGGING.write(LOG_ME)
					LOG_ME = "The Default (English) Property File is:\n"
					print LOG_ME
					LOGGING.write(LOG_ME)
					LOG_ME = "\t\t" + default_property + "\n"
					print LOG_ME
					LOGGING.write(LOG_ME)
					LOG_ME = "The NEW Property File is:\n"
					print LOG_ME
					LOGGING.write(LOG_ME)
					LOG_ME = "\t\t" + temp + "\n\n"
					print LOG_ME
					LOGGING.write(LOG_ME)
					LOGGING.close()
					
					MHP.feed(read_html.read()) # Read the HTML File into the HTML Parser
					
					# Make the NEW (.new) Property File
					MHP.make_file()
					
					#MHP.close() # Keep things Tidy
					
				else:
					
					continue # Finish running the list
					
class Tran_State(object):
	'''
	The Tran_State class will update the rest of the program as to the 
	contents of the Translation ID and Property Dictionary
	'''
	
	def __init__(self, tagName, tranId, doTranslate=True):
		'''
		Initialize the run by importing the necessary data
		'''
		
		self.tagName = tagName # The name of the TAG
		self.tranId = tranId # The Translation ID
		self.childPointer = 0 # If the Parent has a child, counter
		self.doTranslate = doTranslate # Setting the bool
		
	def __str__(self):
		'''
		__str___ returns the string to be used to parse the HTML for 
		the Property Files
		'''
		
		return "TranState: tag=%s, id=%s, pointer=%s" % (self.tagName, self.tranId, self.childPointer)
	
	def __repr__(self):
		'''
		__repr__ teturns the contents of __str__
		'''
		
		return self.__str__()

class My_Html_Parser(HTMLParser):
	'''
	This is the HTML Parsing Routine
	'''
	
	def my_init(self, props, new_file_name, defaultProps):
		'''
		my_init initializes for the HTML Parsing
		'''
		
		self.props = props.getPropertyDict() # We get the Dictionary for the Properties File
		self.defaultProps = defaultProps.getPropertyDict() # We get the Dictionary for the Default Properties File
		self.transtack = [] # We create a LIST for the Translations
		self.__new_file = new_file_name # This is the .new Property File Name
		self.__property_file_whole = [] # Tis is the list to hold the new info for the new Property Files
		self.snippet = '' # We create the snipped for the new Property in the Property File
		self.tranidPattern = re.compile("""\s*id\s*=\s*['"]tran\d+['"]""") # To identify the ID in the HTML for Removal
		self.notranslatePattern = re.compile(r'\bnotranslate\b') # To identify the "no translate" items in the HTML
		self.spaceEntityPattern = re.compile(r'\&nbsp\;') # To identify th troublesome &nbsp characters
		self.subindexPattern = re.compile(r'\.\d+$') # to strip the .0 (etc) off the end of a property key
		self.textBuffer = '' # A text buffer
		self.skipTags = ['img', 'br', 'input'] # A list of tags in the HTML to ignore
		self.tranids = set()
		for key in self.defaultProps.keys():
			self.tranids.add(self.subindexPattern.sub('', key))

	def handle_starttag(self, tag, attrs):
		'''
		handle_starttag will identify and handle any Start Tags in the
		HTML
		'''
		
		# If an end_text is encountered
		self.__handle_end_text()
		
		stackWasEmpty = len(self.transtack) == 0 # If the stack is empty make it empty
		(id, doTranslate, isTranslated) = self.__get_id_and_do_translate_and_is_translated(attrs) # Split out the attributes
		
		# Split out the attributes
		if isTranslated or (not stackWasEmpty): 
			self.__push_new_transtate(tag, id, doTranslate) 
			
		# We are already formulating a snippet. We MUST emit something.
		if not stackWasEmpty: 

			# Get the Start Tag
			starttag = self.get_starttag_text()
			
			# Get the TranID
			starttag = self.tranidPattern.sub('', starttag)
			
			self.snippet += starttag # Continue with the Snippet Creation
			
	def __get_id_and_do_translate_and_is_translated(self, attrs):
		'''
		__get_id_and_do_translate_and_is_translated will take the ID and
		verify it is translated
		'''
		
		# Set the Defaults needed
		id = None 
		doTranslate = True
		isTranslated = False
		
		# Split out the info from the Attributes, compare them, identify needed and necessary issues
		for pair in attrs:
			
			if pair[0] == "id":
				id = pair[1]
				
				if id in self.tranids:
					isTranslated = True
					
			elif pair[0] == "class":
				clazz = pair[1]
				
				if self.notranslatePattern.search(clazz):
					doTranslate = False
				
		return (id, doTranslate, isTranslated) # Return the necessary items to continue the process
	
	def __push_new_transtate(self, tag, id, doTranslate):
		'''
		__push_new_transtate will push the new translation into the files
		'''
		
		if len(self.transtack) > 0:
			self.transtack[-1].childPointer += 1 # this tag is a child of the enclosing tag
			
		if not tag.lower() in self.skipTags:
			transtate = Tran_State(tag, id, doTranslate)
			self.transtack.append(transtate)

	def handle_endtag(self, tag):
		'''
		handle_endtag will handle any of the end tags in the HTML file
		'''
		
		# If an end_text is encountered
		self.__handle_end_text()
		
		
		if self.is_making_snippet():
			transtate = self.transtack.pop()
			
			# we are still formulating the snippet
			if self.is_making_snippet():
				self.snippet += "</%s>" % tag
				
			else: # we've finished the snippet.  Emmit.
				self.__property_file_whole.append("%s=%s" % (transtate.tranId, self.snippet))
				self.snippet = ''
				
	def is_making_snippet(self):
		'''
		is_making_snippet answers the question, are we maing a snippet?
		'''
		
		return len(self.transtack) > 0
	
	def handle_data(self, data):
		'''
		handle_data handles the data
		'''
		
		self.textBuffer += data
		
	def handle_charref(self, name):
		'''
		handle_charref handles the character references
		'''
		
		self.textBuffer += name
		
	def handle_entityref(self, name):
		'''
		handle_entityref handles the entity references
		'''
		
		self.textBuffer += "&" + name + ";"
		
	def __handle_end_text(self):
		'''
		__handle_end_text will handle any of the end text items 
		encountered to build the html snippet
		'''
		
		# Initialize Variables
		text = self.textBuffer
		self.textBuffer = ''
		
		# While making a snippet
		if text != '' and self.is_making_snippet():
			trankey = self.get_next_tran_key()
			x = text.strip()
			
			if self.transtack[-1].doTranslate:
				
				try: # If the trankey does not exist in the Localized File
					x = self.props[trankey]
					
				except KeyError:
					
					if len(self.spaceEntityPattern.sub('', text).strip()) > 0:
						
						try: # We let the user know that there is a missing Tran Key. bit we found an equivelent in the Default (English) that we will use
							x = self.defaultProps[trankey]
							### Logging
							LOGGING = open('/home/sandbox/SCRIPT_RUN.LOG', 'a') #Log file location
							LOG_ME = "Something Missing from the Language Property File -- BUT -- found in Default (English) Property File:\t%s\n\n" % trankey
							print LOG_ME
							LOGGING.write(LOG_ME)
							LOGGING.close()
														
						except KeyError:
							### Logging
							LOGGING = open('/home/sandbox/SCRIPT_RUN.LOG', 'a') #Log file location
							LOG_ME = "Missing key that that exists but not in the Properties Files:\t%s\n\n" % trankey
							print LOG_ME
							LOGGING.write(LOG_ME)
							LOGGING.close()

			# Continue Building the Snippet with either the Localized Version or the English Version				
			self.snippet += x
		
	def get_next_tran_key(self):
		'''
		get_next_tran_key will iterate and provide the next Translation Key
		'''
		
		transtate = self.transtack[-1]
		trankey = "%s.%i" % (transtate.tranId, transtate.childPointer)
		transtate.childPointer += 1
		
		return trankey
		
	def make_file(self):
		'''
		make_file makes the new (.new) Properties Files by creating 
		the Physical File on the Drive in the right place, then by 
		including all the stuff we have been collecting in the snippet.
		'''
			
		N = open(self.__new_file, 'w')
		
		for write_me in self.__property_file_whole:
			
			N.write(write_me + "\n")
			
		N.close()
	
if __name__ == '__main__':
	'''
	The MAIN section of the program does 4 things:
	#1 we get the user input on the location of the files
	#2 we pull the list of files, both property files and html files
	#3 we then create the new property files with the concantinated strings
	'''
	
	# First we get the User Input
	GUI = Get_User_Input()
	
	# Next we Pull the lists of HTML and Property Files
	PF = Pull_Files(GUI.get_path())
	
	# Then we concantinate the new strings and create a new set of files
	PACS = Pull_And_Concant_Strings(PF.get_html(), PF.get_properties())
	
	# Last we rename the OLD files to ".OLD" and the ".NEW" files to the 
	# regular file name
	### When we are sure, we will remove the ".OLD" files, so if we miss
	### something, or have other issues, we have the fall back.
