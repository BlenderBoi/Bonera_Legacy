import bpy
import bpy_extras.io_utils
import json
from Bonera_Toolkit import Utility_Functions
import pathlib


def read_some_data(context, filepath):

    scn = context.scene

    bonera_data = scn.Bonera_Scene_Data

    item_list = bonera_data.Hierarchy_Template
    item_index = bonera_data.Hierarchy_Template_Index


    new_template = bonera_data.Hierarchy_Template.add()
    new_template.name = pathlib.Path(filepath).stem

    with open(filepath) as f:
        datas = json.load(f)

    for key, value in datas.items():

        if len(item_list) > 0:

            new_parent = new_template.parent.add()
            new_parent.name = key

            for child in value:
                new_child = new_parent.children.add()
                new_child.name = child

    Utility_Functions.update_UI()

    return {'FINISHED'}

class BONERA_OT_Import_Hierarchy_Template(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Import Hierarchy Template"""
    bl_idname = "bonera.import_hierarchy_template"
    bl_label = "Import Hierarchy Template"
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



classes = [BONERA_OT_Import_Hierarchy_Template]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
