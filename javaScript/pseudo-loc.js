//Created by David Mamanakis

module.exports = function() {
  var fs = require('fs');
  var path = require('path');
  var filler = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.';
  var fillFrom = 0;
  var keyHashCode = 0;

  var replacementMap = {};
  replacementMap.A = ['À','Á','Â','Ã','Ä','Å','Ā','Ą','Ă','Ѧ'];
  replacementMap.C = ['Ç','Ć','Č','Ĉ','Ċ'];
  replacementMap.D = ['Ď','Đ'];
  replacementMap.E = ['È','É','Ê','Ë','Ē','Ę','Ě','Ĕ','Ė','Э','Ѯ'];
  replacementMap.G = ['Ĝ','Ğ','Ġ','Ģ'];
  replacementMap.H = ['Ĥ','Ħ'];
  replacementMap.I = ['Ì','Í','Î','Ï','Ī','Ĩ','Ĭ','Į','İ'];
  replacementMap.J = ['Ĵ'];
  replacementMap.K = ['Ķ'];
  replacementMap.L = ['Ł','Ľ','Ĺ','Ļ','Ŀ'];
  replacementMap.N = ['Ñ','Ń','Ň','Ņ','Ŋ','П','И'];
  replacementMap.O = ['Ò','Ó','Ô','Õ','Ö','Ø','Ō','Ő','Ŏ'];
  replacementMap.R = ['Ŕ','Ř','Ŗ','Я'];
  replacementMap.S = ['Ś','Š','Ş','Ŝ','Ș'];
  replacementMap.T = ['Ť','Ţ','Ŧ','Ț'];
  replacementMap.U = ['Ù','Ú','Û','Ü','Ū','Ů','Ű','Ŭ','Ũ','Ų','Ц'];
  replacementMap.V = ['Ѵ'];
  replacementMap.W = ['Ŵ','Ш','Щ','Ѡ'];
  replacementMap.X = ['Ж'];
  replacementMap.Y = ['Ý','Ŷ','Ÿ'];
  replacementMap.Z = ['Ź','Ž','Ż'];
  replacementMap.a = ['à','á','â','ã','ä','å','ā','ą','ă'];
  replacementMap.b = ['Б','Ъ','Ь','Ѣ'];
  replacementMap.c = ['ç','ć','č','ĉ','ċ'];
  replacementMap.d = ['ď','đ'];
  replacementMap.e = ['è','é','ê','ë','ē','ę','ě','ĕ','ė'];
  replacementMap.f = ['ƒ'];
  replacementMap.g = ['ĝ','ğ','ġ','ģ'];
  replacementMap.h = ['ĥ','ħ'];
  replacementMap.i = ['ì','í','î','ï','ī','ĩ','ĭ','į','ı'];
  replacementMap.j = ['ĵ'];
  replacementMap.k = ['ķ','ĸ'];
  replacementMap.l = ['ł','ľ','ĺ','ļ','ŀ'];
  replacementMap.n = ['ñ','ń','ň','ņ','ŉ','ŋ'];
  replacementMap.o = ['ò','ó','ô','õ','ö','ø','ō','ő','ŏ','Ф'];
  replacementMap.r = ['ŕ','ř','ŗ','я'];
  replacementMap.s = ['ś','š','ş','ŝ','ș'];
  replacementMap.t = ['ť','ţ','ŧ','ț'];
  replacementMap.u = ['ù','ú','û','ü','ū','ů','ű','ŭ','ũ','ų'];
  replacementMap.v = ['ѵ'];
  replacementMap.w = ['ŵ'];
  replacementMap.y = ['ý','ÿ','ŷ','Ч','Ѱ'];
  replacementMap.z = ['ž','ż','ź'];

  var mixedLangs = [
    // Japanese Chars
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

    // Korean Chars
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

    // Chinese Chars
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

    // Russian Chars
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

    // Latin Chars
    'Ãé:',
    'Ûç:',
    'Çó:',
    'Ñá:',
    'Ýň:',
    'Èç:',
    'Ìë:',
    'Îú:',
    'Öà:',
    'Ūê:'
  ];

  // local functions
  var createEOPropFile, makeEOProp, convertProp, createFiller, computeHash;

  // creates pseudo locale file from one english locale file
  createEOPropFile = function(engPropFileName) {
    var engProps,eoProps,eoPropFileName,fileContents;
    eoPropFileName = path.join(path.dirname(engPropFileName) + path.sep, path.basename(engPropFileName,'_en.json') + '_eo.json');

    try {
      fileContents = fs.readFileSync(engPropFileName, 'utf8');
      engProps = JSON.parse(fileContents);

      eoProps = {};
      var key;
      for(key in engProps) {
        // make sure we aren't trying to convert any inherited properties
        if(engProps.hasOwnProperty(key)) {
          keyHashCode = computeHash2(key);
          eoProps[key] = makeEOProp(engProps[key]);
        }
      }
      // stringify with proper formatting (2 spaces for tab)
      eoProps = JSON.stringify(eoProps,null,2);

      fs.writeFileSync(eoPropFileName,eoProps);
    } catch(err) {
      throw err;
    }
  };
  // converts characters, adds length, and adds CKJ characters for a single string in a locale
  makeEOProp = function(enProp) {
    var newValue,suffix,expansion,length,combinedLength;

    newValue = convertProp(enProp);
    suffix = mixedLangs[keyHashCode % mixedLangs.length];

    length = newValue.length;
    combinedLength = length + suffix.length;

    // add extra length to each string
    if(length <= 0) {
      expansion = '';
    } else if(length > 0 && length <= 5) {
      expansion = createFiller(newValue, 9 - combinedLength);
    } else if(length >= 6 && length <= 25) {
      expansion = createFiller(newValue, parseInt(length * 1.9) - combinedLength);
    } else if(length >= 26 && length <= 40) {
      expansion = createFiller(newValue, parseInt(length * 1.6) - combinedLength);
    } else if(length >= 41 && length <= 70) {
      expansion = createFiller(newValue, parseInt(length * 1.3) - combinedLength);
    } else {
      expansion = createFiller(newValue, length - combinedLength);
    }

    return newValue + expansion + ' :' + suffix;
  };
  computeHash2 = function(str){
    var hash = 0, myChar;
    if (str.length == 0) return hash;
    for (var i = 0; i < str.length; i++) {
      myChar = str.charCodeAt(i);
      hash = ((hash<<5)-hash)+myChar;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  };
  // performs the character replacement for pseudo locale creation
  convertProp = function(prop) {
    var isInTag = false,
        isInVar = false,
        ret = '';
    // ??? remove any html encoding from file

    // TODO every tag should be treated separately
    var propLength = prop.length;
    for(var i=0;i<propLength;i++) {
      var current = prop[i],
          next = prop[i+1];

      // ignore HTML tags (but not content inside opening and closing tags,
      // e.g. for <p>Something</p> ignores <p> and </p> but not "Something")
      // also inside replacement variables, e.g. %{myVar}
      if (isInTag) {
        if (current === '>') {
          isInTag = false;
        }
        ret += current;
        continue;
      } else if (isInVar) {
        if (current === '}') {
          isInVar = false;
        }
        ret += current;
        continue;
      } else if (current === '<') {
        isInTag = true;
        ret += current;
        continue;
      } else if ((current === '%' && next === '{') ||
                 (current === '{' && next === '{')) {
        isInVar = true;
        ret += current;
        continue;
      }

      if(typeof replacementMap[current] != 'undefined') {
        var replacements = replacementMap[current];
        ret += replacements[keyHashCode % replacements.length];
      } else{
        ret += current;
      }
    }
    // ??? put html encoding back?
    return ret;
  };

  computeHash = function(str) {
    if (!str) return 0;
    var hash = 0,
      len = str.length;
    for (var i = 0; i < len; i++) {
      hash = hash * 31 + str.charCodeAt(i);
    }
    return hash % filler.length;
  };

  // returns filler text of length count consistent for the value
  createFiller = function(value, count) {
    // Lead with a space for readability
    var fill = ' ';
    if(!value || !count || count <= 0) {
      return '';
    } else if (count == 1) {
      return fill;
    } else {
      // decrement count by initial filler space
      count--;
      var hash = computeHash(value);
      var fillSource = filler;
      // if there aren't enough characters in the filler starting at the hash, make the filler longer
      while (hash + count > fillSource.length) {
        fillSource += " " + fillSource;
      }
      fill += fillSource.substr(hash, count);
      return fill;
    }
  };

  // Return public interface
  return {
    // finds all the english locales in the base locale directory and converts them into pseudo locales
    execute: function(propertiesSourceDirectory) {
      var engPropFiles;
      engPropFiles = [];
      try {
        if (!fs.existsSync(propertiesSourceDirectory)) {
          console.warn("Skipping directory because it does not exist: " + propertiesSourceDirectory);
          return true;
        }
        var dirEntries = fs.readdirSync(propertiesSourceDirectory);

        var dirEntriesLength = dirEntries.length;
        for(var i=0;i<dirEntriesLength;i++) {
          var currentEntry = dirEntries[i];
          var stat;
          try {
            // have to resolve path for some reason
            stat = fs.statSync(path.resolve(propertiesSourceDirectory, currentEntry));
          } catch (err) {
            throw err;
          }

          // recurse through sub directories
          if(stat.isDirectory()) {
            this.execute(path.resolve(propertiesSourceDirectory,currentEntry));
          } else if(currentEntry[0] != '.' && path.extname(currentEntry) == '.json' && currentEntry.indexOf('_en.json') != -1){
            engPropFiles.push(currentEntry)
          }
        }

        var engPropFilesLength = engPropFiles.length;

        for(var i=0;i<engPropFilesLength;i++){
          var filePath = path.resolve(propertiesSourceDirectory,engPropFiles[i]);
          createEOPropFile(filePath);
        }
      } catch(err) {
        return err;
      }
      return true;
    },
    computeHash: computeHash,
    createFiller: createFiller

  };
};
