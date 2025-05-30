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
