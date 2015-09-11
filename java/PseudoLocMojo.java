package org..maven.plugins;

import org.apache.commons.lang.StringEscapeUtils;
import org.apache.commons.lang.StringUtils;
import org.apache.maven.plugin.AbstractMojo;
import org.apache.maven.plugin.MojoExecutionException;
import org.codehaus.plexus.util.FileUtils;

import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;

/**
 * Goal which generates the pseudo localization files for projects.
 *
 * @goal generate-pseudo-loc
 */
public class PseudoLocMojo extends AbstractMojo {

  static {
    HashMap<Character, Character[]> replacementMap = new HashMap<Character, Character[]>();

    replacementMap.put('A', new Character[] { 'À','Á','Â','Ã','Ä','Å','Ā','Ą','Ă','Ѧ' });
    replacementMap.put('C', new Character[] { 'Ç','Ć','Č','Ĉ','Ċ' });
    replacementMap.put('D', new Character[] { 'Ď','Đ' });
    replacementMap.put('E', new Character[] { 'È','É','Ê','Ë','Ē','Ę','Ě','Ĕ','Ė','Э','Ѯ' });
    replacementMap.put('G', new Character[] { 'Ĝ','Ğ','Ġ','Ģ' });
    replacementMap.put('H', new Character[] { 'Ĥ','Ħ' });
    replacementMap.put('I', new Character[] { 'Ì','Í','Î','Ï','Ī','Ĩ','Ĭ','Į','İ' });
    replacementMap.put('J', new Character[] { 'Ĵ' });
    replacementMap.put('K', new Character[] { 'Ķ' });
    replacementMap.put('L', new Character[] { 'Ł','Ľ','Ĺ','Ļ','Ŀ' });
    replacementMap.put('N', new Character[] { 'Ñ','Ń','Ň','Ņ','Ŋ','П','И' });
    replacementMap.put('O', new Character[] { 'Ò','Ó','Ô','Õ','Ö','Ø','Ō','Ő','Ŏ' });
    replacementMap.put('R', new Character[] { 'Ŕ','Ř','Ŗ','Я' });
    replacementMap.put('S', new Character[] { 'Ś','Š','Ş','Ŝ','Ș' });
    replacementMap.put('T', new Character[] { 'Ť','Ţ','Ŧ','Ț' });
    replacementMap.put('U', new Character[] { 'Ù','Ú','Û','Ü','Ū','Ů','Ű','Ŭ','Ũ','Ų','Ц' });
    replacementMap.put('V', new Character[] { 'Ѵ' });
    replacementMap.put('W', new Character[] { 'Ŵ','Ш','Щ','Ѡ' });
    replacementMap.put('X', new Character[] { 'Ж' });
    replacementMap.put('Y', new Character[] { 'Ý','Ŷ','Ÿ' });
    replacementMap.put('Z', new Character[] { 'Ź','Ž','Ż' });
    replacementMap.put('a', new Character[] { 'à','á','â','ã','ä','å','ā','ą','ă' });
    replacementMap.put('b', new Character[] { 'Б','Ъ','Ь','Ѣ' });
    replacementMap.put('c', new Character[] { 'ç','ć','č','ĉ','ċ' });
    replacementMap.put('d', new Character[] { 'ď','đ' });
    replacementMap.put('e', new Character[] { 'è','é','ê','ë','ē','ę','ě','ĕ','ė' });
    replacementMap.put('f', new Character[] { 'ƒ' });
    replacementMap.put('g', new Character[] { 'ĝ','ğ','ġ','ģ' });
    replacementMap.put('h', new Character[] { 'ĥ','ħ' });
    replacementMap.put('i', new Character[] { 'ì','í','î','ï','ī','ĩ','ĭ','į','ı' });
    replacementMap.put('j', new Character[] { 'ĵ' });
    replacementMap.put('k', new Character[] { 'ķ','ĸ' });
    replacementMap.put('l', new Character[] { 'ł','ľ','ĺ','ļ','ŀ' });
    replacementMap.put('n', new Character[] { 'ñ','ń','ň','ņ','ŉ','ŋ' });
    replacementMap.put('o', new Character[] { 'ò','ó','ô','õ','ö','ø','ō','ő','ŏ','Ф' });
    replacementMap.put('r', new Character[] { 'ŕ','ř','ŗ','я' });
    replacementMap.put('s', new Character[] { 'ś','š','ş','ŝ','ș' });
    replacementMap.put('t', new Character[] { 'ť','ţ','ŧ','ț' });
    replacementMap.put('u', new Character[] { 'ù','ú','û','ü','ū','ů','ű','ŭ','ũ','ų' });
    replacementMap.put('v', new Character[] { 'ѵ' });
    replacementMap.put('w', new Character[] { 'ŵ' });
    replacementMap.put('y', new Character[] { 'ý','ÿ','ŷ','Ч','Ѱ' });
    replacementMap.put('z', new Character[] { 'ž','ż','ź' });

    REPLACEMENT_CHARS = replacementMap;
  }

  private static final HashMap<Character, Character[]> REPLACEMENT_CHARS;

  private static final String[] MIXED_LANGS = new String[] {
    // Japanese Chars
    "鼻毛]",
    "指先]",
    "眉毛]",
    "ひれ]",
    "ヘビ]",
    "カブ]",
    "子供]",
    "日本]",
    "言語]",
    "馬鹿]",

    // Korean Chars
    "영어]",
    "소금]",
    "트럭]",
    "히피]",
    "포크]",
    "토성]",
    "아픈]",
    "오리]",
    "얼음]",
    "극지]",

    // Chinese Chars
    "孩炁]",
    "嬉炜]",
    "雲炖]",
    "占炈]",
    "胡炂]",
    "膀炏]",
    "沙炔]",
    "蠢炝]",
    "烘炒]",
    "蝸炑]"
  };

  /**
   * Where the property files are found in the source tree.
   *
   * @parameter expression="${basedir}"
   * @required
   */
  protected File propertiesSourceDirectory;

  public static final String EN_PROPERTIES_INCLUDE = "**/*.properties";

  public static final String EXCLUDES = "**/*-test.properties,**/application.properties,**/src/main/conf/**,**/tomcat-install/**,**/plugins/**,**/component.properties,**/integration.properties,**/target/**";

  public static final String EN_PROPERTIES_EXCLUDE = "**/*_??.properties," + EXCLUDES;

  /* Used for testing outside the plugin. */
  public static void main(String[] args) {
    String baseDir = null;
    if (args.length == 1) {
      baseDir = args[0];
    }
    else {
      System.err.println("Requires single parameter to specify base directory");
    }
    PseudoLocMojo pseudoLocMojo = new PseudoLocMojo();
    pseudoLocMojo.propertiesSourceDirectory = new File(baseDir);
    try {
      pseudoLocMojo.execute();
    }
    catch (MojoExecutionException e) {
      e.printStackTrace();
    }
  }

  public void execute() throws MojoExecutionException {
    getLog().info("Making pseudo locale properties files.");

    try {
      @SuppressWarnings("unchecked")
      List<String> engPropFiles = FileUtils.getFileNames(propertiesSourceDirectory, EN_PROPERTIES_INCLUDE, EN_PROPERTIES_EXCLUDE, false, false);

      for(String engPropFile : engPropFiles) {
        createEOProp(new File(propertiesSourceDirectory, engPropFile));
      }
    } catch (IOException e) {
      throw new MojoExecutionException(e.getMessage(), e);
    }
  }

  private void createEOProp(File engPropFile) throws IOException, MojoExecutionException {
    File eoPropFile = new File(engPropFile.getParentFile(), engPropFile.getName().substring(0, engPropFile.getName().length() - ".properties".length()) + "_eo.properties");

    try {
      List lines = FileUtils.loadFile(engPropFile);
      String[] convertedLines = new String[lines.size()];

      for(int i = 0, s = lines.size(); i < s; i++) {
        convertedLines[i] = makeEOPropLine((String)lines.get(i));
      }

      if (eoPropFile.exists()) {
        if (!eoPropFile.delete()) {
          throw new IOException("Cannot delete file: " + eoPropFile);
        }
      }

      if (!eoPropFile.createNewFile()) {
        throw new IOException("Cannot create file: " + eoPropFile);
      }

      getLog().info("Writing file: " + eoPropFile);
      FileUtils.fileWrite(eoPropFile.getAbsolutePath(), joinArray(convertedLines, System.getProperty("line.separator", "\n")));

    } catch(IOException e) {
      getLog().info("Error file: " + eoPropFile);

      throw e;
    }
  }

  private String makeEOPropLine(String enPropLine) throws IOException {
    int split = enPropLine.indexOf("=");

    if (split < 0) {
      throw new IOException("Could not find equals sign in property file.");
    }
    // Use each properties key as a hashCode to get different pseudo-loc output
    String key = enPropLine.substring(0, split);
    int hashCode = Math.abs(key.hashCode());

    StringBuffer newValue = convertValue(enPropLine.substring(split + 1, enPropLine.length()), hashCode);
    int index = hashCode % MIXED_LANGS.length;
    String suffix = MIXED_LANGS[index];
    String expansion;

    int length = newValue.length();
    int combinedLength = length + suffix.length();

    if(length <= 0) {
      expansion = "";
    } else if(length > 0 && length <= 5) {
      expansion = StringUtils.repeat("_", 9 - combinedLength);
    } else if(length >= 6 && length <= 25) {
      expansion = StringUtils.repeat("_", (int)((double)length * 1.9) - combinedLength);
    } else if(length >= 26 && length <= 40) {
      expansion = StringUtils.repeat("_", (int)((double)length * 1.6) - combinedLength);
    } else if(length >= 41 && length <= 70) {
      expansion = StringUtils.repeat("_", (int)((double)length * 1.3) - combinedLength);
    } else {
      expansion = StringUtils.repeat("_", length - combinedLength);
    }

    newValue.append(expansion);
    newValue.append("||");
    newValue.append(suffix);

    return enPropLine.substring(0, split) + "=[" + newValue.toString();
  }

  private StringBuffer convertValue(String value, int hashCode) {
    // Remove any html encoding from file.
    value = StringEscapeUtils.unescapeHtml(value);

    // replace mappable chars with REPLACEMENT_CHARS.
    char[] strChars = value.toCharArray();
    boolean isInTag = false;
    for(int i = 0; i < strChars.length; i++) {
      char current = strChars[i];

      // Ignore anything that is inbetween html brackets.
      if(isInTag) {
        if(current == '>') {
          isInTag = false;
        }

        continue;
      } else if(current == '<') {
        isInTag = true;

        continue;
      }

      if (REPLACEMENT_CHARS.containsKey(current)) {
        Character[] replacements = REPLACEMENT_CHARS.get(current);
        int index = hashCode % replacements.length;
        strChars[i] = replacements[index];
      }
    }

    return new StringBuffer(new String(strChars));
  }

  private String joinArray(String[] array, String separator) {
    StringBuilder buffer = new StringBuilder();
    boolean isFirst = true;

    for(String line : array) {
      if(isFirst) {
        isFirst = false;
      } else {
        buffer.append(separator);
      }

      buffer.append(line);
    }

    return buffer.toString();
  }
}
