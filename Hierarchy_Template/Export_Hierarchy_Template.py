import bpy
import bpy_extras.io_utils
import json
import pathlib

def write_some_data(context, filepath):

    scn = context.scene

    bonera_data = scn.Bonera_Scene_Data


    item_list = bonera_data.Hierarchy_Template
    item_index = bonera_data.Hierarchy_Template_Index

    datas = {}

    if len(item_list) > item_index:

        Active_Template = item_list[item_index]

        for item in Active_Template.parent:

            datas[item.name] = list([child.name for child in item.children])

        with open(filepath, "w") as f:
            json.dump(datas, f, indent=2)

    return {'FINISHED'}

class BONERA_OT_Export_Hierarchy_Template(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    """Export Hierarchy Template"""
    bl_idname = "bonera.export_hierarchy_template"
    bl_label = "Export Hierarchy Template"
    bl_options = {'UNDO', "REGISTER"}

    filename_ext = ".json"

    filter_glob: bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def invoke(self, context, _event):

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data
        item_list = bonera_data.Hierarchy_Template
        item_index = bonera_data.Hierarchy_Template_Index

        if len(item_list) > item_index:
            active_template = item_list[item_index]
            self.filepath = self.filepath + active_template.name
        else:
            self.report({"INFO"}, "No Template to Be Export")
            return {"FINISHED"}

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}



    def execute(self, context):
        return write_some_data(context, self.filepath)



classes = [BONERA_OT_Export_Hierarchy_Template]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
