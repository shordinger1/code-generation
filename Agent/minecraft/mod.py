import os.path
import subprocess
from Agent.minecraft.block import block_class
from Agent.minecraft.item import item_class
from Agent.minecraft.library_like_class import library_like_class
from Agent.minecraft.static_files import *
from Agent.minecraft.static_files import set_item_base, package_root, set_block_base, \
    set_item_blocks_base, set_machine_entities_base, set_recipes_base, set_potions_base, set_renders_base, \
    set_entities_base, set_mobs_base, set_item_register, set_block_register, set_item_blocks_register, \
    set_machine_entities_register, set_recipes_register, set_potions_register, set_renders_register, \
    set_entities_register, set_mobs_register
from code_template.java_template_class import java_template_class
from ast_rag import DynamicRAG
from language_provider.java.Gradle import DependencyAnalyzer
from language_provider.java.JavaAnalyzer import analysis_java_files


class minecraft_mod:

    def __init__(self, mod_name: str, dev_root: str, dev_name: str):
        self.mod_name = mod_name
        self.dev_name = dev_name
        init_global(dev_root, f"com/{self.dev_name}/{self.mod_name}")
        print(get_root(), get_package())
        self.gradle_root = f'{get_root()}/gradlew.bat'
        os.makedirs(os.path.join(get_root(), f'src/main/resources/assets/{self.mod_name.lower()}/lang/'), exist_ok=True)
        self.lang_file_en = os.path.join(get_root(), f'src/main/resources/assets/{self.mod_name.lower()}/lang/',
                                         'en_US.lang')
        self.lang_file_zh = os.path.join(get_root(),
                                         f'src/main/resources/assets/{self.mod_name.lower()}/lang/',
                                         'zh_CN.lang')
        self.lang_en = {}
        self.lang_zh = {}
        self.items = {}
        self.blocks = {}
        self.item_blocks = {}
        self.machine_entities = {}
        self.recipes = {}
        self.potions = {}
        self.renders = {}
        self.entities = {}
        self.mobs = {}
        self.lib_rag = DynamicRAG(f"{mod_name}_library")
        self.mcp_rag = DynamicRAG(f"{mod_name}_minecraft")
        self.mod_rag = DynamicRAG(f"{mod_name}_mod")
        # self.task_tree = TaskTree('automatic minecraft mod generation')
        init_base_and_registry()

    def rag_init(self):
        mcp = analysis_java_files(f"{get_root()}/build")
        self.mcp_rag.batch_add_data(mcp)
        mod = analysis_java_files(f"{get_root()}/src/main/java")
        self.mod_rag.batch_add_data(mod)
        dep_analyzer = DependencyAnalyzer()
        try:
            dependency_methods = dep_analyzer.analyze_dependencies()
        finally:
            dep_analyzer.cleanup()
        self.lib_rag.batch_add_data(dependency_methods)

    def generate_main_mod_file(self):
        template = java_template_class(get_root(), self.mod_name,
                                       f"com/{self.dev_name}/{self.mod_name}").add_import(
            "import org.apache.logging.log4j.LogManager;",
            "import org.apache.logging.log4j.LogManager;",
            "import org.apache.logging.log4j.Logger;",
            "import cpw.mods.fml.common.Mod;",
            "import cpw.mods.fml.common.SidedProxy;",
            "import cpw.mods.fml.common.event.FMLInitializationEvent;",
            "import cpw.mods.fml.common.event.FMLPostInitializationEvent;",
            "import cpw.mods.fml.common.event.FMLPreInitializationEvent;",
            "import cpw.mods.fml.common.event.FMLServerStartingEvent;"
        )
        template.init_code(f"\
@Mod(modid = {self.mod_name}.MODID, version = Tags.VERSION, name = \"{self.mod_name}\", acceptedMinecraftVersions = \"[1.7.10]\")\n \
public class {self.mod_name} {{\n \
\n \
    public static final String MODID = \"{self.mod_name}\";\n \
    public static final Logger LOG = LogManager.getLogger(MODID);\n \
\n \
    @SidedProxy(clientSide = \"com.{self.dev_name}.{self.mod_name}.ClientProxy\", serverSide = \"com.{self.dev_name}.{self.mod_name}.CommonProxy\")\n \
    public static CommonProxy proxy;\n \
\n \
    @Mod.EventHandler\n \
    // preInit \"Run before anything else. Read your config, create blocks, items, etc, and register them with the\n \
    // GameRegistry.\" (Remove if not needed)\n \
    public void preInit(FMLPreInitializationEvent event)\n {{ \
        proxy.preInit(event);\n \
    }}\n \
\n \
    @Mod.EventHandler\n \
    // load \"Do your mod setup. Build whatever data structures you care about. Register recipes.\" (Remove if not needed)\n \
    public void init(FMLInitializationEvent event)\n {{ \
        proxy.init(event); \
    }}\n \
\n \
    @Mod.EventHandler \
    // postInit \"Handle interaction with other mods, complete your setup based on this.\" (Remove if not needed)\n \
    public void postInit(FMLPostInitializationEvent event)\n {{ \
        proxy.postInit(event);\n \
    }}\n \
\n \
    @Mod.EventHandler\n \
    // register server commands in this event handler (Remove if not needed)\n \
    public void serverStarting(FMLServerStartingEvent event)\n {{\n \
        proxy.serverStarting(event);\n \
    }}\n \
}}\n \
")
        template.write_to_file()
        gradle_setting = f"# ExampleMod tag to use as Blowdryer (Spotless, etc.) settings version, leave empty to disable.\n \
# LOCAL to test local config updates.\n \
gtnh.settings.blowdryerTag = 0.2.2\n \
\n \
# Human-readable mod name, available for mcmod.info population.\n \
modName = {self.mod_name}\n \
\n \
# Case-sensitive identifier string, available for mcmod.info population and used for automatic mixin JSON generation.\n \
# Conventionally lowercase.\n \
modId = {self.mod_name}\n \
\n \
# Root package of the mod, used to find various classes in other properties,\n \
# mcmod.info substitution, enabling assertions in run tasks, etc.\n \
modGroup = com.{self.dev_name}.{self.mod_name}\n \
\n \
# Whether to use modGroup as the maven publishing group.\n \
# When false, com.github.GTNewHorizons is used.\n \
useModGroupForPublishing = true\n \
\n \
# Updates your build.gradle and settings.gradle automatically whenever an update is available.\n \
autoUpdateBuildScript = false\n \
\n \
# Version of Minecraft to target\n \
minecraftVersion = 1.7.10\n \
\n \
# Version of Minecraft Forge to target\n \
forgeVersion = 10.13.4.1614\n \
\n \
# Specify an MCP channel for dependency deobfuscation and the deobfParams task.\n \
channel = stable\n \
\n \
# Specify an MCP mappings version for dependency deobfuscation and the deobfParams task.\n \
mappingsVersion = 12\n \
\n \
# Defines other MCP mappings for dependency deobfuscation.\n \
remoteMappings = https\://raw.githubusercontent.com/MinecraftForge/FML/1.7.10/conf/\n \
\n \
# Select a default username for testing your mod. You can always override this per-run by running\n \
# `./gradlew runClient --username=AnotherPlayer`, or configuring this command in your IDE.\n \
developmentEnvironmentUserName = Developer\n \
\n \
# Enables using modern Java syntax (up to version 17) via Jabel, while still targeting JVM 8.\n \
# See https://github.com/bsideup/jabel for details on how this works.\n \
enableModernJavaSyntax = true\n \
\n \
# Enables injecting missing generics into the decompiled source code for a better coding experience.\n \
# Turns most publicly visible List, Map, etc. into proper List<E>, Map<K, V> types.\n \
enableGenericInjection = true\n \
\n \
# Generate a class with a String field for the mod version named as defined below.\n \
# If generateGradleTokenClass is empty or not missing, no such class will be generated.\n \
# If gradleTokenVersion is empty or missing, the field will not be present in the class.\n \
generateGradleTokenClass = com.{self.dev_name}.{self.mod_name}.Tags\n \
\n \
# Name of the token containing the project's current version to generate/replace.\n \
gradleTokenVersion = VERSION\n \
\n \
# [DEPRECATED]\n \
# Multiple source files can be defined here by providing a comma-separated list: Class1.java,Class2.java,Class3.java\n \
# public static final String VERSION = \"GRADLETOKEN_VERSION\";\n \
# The string's content will be replaced with your mod's version when compiled. You should use this to specify your mod's\n \
# version in @Mod([...], version = VERSION, [...]).\n \
# Leave these properties empty to skip individual token replacements.\n \
replaceGradleTokenInFile =\n \
\n \
# In case your mod provides an API for other mods to implement you may declare its package here. Otherwise, you can\n \
# leave this property empty.\n \
# Example value: (apiPackage = api) + (modGroup = com.myname.mymodid) -> com.myname.mymodid.api\n \
apiPackage =\n \
\n \
# Specify the configuration file for Forge's access transformers here. It must be placed into /src/main/resources/META-INF/\n \
# There can be multiple files in a space-separated list.\n \
# Example value: mymodid_at.cfg nei_at.cfg\n \
accessTransformersFile =\n \
\n \
# Provides setup for Mixins if enabled. If you don't know what mixins are: Keep it disabled!\n \
usesMixins = false\n \
\n \
# Set to a non-empty string to configure mixins in a separate source set under src/VALUE, instead of src/main.\n \
# This can speed up compile times thanks to not running the mixin annotation processor on all input sources.\n \
# Mixin classes will have access to \"main\" classes, but not the other way around.\n \
separateMixinSourceSet =\n \
\n \
# Adds some debug arguments like verbose output and class export.\n \
usesMixinDebug = false\n \
\n \
# Specify the location of your implementation of IMixinConfigPlugin. Leave it empty otherwise.\n \
mixinPlugin =\n \
\n \
# Specify the package that contains all of your Mixins. You may only place Mixins in this package or the build will fail!\n \
mixinsPackage =\n \
\n \
# Specify the core mod entry class if you use a core mod. This class must implement IFMLLoadingPlugin!\n \
# This parameter is for legacy compatibility only\n \
# Example value: (coreModClass = asm.FMLPlugin) + (modGroup = com.myname.mymodid) -> com.myname.mymodid.asm.FMLPlugin\n \
coreModClass =\n \
\n \
# If your project is only a consolidation of mixins or a core mod and does NOT contain a 'normal' mod ( = some class\n \
# that is annotated with @Mod) you want this to be true. When in doubt: leave it on false!\n \
containsMixinsAndOrCoreModOnly = false\n \
\n \
# Enables Mixins even if this mod doesn't use them, useful if one of the dependencies uses mixins.\n \
forceEnableMixins = false\n \
\n \
# If enabled, you may use 'shadowCompile' for dependencies. They will be integrated into your jar. It is your\n \
# responsibility to check the license and request permission for distribution if required.\n \
usesShadowedDependencies = false\n \
\n \
# If disabled, won't remove unused classes from shadowed dependencies. Some libraries use reflection to access\n \
# their own classes, making the minimization unreliable.\n \
minimizeShadowedDependencies = true\n \
\n \
# If disabled, won't rename the shadowed classes.\n \
relocateShadowedDependencies = true\n \
\n \
# Adds CurseMaven, Modrinth, and some more well-known 1.7.10 repositories.\n \
includeWellKnownRepositories = true\n \
\n \
# A list of repositories to exclude from the includeWellKnownRepositories setting. Should be a space separated\n \
# list of strings, with the acceptable keys being(case does not matter):\n \
# cursemaven\n \
# modrinth\n \
excludeWellKnownRepositories =\n \
\n \
# Change these to your Maven coordinates if you want to publish to a custom Maven repository instead of the default GTNH Maven.\n \
# Authenticate with the MAVEN_USER and MAVEN_PASSWORD environment variables.\n \
# If you need a more complex setup disable maven publishing here and add a publishing repository to addon.gradle.\n \
usesMavenPublishing = true\n \
\n \
# Maven repository to publish the mod to.\n \
# mavenPublishUrl = https\://nexus.gtnewhorizons.com/repository/releases/\n \
\n \
# Publishing to Modrinth requires you to set the MODRINTH_TOKEN environment variable to your current Modrinth API token.\n \
#\n \
# The project's ID on Modrinth. Can be either the slug or the ID.\n \
# Leave this empty if you don't want to publish to Modrinth.\n \
modrinthProjectId =\n \
\n \
# The project's relations on Modrinth. You can use this to refer to other projects on Modrinth.\n \
# Syntax: scope1-type1:name1;scope2-type2:name2;...\n \
# Where scope can be one of [required, optional, incompatible, embedded],\n \
#       type can be one of [project, version],\n \
#       and the name is the Modrinth project or version slug/id of the other mod.\n \
# Example: required-project:fplib;optional-project:gasstation;incompatible-project:gregtech\n \
# Note: GTNH Mixins is automatically set as a required dependency if usesMixins = true\n \
modrinthRelations =\n \
\n \
# Publishing to CurseForge requires you to set the CURSEFORGE_TOKEN environment variable to one of your CurseForge API tokens.\n \
#\n \
# The project's numeric ID on CurseForge. You can find this in the About Project box.\n \
# Leave this empty if you don't want to publish on CurseForge.\n \
curseForgeProjectId =\n \
\n \
# The project's relations on CurseForge. You can use this to refer to other projects on CurseForge.\n \
# Syntax: type1:name1;type2:name2;...\n \
# Where type can be one of [requiredDependency, embeddedLibrary, optionalDependency, tool, incompatible],\n \
#       and the name is the CurseForge project slug of the other mod.\n \
# Example: requiredDependency:railcraft;embeddedLibrary:cofhlib;incompatible:buildcraft\n \
# Note: UniMixins is automatically set as a required dependency if usesMixins = true.\n \
curseForgeRelations =\n \
\n \
# Optional parameter to customize the produced artifacts. Use this to preserve artifact naming when migrating older\n \
# projects. New projects should not use this parameter.\n \
# customArchiveBaseName =\n \
\n \
# Optional parameter to have the build automatically fail if an illegal version is used.\n \
# This can be useful if you e.g. only want to allow versions in the form of '1.1.xxx'.\n \
# The check is ONLY performed if the version is a git tag.\n \
# Note: the specified string must be escaped, so e.g. 1\\.1\\.\\d+ instead of 1\.1\.\d+\n \
# versionPattern =\n \
\n \
# Uncomment to prevent the source code from being published.\n \
# noPublishedSources = true\n \
\n \
# Uncomment this to disable Spotless checks.\n \
# This should only be uncommented to keep it easier to sync with upstream/other forks.\n \
# That is, if there is no other active fork/upstream, NEVER change this.\n \
disableSpotless = true\n \
\n \
# Uncomment this to disable Checkstyle checks (currently wildcard import check).\n \
# disableCheckstyle = true\n \
\n \
# Override the IDEA build type. Valid values are: "" (leave blank, do not override), \"idea\" (force use native IDEA build), \"gradle\"\n \
# (force use delegated build).\n \
# This is meant to be set in $HOME/.gradle/gradle.properties.\n \
# e.g. add \"systemProp.org.gradle.project.ideaOverrideBuildType = idea\" will override the build type to be native build.\n \
# WARNING: If you do use this option, it will overwrite whatever you have in your existing projects. This might not be what you want!\n \
# Usually there is no need to uncomment this here as other developers do not necessarily use the same build type as you.\n \
# ideaOverrideBuildType = idea\n \
\n \
# Whether IDEA should run spotless checks when pressing the Build button.\n \
# This is meant to be set in $HOME/.gradle/gradle.properties.\n \
# ideaCheckSpotlessOnBuild = true\n \
\n \
"
        gradle_path = os.path.join(get_root(), "gradle.properties")
        with open(gradle_path, "w") as f:
            f.write(gradle_setting)
        config_java = java_template_class(get_root(), "Config",
                                          f"com/{self.dev_name}/{self.mod_name}").add_import(
            "import java.io.File;",
            "import net.minecraftforge.common.config.Configuration;"
        )
        config_java.init_code(
            f"public class Config {{\n \
\n \
    public static String greeting = \"Hello World\";\n \
\n \
    public static void synchronizeConfiguration(File configFile) {{\n \
        Configuration configuration = new Configuration(configFile);\n \
\n \
        greeting = configuration.getString(\"greeting\", Configuration.CATEGORY_GENERAL, greeting, \"How shall I greet?\");\n \
\n \
        if (configuration.hasChanged()) {{\n \
            configuration.save();\n \
        }}\n \
    }}\n \
}}\n \
"
        )
        config_java.write_to_file()
        common_proxy = java_template_class(get_root(), "CommonProxy",
                                           f"com/{self.dev_name}/{self.mod_name}").add_import(
            "import cpw.mods.fml.common.event.FMLInitializationEvent;",
            "import cpw.mods.fml.common.event.FMLPostInitializationEvent;",
            "import cpw.mods.fml.common.event.FMLPreInitializationEvent;",
            "import cpw.mods.fml.common.event.FMLServerStartingEvent;"
        )
        common_proxy.init_code(
            f"""
            public class CommonProxy {{

    // preInit "Run before anything else. Read your config, create blocks, items, etc, and register them with the
    // GameRegistry." (Remove if not needed)
    public void preInit(FMLPreInitializationEvent event) {{
        Config.synchronizeConfiguration(event.getSuggestedConfigurationFile());

        {self.mod_name}.LOG.info(Config.greeting);
        {self.mod_name}.LOG.info("I am AutoGenerated at version " + Tags.VERSION);
    }}

    // load "Do your mod setup. Build whatever data structures you care about. Register recipes." (Remove if not needed)
    public void init(FMLInitializationEvent event) {{}}

    // postInit "Handle interaction with other mods, complete your setup based on this." (Remove if not needed)
    public void postInit(FMLPostInitializationEvent event) {{}}

    // register server commands in this event handler (Remove if not needed)
    public void serverStarting(FMLServerStartingEvent event) {{}}
}}

            """
        )
        common_proxy.write_to_file()
        client_proxy = java_template_class(get_root(), "ClientProxy",
                                           f"com/{self.dev_name}/{self.mod_name}").add_import(
        )
        client_proxy.init_code(
            """
            public class ClientProxy extends CommonProxy {

    // Override CommonProxy methods here, if you want a different behaviour on the client (e.g. registering renders).
    // Don't forget to call the super methods as well.

}

            """
        )
        client_proxy.write_to_file()

    def process(self):
        pass

    def add_items(self, *item_names):
        for item in item_names:
            print(f"Item {item} added to com/{self.dev_name}/{self.mod_name}/item")
            self.items[item] = item_class(get_root(), item, f"com/{self.dev_name}/{self.mod_name}/common/item")
            self.lang_en[self.items[item].class_name] = item

    def add_blocks(self, *block_names, **block_kwargs):
        """添加方块到项目，支持自定义方块属性"""
        for block in block_names:
            print(f"Block {block} added to com/{self.dev_name}/{self.mod_name}/block")
            self.blocks[block] = block_class(
                project_root=get_root(),
                block_name=block,
                package=f"com/{self.dev_name}/{self.mod_name}/common/block",
                **block_kwargs  # 传递自定义参数给block_class
            )
            self.lang_en[f"tile.{block}.name"] = f"{block} Block"

    def write_items(self):
        get_item_register().insert_static_into_code()
        get_item_register().write_to_file()
        for k, v in self.items.items():
            v.write_to_file()

    def write_blocks(self):
        get_block_register().insert_static_into_code()
        get_block_register().write_to_file()
        for k, v in self.blocks.items():
            v.write_to_file()

    def write_lang(self, key, value):
        en = open(self.lang_file_en, 'a')
        zh = open(self.lang_file_zh, 'a')
        en.write(f"{key}={value}\n")
        zh.write(f"{key}={value}\n")
        en.close()
        zh.close()

    def write_lang_all(self, reset=True):
        # TODO should update all lang files? Or just refresh some of key?
        en = open(self.lang_file_en, 'w')
        zh = open(self.lang_file_zh, 'w')
        for k, v in self.lang_en.items():
            en.write(f"{k}={v}\n")
        for k, v in self.lang_zh.items():
            en.write(f"{k}={v}\n")

    def read_lang_all(self):
        en = open(self.lang_file_en, 'r')
        zh = open(self.lang_file_zh, 'r')
        for l in en.readline():
            l = l.split('=')
            self.lang_en[l[0]] = l[1]
        for l in zh.readline():
            l = l.split('=')
            self.lang_zh[l[0]] = l[1]

    def build(self):
        print(['cd', get_root()])
        subprocess.run([self.gradle_root, 'build'], cwd=get_root(),
                       check=True,
                       stdout=subprocess.DEVNULL)

    def spotless(self):
        print([self.gradle_root, 'spotlessApply'])
        subprocess.run([self.gradle_root, 'spotlessApply'], cwd=get_root(),
                       check=True,
                       stdout=subprocess.DEVNULL)


def init_base_and_registry():
    root = get_root()
    if root == "default":
        print("you should register a mod before init")
        exit(1)

    # 替换所有直接赋值为 set_ 函数调用
    set_item_base(java_template_class(root, 'ItemBase', os.path.join(package_root, 'common/item')))
    set_block_base(java_template_class(root, 'BlockBase', os.path.join(package_root, 'common/block')))
    set_item_blocks_base(java_template_class(root, 'ItemBlocksBase', os.path.join(package_root, 'common/item')))
    set_machine_entities_base(
        java_template_class(root, 'MachineEntitiesBase', os.path.join(package_root, 'common/machine')))
    set_recipes_base(java_template_class(root, 'RecipesBase', os.path.join(package_root, 'common/recipe')))
    set_potions_base(java_template_class(root, 'PotionsBase', os.path.join(package_root, 'common/potion')))
    set_renders_base(java_template_class(root, 'RendersBase', os.path.join(package_root, 'common/render')))
    set_entities_base(java_template_class(root, 'EntitiesBase', os.path.join(package_root, 'common/entity')))
    set_mobs_base(java_template_class(root, 'MobsBase', os.path.join(package_root, 'common/mob')))

    set_item_register(library_like_class(root, 'ItemRegister', os.path.join(package_root, 'common/item')))
    set_block_register(library_like_class(root, 'BlockRegister', os.path.join(package_root, 'common/block')))
    set_item_blocks_register(
        library_like_class(root, 'ItemBlocksRegister', os.path.join(package_root, 'common/item')))
    set_machine_entities_register(
        library_like_class(root, 'MachineEntitiesRegister', os.path.join(package_root, 'common/machine')))
    set_recipes_register(
        library_like_class(root, 'RecipesRegister', os.path.join(package_root, 'common/recipe')))
    set_potions_register(
        library_like_class(root, 'PotionsRegister', os.path.join(package_root, 'common/potion')))
    set_renders_register(
        library_like_class(root, 'RendersRegister', os.path.join(package_root, 'common/render')))
    set_entities_register(
        library_like_class(root, 'EntitiesRegister', os.path.join(package_root, 'common/entity')))
    set_mobs_register(library_like_class(root, 'MobsRegister', os.path.join(package_root, 'common/mob')))
