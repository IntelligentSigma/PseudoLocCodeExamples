package org..maven.plugins;

import org.apache.maven.plugin.AbstractMojo;
import org.apache.maven.plugin.MojoExecutionException;
import org.apache.maven.project.MavenProject;
import org.codehaus.plexus.util.FileUtils;

import java.io.File;
import java.io.IOException;
import java.util.List;

/**
 * Base class for the other translation mojos.
 */
public abstract class AbstractTranslationBundleMojo extends AbstractMojo {

    /**
     * @parameter default-value="${project}"
     */
    private MavenProject project;

    public static final String TAGGED_PROPERTIES_FILE_NAME_TEMPLATE = "_%s.properties";

    public static final String BARE_PROPERTIES_FILE_NAME = ".properties";

    protected void copyFiles(File fromDirectory, File toDirectory, String includeFilter, String excludeFilter,
                             String endsWith, String replaceWith) throws MojoExecutionException {
        if ((endsWith == null) != (replaceWith == null)) {
            throw new MojoExecutionException("Must pass both endsWith and replaceWith or neither.");
        }

        List<String> srcFileNames;

        try {
            srcFileNames = FileUtils.getFileNames(fromDirectory, includeFilter, excludeFilter, false, false);
        } catch (IOException e) {
            throw new MojoExecutionException(e.getMessage(), e);
        }

        if (srcFileNames != null) {
            for (String name : srcFileNames) {
                File srcFile = new File(fromDirectory, name);
                String destName = name;

                if (endsWith != null && name.endsWith(endsWith)) {
                    destName = name.substring(0, name.length() - endsWith.length()) + replaceWith;
                }

                File destFile = new File(toDirectory, destName);

                try {
                    FileUtils.copyFile(srcFile, destFile);
                } catch (IOException e) {
                    throw new MojoExecutionException(e.getMessage(), e);
                }
            }
        }
    }
}
