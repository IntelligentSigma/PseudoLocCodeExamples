package org..maven.plugins;

import org.apache.maven.plugin.MojoExecutionException;
import org.apache.maven.plugin.MojoFailureException;

import java.io.File;

/**
 * Goal which will copy all of the html and properties files for all of the languages and place them in an archive for
 * sending to translations.
 *
 * @goal export-all
 * @phase process-sources
 * @aggregator true
 */
public class ExportAllTranslationBundleMojo extends AbstractExportTranslationBundleMojo {

    /**
     * Location of the file.
     *
     * @parameter expression="${project.build.directory}/translationExportAll"
     * @required
     */
    private File temporaryOutputDirectory;

    public static final String EN = "en";

    public static final String LANGUAGES = "de,es,fr,it,ja,ko,pt,ru,zh";

    public static final String LANG_PROPERTIES_SECTION_TEMPLATE = "%s/properties";

    public static final String LANG_PROPERTIES_INCLUDE_TEMPLATE = "**/*_%s.properties";

    public void execute() throws MojoExecutionException, MojoFailureException {
        getLog().info("Exporting html/properties files to archive for sending to the Translations department - splits out language files separately");
        cleanTemporaryOutputDirectory();

        copyHtmlBundleSection();

        getLog().info("Language = en");
        copyEnPropertiesBundleSection(String.format(LANG_PROPERTIES_SECTION_TEMPLATE, EN));

        for (String language : LANGUAGES.split(",")) {
            language = language.trim();
            getLog().info("Language = " + language);
            copyLangPropertiesBundleSection(language);
        }

        createArchive("translationExportAll.zip");
    }

    private void copyLangPropertiesBundleSection(String lang) throws MojoExecutionException {
        String endsWith = String.format(TAGGED_PROPERTIES_FILE_NAME_TEMPLATE, lang);
        String section = String.format(LANG_PROPERTIES_SECTION_TEMPLATE, lang);
        String include = String.format(LANG_PROPERTIES_INCLUDE_TEMPLATE, lang);
        
        copyBundleSection(propertiesSourceDirectory, section, include, EXCLUDES, endsWith, BARE_PROPERTIES_FILE_NAME);
    }

    @Override
    protected File getTemporaryOutputDirectory() {
        return temporaryOutputDirectory;
    }
}
