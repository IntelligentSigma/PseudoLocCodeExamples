# Created by David Mamanakis

targetFolder = 'target'

module.exports = (log, fs, async, path, utils, defaultAppName) ->
  # Local Functions
  addReadmeFile = (basePath) ->
    (cb) ->
      log "Add README file with encoding instructions"
      contents = "Please return translated files in native UTF-8 format WITHOUT any unicode escaped characters."
      utils.run "echo #{contents} > #{basePath}/README", cb

  # Converts a json file to a properties file and places the properties file in the targetFolder
  convertJSONtoProp = (baseSrcPath) -> 
    (file, cb) ->
      propFileName = "#{targetFolder}/#{defaultAppName}/#{file.replace('./','').replace('.json', '.properties')}"
      propDir = path.dirname propFileName
      file = path.resolve baseSrcPath, file

      async.waterfall [
        (cb) ->
          if not fs.existsSync(propDir)
            utils.run "mkdir -p #{propDir}", cb
          else
            cb()
        , (cb) -> 
          fs.readFile file, 'utf8', cb
        , (jsonFile, cb) ->
          json = JSON.parse jsonFile
          props = []
          utils.objectToProps '', props, json
          cb null, props
        , (props, cb) ->
          fs.writeFile propFileName, props.join('\n'), 'utf8', cb
      ], (err) ->
        if err
          log "Error creating the '#{propFileName}' file: #{err}"
        else
          log "'#{propFileName}' was successfully written"
        cb err, propFileName

  # Converts a properties file to a json file and places the json file back in the src tree where it's english counterpart came from
  convertProptoJSON = (lang, rootFolder, baseDestPath) ->
    (file, cb) ->
      toks = file.split '/'
      fileEnd = if lang? then "_#{lang}.json" else ".json"
      destFile = (toks[1..].join '/').replace /(_en)?.properties/, fileEnd
      destFile = path.resolve baseDestPath, destFile
      async.waterfall [
        (cb) -> 
          fs.readFile "#{rootFolder}/#{file}", 'utf8', cb
        , (propFile, cb) ->
          json = utils.propStringToObject(propFile)
          cb null, JSON.stringify(json, null, 4)
        , (jsonString, cb) ->
          fs.writeFileSync destFile, jsonString, 'utf8'
          cb null
      ], (err) ->
        if err
          log "ERROR creating the '#{destFile}' file: #{err}"
        cb err, destFile

  mkDir = (baseDestPath) ->
    (file, cb) ->
      thePath = path.resolve baseDestPath, path.dirname(file)
      utils.run "mkdir -p #{thePath}", ->
        cb()

  # Return public interface
  return {
    convertArchiveToJSON: (options) ->
      log "Convert properties files to json..."
      convertedTarget = "#{targetFolder}/_converted"
      archiveName = options.zipName ? null
      if archiveName is null
        throw new Error('zipName is a required parameter and should refer to the zip archive that contains the translations to convert')
      lang = options.languageCode ? null
      if lang is null
        log "WARNING: No 'lang' parameter was given. Converting files without inserting a lang code into file name."

      async.waterfall [
        (cb) ->
          log "Create import target folder: #{targetFolder}"
          utils.run "rm -rf #{targetFolder}; mkdir -p #{targetFolder}", cb
        , (cb) ->
          log "Unzip '#{archiveName}' archive into target folder"
          utils.run "unzip -q #{archiveName} -d #{targetFolder}; mkdir -p #{convertedTarget}", ->
            cb()
        , (cb) ->
          log "Move files back to their src folders"
          utils.run "cd #{targetFolder}; find . -name '*.properties'", (output) ->
            files = output.split("\n")
            files = files[0...files.length-1] #remove empty entry at end of array

            async.map files, mkDir(convertedTarget), (err) ->
              async.map files, convertProptoJSON(lang, targetFolder, convertedTarget), (err, jsonFiles) ->
                cb err
      ], (error) ->
        if error? and error.length isnt 0
          log "Translation convert FAILED: #{error}"
        else
          log "Translations were successfully converted from the #{archiveName} archive and placed in '#{convertedTarget}'."
        if options?.cb? then options.cb()

    exportEnglish: (options) ->
      log "Exporting english i18n files for '#{defaultAppName}'..."
      archiveName = "#{defaultAppName}_translations.zip"
      baseAppPath = options.baseAppPath ? "."

      async.waterfall [
        (cb) ->
          log "Create export target folder: #{targetFolder}"
          utils.run "rm -rf #{targetFolder}; mkdir -p #{targetFolder}/#{defaultAppName}", cb
        , addReadmeFile(targetFolder)
        , (cb) ->
          log "Pull list of all of the english i18n files"
          log "find #{baseAppPath}/locales #{baseAppPath}/assets/js -name '*_en.json'"
          utils.run "cd #{baseAppPath}; find ./locales ./assets/js -name '*_en.json'", (output) ->
            files = output.split("\n")
            log files
            files = files[0...files.length-1] #remove empty entry at end of array
            async.map files, convertJSONtoProp(baseAppPath), (err, propFiles) ->
              cb null, propFiles
        , (propFiles, cb) ->
          log "Create archive file: #{targetFolder}/#{archiveName}"
          utils.run "cd #{targetFolder}; zip -q -r #{archiveName} ./*", cb
      ], (error) ->
        if error? and error.length isnt 0
          log "Translation export failed: #{error}"
        else
          log "Translations were successfully exported and the #{targetFolder}/#{archiveName} was created."
        if options?.cb? then options.cb()

    exportAll: (options) ->
      log "Exporting all i18n properties files for '#{defaultAppName}'..."
      archiveName = "#{defaultAppName}_propertiesAll.zip"
      baseAppPath = options.baseAppPath ? "."

      async.waterfall [
        (cb) ->
          log "Create export target folder: #{targetFolder}"
          utils.run "rm -rf #{targetFolder}; mkdir -p #{targetFolder}/#{defaultAppName}", cb
        , addReadmeFile(targetFolder)
        , (cb) ->
          log "Pull list of all of the english i18n files"
          log "find #{baseAppPath}/locales #{baseAppPath}/assets/js -name '*_??.json'"
          utils.run "cd #{baseAppPath}; find ./locales ./assets/js -name '*_??.json'", (output) ->
            files = output.split("\n")
            files = files[0...files.length-1] #remove empty entry at end of array
            log "Found #{files.length} files"
            async.map files, convertJSONtoProp(baseAppPath), (err, propFiles) ->
              cb null, propFiles
        , (propFiles, cb) ->
          log "Create archive file: #{targetFolder}/#{archiveName}"
          utils.run "cd #{targetFolder}; zip -q -r #{archiveName} ./*", cb
      ], (error) ->
        if error? and error.length isnt 0
          log "Translation export failed: #{error}"
        else
          log "Translations were successfully exported and the #{targetFolder}/#{archiveName} was created."
        if options?.cb? then options.cb()

    importTranslations: (options) ->
      log "Import translations files for '#{defaultAppName}'..."
      baseAppPath = options.baseAppPath ? "."
      archiveName = options.zipName ? null
      if archiveName is null
        throw new Error('zipName is a required parameter and should refer to the zip archive that contains the translations to import')
      lang = options.languageCode ? null
      if lang is null
        throw new Error('languageCode is a required parameter and should contain the language code of the files you are importing (e.g., fr, es, etc)')

      async.waterfall [
        (cb) ->
          log "Create import target folder: #{targetFolder}"
          utils.run "rm -rf #{targetFolder}; mkdir -p #{targetFolder}", cb
        , (cb) ->
          log "Checking type of archive #{archiveName}"
          if fs.statSync(archiveName).isDirectory()
            log "zipName #{archiveName} is a directory, copying contents into target folder instead of unzipping"
            # normalize directory name, removing trailing slashes
            archiveName = path.resolve('', archiveName)
            utils.run "cp -R #{archiveName} #{targetFolder}", ->
              cb()
          else
            log "Unzip '#{archiveName}' archive into target folder"
            utils.run "unzip -q #{archiveName} -d #{targetFolder}", ->
              cb()
        , (cb) ->
          log "Verify archive format"
          folderName = path.basename archiveName, '.zip'
          rootFolder = "#{targetFolder}/#{folderName}/#{defaultAppName}_translations/#{defaultAppName}"
          if not fs.existsSync(rootFolder)
            cb("Invalid archive format: '#{rootFolder}' folder does not exist")
          else
            log "Archive format valid.  Importing files from: '#{rootFolder}'"
            cb(null, rootFolder)
        , (rootFolder, cb) ->
          log "Move files back to their src folders"
          utils.run "cd #{rootFolder}; find . -name '*.properties'", (output) ->
            files = output.split("\n")
            files = files[0...files.length-1] #remove empty entry at end of array
            async.map files, convertProptoJSON(lang, rootFolder, baseAppPath), (err, jsonFiles) ->
              cb err
      ], (error) ->
        if error? and error.length isnt 0
          log "Translation import FAILED: #{error}"
        else
          log "Translations were successfully imported from the #{archiveName} archive."
        if options?.cb? then options.cb()

    createPseudoLoc: (options) ->
      pseudo = require("./pseudo-loc.js")()
      log "Creating pseudo-locale for '#{defaultAppName}'..."
      baseAppPath = options.baseAppPath ? "."
      localeDirectory = options.localeDir ? "#{baseAppPath}/locales"
      modulesDirectory = options.modulesDir ? "#{baseAppPath}/assets/js/modules"
      angularDirectory = options.modulesDir ? "#{baseAppPath}/assets/js/angular"
      async.parallel [
        (cb) ->
          log "Generating pseudo-locale files in directory: #{localeDirectory}"
          ret = pseudo.execute localeDirectory
#          log "#{localeDirectory} returned #{ret}"
          cb(null, ret)
      , (cb) ->
          log "Generating pseudo-locale files in directory: #{modulesDirectory}"
          ret = pseudo.execute modulesDirectory
#          log "#{modulesDirectory} returned #{ret}"
          cb(null, ret)
      , (cb) ->
          log "Generating pseudo-locale files in directory: #{angularDirectory}"
          ret = pseudo.execute angularDirectory
#          log "#{angularDirectory} returned #{ret}"
          cb(null, ret)
      ], (error, results) ->
        if error? and error.length isnt 0
          log "Pseudo-locale generation FAILED: #{error}"
        else
#          log "Pseudo-locale generation SUCCEEDED"
          if results[0] isnt true || results[1] isnt true
            log "Result status of task: #{results}"
          else
            log "Pseudo-locale files were successfully created."
          if options?.cb? then options.cb(results[0] && results[1])
  }
