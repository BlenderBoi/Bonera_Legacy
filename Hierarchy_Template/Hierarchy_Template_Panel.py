import bpy
from Bonera_Toolkit import Utility_Functions



class BONERA_UL_Hierarchy_Template(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.prop(item, "name", text="", emboss=False)

class BONERA_UL_Hierarchy_Parent(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.prop(item, "name", text="", emboss=False)

class BONERA_UL_Hierarchy_Children(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.prop(item, "name", text="", emboss=False)


class BONERA_ARMATURE_PT_Hierarchy_Template(bpy.types.Panel):

    bl_label = "Hierarchy Template"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bonera"
    bl_options =  {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):

        preferences = Utility_Functions.get_addon_preferences()
        if preferences.SECTION_Hierarchy_Template:
            return True

    def draw(self, context):

        scn = context.scene
        layout = self.layout



        bonera_data = scn.Bonera_Scene_Data
        active_index = bonera_data.Hierarchy_Template_Index

        row = layout.row(align=False)
        row.template_list("BONERA_UL_Hierarchy_Template", "", bonera_data, "Hierarchy_Template", bonera_data, "Hierarchy_Template_Index")
        col = row.column(align=True)

        operator = col.operator("bonera.hierarchy_template_list_operator", text="", icon="ADD")
        operator.operation = "ADD"
        operator.index = active_index

        operator = col.operator("bonera.hierarchy_template_list_operator", text="", icon="REMOVE")
        operator.operation = "REMOVE"
        operator.index = active_index

        col.separator()

        operator = col.operator("bonera.hierarchy_template_list_operator", text="", icon="TRIA_UP")
        operator.operation = "UP"
        operator.index = active_index

        operator = col.operator("bonera.hierarchy_template_list_operator", text="", icon="TRIA_DOWN")
        operator.operation = "DOWN"
        operator.index = active_index



        box = layout.box()
        if Utility_Functions.draw_subpanel(bonera_data, bonera_data.Show_Hierarchy_Template_Item, "Show_Hierarchy_Template_Item", "Show Item", box):

            if bonera_data.Hierarchy_Template_Index < len(bonera_data.Hierarchy_Template):

                Active_Template = bonera_data.Hierarchy_Template[bonera_data.Hierarchy_Template_Index]
                active_index = Active_Template.active_index

                row = box.row(align=True)
                col = row.column(align=True)

                col.label(text="Parent Bone")
                col.template_list("BONERA_UL_Hierarchy_Parent", "", Active_Template, "parent", Active_Template, "active_index")

                row_item = col.row(align=True)


                operator = row_item.operator("bonera.ht_parent_list_operator", text="", icon="ADD")
                operator.operation = "ADD"
                operator.index = active_index

                operator = row_item.operator("bonera.ht_parent_list_operator", text="", icon="REMOVE")
                operator.operation = "REMOVE"
                operator.index = active_index

                row_item.separator()

                operator = row_item.operator("bonera.ht_parent_list_operator", text="", icon="TRIA_UP")
                operator.operation = "UP"
                operator.index = active_index

                operator = row_item.operator("bonera.ht_parent_list_operator", text="", icon="TRIA_DOWN")
                operator.operation = "DOWN"
                operator.index = active_index


                box.operator("bonera.batch_rename_hierarchy_template", text="Batch Rename")

                if Active_Template.active_index < len(Active_Template.parent):

                    active_parent = Active_Template.parent[Active_Template.active_index]
                    active_index = active_parent.active_index
                    col = row.column(align=True)

                    col.label(text="Childrens Bone")
                    col.template_list("BONERA_UL_Hierarchy_Children", "", active_parent, "children", active_parent, "active_index")

                    row_item = col.row(align=True)

                    operator = row_item.operator("bonera.ht_children_list_operator", text="", icon="ADD")
                    operator.operation = "ADD"
                    operator.index = active_index

                    operator = row_item.operator("bonera.ht_children_list_operator", text="", icon="REMOVE")
                    operator.operation = "REMOVE"
                    operator.index = active_index

                    row_item.separator()

                    operator = row_item.operator("bonera.ht_children_list_operator", text="", icon="TRIA_UP")
                    operator.operation = "UP"
                    operator.index = active_index

                    operator = row_item.operator("bonera.ht_children_list_operator", text="", icon="TRIA_DOWN")
                    operator.operation = "DOWN"
                    operator.index = active_index









                else:
                    col = row.column(align=True)
                    col.label(text="Childrens Bone")
                    box = col.box()
                    operator = box.operator("bonera.ht_parent_list_operator", text="Add Parent Bone", icon="ADD")
                    operator.operation = "ADD"
                    operator.index = active_index
            else:
                operator = box.operator("bonera.hierarchy_template_list_operator", text="New Template", icon="ADD")
                operator.operation = "ADD"
                operator.index = active_index


        layout.operator("bonera.hierarchy_template_create_from_armature", text="Create Template From Armature", icon="PLUS")

        layout.operator("bonera.apply_hierarchy_template_to_selected", text="Apply Hierarchy Template")




        row = layout.row(align=True)
        row.operator("bonera.import_hierarchy_template", text="Import", icon="IMPORT")
        row.operator("bonera.export_hierarchy_template", text="Export", icon="EXPORT")





ENUM_list_operation = [("ADD","Add","Add"),("REMOVE","Remove","Remove"),("UP","Up","Up"),("DOWN","Down","Down")]


class BONERA_HT_Children_List_Operator(bpy.types.Operator):

    """List Operator"""

    bl_idname = "bonera.ht_children_list_operator"
    bl_label = "List Operator"
    bl_options = {'UNDO', "REGISTER"}

    operation: bpy.props.EnumProperty(items=ENUM_list_operation)
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty(default="Bone_Child")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Children Bone Name")


    def invoke(self, context, event):

        scn = context.scene


        if self.operation in ["ADD"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


    def execute(self, context):


        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data


        item_list = None
        item_index = None
        active_template = None

        template_item_list = bonera_data.Hierarchy_Template
        template_item_index = bonera_data.Hierarchy_Template_Index

        if template_item_index < len(template_item_list):
            active_template = template_item_list[template_item_index]

            if active_template:

                if len(active_template.parent) > active_template.active_index:

                    active_parent = active_template.parent[active_template.active_index]


                    item_list =  active_parent.children
                    item_index = active_parent.active_index


                    if self.operation == "REMOVE":
                        item_list.remove(self.index)

                        if len(item_list) == active_parent.active_index:
                            active_parent.active_index = len(item_list) - 1
                        if len(item_list) == 0:
                            active_parent.active_index = 0
                        Utility_Functions.update_UI()
                        return {'FINISHED'}

                    if self.operation == "ADD":

                        item = item_list.add()
                        item.name = self.name
                        active_parent.active_index = len(item_list) - 1
                        Utility_Functions.update_UI()
                        return {'FINISHED'}

                    if self.operation == "UP":
                        if item_index >= 1:
                            item_list.move(item_index, item_index-1)
                            active_parent.active_index-= 1
                            return {'FINISHED'}

                    if self.operation == "DOWN":
                        if len(item_list)-1 > item_index:
                            item_list.move(item_index, item_index+1)
                            active_parent.active_index+= 1
                            return {'FINISHED'}

        Utility_Functions.update_UI()
        return {'FINISHED'}






class BONERA_HT_Parent_List_Operator(bpy.types.Operator):

    """List Operator"""
    bl_idname = "bonera.ht_parent_list_operator"
    bl_label = "List Operator"
    bl_options = {'UNDO', "REGISTER"}

    operation: bpy.props.EnumProperty(items=ENUM_list_operation)
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty(default="Bone_Parent")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Parent Bone Name")


    def invoke(self, context, event):

        scn = context.scene


        if self.operation in ["ADD"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


    def execute(self, context):


        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = None
        item_index = None
        active_template = None

        template_item_list = bonera_data.Hierarchy_Template
        template_item_index = bonera_data.Hierarchy_Template_Index

        if template_item_index < len(template_item_list):
            active_template = template_item_list[template_item_index]
            item_list =  active_template.parent
            item_index = active_template.active_index

        if active_template:


            if self.operation == "REMOVE":
                item_list.remove(self.index)

                if len(item_list) == active_template.active_index:
                    active_template.active_index = len(item_list) - 1
                if len(item_list) == 0:
                    active_template.active_index = 0
                Utility_Functions.update_UI()
                return {'FINISHED'}

            if self.operation == "ADD":

                item = item_list.add()
                item.name = self.name
                active_template.active_index = len(item_list) - 1
                Utility_Functions.update_UI()
                return {'FINISHED'}

            if self.operation == "UP":
                if item_index >= 1:
                    item_list.move(item_index, item_index-1)
                    active_template.active_index-= 1
                    return {'FINISHED'}

            if self.operation == "DOWN":
                if len(item_list)-1 > item_index:
                    item_list.move(item_index, item_index+1)
                    active_template.active_index+= 1
                    return {'FINISHED'}

        Utility_Functions.update_UI()
        return {'FINISHED'}





class BONERA_Hierarchy_Template_List_Operator(bpy.types.Operator):

    """List Operator"""
    bl_idname = "bonera.hierarchy_template_list_operator"
    bl_label = "List Operator"
    bl_options = {'UNDO', "REGISTER"}

    operation: bpy.props.EnumProperty(items=ENUM_list_operation)
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty(default="Parameter01")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Template Name")


    def invoke(self, context, event):

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        self.name = "Template_" + str(len(bonera_data.Hierarchy_Template))

        if self.operation in ["ADD"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


    def execute(self, context):

        # obj = context.object
        # data = obj.data

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = bonera_data.Hierarchy_Template
        item_index = bonera_data.Hierarchy_Template_Index

        if self.operation == "REMOVE":
            item_list.remove(self.index)

            if len(item_list) == bonera_data.Hierarchy_Template_Index:
                bonera_data.Hierarchy_Template_Index = len(item_list) - 1
            if len(item_list) == 0:
                bonera_data.Hierarchy_Template_Index= 0
            Utility_Functions.update_UI()

            return {'FINISHED'}

        if self.operation == "ADD":

            item = item_list.add()
            item.name = self.name
            bonera_data.Hierarchy_Template_Index = len(item_list) - 1
            Utility_Functions.update_UI()
            return {'FINISHED'}

        if self.operation == "UP":
            if item_index >= 1:
                item_list.move(item_index, item_index-1)
                bonera_data.Hierarchy_Template_Index -= 1
                return {'FINISHED'}

        if self.operation == "DOWN":
            if len(item_list)-1 > item_index:
                item_list.move(item_index, item_index+1)
                bonera_data.Hierarchy_Template_Index += 1
                return {'FINISHED'}

        Utility_Functions.update_UI()
        return {'FINISHED'}


class BONERA_HT_Create_Template_From_Armature(bpy.types.Operator):
    """Create Template From Armature"""
    bl_idname = "bonera.hierarchy_template_create_from_armature"
    bl_label = "Template From Armature"
    bl_options = {'UNDO', "REGISTER"}

    skip_childless_bone: bpy.props.BoolProperty(default=False)
    new_template: bpy.props.BoolProperty(default=True)


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "skip_childless_bone", text="Skip Childless Bone")
        layout.prop(self, "new_template", text="New Template")


    def invoke(self, context, event):


        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        scn = context.scene
        selected_objects = [obj for obj in context.selected_objects if obj.type == "ARMATURE"]

        mode = context.mode


        if len(selected_objects) > 0:

            for obj in selected_objects:

                bonera_data = scn.Bonera_Scene_Data
                hierarchy_template = bonera_data.Hierarchy_Template
                hierarchy_template_index = bonera_data.Hierarchy_Template_Index

                active_template = None

                if self.new_template:
                    active_template = hierarchy_template.add()
                    active_template.name = obj.name + "_template"
                    bonera_data.Hierarchy_Template_Index = len(hierarchy_template) - 1

                else:

                    if len(hierarchy_template) > hierarchy_template_index:
                        active_template = hierarchy_template[hierarchy_template_index]
                    else:
                        active_template = hierarchy_template.add()
                        active_template.name = self.template_name
                        bonera_data.Hierarchy_Template_Index = len(hierarchy_template) - 1


                if mode == "OBJECT":
                    bones = obj.data.bones
                if mode == "POSE":
                    bones = obj.data.bones
                if mode == "EDIT_ARMATURE":
                    bones = obj.data.edit_bones

                for bone in bones:



                    if self.skip_childless_bone:
                        if len(bone.children) == 0:
                            continue

                    if mode in ["EDIT_ARMATURE", "POSE"]:
                        if not bone.select:
                            continue


                    parent_item = active_template.parent.add()
                    parent_item.name = bone.name

                    for child in bone.children:
                        children_item = parent_item.children.add()
                        children_item.name = child.name











        Utility_Functions.update_UI()
        return {'FINISHED'}





class BONERA_HT_Apply_Template_Hierarchy(bpy.types.Operator):
    """Apply Template Hierarchy To Selected Armature"""
    bl_idname = "bonera.apply_hierarchy_template_to_selected"
    bl_label = "Apply Hierarchy Template To Selected"
    bl_options = {'UNDO', "REGISTER"}


    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a Destructive Operation, Are You Sure?", icon="ERROR")


    def invoke(self, context, event):


        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        scn = context.scene
        selected_objects = [obj for obj in context.selected_objects if obj.type == "ARMATURE"]

        mode = context.mode



        if len(selected_objects) > 0:

            restore_mode = selected_objects[0].mode



            for obj in selected_objects:

                Utility_Functions.object_switch_mode(obj, "EDIT")
                bonera_data = scn.Bonera_Scene_Data
                hierarchy_template = bonera_data.Hierarchy_Template
                hierarchy_template_index = bonera_data.Hierarchy_Template_Index

                active_template = None

                if len(hierarchy_template) > hierarchy_template_index:
                    active_template = hierarchy_template[hierarchy_template_index]

                    # for bone in obj.data.bones:

                    for parent_item in active_template.parent:
                        bone = obj.data.edit_bones.get(parent_item.name)

                        if mode in ["EDIT_ARMATURE", "POSE"]:
                            if not bone.select:
                                continue

                        if bone:
                            for child_item in parent_item.children:
                                child_bone = obj.data.edit_bones.get(child_item.name)
                                if child_bone:
                                    child_bone.parent = bone



            Utility_Functions.object_switch_mode(obj, restore_mode)











        Utility_Functions.update_UI()
        return {'FINISHED'}



class BONERA_Align_Parent_To_Child(bpy.types.Operator):
    """Align Parent Bone to Child"""
    bl_idname = "bonera.align_parent_to_child"
    bl_label = "Align Parent To Child"
    bl_options = {'UNDO', "REGISTER"}

    connect_bone: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a Destructive Operation, Are You Sure?", icon="ERROR")
        layout.prop(self, "connect_bone", text="Connect Bone")


    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        scn = context.scene
        selected_objects = [obj for obj in context.selected_objects if obj.type == "ARMATURE"]

        mode = context.mode



        if len(selected_objects) > 0:

            restore_mode = selected_objects[0].mode


            for obj in selected_objects:

                Utility_Functions.object_switch_mode(obj, "EDIT")
                bonera_data = scn.Bonera_Scene_Data

                for bone in obj.data.edit_bones:

                    if mode in ["EDIT_ARMATURE", "POSE"]:
                        if not bone.select:
                            continue

                    if bone:

                        child_bone_pos = [cb.head for cb in bone.children]
                        child_midpoint = Utility_Functions.midpoint(child_bone_pos, "CENTER")


                        for child_bone in bone.children:
                            bone.tail = child_midpoint
                            if self.connect_bone:
                                child_bone.use_connect = True
                                # child_bone.parent = bone



            Utility_Functions.object_switch_mode(obj, restore_mode)











        Utility_Functions.update_UI()
        return {'FINISHED'}


























ENUM_Rename_Mode = [("REPLACE", "Replace", "Replace"), ("PREFIX","Prefix","Prefix"),("SUFFIX","Suffix","Suffix")]

class BONERA_HT_Batch_Rename(bpy.types.Operator):
    """Batch Rename Hierarchy Template"""
    bl_idname = "bonera.batch_rename_hierarchy_template"
    bl_label = "Batch Rename Hierarchy Template"
    bl_options = {'UNDO', "REGISTER"}

    name_a: bpy.props.StringProperty()
    name_b: bpy.props.StringProperty()
    rename_parent: bpy.props.BoolProperty(default=True)
    rename_children: bpy.props.BoolProperty(default=True)
    mode: bpy.props.EnumProperty(items=ENUM_Rename_Mode)



    def draw(self, context):
        layout = self.layout

        layout.prop(self, "mode", expand=True)

        if self.mode == "REPLACE":
            layout.prop(self, "name_a", text="Find")
            layout.prop(self, "name_b", text="Replace")

        if self.mode == "PREFIX":
            layout.prop(self, "name_a", text="Prefix")

        if self.mode == "SUFFIX":
            layout.prop(self, "name_a", text="Suffix")

        layout.prop(self, "rename_parent", text="Rename Parent")
        layout.prop(self, "rename_children", text="Rename Children")


    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)


    def execute(self, context):

        scn = context.scene

        bonera_data = scn.Bonera_Scene_Data
        hierarchy_template = bonera_data.Hierarchy_Template
        hierarchy_template_index = bonera_data.Hierarchy_Template_Index

        active_template = None

        if len(hierarchy_template) > hierarchy_template_index:
            active_template = hierarchy_template[hierarchy_template_index]

            for parent_item in active_template.parent:

                if self.rename_parent:
                    if self.mode == "REPLACE":
                        parent_item.name = parent_item.name.replace(self.name_a, self.name_b)
                    if self.mode == "PREFIX":
                        parent_item.name = self.name_a + parent_item.name
                    if self.mode == "SUFFIX":
                        parent_item.name = parent_item.name + self.name_a


                for child_item in parent_item.children:
                    if self.rename_children:
                        if self.mode == "REPLACE":
                            child_item.name = child_item.name.replace(self.name_a, self.name_b)
                        if self.mode == "PREFIX":
                            child_item.name = self.name_a + child_item.name
                        if self.mode == "SUFFIX":
                            child_item.name = child_item.name + self.name_a














        Utility_Functions.update_UI()
        return {'FINISHED'}





classes=[BONERA_Align_Parent_To_Child, BONERA_HT_Batch_Rename, BONERA_HT_Apply_Template_Hierarchy, BONERA_HT_Create_Template_From_Armature, BONERA_HT_Children_List_Operator, BONERA_HT_Parent_List_Operator, BONERA_UL_Hierarchy_Children, BONERA_UL_Hierarchy_Parent, BONERA_UL_Hierarchy_Template, BONERA_Hierarchy_Template_List_Operator]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)



def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
