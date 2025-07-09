from overrides import overrides

from Agent.minecraft.library_like_class import library_like_class
from code_template.java_template_class import java_template_class
from Agent.minecraft.static_files import get_item_register
from pydantic import BaseModel


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
        get_item_register().add_import(f"import {self.package}.{self.class_name};".replace('/', '.'))

    @overrides
    def get_template(self):
        pass

    @staticmethod
    def generate(item, item_template):
        prompt = f"""
        You are a professional Minecraft mod developer. Create a custom item based on the following user requirement:  
        name:{item_template.name}
        hint:{item_template.hint}
        function:{item_template.function}
        description:{item_template.description}
        """
        item.process(prompt)
        return item
        # this place should use rag for item function generation

    class template(BaseModel):
        name: str
        hint: str
        function: list[str]
        description: list[str]

        @staticmethod
        def prompt(user_requirement):
            return f"""  
        You are a professional Minecraft mod developer. Create a custom item based on the following user requirement:  
        "{user_requirement}"  

        Generate an item with following details:  
        1. name (str): CamelCase item name (e.g., EnderPearl)  
        2. hint (str): Short in-game tooltip (Minecraft-style, max 20 words, optional § color codes)  
        3. function (list[str]): abilities user provided (action-oriented phrases, max 10 words each)  
        4. description (list[str]): lore/background sentences related to functions (Minecraft-themed)  
        
        Note: do not generate anything user not provide. If user doesn't tell anything about the abilities, 
        just keep it empty. 

        Example:  
            name: "ThunderAxe"  
            hint:  "§6Axe that summons lightning §o(Right-click)"  
            function:  [  
                "30% chance to summon lightning on hit",  
                "Deals triple damage to aquatic mobs",  
                "Right-click to summon thunderstorm"  
            ]  
            description:  [  
                "Forged from lightning-struck oak",  
                "The blade crackles with storm energy",  
                "Wielded by ancient thunder shamans"  
            ]  
        Note: 
        1.description should be a hint to each function. 
        2.list any possible function from full description.

        Output ONLY the formatted result, no explanations.
        """
