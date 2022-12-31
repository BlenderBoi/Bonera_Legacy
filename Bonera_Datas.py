
import bpy


def ENUM_PLR_Renamer_Switcher(self, context):

    scn = context.scene
    bonera_data = scn.Bonera_Scene_Data

    items = []
    item_list = bonera_data.PLR_Renamers

    if len(item_list) > 0:

        for index, item in enumerate(item_list):
            Item = (str(index), item.name, item.name)
            items.append(Item)

    Item = ("NEW*", "New*", "NEW*")
    items.append(Item)




    return items


def POLL_Bone_From_Selection_Armature(self, object):
    return object.type == 'ARMATURE'

def UPDATE_PLR_Renamer(self, context):
    scn = context.scene
    bonera_data = scn.Bonera_Scene_Data


    if bonera_data.PLR_Renamer_Switcher == "NEW*":

        item_list = bonera_data.PLR_Renamers
        item_index = bonera_data.PLR_Renamers_index

        item = item_list.add()
        item.name = "RenameList_" + str(len(bonera_data.PLR_Renamers))
        bonera_data.PLR_Renamers_index = len(item_list) - 1

    bonera_data.PLR_Renamers_index = int(bonera_data.PLR_Renamer_Switcher)

# def UPDATE_PLR_Renamer_Switcher(self, context):
    # scn = context.scene
    # scn.PLR_Renamer_Switcher = str(scn.PLR_Renamers_index)

    # scn.PLR_Renamer_Switcher = scn.PLR_Renamers[scn.PLR_Renamers_index]
    # Utility.update_UI()
    # pass


def Armature_Picker_Poll(self, object):

    if object.type == "ARMATURE":
        return True

def Curve_Picker_Poll(self, object):

    if object.type == "CURVE":
        return True


class BONERA_PLR_Pair_Rename(bpy.types.PropertyGroup):
    name_A : bpy.props.StringProperty()
    name_B : bpy.props.StringProperty()

class BONERA_PLR_Renamers(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty()
    rename_pairs : bpy.props.CollectionProperty(type=BONERA_PLR_Pair_Rename)
    rename_pairs_index : bpy.props.IntProperty()

class BONERA_BUIG(bpy.types.PropertyGroup):
    label : bpy.props.StringProperty()



class BONERA_HT_Children(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()

class BONERA_HT_Parent(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    children: bpy.props.CollectionProperty(type=BONERA_HT_Children)
    active_index: bpy.props.IntProperty()


class BONERA_Hierarchy_Template(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty()
    parent: bpy.props.CollectionProperty(type=BONERA_HT_Parent)
    active_index: bpy.props.IntProperty()



class Bonera_Scene_Data(bpy.types.PropertyGroup):
    Bone_From_Selection_Armature: bpy.props.PointerProperty(type=bpy.types.Object, poll=POLL_Bone_From_Selection_Armature)


    PLR_Renamer_Switcher: bpy.props.EnumProperty(items=ENUM_PLR_Renamer_Switcher, update=UPDATE_PLR_Renamer)
    PLR_Renamers: bpy.props.CollectionProperty(type=BONERA_PLR_Renamers)

    PLR_Renamers_Editindex: bpy.props.IntProperty()
    PLR_Renamers_index: bpy.props.IntProperty()

    BUIG_Armature_Picker : bpy.props.PointerProperty(type=bpy.types.Object, poll=Armature_Picker_Poll)
    BUIG : bpy.props.CollectionProperty(type=BONERA_BUIG)
    BUIG_Index : bpy.props.IntProperty()

    Hierarchy_Template: bpy.props.CollectionProperty(type=BONERA_Hierarchy_Template)
    Hierarchy_Template_Index : bpy.props.IntProperty()
    Show_Hierarchy_Template_Item: bpy.props.BoolProperty(default=True)


    Curve_Picker: bpy.props.PointerProperty(type=bpy.types.Object, poll=Curve_Picker_Poll)
    Armature_Picker : bpy.props.PointerProperty(type=bpy.types.Object, poll=Armature_Picker_Poll)


class Bonera_Util_Property(bpy.types.PropertyGroup):

    parent_target: bpy.props.StringProperty()



classes = [BONERA_HT_Children, BONERA_HT_Parent, BONERA_BUIG, BONERA_Hierarchy_Template, BONERA_PLR_Pair_Rename, BONERA_PLR_Renamers, Bonera_Scene_Data, Bonera_Util_Property]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.Bonera_Scene_Data = bpy.props.PointerProperty(type=Bonera_Scene_Data)
    bpy.types.Bone.Bonera_Util_Property = bpy.props.PointerProperty(type=Bonera_Util_Property)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.Bonera_Scene_Data
    del bpy.types.Bone.Bonera_Util_Property

if __name__ == "__main__":
    register()
