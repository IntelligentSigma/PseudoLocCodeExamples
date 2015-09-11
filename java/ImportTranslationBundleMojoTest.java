package org..maven.plugins;

import org.testng.Assert;

import java.io.File;

/**
 * A test for {@link ImportTranslationBundleMojo}.
 *
 * @author pabstec
 */
public class ImportTranslationBundleMojoTest {
    @org.testng.annotations.Test
    public void determineLocale() throws Exception {
        ImportTranslationBundleMojo sut = new ImportTranslationBundleMojo();
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_German.zip")), "de");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_Spanish.zip")), "es");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_French.zip")), "fr");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_Italian.zip")), "it");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_Japanese.zip")), "ja");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_Korean.zip")), "ko");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_Portuguese.zip")), "pt");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_Russian.zip")), "ru");
        Assert.assertEquals(sut.determineLocale(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_Chinese.zip")), "zh");
    }

    @org.testng.annotations.Test
    public void getNameWithoutSuffix() throws Exception {
        ImportTranslationBundleMojo sut = new ImportTranslationBundleMojo();
        Assert.assertEquals(sut.getNameWithoutSuffix(new File("/tmp/PD50042053_C36_FT_Properties_Update_320_German.zip")),
                "PD50042053_C36_FT_Properties_Update_320_German");
    }
}
