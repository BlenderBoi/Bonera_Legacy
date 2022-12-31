
from . import Import_Pair_List
from . import Pair_List_Renamer_Panel
from . import Export_Pair_List

modules = [
    Import_Pair_List,
    Export_Pair_List,
    Pair_List_Renamer_Panel,
    ]

def register():

    for module in modules:
        module.register()

def unregister():

    for module in modules:
        module.unregister()

if __name__ == "__main__":
    register()
