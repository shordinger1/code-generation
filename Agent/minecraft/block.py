from overrides import overrides

from Agent.minecraft.library_like_class import library_like_class
from code_template.java_template_class import java_template_class
from Agent.minecraft.static_files import get_block_register


class block_class(java_template_class):

    def __init__(self, project_root, block_name, package,
                 has_tile_entity=False, has_item_block=True,
                 has_special_render=False, has_custom_activation=False):
        super().__init__(project_root, f"Block{block_name}", package + '/blocks')
        self.block_name = block_name
        self.has_tile_entity = has_tile_entity
        self.has_item_block = has_item_block
        self.has_special_render = has_special_render
        self.has_custom_activation = has_custom_activation

        # 初始化BlockRegister
        if isinstance(get_block_register(), library_like_class):
            if not get_block_register().inited:
                get_block_register().add_import(
                    "import net.minecraft.block.Block;",
                    "import net.minecraft.block.material.Material;",
                    "import cpw.mods.fml.common.registry.GameRegistry;",
                    "import java.util.ArrayList;"
                )
                get_block_register().init_code(f"""
public class BlockRegister {{

    public static void registry() {{
        registryBlocks();
    }}

    private static void registryBlocks() {{
        for (Object block : Container.get_all()) {{
            if (block instanceof Block blk) {{
                GameRegistry.registerBlock(blk, blk.getUnlocalizedName());
            }}
        }}
    }}
}}
                """)

        # 添加Block类所需的基础导入
        base_imports = [
            "import cpw.mods.fml.relauncher.Side;",
            "import cpw.mods.fml.relauncher.SideOnly;",
            "import net.minecraft.creativetab.CreativeTabs;",
            "import net.minecraft.block.Block;",
            "import net.minecraft.block.material.Material;",
            "import net.minecraft.client.renderer.texture.IIconRegister;",
            "import net.minecraft.item.ItemStack;",
            "import net.minecraft.world.World;"
        ]

        # 根据需求添加额外导入
        if self.has_item_block:
            base_imports.extend([
                "import net.minecraft.item.ItemBlock;",
                "import net.minecraft.entity.player.EntityPlayer;",
                "import java.util.List;"
            ])

        if self.has_tile_entity:
            base_imports.append("import net.minecraft.tileentity.TileEntity;")

        if self.has_custom_activation:
            base_imports.extend([
                "import net.minecraft.entity.EntityLivingBase;",
                "import net.minecraft.util.MathHelper;"
            ])

        self.add_import(*base_imports)

        # 生成Block类代码
        block_code = f"""
public class {self.class_name} extends Block {{

    public {self.class_name}(CreativeTabs aCreativeTabs) {{
        super(Material.iron);
        this.setResistance(20f);
        this.setHardness(-1.0f);
        this.setBlockName("{self.block_name}");
        this.setLightLevel(100.0f);
        this.setCreativeTab(aCreativeTabs);
    }}
"""
        # 添加特殊渲染方法
        if self.has_special_render:
            block_code += """
    @Override
    @SideOnly(Side.CLIENT)
    public void registerBlockIcons(IIconRegister iconRegister) {
        blockIcon = iconRegister.registerIcon("modid:TRANSPARENT");
    }

    @Override
    public boolean isOpaqueCube() {
        return false;
    }

    @Override
    public boolean renderAsNormalBlock() {
        return false;
    }

    @Override
    public int getRenderType() {
        return -1;
    }
"""

        # 添加TileEntity支持
        if self.has_tile_entity:
            block_code += """
    @Override
    public boolean hasTileEntity(int metadata) {
        return true;
    }

    @Override
    public TileEntity createTileEntity(World world, int metadata) {
        return new Tile{block_name}();
    }
""".replace("{block_name}", block_name)

        # 添加方块激活逻辑
        if self.has_custom_activation:
            block_code += """
    @Override
    public boolean onBlockActivated(World world, int x, int y, int z, EntityPlayer player, 
                                    int side, float hitX, float hitY, float hitZ) {
        // 自定义激活逻辑
        return super.onBlockActivated(world, x, y, z, player, side, hitX, hitY, hitZ);
    }

    @Override
    public void onBlockPlacedBy(World world, int x, int y, int z, 
                                EntityLivingBase placer, ItemStack stack) {
        // 自定义放置逻辑
    }
"""

        # 添加ItemBlock内部类
        if self.has_item_block:
            block_code += f"""
    // ItemBlock for {self.class_name}
    public static class ItemBlock{self.class_name} extends ItemBlock {{

        public ItemBlock{self.class_name}(Block block) {{
            super(block);
            this.setCreativeTab(TstCreativeTabs.TabGeneral);
            this.setHasSubtypes(true);
            this.setMaxDamage(0);
        }}

        @Override
        public String getUnlocalizedName(ItemStack stack) {{
            return super.getUnlocalizedName() + "." + stack.getItemDamage();
        }}

        @Override
        public int getMetadata(int meta) {{
            return meta;
        }}

        @Override
        @SideOnly(Side.CLIENT)
        public void addInformation(ItemStack stack, EntityPlayer player, 
                                  List list, boolean advanced) {{
            // 添加物品提示信息
            list.add("§bSpecial block functionality");
        }}
    }}
"""

        block_code += "\n}"
        self.init_code(block_code)

        # 在BlockRegister中添加注册条目
        register_field = f"{self.class_name.upper()}(new {self.class_name}(blockCreativeTabs)),"
        get_block_register().add_static_field(register_field)
        get_block_register().add_import(f"import {self.package.replace('/', '.')}.{self.class_name};")

    @overrides
    def get_template(self):
        pass
