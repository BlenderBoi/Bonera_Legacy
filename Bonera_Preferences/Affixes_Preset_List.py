import bpy
from .. import Utility_Functions

class BONERA_Prefix(bpy.types.PropertyGroup):

    name : bpy.props.StringProperty()

class BONERA_Suffix(bpy.types.PropertyGroup):

    name : bpy.props.StringProperty()

class BONERA_UL_Affixes_List(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False)

#---------------------ENUM AREA---------------------

ENUM_list_choice = [("PREFIX","Prefix","Prefix"),("SUFFIX","Suffix","Suffix")]
ENUM_list_operation = [("ADD","Add","Add"),("REMOVE","Remove","Remove"), ("UP", "Up", "Up"), ("DOWN", "Down", "Down")]

#---------------------ENUM AREA---------------------

class BONERA_OT_Load_Reccommended(bpy.types.Operator):

    bl_idname = "bonera.load_reccommended"
    bl_label = "Load Reccommended"
    bl_info = {'REGISTER', "UNDO"}

    def execute(self, context):

        preferences = Utility_Functions.get_addon_preferences()

        preload_prefix = ["DEF_","MCH_", "CTRL_"]
        preload_suffix = ["_L","_R", "_Left", "_Right"]

        prefixes = preferences.Prefix_List
        suffixes = preferences.Suffix_List

        prefixes.clear()
        suffixes.clear()



        for s in preload_prefix:

            item = prefixes.add()
            item.name = s

        for p in preload_suffix:

            item = suffixes.add()
            item.name = p

        return {'FINISHED'}

class BONERA_Affixes_List_Operator(bpy.types.Operator):

    bl_idname = "bonera.affixes_list_operator"
    bl_label = "Affixes List Operator"

    list: bpy.props.EnumProperty(items=ENUM_list_choice)
    operation: bpy.props.EnumProperty(items=ENUM_list_operation)

    name: bpy.props.StringProperty()

    def draw(self, context):

        layout = self.layout

        if self.operation == "ADD":
            layout.prop(self, "name", text="Name")


    def invoke(self, context, event):
        if self.operation == "ADD":
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):

        preferences = Utility_Functions.get_addon_preferences()

        if self.list == "PREFIX":

            item_list = preferences.Prefix_List
            item_index = preferences.Prefix_List_Index

        if self.list == "SUFFIX":

            item_list = preferences.Suffix_List
            item_index = preferences.Suffix_List_Index

        if self.operation == "ADD":
            if self.name:
                item = item_list.add()
                item.name = self.name

                if self.list == "PREFIX":
                    preferences.Prefix_List_Index = len(item_list) - 1
                if self.list == "SUFFIX":
                    preferences.Suffix_List_Index = len(item_list) - 1

            Utility_Functions.update_UI()

            return {'FINISHED'}

        if self.operation == "REMOVE":

            item_list = item_list.remove(item_index)

        if self.operation == "UP":
            if item_index >= 1:
                item_list.move(item_index, item_index-1)

                if self.list == "PREFIX":
                    preferences.Prefix_List_Index -= 1
                if self.list == "SUFFIX":
                    preferences.Suffix_List_Index -= 1

                Utility_Functions.update_UI()
                return {'FINISHED'}

        if self.operation == "DOWN":
            if len(item_list)-1 > item_index:
                item_list.move(item_index, item_index+1)


                if self.list == "PREFIX":
                    preferences.Prefix_List_Index += 1
                if self.list == "SUFFIX":
                    preferences.Prefix_List_Index += 1

                Utility_Functions.update_UI()
                return {'FINISHED'}


        return {'FINISHED'}

classes = [BONERA_Prefix, BONERA_Suffix, BONERA_UL_Affixes_List, BONERA_Affixes_List_Operator, BONERA_OT_Load_Reccommended]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
