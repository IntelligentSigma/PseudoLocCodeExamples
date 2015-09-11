package org..maven.plugins;

import org.apache.maven.plugin.MojoExecutionException;
import org.codehaus.plexus.archiver.ArchiverException;
import org.codehaus.plexus.archiver.zip.ZipArchiver;
import org.codehaus.plexus.util.FileUtils;

import java.io.File;
import java.io.IOException;

/**
 * Base class for the mojos that export translation files.
 */
public abstract class AbstractExportTranslationBundleMojo extends AbstractTranslationBundleMojo {

    /**
     * Location of the file.
     *
     * @parameter expression="${project.build.directory}"
     * @required
     */
    protected File outputDirectory;

    /**
     * Where the html files are found in the source tree.
     *
     * @parameter expression="${basedir}"
     * @required
     */
    protected File htmlSourceDirectory;

    /**
     * Where the property files are found in the source tree.
     *
     * @parameter expression="${basedir}"
     * @required
     */
    protected File propertiesSourceDirectory;

    public static final String HTML_INCLUDE = "**/*.htm,**/*.html,**/*.ssi";

    public static final String HTML_SECTION = "html";

    public static final String EN_PROPERTIES_INCLUDE = "**/*.properties";

    public static final String EXCLUDES = "**/target/**,**/*Gadget.html,**/*-test.properties,**/application.properties,**/src/main/conf/**,**/tomcat-install/**,**/plugins/**,**/component.properties,**/integration.properties";

    public static final String EN_PROPERTIES_EXCLUDE = "**/*_??.properties," + EXCLUDES;

    /**
     * The Zip archiver.
     *
     * @component role="org.codehaus.plexus.archiver.Archiver" roleHint="zip"
     */
    protected ZipArchiver zipArchiver;

    protected abstract File getTemporaryOutputDirectory();

    protected void copyBundleSection(File sourceDirectory, String bundleSection, String includeFilter,
                                   String excludeFilter) throws MojoExecutionException {
        copyBundleSection(sourceDirectory, bundleSection, includeFilter, excludeFilter, null, null);
    }

    protected void copyBundleSection(File sourceDirectory, String bundleSection, String includeFilter,
                                     String excludeFilter, String endsWith, String replaceWith)
            throws MojoExecutionException {
        File sectionOutputDir = new File(getTemporaryOutputDirectory(), bundleSection);
        copyFiles(sourceDirectory, sectionOutputDir, includeFilter, excludeFilter, endsWith, replaceWith);
    }

    protected void cleanTemporaryOutputDirectory() throws MojoExecutionException {
        if (getTemporaryOutputDirectory().exists()) {
            try {
                FileUtils.cleanDirectory(getTemporaryOutputDirectory());
            } catch (IOException e) {
                throw new MojoExecutionException(e.getMessage(), e);
            }
        }
    }

    protected void createArchive(String archiveName) throws MojoExecutionException {
        File archiveFile = new File(outputDirectory, archiveName);

        try {
            zipArchiver.addDirectory(getTemporaryOutputDirectory());
            zipArchiver.setDestFile(archiveFile);
            zipArchiver.createArchive();
        } catch (ArchiverException e) {
            throw new MojoExecutionException(e.getMessage(), e);
        } catch (IOException e) {
            throw new MojoExecutionException(e.getMessage(), e);
        }
    }

    protected void copyHtmlBundleSection() throws MojoExecutionException {
        copyBundleSection(htmlSourceDirectory, HTML_SECTION, HTML_INCLUDE, EXCLUDES);
    }

    protected void copyEnPropertiesBundleSection(String enSectionName) throws MojoExecutionException {
        copyBundleSection(propertiesSourceDirectory, enSectionName, EN_PROPERTIES_INCLUDE,
                EN_PROPERTIES_EXCLUDE);
    }
}
