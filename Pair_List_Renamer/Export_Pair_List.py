import bpy
import bpy_extras.io_utils
import json

def write_some_data(context, filepath):

    scn = context.scene

    bonera_data = scn.Bonera_Scene_Data


    item_list = bonera_data.PLR_Renamers
    item_index = bonera_data.PLR_Renamers_index

    datas = {}

    if len(item_list) > 0:
        Active_Renamer = item_list[item_index]

        for item in Active_Renamer.rename_pairs:

            active_renamer = item_list[item_index]
            datas[item.name_A] = item.name_B

        with open(filepath, "w") as f:
            json.dump(datas, f, indent=2)

    return {'FINISHED'}

class BONERA_OT_Export_Rename_Pair_List(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Pair List (Duplicates will be ignored)"""
    bl_idname = "bonera.export_rename_pair_list"
    bl_label = "Export Rename Pair List"
    bl_options = {'UNDO', "REGISTER"}

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        return write_some_data(context, self.filepath)



classes = [BONERA_OT_Export_Rename_Pair_List]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
