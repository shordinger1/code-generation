import os.path

from Agent.minecraft.library_like_class import library_like_class
from code_template.java_template_class import java_template_class

project_root = "default"
package_root = "default"

item_base = None
block_base = None
item_blocks_base = None
machine_entities_base = None
recipes_base = None
potions_base = None
renders_base = None
entities_base = None
mobs_base = None
item_register = None
block_register = None
item_blocks_register = None
machine_entities_register = None
recipes_register = None
potions_register = None
renders_register = None
entities_register = None
mobs_register = None


def init_global(root, pkg):
    global project_root, package_root
    project_root = root
    package_root = pkg


def get_root():
    return project_root


def get_package():
    return package_root


# Getter functions
def get_item_base(): return item_base


def get_block_base(): return block_base


def get_item_blocks_base(): return item_blocks_base


def get_machine_entities_base(): return machine_entities_base


def get_recipes_base(): return recipes_base


def get_potions_base(): return potions_base


def get_renders_base(): return renders_base


def get_entities_base(): return entities_base


def get_mobs_base(): return mobs_base


def get_item_register(): return item_register


def get_block_register(): return block_register


def get_item_blocks_register(): return item_blocks_register


def get_machine_entities_register(): return machine_entities_register


def get_recipes_register(): return recipes_register


def get_potions_register(): return potions_register


def get_renders_register(): return renders_register


def get_entities_register(): return entities_register


def get_mobs_register(): return mobs_register


# Setter functions
def set_item_base(value): global item_base; item_base = value


def set_block_base(value): global block_base; block_base = value


def set_item_blocks_base(value): global item_blocks_base; item_blocks_base = value


def set_machine_entities_base(value): global machine_entities_base; machine_entities_base = value


def set_recipes_base(value): global recipes_base; recipes_base = value


def set_potions_base(value): global potions_base; potions_base = value


def set_renders_base(value): global renders_base; renders_base = value


def set_entities_base(value): global entities_base; entities_base = value


def set_mobs_base(value): global mobs_base; mobs_base = value


def set_item_register(value): global item_register; item_register = value


def set_block_register(value): global block_register; block_register = value


def set_item_blocks_register(value): global item_blocks_register; item_blocks_register = value


def set_machine_entities_register(value): global machine_entities_register; machine_entities_register = value


def set_recipes_register(value): global recipes_register; recipes_register = value


def set_potions_register(value): global potions_register; potions_register = value


def set_renders_register(value): global renders_register; renders_register = value


def set_entities_register(value): global entities_register; entities_register = value


def set_mobs_register(value): global mobs_register; mobs_register = value


def init_base_and_registry():
    if project_root == "default":
        print("you should register a mod before init")
        exit(1)
    global item_base, block_base, item_blocks_base, machine_entities_base, recipes_base, potions_base, renders_base, \
        entities_base, mobs_base, item_register, block_register, item_blocks_register, machine_entities_register, \
        recipes_register, potions_register, renders_register, entities_register, mobs_register
    item_base = java_template_class(project_root, 'ItemBase', os.path.join(package_root, 'common/item'))
    block_base = java_template_class(project_root, 'BlockBase', os.path.join(package_root, 'common/block'))
    item_blocks_base = java_template_class(project_root, 'ItemBlocksBase', os.path.join(package_root, 'common/item'))
    machine_entities_base = java_template_class(project_root, 'MachineEntitiesBase',
                                                os.path.join(package_root, 'common/machine'))
    recipes_base = java_template_class(project_root, 'RecipesBase', os.path.join(package_root, 'common/recipe'))
    potions_base = java_template_class(project_root, 'PotionsBase', os.path.join(package_root, 'common/potion'))
    renders_base = java_template_class(project_root, 'RendersBase', os.path.join(package_root, 'common/render'))
    entities_base = java_template_class(project_root, 'EntitiesBase', os.path.join(package_root, 'common/entity'))
    mobs_base = java_template_class(project_root, 'MobsBase', os.path.join(package_root, 'common/mob'))
    item_register = library_like_class(project_root, 'ItemRegister', os.path.join(package_root, 'common/item'))
    block_register = library_like_class(project_root, 'BlockRegister', os.path.join(package_root, 'common/block'))
    item_blocks_register = library_like_class(project_root, 'ItemBlocksRegister',
                                              os.path.join(package_root, 'common/item'))
    machine_entities_register = library_like_class(project_root, 'MachineEntitiesRegister',
                                                   os.path.join(package_root, 'common/machine'))
    recipes_register = library_like_class(project_root, 'RecipesRegister', os.path.join(package_root, 'common/recipe'))
    potions_register = library_like_class(project_root, 'PotionsRegister', os.path.join(package_root, 'common/potion'))
    renders_register = library_like_class(project_root, 'RendersRegister', os.path.join(package_root, 'common/render'))
    entities_register = library_like_class(project_root, 'EntitiesRegister',
                                           os.path.join(package_root, 'common/entity'))
    mobs_register = library_like_class(project_root, 'MobsRegister', os.path.join(package_root, 'common/mob'))
