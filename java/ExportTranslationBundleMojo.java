package org..maven.plugins;

import org.apache.maven.plugin.MojoExecutionException;

import java.io.File;

/**
 * Goal which copies the english html and properties files into a zip archive suitable for sending to the translations
 * department.
 *
 * @goal export
 * @phase process-sources
 * @aggregator true
 */
public class ExportTranslationBundleMojo extends AbstractExportTranslationBundleMojo {
    /**
     * Location of the file.
     *
     * @parameter expression="${project.build.directory}/translationExport"
     * @required
     */
    private File temporaryOutputDirectory;
    
    public static final String GENERAL_PROPERTIES_SECTION = "properties";

    public void execute() throws MojoExecutionException {
        getLog().info("Exporting html/properties files to archive for sending to the Translations department");

        cleanTemporaryOutputDirectory();
        copyHtmlBundleSection();
        copyEnPropertiesBundleSection(GENERAL_PROPERTIES_SECTION);
        createArchive("translationExport.zip");
    }

    @Override
    protected File getTemporaryOutputDirectory() {
        return temporaryOutputDirectory;
    }
}
