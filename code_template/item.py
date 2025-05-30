from code_template.library_like_class import library_like_class
from code_template.java_template_class import java_template_class
from code_template.static_files import get_item_register


class item_class(java_template_class):

    def __init__(self, project_root, item_name, package):
        super().__init__(project_root, f"Item{item_name}", package + '/general')
        self.item_name = item_name
        if isinstance(get_item_register(), library_like_class):
            if not get_item_register().inited:
                get_item_register().add_import(
                    "import net.minecraft.item.Item.ToolMaterial;",
                    "import java.util.LinkedHashMap;",
                    "import java.util.Map;",
                    "import cpw.mods.fml.common.registry.GameRegistry;",
                    "import net.minecraft.item.Item;",
                    "import java.util.ArrayList;"
                )
                get_item_register().init_code(f"""
               public class ItemRegister {{

    public static void registry() {{
        registryItems();
    }}

    private static void registryItems() {{
        for (Object item : Container.get_all()) {{
            if (item instanceof Item it) {{
                GameRegistry.registerItem(it, it.getUnlocalizedName());
            }}
        }}
    }}
}}
               """)
        self.add_import(
            "import cpw.mods.fml.relauncher.Side;",
            "import cpw.mods.fml.relauncher.SideOnly;",
            "import net.minecraft.creativetab.CreativeTabs;",
            "import net.minecraft.item.Item;",
            "import net.minecraft.item.ItemStack;"
        )
        self.init_code(f"""

public class {self.class_name} extends Item {{

    public {self.class_name}(CreativeTabs aCreativeTabs) {{
        super();
        this.setCreativeTab(aCreativeTabs);
        this.setUnlocalizedName(\"{self.item_name}\");
    }}
}}
        
        """)
        get_item_register().add_static_field(f"{self.class_name.upper()}(new {self.class_name}(itemCreativeTabs)),")
        get_item_register().add_import(f"import {self.package}.{self.class_name};".replace('/','.'))
