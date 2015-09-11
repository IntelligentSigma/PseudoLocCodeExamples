#!/usr/bin/env python
# -*- coding: utf-8 -*-

####################################################################################
##
##	File: concant_properties.py
##	Authors: Clinton De Young, Tyler Peterson and Dave Mamanakis
##	Date: August 16, 2010
##
##	-------------------------------------------------------------------------------
##	Description: Change csv files into property files. CSV to key/value.
##
####################################################################################

import codecs
import os
import os.path
import shutil

COMMA_CHARACTER = 'COMMA_CHARACTER'
DOUBLE_DOUBLE_QUOTE = 'DOUBLE_DOUBLE_QUOTE'

# Input file
inputFolder = 'input'
inFiles = os.listdir(inputFolder)

# Setup the output folder so it exists and is empty
outputFolder = 'output'
if os.path.isdir(outputFolder):
  shutil.rmtree(outputFolder)
os.makedirs(outputFolder)

for inFile in inFiles:
  language = inFile.split('.')[0][13:] #pull the language out of file name 'translations_en.csv'
  #print("language=", language)

  # Read in the source csv file
  #f = codecs.open(inputFolder + "/" + inFile, 'r', 'utf-8')
  f = codecs.open(inputFolder + "/" + inFile, 'r')
  lines = f.readlines()
  f.close()

  files = {}
  lineCount = 0

  # Parse lines
  for line in lines:
    line = line.strip()

    if len(line) == 0:
      continue

    lineCount += 1

    # fix lines so that ',' characters appearing between double quotes don't get split on
    if line.find('"') != -1:
      line = line.replace('""', DOUBLE_DOUBLE_QUOTE)
      quotedStrings = line.split('"')
      if len(quotedStrings) == 3:
        quotedStrings[1] = quotedStrings[1].replace(",", COMMA_CHARACTER)
        line = '"'.join(quotedStrings)
      elif len(quotedStrings) != 1:
        print("UNKNOWN FORMAT FOR QUOTED STRING:", line)
      line = line.replace(DOUBLE_DOUBLE_QUOTE, '""')

    toks = line.split(',')
    key = toks[0]
    
    if '/static/help' in key or 'faq' in key or '/static/cmisrequestform.htm' in key or '/static/ordinancenotavailable.htm' in key: #skip properties files
      continue
    
    # add key entry if not already there
    if key not in files:
      files[key] = []

    # parse the file string into it's parts
    fileParts = key.split('/')
    fileNameWithExtension = fileParts[-1]
    fileName = fileNameWithExtension.split('.')[0]
    filePath = '/'.join(fileParts[0:len(fileParts) - 1])

    # set id to first part of token if second part is a number, otherwise set id to entire token value
    idIndex = toks[1].split('.')
    if '.properties' in key:
        childIndex = 0
        id = toks[1]
    else :
        try:
          childIndex = int(idIndex[1])
          id = idIndex[0]
        except:
          childIndex = 0
          id = toks[1]

    # add name/value pair entry for this line
    theValue = toks[3].replace(COMMA_CHARACTER, ',')
    if len(theValue) > 0 and theValue[0] == '"' :
      theValue = theValue[1:]
    if len(theValue) > 0 and theValue[-1] == '"' :
      theValue = theValue[0:-1]
    files[key].append({'id': id, 'childIndex': childIndex, 'value': theValue, 'fileName': fileName, 'filePath': filePath})

  print("Processed {0} lines in {1} file.".format(lineCount, inFile))

  # Output the processed file(s)
  for key in list(files.keys()):
    # sort the list by id so different languages will be in roughly the same order
    files[key].sort(key=lambda x: x['id'])

    # pull the first entry to get the file/path information
    firstEntry = files[key][0]

    isPropFile = False
    if '.properties' in key:
      # START CODE FOR OUTPUTING FILES IN FOLDER HIERARCHY
      # make sure folder exists for this file
      if not os.path.isdir(outputFolder + firstEntry['filePath']) :
        #print("Creating dir: " + outputFolder + firstEntry['filePath'])
        os.makedirs(outputFolder + firstEntry['filePath'])

      # create file and write name value pairs to it
      thisFilePath = outputFolder + firstEntry['filePath'] + '/' + firstEntry['fileName']
      if language != 'en':
          thisFilePath += '_' + language
      thisFilePath += '.properties'
	  
      isPropFile = True
      # END CODE FOR OUTPUTING FILES IN FOLDER HIERARCHY
    else:
      # START CODE FOR OUTPUT A FLAT FILE SYSTEM WITH ALL PROPERTY FILES IN ONE FOLDER
      thisFilePath = outputFolder + '/' + firstEntry['fileName']
      if language != 'en':
        thisFilePath += '_' + language
      thisFilePath += '.properties'

      if os.path.isfile(thisFilePath):
        print('Duplicate file name found: ' + firstEntry['filePath'] + "/" + firstEntry['fileName'])
        continue
      # END CODE FOR OUTPUT A FLAT FILE SYSTEM WITH ALL PROPERTY FILES IN ONE FOLDER

    #o = codecs.open(thisFilePath, 'w', 'utf-8')
    o = codecs.open(thisFilePath, 'w')
    for entry in files[key]:
      name = "{0}{1}".format(entry['id'], "" if isPropFile else "." + str(entry['childIndex']))
      #name = "{0}{1}".format(entry['id'], isPropFile ? "" : "." + entry['childIndex'])
      o.write('{0}={1}\n'.format(name, entry['value']))
    o.close()
