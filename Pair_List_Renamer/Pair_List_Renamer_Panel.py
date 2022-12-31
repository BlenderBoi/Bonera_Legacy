import bpy
from Bonera_Toolkit import Utility_Functions



class BONERA_PT_Pair_List_Renamer(bpy.types.Panel):

    bl_label = "Pair List Renamer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bonera"
    bl_options =  {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        preferences = Utility_Functions.get_addon_preferences()

        if preferences.SECTION_Bonera_Pair_Renamer:
            return True


    def draw(self, context):

        scn = context.scene

        bonera_data = scn.Bonera_Scene_Data


        layout = self.layout
        preferences = Utility_Functions.get_addon_preferences()

        RENAMERS = bonera_data.PLR_Renamers
        RENAMERS_active_index = bonera_data.PLR_Renamers_index

        if len(RENAMERS) > 0:
            layout.prop(bonera_data, "PLR_Renamer_Switcher", text="")

            active_RENAMERS = RENAMERS[bonera_data.PLR_Renamers_index]

            row = layout.row(align=False)

            col = row.column(align=True)

            col.template_list("BONERA_UL_PLR_Rename_Pairs", "", active_RENAMERS, "rename_pairs", active_RENAMERS, "rename_pairs_index")

            col2 = row.column(align=True)
            operator = col2.operator("bonera.plr_pair_list_operator", text="", icon="ADD")
            operator.operation = "ADD"


            operator = col2.operator("bonera.plr_pair_list_operator", text="", icon="REMOVE")
            operator.operation = "REMOVE"
            col2.separator()
            col2.operator("bonera.plr_swap_pair", text="", icon="ARROW_LEFTRIGHT")
            col2.separator()
            operator = col2.operator("bonera.plr_pair_list_operator", text="", icon="TRIA_UP")
            operator.operation = "UP"

            operator = col2.operator("bonera.plr_pair_list_operator", text="", icon="TRIA_DOWN")
            operator.operation = "DOWN"

            # col2.separator()


            # col2.separator()

            #Set to Correct Index
            operator.index = active_RENAMERS.rename_pairs_index

            col.prop(active_RENAMERS, "name", text="")

            layout.operator("bonera.plr_rename_list", text="Rename List")
            layout.operator("bonera.plr_list_loader", text="Load Name")

            row = layout.row(align=True)

            row.operator("bonera.import_rename_pair_list", text="Import")
            row.operator("bonera.export_rename_pair_list", text="Export")

            operator = layout.operator("bonera.plr_pair_list_operator", text="Clear List", icon="TRASH")
            operator.operation = "CLEAR"

        else:
            operator = layout.operator("bonera.plr_list_operator", text="Add Renamer", icon="ADD")
            operator.operation = "ADD"

        if preferences.show_RENAMER_List:
            SHOW_ICON = "TRIA_DOWN"
        else:
            SHOW_ICON = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"

        row.prop(preferences, "show_RENAMER_List", text="Renamer List", emboss=False, icon=SHOW_ICON)

        if preferences.show_RENAMER_List:
            row = layout.row(align=True)
            row.template_list("BONERA_UL_PLR_Renamers", "", bonera_data, "PLR_Renamers", bonera_data, "PLR_Renamers_Editindex")

            col = row.column(align=True)

            operator = col.operator("bonera.plr_list_operator", text="", icon="ADD")
            operator.operation = "ADD"
            operator.index = bonera_data.PLR_Renamers_Editindex

            operator = col.operator("bonera.plr_list_operator", text="", icon="REMOVE")
            operator.operation = "REMOVE"
            operator.index = bonera_data.PLR_Renamers_Editindex

            col.separator()

            operator = col.operator("bonera.plr_list_operator", text="", icon="TRIA_UP")
            operator.operation = "UP"
            operator.index = bonera_data.PLR_Renamers_Editindex

            operator = col.operator("bonera.plr_list_operator", text="", icon="TRIA_DOWN")
            operator.operation = "DOWN"
            operator.index = bonera_data.PLR_Renamers_Editindex

            col.separator()

            operator = layout.operator("bonera.plr_list_operator", text="Clear List", icon="TRASH")
            operator.operation = "CLEAR"
            operator.index = bonera_data.PLR_Renamers_Editindex

ENUM_list_operation = [("ADD","Add","Add"),("REMOVE","Remove","Remove"),("UP","Up","Up"),("DOWN","Down","Down"), ("CLEAR", "Clear", "Clear")]
ENUM_Pair_list_operation = [("ADD","Add","Add"),("REMOVE","Remove","Remove"), ("SWAP", "Swap", "Swap"),("UP","Up","Up"),("DOWN","Down","Down"), ("CLEAR", "Clear", "Clear")]

class BONERA_PLR_Pair_List_Operator(bpy.types.Operator):
    """Pair List Operator"""
    bl_idname = "bonera.plr_pair_list_operator"
    bl_label = "List Operator"
    bl_options = {'UNDO', "REGISTER"}

    operation: bpy.props.EnumProperty(items=ENUM_Pair_list_operation)
    index: bpy.props.IntProperty()
    NameA: bpy.props.StringProperty(default="NameA")
    NameB: bpy.props.StringProperty(default="NameB")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "NameA", text="Name A")
        layout.prop(self, "NameB", text="Name B")


    def invoke(self, context, event):

        if self.operation in ["ADD"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


    def execute(self, context):

        # obj = context.object
        # data = obj.data

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = bonera_data.PLR_Renamers
        item_index = bonera_data.PLR_Renamers_index



        if len(item_list) > 0:


            active_item = item_list[item_index]
            item_pair_list = active_item.rename_pairs
            item_pair_index = active_item.rename_pairs_index

            if self.operation == "CLEAR":
                item_pair_list.clear()

            if self.operation == "REMOVE":
                if len(item_pair_list) > 0:
                    item_pair_list.remove(item_pair_index)

                    if len(item_pair_list) == active_item.rename_pairs_index:
                        active_item.rename_pairs_index = len(item_pair_list) - 1

                    Utility_Functions.update_UI()

                return {'FINISHED'}

            if self.operation == "ADD":

                item = item_pair_list.add()
                item.name_A = self.NameA
                item.name_B = self.NameB
                active_item.rename_pairs_index = len(item_pair_list) - 1
                Utility_Functions.update_UI()
                return {'FINISHED'}

            if self.operation == "SWAP":
                if len(item_pair_list) > 0:
                    item = item_pair_list[self.index]

                    NameA = item.name_A
                    NameB = item.name_B

                    item.name_B = NameA
                    item.name_A = NameB


                    Utility_Functions.update_UI()
                return {'FINISHED'}

            if self.operation == "UP":
                if item_pair_index >= 1:
                    item_pair_list.move(item_pair_index, item_pair_index-1)
                    active_item.rename_pairs_index -= 1
                    return {'FINISHED'}

            if self.operation == "DOWN":
                if len(item_pair_list)-1 > item_pair_index:
                    item_pair_list.move(item_pair_index, item_pair_index+1)
                    active_item.rename_pairs_index += 1
                    return {'FINISHED'}



        Utility_Functions.update_UI()
        return {'FINISHED'}

class BONERA_PLR_Swap_Pair(bpy.types.Operator):
    """Swap Pair"""
    bl_idname = "bonera.plr_swap_pair"
    bl_label = "Swap Pair"
    bl_options = {'UNDO', "REGISTER"}

    def execute(self, context):

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = bonera_data.PLR_Renamers
        item_index = bonera_data.PLR_Renamers_index

        if len(item_list) > 0:
            active_renamer = item_list[item_index]

            Rename_Pairs = active_renamer.rename_pairs

            for pair in Rename_Pairs:
                nameA = pair.name_A
                nameB = pair.name_B

                pair.name_A = nameB
                pair.name_B = nameA


        Utility_Functions.update_UI()
        return {'FINISHED'}

class BONERA_PLR_List_Operator(bpy.types.Operator):
    """List Operator"""
    bl_idname = "bonera.plr_list_operator"
    bl_label = "List Operator"
    bl_options = {'UNDO', "REGISTER"}

    operation: bpy.props.EnumProperty(items=ENUM_list_operation)
    index: bpy.props.IntProperty()
    name: bpy.props.StringProperty(default="Parameter01")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Name")


    def invoke(self, context, event):


        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        RENAMERS = bonera_data.PLR_Renamers

        self.name = "RenameList_" + str(len(RENAMERS))

        if self.operation in ["ADD"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)

    def execute(self, context):

        obj = context.object
        # data = obj.data

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = bonera_data.PLR_Renamers
        item_index = bonera_data.PLR_Renamers_Editindex

        if self.operation == "CLEAR":
            item_list.clear()


        if self.operation == "REMOVE":


            current_item = bonera_data.PLR_Renamer_Switcher

            item_list.remove(item_index)

            if bonera_data.PLR_Renamer_Switcher == "NEW*":
                if len(item_list) > 0:
                    bonera_data.PLR_Renamer_Switcher = str(len(item_list) - 1)
            else:
                bonera_data.PLR_Renamer_Switcher = current_item


            if len(item_list) == bonera_data.PLR_Renamers_Editindex:
                bonera_data.PLR_Renamers_Editindex = len(item_list) - 1

            Utility_Functions.update_UI()
            return {'FINISHED'}

        if self.operation == "ADD":

            item = item_list.add()
            item.name = self.name
            bonera_data.PLR_Renamers_Editindex = len(item_list) - 1
            Utility_Functions.update_UI()
            return {'FINISHED'}

        if self.operation == "UP":
            if item_index >= 1:
                item_list.move(item_index, item_index-1)
                bonera_data.PLR_Renamers_Editindex -= 1
                return {'FINISHED'}

        if self.operation == "DOWN":
            if len(item_list)-1 > item_index:
                item_list.move(item_index, item_index+1)
                bonera_data.PLR_Renamers_Editindex += 1
                return {'FINISHED'}


        Utility_Functions.update_UI()
        return {'FINISHED'}

def ENUM_Loader_Mode(self, context):

    items = []
    # object = context.object
    object = bpy.context.view_layer.objects.get(self.Load_Object)

    if object:
        if object.type == "MESH":
            item = ("VERTEX_GROUPS", "Vertex Groups", "Vertex Group")
            items.append(item)

        if object.type in ["MESH", "CURVE"]:
            item = ("SHAPEKEYS", "Shapekey", "Shapekey")
            items.append(item)

        if object.type == "ARMATURE":
            item = ("BONES", "Bones", "Bones")
            items.append(item)

    if len(items) == 0:
        items = [("NONE", "None", "None")]

    return items

class BONERA_PLR_List_Loader(bpy.types.Operator):
    """Load List"""
    bl_idname = "bonera.plr_list_loader"
    bl_label = "List Loader"
    bl_options = {'UNDO', "REGISTER"}

    Loader_Mode: bpy.props.EnumProperty(items=ENUM_Loader_Mode)
    Load_Object: bpy.props.StringProperty()

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "Loader_Mode", text="Mode")
        layout.prop_search(self, "Load_Object", bpy.context.view_layer, "objects", text="Object")

    def invoke(self, context, event):
        if context.object:
            self.Load_Object = context.object.name

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        obj = bpy.context.view_layer.objects.get(self.Load_Object)

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = bonera_data.PLR_Renamers
        item_index = bonera_data.PLR_Renamers_index

        if obj:

            if len(item_list) > 0:
                active_renamer = item_list[item_index]

                if self.Loader_Mode == "VERTEX_GROUPS":
                    for vertex_group in obj.vertex_groups:

                        item_pairs = active_renamer.rename_pairs
                        item = item_pairs.add()
                        item.name_A = vertex_group.name

                if self.Loader_Mode == "BONES":
                    for bone in obj.data.bones:

                        item_pairs = active_renamer.rename_pairs
                        item = item_pairs.add()
                        item.name_A = bone.name

                if self.Loader_Mode == "SHAPEKEYS":

                    if obj.data.shape_keys:

                        for shapekey in obj.data.shape_keys.key_blocks:

                            item_pairs = active_renamer.rename_pairs
                            item = item_pairs.add()
                            item.name_A = shapekey.name

        Utility_Functions.update_UI()
        return {'FINISHED'}

def ENUM_Renamer_Mode(self, context):

    items = []
    object = bpy.context.view_layer.objects.get(self.object)

    if object:
        if object.type == "MESH":
            item = ("VERTEX_GROUPS", "Vertex Groups", "Vertex Group")
            items.append(item)

        if object.type in ["MESH", "CURVE"]:
            item = ("SHAPEKEYS", "Shapekey", "Shapekey")
            items.append(item)

        if object.type == "ARMATURE":
            item = ("BONES", "Bones", "Bones")
            items.append(item)

    if len(items) == 0:
        items = [("NONE", "None", "None")]

    return items

class BONERA_OT_PLR_Rename_List(bpy.types.Operator):
    """Rename List"""
    bl_idname = "bonera.plr_rename_list"
    bl_label = "Rename List"
    bl_options = {'UNDO', "REGISTER"}


    mode : bpy.props.EnumProperty(items=ENUM_Renamer_Mode)
    object: bpy.props.StringProperty()


    def invoke(self, context, event):

        if context.object:
            self.object = context.object.name

        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        layout = self.layout
        layout.prop_search(self, "object", context.view_layer, "objects")
        layout.prop(self, "mode", text="Mode")

    def execute(self, context):

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = bonera_data.PLR_Renamers
        item_index = bonera_data.PLR_Renamers_index

        object = context.view_layer.objects.get(self.object)

        # selected_objects = [object for object in context.selected_objects]

        # for object in selected_objects:

        if object:
            if object:

                if len(item_list) > 0:
                    active_renamer = item_list[item_index]

                    item_pairs = active_renamer.rename_pairs

                    for pair in item_pairs:

                        if self.mode == "BONES":

                            if object.type in ["ARMATURE"]:
                                bone = object.data.bones.get(pair.name_A)
                                if bone:
                                    if pair.name_B:
                                        bone.name = pair.name_B

                        if self.mode == "VERTEX_GROUPS":

                            if object.type in ["MESH"]:
                                vertex_group = object.vertex_groups.get(pair.name_A)

                                if vertex_group:
                                    if pair.name_B:
                                        vertex_group.name = pair.name_B

                        if self.mode == "SHAPEKEYS":
                            if object.type in ["MESH", "CURVE"]:
                                if object.data.shape_keys:
                                    shape_key = object.data.shape_keys.key_blocks.get(pair.name_A)

                                    if shape_key:
                                        if pair.name_B:
                                            shape_key.name = pair.name_B

        return {'FINISHED'}

class BONERA_UL_PLR_Renamers(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.prop(item, "name", text="", emboss=False)

class BONERA_UL_PLR_Rename_Pairs(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        row.label(text="", icon="SORTALPHA")
        row.prop(item, "name_A", text="", emboss=True)

        operator = row.operator("bonera.plr_pair_list_operator", text="", icon="ARROW_LEFTRIGHT")
        operator.operation = "SWAP"
        operator.index = index


        row.prop(item, "name_B", text="", emboss=True)

        # row.label(text="", icon="OUTLINER_DATA_GP_LAYER")





classes = [BONERA_PT_Pair_List_Renamer, BONERA_OT_PLR_Rename_List, BONERA_PLR_Swap_Pair, BONERA_PLR_List_Loader, BONERA_PLR_Pair_List_Operator, BONERA_PLR_List_Operator, BONERA_UL_PLR_Renamers, BONERA_UL_PLR_Rename_Pairs]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.Scene.PLR_Renamer_Switcher = bpy.props.EnumProperty(items=ENUM_PLR_Renamer_Switcher, update=UPDATE_PLR_Renamer)
    # bpy.types.Scene.PLR_Renamers = bpy.props.CollectionProperty(type=BONERA_PLR_Renamers)
    # bpy.types.Scene.PLR_Renamers_Editindex= bpy.props.IntProperty(update=UPDATE_PLR_Renamer_Switcher)
    # bpy.types.Scene.PLR_Renamers_index= bpy.props.IntProperty(update=UPDATE_PLR_Renamer_Switcher)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    # del bpy.types.Scene.PLR_Renamers
    # del bpy.types.Scene.PLR_Renamers_index

if __name__ == "__main__":
    register()
