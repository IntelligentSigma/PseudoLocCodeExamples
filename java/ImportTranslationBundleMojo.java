package org..maven.plugins;

import org.apache.maven.plugin.MojoExecutionException;
import org.apache.maven.plugin.MojoFailureException;
import org.codehaus.plexus.archiver.ArchiverException;
import org.codehaus.plexus.archiver.zip.ZipUnArchiver;
import org.codehaus.plexus.util.FileUtils;

import java.io.File;
import java.io.FilenameFilter;
import java.io.IOException;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * A goal that processes the archive from translations that contains a folder per language which in turn contains the
 * properties files for that language that mirror the src/main/localization folder.  This goal combines those folders
 * into a single hierarchy and renames the properties files with the _[lang].properties convention.  Looks for source
 * archive in target/translatedFiles.zip and places combined output in target/translationImport.  Output needs to be
 * manually copied to src/main/localization.
 * 
 * @goal import
 * @phase process-sources
 * @aggregator true
 */
public class ImportTranslationBundleMojo extends AbstractTranslationBundleMojo {

    public static final String INCLUDE_FILTER = "**/*.properties";
    public static final String PROPERTIES_INCLUDE_FILTER = INCLUDE_FILTER;
    public static final Map<String,String> LOCALE_BY_NAME = new LinkedHashMap<String,String>();
    static {
        LOCALE_BY_NAME.put("german", "de");
        LOCALE_BY_NAME.put("spanish", "es");
        LOCALE_BY_NAME.put("french", "fr");
        LOCALE_BY_NAME.put("italian", "it");
        LOCALE_BY_NAME.put("japanese", "ja");
        LOCALE_BY_NAME.put("korean", "ko");
        LOCALE_BY_NAME.put("portuguese", "pt");
        LOCALE_BY_NAME.put("russian", "ru");
        LOCALE_BY_NAME.put("chinese", "zh");
    }
    public static final String LANGUAGES = "de,es,fr,it,ja,ko,pt,ru,zh";
    public static final String EXCLUDE_FILTER = null;
    public static final String REPLACE_WITH = "_%s.properties";
    public static final String ENDS_WITH = ".properties";

    /**
     * Location of the .zip files provided by translation.  It will look for all .zip files in this directory.
     *
     * @parameter expression="${project.basedir}"
     * @required
     */
    private File translationArchiveSourceDirectory;

    /**
     * Location of the files.  It will look for all .zip files in this directory.
     *
     * @parameter expression="${project.build.directory}/rawIncomingTranslations"
     * @required
     */
    private File rawIncomingTranslationsDirectory;

    /**
     * Where to put the translations.  It is going to the basedir since we can assume we're using a version control
     * system that will allow comparing and reverting as needed.
     *
     * @parameter expression="${project.basedir}"
     * @required
     */
    private File translationImportDirectory;

    /**
     * The Zip archiver.
     *
     * @component role="org.codehaus.plexus.archiver.UnArchiver" roleHint="zip"
     */
    private ZipUnArchiver zipUnArchiver;

    public void execute() throws MojoExecutionException, MojoFailureException {
        File[] translationArchives = translationArchiveSourceDirectory.listFiles(new FilenameFilter() {
            @Override
            public boolean accept(File file, String s) {
                return s.toLowerCase().endsWith(".zip");
            }
        });
        for (File translationArchive : translationArchives) {
            importTranslationArchive(translationArchive);
        }
    }

    private void importTranslationArchive(File translatedFilesArchive) throws MojoExecutionException {
        File baseExtractedDirectory = rawIncomingTranslationsDirectory;
        extractFiles(translatedFilesArchive, baseExtractedDirectory);
        importUsingOldWayWithMultipleLanguagesInOneFile();

        String locale = determineLocale(translatedFilesArchive);
        if (locale != null) {
            getLog().info("Importing locale=" + locale + " from file=" + translatedFilesArchive);
            File propertiesDirectory = new File(new File(new File(baseExtractedDirectory, getNameWithoutSuffix(translatedFilesArchive)), "translationExport"), "properties");
            copyFiles(propertiesDirectory, translationImportDirectory, INCLUDE_FILTER, EXCLUDE_FILTER, ENDS_WITH, String.format(REPLACE_WITH, locale));
        }
    }

    String getNameWithoutSuffix(File file) {
        String name = file.getName();
        return name.substring(0, name.lastIndexOf("."));
    }

    private void extractFiles(File translatedFilesArchive, File temporaryDestDirectory) throws MojoExecutionException {
        if (temporaryDestDirectory.exists()) {
            try {
                FileUtils.cleanDirectory(temporaryDestDirectory);
            } catch (IOException e) {
               throw new MojoExecutionException(e.getMessage(), e);
            }
        } else {
            if (!temporaryDestDirectory.mkdirs()) {
                getLog().warn("mkdirs returned false for : " + temporaryDestDirectory);
            }
        }
        zipUnArchiver.setSourceFile(translatedFilesArchive);
        zipUnArchiver.setDestDirectory(temporaryDestDirectory);

        try {
            zipUnArchiver.extract();
        } catch (ArchiverException e) {
            throw new MojoExecutionException(e.getMessage(), e);
        }
    }

    public String determineLocale(File translatedFilesArchive) {
        String[] namePieces = translatedFilesArchive.getName().split("_|\\.");
        String language = namePieces[namePieces.length - 2].toLowerCase();
        if (!LOCALE_BY_NAME.containsKey(language)) {
            getLog().warn("Not importing as a single locale file since unrecognized language: " + language);
        }
        return LOCALE_BY_NAME.get(language);
    }

    private void importUsingOldWayWithMultipleLanguagesInOneFile() throws MojoExecutionException {
        for (String language : LOCALE_BY_NAME.values()) {
            language = language.trim();

            File fromDir = new File(rawIncomingTranslationsDirectory, language + "/properties");
            if (fromDir.exists()) {
                getLog().info("Importing Language (the old way): " + language);

                File toDir = translationImportDirectory;
                String includeFilter = PROPERTIES_INCLUDE_FILTER;
                String excludeFilter = null;
                String endsWith = BARE_PROPERTIES_FILE_NAME;
                String replaceWith = String.format(TAGGED_PROPERTIES_FILE_NAME_TEMPLATE, language);

                copyFiles(fromDir, toDir, includeFilter, excludeFilter, endsWith, replaceWith);
            }
        }
    }
}
