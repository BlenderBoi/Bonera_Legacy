import bpy
import bpy_extras.io_utils
import json
from Bonera_Toolkit import Utility_Functions


def read_some_data(context, filepath):

    scn = context.scene

    bonera_data = scn.Bonera_Scene_Data

    item_list = bonera_data.PLR_Renamers
    item_index = bonera_data.PLR_Renamers_index

    with open(filepath) as f:
        datas = json.load(f)

    for key, value in datas.items():

        if len(item_list) > 0:
            active_renamer = item_list[item_index]

            item_pairs = active_renamer.rename_pairs
            item = item_pairs.add()
            item.name_A = key
            item.name_B = value

    Utility_Functions.update_UI()

    return {'FINISHED'}

class BONERA_OT_Import_Rename_Pair_List(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Pair List"""
    bl_idname = "bonera.import_rename_pair_list"
    bl_label = "Import Rename Pair List"
    bl_options = {'UNDO', "REGISTER"}

    # Add_To_Active_Renamer: bpy.props.BoolProperty(default=False)

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        return read_some_data(context, self.filepath)



classes = [BONERA_OT_Import_Rename_Pair_List]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
