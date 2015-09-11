#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################################################
##
##	File: concant_properties.py
##	Authors: Clinton De Young, Tyler Peterson and Dave Mamanakis
##	Date: November 2, 2010
##
##	-------------------------------------------------------------------------------
##	Description: Pseudo Localizes all strings in the code bases
##
####################################################################################

import sys
import getopt
import os
import io
import codecs
from subprocess import Popen, PIPE
import re
import shutil
from exceptions import IOError
from random import randint
from Properties import Properties
from pprint import pformat
from HTMLParser import HTMLParser

class PseudoTranslate(object):
	'''
	The PseudoTranslate class takes a string, converts it to a pseudo
	localized representation, and then regurgitates it as a flowing mess to
	the caller via a get method.
	'''
	
	# This is a list of the supported targets.  Whenever you accept user 
	# input, you should validate against this list to make sure that they 
	# have selected a valid target before proceeding.  The "all" target 
	# will generate a mixed language build.
	__supported_targets = [
		'ja_JP',
		'ko_KR',
		'zh_TW',
		'de_DE',
		'fr_FR',
		'it_IT',
		'es_MX',
		'pt_BR',
		'ru_RU',
		'all'
	]
	
	# Displaying any supported language regardless of the language your 
        # UI is set to, we should test pseudo localized builds using all 
        # supported languages
	__mixed_language_strings = [
		# Japanese Chars
		'鼻毛:',
		'指先:',
		'眉毛:',
		'ひれ:',
		'ヘビ:',
		'カブ:',
		'子供:',
		'日本:',
		'言語:',
		'馬鹿:',
		
		# Korean Chars
		'영어:',
		'소금:',
		'트럭:',
		'히피:',
		'포크:',
		'토성:',
		'아픈:',
		'오리:',
		'얼음:',
		'극지:',
		
                # DO NOT FORGET: There are several TYPES of Chinese Characters:
                # CJK-Ext.A, CJK-Ext.B, CJK-Ext.C, CJK-Ext.D (They may require different fonts for support).
		# Chinese Chars
		'孩子:',
		'嬉皮:',
		'雲彩:',
		'占星:',
		'胡說:',
		'膀胱:',
		'沙拉:',
		'蠢貨:',
		'烘烤:',
		'蝸牛:',
		
		# Russian Chars
		'да:',
		'ща:',
		'по:',
		'не:',
		'из:',
		'за:',
		'Ий:',
		'дя:',
		'ИФ:',
		'ья:',
		
		# Latin Chars
		'Ãé:',
		'Ûç:',
		'Çó:',
		'Ñá:',
		'Ýň:',
		'Èç:',
		'Ìë:',
		'Îú:',
		'Öà:',
		'Ūê:',
	]
	
	# In a pseudo localized build, all vowels and some consonants will be 
	# replaced with extended characters that look similar.  This helps test
	# whether or not a string has been properly placed in resource files.
	# Regardless of the type of pseudo build you do (all languages vs. only 
	# the target UI language), this hash will be used.
	__replacement_characters = {
		'A':['À','Á','Â','Ã','Ä','Å','Ā','Ą','Ă','Ѧ'],
		'C':['Ç','Ć','Č','Ĉ','Ċ'],
		'D':['Ď','Đ'],
		'E':['È','É','Ê','Ë','Ē','Ę','Ě','Ĕ','Ė','Э','Ѯ'],
		'G':['Ĝ','Ğ','Ġ','Ģ'],
		'H':['Ĥ','Ħ'],
		'I':['Ì','Í','Î','Ï','Ī','Ĩ','Ĭ','Į','İ'],
		'J':['Ĵ'],
		'K':['Ķ'],
		'L':['Ł','Ľ','Ĺ','Ļ','Ŀ'],
		'N':['Ñ','Ń','Ň','Ņ','Ŋ','П','И'],
		'O':['Ò','Ó','Ô','Õ','Ö','Ø','Ō','Ő','Ŏ'],
		'R':['Ŕ','Ř','Ŗ','Я'],
		'S':['Ś','Š','Ş','Ŝ','Ș'],
		'T':['Ť','Ţ','Ŧ','Ț'],
		'U':['Ù','Ú','Û','Ü','Ū','Ů','Ű','Ŭ','Ũ','Ų','Ц'],
		'V':['Ѵ'],
		'W':['Ŵ','Ш','Щ','Ѡ'],
		'X':['Ж'],
		'Y':['Ý','Ŷ','Ÿ'],
		'Z':['Ź','Ž','Ż'],
		'a':['à','á','â','ã','ä','å','ā','ą','ă',''],
		'b':['Б','Ъ','Ь','Ѣ'],
		'c':['ç','ć','č','ĉ','ċ'],
		'd':['ď','đ'],
		'e':['è','é','ê','ë','ē','ę','ě','ĕ','ė'],
		'f':['ƒ'],
		'g':['ĝ','ğ','ġ','ģ'],
		'h':['ĥ','ħ'],
		'i':['ì','í','î','ï','ī','ĩ','ĭ','į','ı'],
		'j':['ĵ'],
		'k':['ķ','ĸ'],
		'l':['ł','ľ','ĺ','ļ','ŀ'],
		'n':['ñ','ń','ň','ņ','ŉ','ŋ'],
		'o':['ò','ó','ô','õ','ö','ø','ō','ő','ŏ','Ф'],
		'r':['ŕ','ř','ŗ','я'],
		's':['ś','š','ş','ŝ','ș'],
		't':['ť','ţ','ŧ','ț'],
		'u':['ù','ú','û','ü','ū','ů','ű','ŭ','ũ','ų'],
		'v':['ѵ'],
		'w':['ŵ'],
		'y':['ý','ÿ','ŷ','Ч','Ѱ'],
		'z':['ž','ż','ź'],
	}
	
	__pseudo_string = ""
	__string_package = ""
	__target = ""
	
	def __init__(self, str):
		
		# If the user has specified a valid language, process the 
		# request. Otherwise, raise an exception.
		self.__str = str
		self.__string_package = self.__mixed_language_strings
		self.__storage = {}
		
		self.__pseudo_localize()
					
	def __pseudo_localize(self):
		''' 
		__pseudo_localize does the work of making the Pseudo Strings
		'''
		
		temp = ''
		s = 0
		grab_em = ''
		
		# Replace any characters that exist as keys in the 
		# self.__replacement_characters hash with a random character 
		# from the appropriate value list.
			
		set_me = False
		num = 0
		
		# We had to account for some of the escaped characters, "&lt;"
		for char in self.__str:
			
			if char == "&":
				num += 1
				set_me = True
				
			if char == ";":
				set_me = False
		
			if set_me is True:
				temp += char
				continue
			
			else:
				if self.__replacement_characters.has_key(char):
					temp += self.__replacement_characters[char][randint(0, len(self.__replacement_characters[char]) - 1)]
			
				else:
					temp += char
			
		# Expand the string
		self.__pseudo_string = self.__expand_string(temp, num)
		
	def __expand_string(self, str, num):
		'''
		expand_string(str) - Take a string as an argument and adds 
		padding onto the end according to the following rules:

		English String		|	Expansion Factor
		1 - 5			|	of about 15 characters
		6 - 25			|	of about 2.2 times
		26 - 40			|	of about 1.9 times
		41 - 70			|	of about 1.7 times
		71 +			|	of about 1.5 times
		'''
		
		end_text = self.__string_package[randint(0, len(self.__string_package) - 1)]
		gorgon = ''
		alpha = ''
		beta = ''
		gamma = ''
		
		# You have to convert the string to unicode in order to count 
		# the number of characters since Python only counts bytes in 
		# UTF-8 strings.
		length = len(unicode(str, 'utf8'))
		existing_text = length + len(unicode(end_text, 'utf8'))

		if num > 0:
			times = num * 6
			minus = length - times
			length = minus
			
			if length == 0:
				end_text = ''
		
		################################################################
		### Use this if you want to add extensions to the end of     ###
		### each of the words in a paragraph, but the end text at    ###
		### the end of the paragraph, not the word.                  ###
		################################################################
		alterations = str.split()
		
		for alpha in alterations:
			length = len(unicode(alpha, 'utf8'))
			existing_text = length + len(unicode(end_text, 'utf8'))
				
			if length <= 0:
				expansion = ''
			
			elif length > 0 and length <= 5:
				expansion = '_' * (9 - existing_text)
				
			elif length >= 6 and length <= 25:
				expansion = '_' * (int(length * 1.9) - existing_text)
				
			elif length >= 26 and length <= 40:
				expansion = '_' * (int(length * 1.6) - existing_text)
				
			elif length >= 41 and length <= 70:
				expansion = '_' * (int(length * 1.3) - existing_text)
				
			else:
				expansion = '_' * (int(length * 1.0) - existing_text)
			
			beta = alpha + expansion + ' '
			
			gamma += beta
			
		gorgon = gamma + ":" + end_text
			
		################################################################
		### Use this if you want to add extensions to the end of the ###
		### paragraph.                                               ###
		################################################################
		#if length <= 0:
			#expansion = ''
		
		#elif length > 0 and length <= 5:
			#expansion = '_' * (15 - existing_text)
			
		#elif length >= 6 and length <= 25:
			#expansion = '_' * (int(length * 2.2) - existing_text)
			
		#elif length >= 26 and length <= 40:
			#expansion = '_' * (int(length * 1.9) - existing_text)
			
		#elif length >= 41 and length <= 70:
			#expansion = '_' * (int(length * 1.7) - existing_text)
			
		#else:
			#expansion = '_' * (int(length * 1.5) - existing_text)
		
		#gorgon = str + expansion + end_text
			
		return gorgon

	def get_pseudo_str(self):
		return self.__pseudo_string
		
	def set_pseudo_str(self, str):
		self.__str = str
		self.__pseudo_localize()
		
class FilesAndStrings(object):
	'''
	The FilesAndStrings class recursively parses the specfied path and
	returns all localizable properties files code base.
	'''
	
	def __init__(self, path):
		self.__path = path
		self.__files = []
		self.__complete_files = []
		self.__translations = []
		self.__filter_1_files = [] # Only the .properties files
		self.__filter_2_files = []
		self.__filter_3_files = []
		self.__filter_4_files = []
		self.__temporary_debug_1 = []
		self.__temporary_debug_2 = []
		
		# We set this list for all the current languages we use in the
		# product we are only interested in the ENGLISH file for this 
		# task
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
			'_th',
			'_nl',
			'_BR',
			'_CN',
			'_JP',
			'_KR',
			'_TW',
			'_eo',
			'_EO',
		] 
		
		self.__generate_file_list()
		self.__generate_string_list()
		
	def __generate_file_list(self):
		'''
		__generate_file_list gets a recursive list of HTML files from
		the directory specified in --path.
		'''
		
		cmd = "/usr/bin/find '%s' -iname '*.properties' -print" % self.__path 
		findProcess = Popen(cmd, shell=True, stdout=PIPE) 
		htmfiles = findProcess.communicate()[0]
		self.__files = htmfiles.split()
		
		for file in self.__files:
			
			# run the first bit of filtering to kill any foreign 
			# language or extra (non language) properties files, we
			# only need the English, localizeable files.
			if ".properties" in file:
				left, right = file.split(".", 1)
				check = left[-3:]
				double_check = left[-13:]
				
				# if the file name contains the last 3 chars of 
				# some foreign language indicator, ignore it.
				if check in self.__ignore: 
					continue
				
				# if this is the last bit on the file name,
				# ignore it.
				elif double_check == '_unicodeasian': 
					continue
					
				# anything in a snapshot directory, ignore it.
				elif 'SNAPSHOT' in file or 'target' in file: 
					continue
				
				# this should leave us with only the English, 
				# Localizeable properties files. Listed.
				else:
					self.__filter_1_files.append(file)
					
		# For (Frankie) only:
		# We filter anything except what is in the following directories
		# if they exist 
		for frankie in self.__filter_1_files:
			
			if 'www-catalogapi/trunk/www-catalogapi-domain/src/main/resources/bundles/' in frankie:
				self.__filter_2_files.append(frankie)
					
			elif 'www-searchapi/trunk/www-searchapi/src/main/resources/bundles/' in frankie:
				self.__filter_2_files.append(frankie)
					
			elif 'www-web/trunk/www-web-app/grails-app/i18n/' in frankie:
				self.__filter_2_files.append(frankie)
				
			else:
				continue
					
		# if we don't have anything in the second filter, fill it
		if not self.__filter_2_files: 
			
			self.__filter_2_files = self.__filter_1_files
					
		# For SISU or other related structures:
		# Removing any of the directories for foreign languages.
		for sisu in self.__filter_2_files:
			
			if 'de_DE' in sisu:
				continue
			
			elif 'es_ES' in sisu:
				continue
			
			elif 'fr_FR' in sisu:
				continue
			
			elif 'it_IT' in sisu:
				continue
			
			elif 'ja_JP' in sisu:
				continue
			
			elif 'ko_KR' in sisu:
				continue
			
			elif 'pt_BR' in sisu:
				continue
			
			elif 'ru_RU' in sisu:
				continue
			
			elif 'zh_TW' in sisu:
				continue
			
			elif 'eo_EO' in sisu:
				continue
			
			elif 'java' in sisu:
				continue
			
			elif 'en_US' in sisu:
				self.__filter_3_files.append(sisu)
			
			else:
				self.__complete_files.append(sisu)
				
		# put the filtered results into the final list
		if self.__filter_3_files:
			self.__complete_files = self.__filter_3_files
			
		# For Gadgets or other related structures:
		# Removing any of the non-language properties.		
		for gadget in self.__complete_files:
			if "langs" in gadget:
				self.__filter_4_files.append(gadget)
				
			else:
				continue
		
		if self.__filter_4_files:
			self.__complete_files = self.__filter_4_files
								
	def __generate_string_list(self):
		'''
		__generate_string_list gets a list of all the strings and IDs
		contained in the list of properties files.
		'''
		
		j = 0
		strings = {}
		faux = {}
		
		# Initialize the HTML Parser to read the HTML
		MHP = My_Html_Parser(); 
							
		# iterate the items in the files list to work on them
		for x_file in self.__complete_files:
			
			# Create the OutPut file name (the PSEUDO file)
			# From FLEX
			if "en_US" in x_file:
				new_file = x_file.replace("en_US", "eo_EO")
			
			#From Frankie	
			elif "www-searchapi" in x_file or "www-web" in x_file or "www-catalogapi" in x_file:
				new_file = x_file.replace(".properties", "_eo.properties")
				
			#From Gadgets	
			elif "langs" in x_file and ".properties" in x_file:
				new_file = x_file.replace(".properties", "_eo.properties")
				
			#From Classic	
			elif "localization" in x_file and ".properties" in x_file:
				new_file = x_file.replace(".properties", "_unicodeasian.properties")
				self.__temporary_debug_1.append(x_file)
				
			else:
				self.__temporary_debug_2.append(x_file)
				continue
			
			# Initialize the English Properties Files via this 
			# program (creates a Dictionary of the Properties)
			eng_props = Properties() 
			eng_props.load(open(x_file))
			# We get the Dictionary for the Default Properties File
			engProps = eng_props.getPropertyDict() 
			
			# Now we iterate the properties to make the list for 
			# PseudoLocalization
			for q in engProps:
				value = engProps[q]
				MHP.reset()
				MHP.my_init() 
				
				# We sometimes use "<" or ">" in our strings
				# This will filter them out for the HTML
				# Parser, to prevent errors.
				# If errors happen, modify this section
				if "<" in value or ">" in value:
					
					if value == "<<First Page":
						value = "&lt;&lt;First Page"
						# Make note of the pseudo 
						# localized string in the "faux"
						# dictionary
						p = PseudoTranslate(value)				
							
						# Continue Building the Snippet 
						# with either the Localized 
						# Version or the English Version				
						tran_tmp = p.get_pseudo_str()
						tmp_tran = tran_tmp.replace ("&lt;", "<")
						
					elif value == "Last Page>>":
						value = "Last Page&gt;&gt;"
						# Make note of the pseudo 
						# localized string in the "faux" 
						# dictionary
						p = PseudoTranslate(value)				
							
						# Continue Building the Snippet 
						# with either the Localized 
						# Version or the English Version				
						tran_tmp = p.get_pseudo_str()
						tmp_tran = tran_tmp.replace ("&gt;", ">")

						
					elif value == "<Previous":
						value = "&lt;Previous"
						# Make note of the pseudo 
						# localized string in the "faux"
						# dictionary
						p = PseudoTranslate(value)				
							
						# Continue Building the Snippet 
						# with either the Localized 
						# Version or the English Version				
						tran_tmp = p.get_pseudo_str()
						tmp_tran = tran_tmp.replace ("&lt;", "<")

						
					elif value == "Next>":
						value = "Next&gt;"
						# Make note of the pseudo 
						# localized string in the "faux"
						# dictionary
						p = PseudoTranslate(value)				
							
						# Continue Building the Snippet
						# with either the Localized 
						# Version or the English Version				
						tran_tmp = p.get_pseudo_str()
						tmp_tran = tran_tmp.replace ("&gt;", ">")

						
					elif value == "<Back":
						value = "&lt;Back"
						# Make note of the pseudo 
						# localized string in the "faux"
						# dictionary
						p = PseudoTranslate(value)				
							
						# Continue Building the Snippet
						# with either the Localized 
						# Version or the English Version				
						tran_tmp = p.get_pseudo_str()
						tmp_tran = tran_tmp.replace ("&lt;", "<")

					
					else:
						# Read the string into the HTML 
						# Parser
						MHP.feed(value) 
						tmp_tran = MHP.get_the_answer()
						
						if tmp_tran == '':
							MHP.my_init()
							MHP.reset()
							try_me = "<body>" + value + "</body>"
							MHP.feed(try_me)
							step_1 = MHP.get_the_answer()
							step_2 = step_1.replace("<body>","")
							step_3 = step_2.replace("</body>","")
							tmp_tran = step_3
							
							if tmp_tran == '':
								print x_file + "\n" + q + "=" + value
									
				else:
					# Make note of the pseudo localized 
					# string in the "faux" dictionary
					p = PseudoTranslate(value)				
						
					# Continue Building the Snippet with
					# either the Localized Version or the 
					# English Version				
					tmp_tran = p.get_pseudo_str()
												
				# Rebuild the format PROPERTY_ID = PROPERTY
				self.__translations.append(q + "=" + tmp_tran)	
						
			# Open the new output file, write it's new content
			N = codecs.open(new_file, 'w')
			
			print "this is #%s of %s files to do" % (j+1, len(self.__complete_files))
			
			j += 1
			
			for write_me in self.__translations:
				
				N.write(write_me + "\n")
				
			N.close()
			
			self.__translations = []
					
class GetUserInput(object):
	'''
	The GetUserInput class grabs command line arguments from the user and
	makes them available
	'''
	
	__path = ""
	
	def __init__(self):
		try:
			options, arguments = getopt.getopt(sys.argv[1:], 'hp:', ['help', 'path='])

		except getopt.GetoptError, e:
			print "A dark buzzard has fouled our breakfast bowl with the following droppings:\n"
			print e
			sys.exit(1)
			
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
		print '----------------------------------------------------------------------'
		print 'USAGE:\n'
		print '\n'
		print '-h, --help\tPrint this help message.'
		print '\n'
		print '-p, --path\tSpecify the path to pull the strings from.\n'
		print '\n'
		print 'Example: pseudo.py -p /home/billy/sandbox/code/\n'
		print '----------------------------------------------------------------------'
		
	def get_path(self):
		return self.__path

class InvalidTargetException(Exception):
	
	def __init__(self, value):
		self.parameter = value
	
	def __str__(self):
		return repr(self.parameter)
		
class My_Html_Parser(HTMLParser):
	'''
	This is the HTML Parsing Routine
	'''
	
	def my_init(self):
		'''
		my_init initializes for the HTML Parsing
		'''
		
		self.__property_file_whole = ''
		self.__the_return_value = ''
		self.__translation = ''
		self.snippet = '' 
		self.textBuffer = '' 
		self.__findTags = ['alt', 'title'] 
		
	def handle_starttag(self, tag, attrs):
		'''
		handle_starttag will identify and handle any Start Tags in the
		HTML
		'''
		
		# If an end_text is encountered
		self.__handle_end_text()
		
		# Get the Start Tag
		starttag = self.get_starttag_text()
		
		if starttag == '<Select>':
			a = starttag.replace("<","&lt;")
			b = a.replace(">","&gt;")
			starttag = b
			
			# Make note of the pseudo localized string in the "faux"
			# dictionary
			p = PseudoTranslate(starttag)				
								
			# Continue Building the Snippet with either the Localized
			# Version or the English Version				
			trantag = p.get_pseudo_str()
			
			#starttag = trantag + ">"
			starttag = trantag
			
		# We had to deal with "input" in the HTML
		for d in range(0, len(attrs)):
			
			spork, foon = attrs[d]
			
			if "input" in starttag:
				
				if spork == "type":
					
					if foon != "checkbox" and foon != "RADIO" and foon != "radio":
						self.__findTags.append("value")			
			
			if spork in self.__findTags:
				need_tran = foon			
				
				# Make note of the pseudo localized string in 
				# the "faux" dictionary
				p = PseudoTranslate(need_tran)				
								
				# Continue Building the Snippet with either the
				# Localized Version or the English Version				
				tranattr = p.get_pseudo_str()
			
				#attrs[d] = spork, tranattr
				after = spork + '="' + tranattr + '"'
				
				attrs[d] = spork, tranattr
				
				jumbo = []
				jumbo = attrs
				
				# Other issues to overcome with blank properties
				# or properties that had odd names (NULL, etc)
				for y in range(0, len(jumbo)+1):
					
					if y == 0:
						elmer, glue = attrs[y]
						
						try:
							temp = elmer + '="' + glue + '" '
							
						except:
							temp = elmer + '="None" '
						
						new_starttag = "<" + temp
						
					elif y > 0 and y < len(jumbo)-1:
						elmer, glue = attrs[y]
						
						try:
							if glue == '':
								
								temp = elmer + glue
								
							else:
								temp = elmer + '="' + glue + '" '
							
						except:
							temp = elmer + '="None" '
							
						new_starttag += temp
						
					elif y == len(jumbo)-1:
						elmer, glue = attrs[y]
						
						try:
							temp = elmer + '="' + glue + '"'
							
						except:
							temp = elmer + '="None" '
							
						new_starttag += temp
						
					elif y == len(jumbo):
						new_starttag += ">"
					
				starttag = new_starttag
				
				# We has other issues with "value"
				if "value" in self.__findTags:
					self.__findTags.remove("value")
		
		# Continue with the Snippet Creation
		self.snippet += starttag 
			
	def handle_endtag(self, tag):
		'''
		handle_endtag will handle any of the end tags in the HTML file
		'''
		
		# If an end_text is encountered
		self.__handle_end_text()
					
		# we are still formulating the snippet
		self.snippet += "</%s>" % tag
				
		#make the big picture
		self.__property_file_whole += (self.snippet)
		self.snippet = ''
					
	def __handle_end_text(self):
		'''
		__handle_end_text will handle any of the end text items 
		encountered to build the html snippet
		'''
		
		# Initialize Variables
		text = self.textBuffer
		self.textBuffer = ''
		
		# While making a snippet
		if text == '' or text == "?" or text == ":" or "|" in text:
			self.snippet += text
			
		else:
			x = text.strip()
			
			# Make note of the pseudo localized string in the "faux"
			# dictionary
			p = PseudoTranslate(x)				
								
			# Continue Building the Snippet with either the 
			# Localized Version or the English Version				
			self.__translation = p.get_pseudo_str()

			# Continue Building the Snippet with either the 
			# Localized Version or the English Version				
			self.snippet += self.__translation
			

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
					
	def get_the_answer(self):
		'''
		return the prop_translation
		'''
		
		return self.__property_file_whole
		
if __name__ == '__main__':
	
	# Get the user's input, i.e. the PATH to the files
	gui = GetUserInput()
	
	try:
		# Execute the routine to do all the work, passing the PATH
		fas = FilesAndStrings(gui.get_path())
		
	except Exception, e:
		print "Agghhh!  You've been attacked by a rabid snail, who's snarling: "
		print e
		sys.exit(1)
	
	
		
