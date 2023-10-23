import bpy
# from .. import Utility
from .. import Utility_Functions

class BONERA_PBL_Layer(bpy.types.PropertyGroup):
    bone : bpy.props.StringProperty()
    reserved : bpy.props.BoolProperty()
    use_name: bpy.props.BoolProperty()

class BONERA_Pseudo_Bone_Layer(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty()
    bones : bpy.props.CollectionProperty(type=BONERA_PBL_Layer)
    bone_index: bpy.props.IntProperty()

#In Front
#Toogle Based on Select and Hide
#Remove From Layer
#Delete Bone
#Solo Button


#Hide Unhide Deform

#Operator
#Create Layer base on Name (Include, Exclude)
#Create Layer from Vanila Bone Layer
#Rename Bone Button

#Lock Rot Lot Scale
def Generate_Bone_Name(self, context, basename):

    if self.prefix == "NONE":
        Prefix = ""
    else:
        Prefix = self.prefix

    if self.suffix == "NONE":
        Suffix = ""
    else:
        Suffix = self.suffix

    name = Prefix + basename + Suffix

    return name

def ENUM_Prefix(self, context):
    preferences = Utility_Functions.get_addon_preferences()
    items = preferences.Prefix_List
    ENUM_Items = []
    ENUM_Items.append(("NONE", "None", "None"))
    for item in items:
        ENUM_Items.append((item.name, item.name, item.name))
    return ENUM_Items

def ENUM_Suffix(self, context):
    preferences = Utility_Functions.get_addon_preferences()
    items = preferences.Suffix_List
    ENUM_Items = []
    ENUM_Items.append(("NONE", "None", "None"))
    for item in items:
        ENUM_Items.append((item.name, item.name, item.name))
    return ENUM_Items


class BONERA_UL_Bone_Pseudo_Bone_Layer(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        # layout.prop(preferences, "ICON_PBL_Visibility", text="Visibility")

        preferences = Utility_Functions.get_addon_preferences()



        row = layout.row(align=True)


        if context.mode == "POSE":
            if preferences.ICON_PBL_Key_Bone:
                row.operator("bonera_pbl.key_bone", text="", icon="KEYTYPE_KEYFRAME_VEC")


        if preferences.ICON_PBL_Mute_Constraint:
            operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="CONSTRAINT")
            operator.index = index
            operator.operation = "MUTE"


        if preferences.ICON_PBL_Solo:

            operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="SOLO_ON")
            operator.index = index
            operator.operation = "SOLO"



        if preferences.ICON_PBL_Visibility:

            operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="HIDE_OFF")
            operator.state = False
            operator.index = index
            operator.operation = "HIDE"

        if preferences.ICON_PBL_Select:
            operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="RESTRICT_SELECT_OFF")
            operator.state = False
            operator.index = index
            operator.operation = "SELECT"

        if preferences.ICON_PBL_Deform:
            operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="OUTLINER_OB_ARMATURE")
            operator.index = index
            operator.operation = "DEFORM"



        row.prop(item, "name", text="", emboss=False)

        if preferences.ICON_PBL_Remove:

            operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="X")
            operator.index = index
            operator.operation = "REMOVE"

class BONERA_UL_PBL_Layer(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout = layout.row(align=True)
        obj = context.object
        bone = None

        if context.mode == "EDIT_ARMATURE":

            bone = obj.data.edit_bones.get(item.bone)

        if context.mode == "POSE":
            bone = obj.pose.bones.get(item.bone)
            if bone:
                bone = bone.bone

        if context.mode == "OBJECT":
            bone = obj.data.bones.get(item.bone)

        if bone:
            layout.prop(bone, "hide", icon="HIDE_OFF", text="")
            # layout.prop(bone, "select", icon="RESTRICT_SELECT_OFF", text="")
            if bone.select:
                layout.operator("bonera_pbl.select_slot_bone", icon="RESTRICT_SELECT_OFF", text="").index = index
            else:
                layout.operator("bonera_pbl.select_slot_bone", icon="RESTRICT_SELECT_ON", text="").index = index


            layout.label(text=item.bone)
            layout.prop(bone, "use_deform", text="Deform")
        else:
            if item.reserved:
                layout.label(text="Reserved", icon="INFO")
                row = layout.row(align=True)

                row.prop(item, "use_name", text="", icon="SETTINGS")

                if item.use_name:

                    row.prop(item, "bone", text="")

                else:
                    row.prop_search(item, "bone", obj.data, "bones", text="")

            else:
                layout.label(text="Missing", icon="ERROR")
                layout.prop_search(item, "bone", obj.data, "bones", text="")

        layout.prop(item, "reserved", text="", icon="FAKE_USER_ON")
        layout.operator("bonera_pbl.edit_bone_name", text="", icon="SORTALPHA").index = index
        layout.operator("bonera_pbl.remove_bone_from_layer", text="", icon="X").index = index



ENUM_list_choice = [("PREFIX","Prefix","Prefix"),("SUFFIX","Suffix","Suffix")]
ENUM_list_operation = [("ADD","Add","Add"),("REMOVE","Remove","Remove"), ("ASSIGN", "Assign", "Assign"), ("UNASSIGN","Unassign","Unassign"), ("HIDE","Hide","Hide"), ("SELECT","Select","Select"), ("DEFORM","Deform","Deform"), ("UP", "Up", "Up"), ("DOWN", "Down", "Down"), ("MUTE", "Mute / Unmute", "Mute"), ("SOLO", "Solo", "Solo")]

class BONERA_PBL_List_Operator(bpy.types.Operator):
    """List Operator"""
    bl_idname = "bonera.pseudo_bone_layer_list_operator"
    bl_label = "List Operator"
    bl_options = {'UNDO', 'REGISTER'}

    operation: bpy.props.EnumProperty(items=ENUM_list_operation)
    name: bpy.props.StringProperty(default="Layer")
    index: bpy.props.IntProperty()

    state: bpy.props.BoolProperty()
    assign_Selected: bpy.props.BoolProperty(default=True)

    def draw(self, context):

        layout = self.layout

        if self.operation == "ADD":
            layout.prop(self, "name", text="Name")
            layout.prop(self, "assign_Selected", text="Assign Selected")

        if self.operation == "DEFORM":
            layout.prop(self, "state", text="Use Deform")

        if self.operation == "MUTE":
            layout.prop(self, "state", text="Mute")


    def invoke(self, context, event):


        obj = context.object

        self.name = "Layer_" + str(len(obj.data.Pseudo_Bone_Layer))

        if self.operation in ["ADD", "DEFORM", "MUTE"]:
            return context.window_manager.invoke_props_dialog(self)
        elif self.operation in ["SOLO"]:
            if event.shift:
                self.state = True
            else:
                self.state = False

            return self.execute(context)
        else:
            return self.execute(context)

    def execute(self, context):

        obj = context.object

        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index




        if self.operation == "REMOVE":
            item_list.remove(self.index)

            if len(item_list) == obj.data.Pseudo_Bone_Layer_Index:
                obj.data.Pseudo_Bone_Layer_Index = len(item_list) - 1
            Utility_Functions.update_UI()
            return {'FINISHED'}

        if self.operation == "ADD":

            item = item_list.add()
            item.name = self.name

            if self.assign_Selected:
                if len(item_list) > 0:

                    active_item = item

                    if context.mode == "EDIT_ARMATURE":
                        bones = context.selected_bones
                    if context.mode == "POSE":
                        bones = context.selected_pose_bones

                    names = [bone.bone for bone in active_item.bones]

                    if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
                        if bones:
                            for bone in bones:
                                if not bone.name in names:
                                    bone_list_item = item.bones.add()
                                    bone_list_item.bone = bone.name

            obj.data.Pseudo_Bone_Layer_Index = len(item_list) - 1
            Utility_Functions.update_UI()
            return {'FINISHED'}


        if self.operation == "ASSIGN":
            if len(item_list) == 0:

                item = item_list.add()
                item.name = self.name

                active_item = item
            else:
                if self.index < len(item_list):
                    active_item = item_list[self.index]
                else:
                    return {'FINISHED'}

            if context.mode == "EDIT_ARMATURE":
                bones = context.selected_bones
            if context.mode == "POSE":
                bones = context.selected_pose_bones

            names = [bone.bone for bone in active_item.bones]

            if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
                if bones:
                    for bone in bones:
                        if not bone.name in names:

                            bone_list_item = active_item.bones.add()
                            bone_list_item.bone = bone.name



        if len(item_list) > 0:
            active_item = obj.data.Pseudo_Bone_Layer[self.index]
            if context.mode == "EDIT_ARMATURE":
                bones = context.selected_bones
            if context.mode == "POSE":
                bones = context.selected_pose_bones

            # if self.operation == "ASSIGN":
            #
            #     names = [bone.bone for bone in active_item.bones]
            #     if context.mode == "EDIT_ARMATURE" or context.mode == "POSE":
            #         if bones:
            #             for bone in bones:
            #                 if not bone.name in names:
            #
            #
            #                     bone_list_item = active_item.bones.add()
            #                     bone_list_item.bone = bone.name

            if self.operation == "UNASSIGN":

                for count in active_item.bones:
                    for index, layer_bone in enumerate(active_item.bones):
                        for bone in bones:
                            if layer_bone.bone == bone.name:
                                active_item.bones.remove(index)
                                break
                        # break

            if self.operation == "HIDE":

                if context.mode == "EDIT_ARMATURE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.edit_bones
                    bone_state = not any([bone.hide for bone in bones if bone.name in bones_name])

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            bone.hide = bone_state

                if context.mode == "POSE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.pose.bones
                    bone_state = not any([bone.bone.hide for bone in bones if bone.name in bones_name])

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            bone = bone.bone
                            bone.hide = bone_state

                if context.mode == "OBJECT":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.bones
                    bone_state = not any([bone.hide for bone in bones if bone.name in bones_name])

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            bone.hide = bone_state




            if self.operation == "SOLO":

                if context.mode == "EDIT_ARMATURE":
                    bones_name = [bone.bone for bone in active_item.bones]
                    bones = obj.data.edit_bones

                    if self.state:
                        for bone in bones:
                            bone.hide = False

                    else:

                        for bone in bones:
                            bone.hide = True


                        for bone_name in bones_name:
                            bone = bones.get(bone_name)
                            if bone:
                                bone.hide = False

                if context.mode == "POSE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.pose.bones

                    if self.state:
                        for bone in bones:
                            bone.bone.hide = False

                    else:

                        for bone in bones:
                            bone.bone.hide = True


                        for bone_name in bones_name:
                            bone = bones.get(bone_name)
                            if bone:
                                bone = bone.bone
                                bone.hide = False

                if context.mode == "OBJECT":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.bones


                    if self.state:
                        for bone in bones:
                            bone.hide = False

                    else:


                        for bone in bones:
                            bone.hide = True



                        for bone_name in bones_name:
                            bone = bones.get(bone_name)
                            if bone:
                                bone.hide = False















            if self.operation == "MUTE":


                if context.mode == "EDIT_ARMATURE":

                    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
                    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.pose.bones

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            for constraint in bone.constraints:
                                constraint.mute = self.state

                if context.mode == "POSE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.pose.bones

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            for constraint in bone.constraints:
                                constraint.mute = self.state

                if context.mode == "OBJECT":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.pose.bones

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            for constraint in bone.constraints:
                                constraint.mute = self.state


            if self.operation == "DEFORM":

                if context.mode == "EDIT_ARMATURE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.edit_bones

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            bone.use_deform = self.state

                if context.mode == "POSE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.bones

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            bone.use_deform = self.state


                if context.mode == "OBJECT":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.bones

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            bone.use_deform = self.state



            if self.operation == "SELECT":

                if context.mode == "EDIT_ARMATURE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.edit_bones
                    bone_state = not any([any([bone.select, bone.select_head, bone.select_tail]) for bone in bones if bone.name in bones_name])

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)

                        if bone:
                            bone = bone
                            bone.select = bone_state
                            bone.select_head = bone_state
                            bone.select_tail = bone_state


                if context.mode == "POSE":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.pose.bones
                    bone_state = not any([any([bone.bone.select, bone.bone.select_head, bone.bone.select_tail]) for bone in bones if bone.name in bones_name])

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)

                        if bone:
                            bone = bone.bone

                            bone.select = bone_state
                            bone.select_head = bone_state
                            bone.select_tail = bone_state

                if context.mode == "OBJECT":
                    bones_name = [bone.bone for bone in active_item.bones]

                    bones = obj.data.bones
                    bone_state = not any([any([bone.select, bone.select_head, bone.select_tail]) for bone in bones if bone.name in bones_name])

                    for bone_name in bones_name:
                        bone = bones.get(bone_name)
                        if bone:
                            bone.select = bone_state
                            bone.select_head = bone_state
                            bone.select_tail = bone_state

            if self.operation == "UP":
                if item_index >= 1:
                    item_list.move(item_index, item_index-1)
                    obj.data.Pseudo_Bone_Layer_Index -= 1
                    return {'FINISHED'}

            if self.operation == "DOWN":
                if len(item_list)-1 > item_index:
                    item_list.move(item_index, item_index+1)
                    obj.data.Pseudo_Bone_Layer_Index += 1
                    return {'FINISHED'}

                # if bones:
                #     for bone in bones:
                #         if bone.name in names:
                #             active_item.bones.remove()



        Utility_Functions.update_UI()
        return {'FINISHED'}












class BONERA_PBL_OT_Clear_Missing_Bone(bpy.types.Operator):
    """Clear Missing Bone"""
    bl_idname = "bonera_pbl.clear_missing_bone"
    bl_label = "Clear Missing Bone"

    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):

        obj = context.object

        bones = obj.data.bones

        if context.mode == "EDIT_ARMATURE":

            bones = obj.data.edit_bones

        if context.mode == "POSE":

            bones = obj.data.bones


        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index

        if len(item_list) > 0:
            active_layer = item_list[item_index]

            for loop in active_layer.bones:

                for index, bone in enumerate(active_layer.bones):



                    if not bones.get(bone.bone):

                        if not bone.reserved:

                            active_layer.bones.remove(index)
                            break



        return {'FINISHED'}












class BONERA_PBL_OT_Unassign_Bone_From_Layer(bpy.types.Operator):
    """Unassign Bone From Layer"""
    bl_idname = "bonera_pbl.remove_bone_from_layer"
    bl_label = "Remove Bone From Layer"
    bl_options = {'UNDO', 'REGISTER'}

    index : bpy.props.IntProperty()

    def execute(self, context):

        obj = context.object

        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index

        if len(item_list) > 0:
            active_layer = item_list[item_index]

            active_layer.bones.remove(self.index)




        pass
        #Get Layer

        # object = context.object
        # Pose_Bone = object.pose.bones
        #
        # for bone in Pose_Bone:
        #     for constraint in bone.constraints:
        #         constraint.mute = self.mute
        #


        return {'FINISHED'}






class BONERA_PBL_OT_Edit_Bone_Name(bpy.types.Operator):
    """Edit Bone Name"""
    bl_idname = "bonera_pbl.edit_bone_name"
    bl_label = "Edit Bone Name"
    bl_options = {'UNDO', 'REGISTER'}

    name: bpy.props.StringProperty()

    edit_slot_name: bpy.props.BoolProperty(default=True)
    edit_bone_name: bpy.props.BoolProperty(default=True)

    index: bpy.props.IntProperty()

    use_addon: bpy.props.BoolProperty(default=False)

    prefix: bpy.props.EnumProperty(items=ENUM_Prefix)
    suffix: bpy.props.EnumProperty(items=ENUM_Suffix)


#Add Prefix and Suffix
    def draw(self, context):

        layout = self.layout

        if self.use_addon:
            col = layout.column(align=True)
            row = col.row(align=True)
            row.scale_x = 2
            row.prop(self, "prefix", text="")
            row.scale_x = 6
            row.prop(self, "name", text="")
            row.scale_x = 2
            row.prop(self, "suffix", text="")

        else:
            layout.prop(self, "name", text="")

        layout.prop(self, "use_addon", text="Prefix / Suffix")
        layout.prop(self, "edit_slot_name", text="Slot Name")
        layout.prop(self, "edit_bone_name", text="Bone Name")

    def invoke(self, context, event):

        obj = context.object
        bones = obj.data.bones

        if context.mode == "EDIT_ARMATURE":

            bones = obj.data.edit_bones

        if context.mode == "POSE":

            bones = obj.data.bones


        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index

        if len(item_list) > 0:

            active_layer = item_list[item_index]

            if len(active_layer.bones) > 0:
                slot = active_layer.bones[self.index].bone
                self.name = slot

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        obj = context.object
        bones = obj.data.bones

        if self.use_addon:
            name = Generate_Bone_Name(self, context, self.name)
        else:
            name = self.name

        if context.mode == "EDIT_ARMATURE":

            bones = obj.data.edit_bones

        if context.mode == "POSE":

            bones = obj.data.bones


        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index

        if len(item_list) > 0:
            active_layer = item_list[item_index]

            if len(active_layer.bones) > 0:
                slot = active_layer.bones[self.index]



                if self.edit_bone_name:
                    bone = bones.get(slot.bone)
                    if bone:
                        bone.name = name

                if self.edit_slot_name:
                    slot.bone = name



        return {'FINISHED'}




ENUM_rename_mode = [("PREFIX","Prefix","Prefix"),("SUFFIX","Suffix","Suffix"),("FIND","Replace","Replace"),("REMOVE","Remove","Remove")]

class BONERA_PBL_OT_Batch_Rename_Layer(bpy.types.Operator):
    """Batch Rename Layer"""
    bl_idname = "bonera_pbl.batch_rename_layer"
    bl_label = "Batch Rename"
    bl_options = {'UNDO', 'REGISTER'}

    index: bpy.props.IntProperty()

    rename_mode: bpy.props.EnumProperty(items=ENUM_rename_mode)

    input_string01: bpy.props.StringProperty()
    input_string02: bpy.props.StringProperty()

    edit_bone_name: bpy.props.BoolProperty(default=True)
    edit_slot_name: bpy.props.BoolProperty(default=True)

    def draw(self, context):

        layout = self.layout
        layout.prop(self, "rename_mode", text="Mode")


        Mode_Name = self.rename_mode.capitalize()

        layout.prop(self, "input_string01", text=Mode_Name)


        if self.rename_mode == "FIND":
            layout.prop(self, "input_string02", text="Replace")

        layout.prop(self, "edit_slot_name", text="Slot Name")
        layout.prop(self, "edit_bone_name", text="Bone Name")


    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):


        obj = context.object
        bones = obj.data.bones




        if context.mode == "EDIT_ARMATURE":

            bones = obj.data.edit_bones

        if context.mode == "POSE":

            bones = obj.data.bones


        item_list = obj.data.Pseudo_Bone_Layer
        item_index = self.index

        if len(item_list) > 0:
            active_layer = item_list[item_index]

            if len(active_layer.bones) > 0:

                for slot in active_layer.bones:


                        if self.rename_mode == "PREFIX":

                            Final_Name = self.input_string01 + slot.bone

                        if self.rename_mode == "SUFFIX":

                            Final_Name =  slot.bone + self.input_string01

                        if self.rename_mode == "REMOVE":

                            Final_Name =  slot.bone.replace(self.input_string01, "")

                        if self.rename_mode == "FIND":

                            Final_Name =  slot.bone.replace(self.input_string01, self.input_string02)


                        if Final_Name:



                            bone = bones.get(slot.bone)

                            if self.edit_slot_name:
                                slot.bone = Final_Name

                            if self.edit_bone_name:
                                if bone:
                                    bone.name = Final_Name



        return {'FINISHED'}



class BONERA_PBL_OT_Select_Slot_Bone(bpy.types.Operator):
    """Select Bone"""
    bl_idname = "bonera_pbl.select_slot_bone"
    bl_label = "Select Slot Bone"
    bl_options = {'UNDO', 'REGISTER'}

    index: bpy.props.IntProperty()

    def execute(self, context):

        obj = context.object
        bones = obj.data.bones


        if context.mode == "EDIT_ARMATURE":

            bones = obj.data.edit_bones

        if context.mode == "POSE":

            bones = obj.data.bones


        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index

        if len(item_list) > 0:
            active_layer = item_list[item_index]

            if len(active_layer.bones) > 0:
                slot = active_layer.bones[self.index]

                bone = bones.get(slot.bone)

                if bone:

                    bone.select = not bone.select
                    bone.select_head = bone.select
                    bone.select_tail = bone.select

                    if bone.select:
                        bones.active = bone

        return {'FINISHED'}













class BONERA_PBL_OT_Add_Bone_Name_Slot(bpy.types.Operator):
    """Add Bone Name Slot"""
    bl_idname = "bonera_pbl.add_bone_name_slot"
    bl_label = "Add By Name"
    bl_options = {'UNDO', 'REGISTER'}

    name: bpy.props.StringProperty(default="Bone")
    prefix: bpy.props.EnumProperty(items=ENUM_Prefix)
    suffix: bpy.props.EnumProperty(items=ENUM_Suffix)

    def draw(self, context):

        layout = self.layout


        col = layout.column(align=True)
        row = col.row(align=True)
        row.scale_x = 2
        row.prop(self, "prefix", text="")
        row.scale_x = 6
        row.prop(self, "name", text="")
        row.scale_x = 2
        row.prop(self, "suffix", text="")



    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        obj = context.object

        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index

        name = Generate_Bone_Name(self, context, self.name)
        # name = self.prefix + self.name + self.suffix


        if len(item_list) > 0:
            active_layer = item_list[item_index]

            item = active_layer.bones.add()
            item.bone = name
            item.reserved = True



        Utility_Functions.update_UI()
        return {'FINISHED'}







class BONERA_PBL_OT_Key_Bone(bpy.types.Operator):
    """Keyframe Bone in this layer"""
    bl_idname = "bonera_pbl.key_bone"
    bl_label = "Key Bone"
    bl_options = {'UNDO', 'REGISTER'}

    Location: bpy.props.BoolProperty(default=True)
    Rotation: bpy.props.BoolProperty(default=True)
    Scale: bpy.props.BoolProperty(default=True)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        obj = context.object

        item_list = obj.data.Pseudo_Bone_Layer
        item_index = obj.data.Pseudo_Bone_Layer_Index


        bones = obj.pose.bones

        if len(item_list) > 0:
            active_layer = item_list[item_index]

            items = active_layer.bones

            for item in items:
                bone = bones.get(item.bone)

                if bone:
                    if self.Location:
                        bone.keyframe_insert("location")

                    if self.Rotation:
                        path = "rotation_euler"
                        if bone.rotation_mode == "QUATERNION":
                            path = "rotation_quaternion"
                        if bone.rotation_mode == "AXIS_ANGLE":
                            path = "rotation_axis_angle"


                        bone.keyframe_insert(path)
                    if self.Scale:
                        bone.keyframe_insert("scale")



        Utility_Functions.update_UI()
        return {'FINISHED'}


def PBL_Draw_Icon(self, context, layout):

    preferences = Utility_Functions.get_addon_preferences()

    row = layout.row(align=True)
    row.alignment = "LEFT"

    if preferences.show_PBL_Bone_Layer_Icon:
        row.prop(preferences, "show_PBL_Bone_Layer_Icon", text="Icon Expose", emboss=False, icon="TRIA_DOWN")
        layout.prop(preferences, "ICON_PBL_Visibility", text="Visibility")
        layout.prop(preferences, "ICON_PBL_Select", text="Select")
        layout.prop(preferences, "ICON_PBL_Deform", text="Deform")
        layout.prop(preferences, "ICON_PBL_Remove", text="Remove")
        layout.prop(preferences, "ICON_PBL_Key_Bone", text="Keyframe")
        layout.prop(preferences, "ICON_PBL_Mute_Constraint", text="Mute / Unmute")

    else:
        row.prop(preferences, "show_PBL_Bone_Layer_Icon", text="Icon Expose", emboss=False, icon="TRIA_RIGHT")

class BONERA_PT_Pseudo_Layer_Panel(bpy.types.Panel):

    bl_label = "Pseudo Bone Layer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bonera"
    bl_options =  {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):

        preferences = Utility_Functions.get_addon_preferences()

        if preferences.SECTION_Bonera_Pseudo_Layers:

            return True

    def draw(self, context):

        obj = context.object
        layout = self.layout

        if obj:
            if obj.type in ["ARMATURE"]:



                if obj:
                    index = obj.data.Pseudo_Bone_Layer_Index

                    preferences = Utility_Functions.get_addon_preferences()

                    row = layout.row(align=False)
                    row.template_list("BONERA_UL_Bone_Pseudo_Bone_Layer", "", obj.data, "Pseudo_Bone_Layer", obj.data, "Pseudo_Bone_Layer_Index")

                    col = row.column(align=True)
                    Operator = col.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="ADD")
                    Operator.operation = "ADD"
                    Operator.index = index
                    Operator.assign_Selected = False

                    Operator = col.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="REMOVE")
                    Operator.operation = "REMOVE"
                    Operator.index = index

                    col.separator()
                    col.menu("BONERA_MT_pbl_icon_expose", text="", icon="VIS_SEL_11")
                    col.separator()

                    Operator = col.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="TRIA_UP")
                    Operator.operation = "UP"
                    Operator.index = index

                    Operator = col.operator("bonera.pseudo_bone_layer_list_operator", text="", icon="TRIA_DOWN")
                    Operator.operation = "DOWN"
                    Operator.index = index

                    row = layout.row(align=True)

                    if context.mode in ["EDIT_ARMATURE", "POSE"]:

                        Operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="New From Selected", icon="PLUS")
                        Operator.operation = "ADD"
                        Operator.index = index
                        Operator.assign_Selected = True

                        row = layout.row(align=True)

                        Operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="Assign", icon="ADD")
                        Operator.operation = "ASSIGN"
                        Operator.index = index

                        Operator = row.operator("bonera.pseudo_bone_layer_list_operator", text="Unassign", icon="REMOVE")
                        Operator.operation = "UNASSIGN"
                        Operator.index = index

                    if len(obj.data.Pseudo_Bone_Layer) > 0:


                        box = layout.box()

                        if preferences.show_bone_list:
                            row = box.row(align=True)
                            row.alignment = "LEFT"
                            row.prop(preferences, "show_bone_list", text="Show Bone List", emboss=False, icon="TRIA_DOWN")

                            if len(obj.data.Pseudo_Bone_Layer) > obj.data.Pseudo_Bone_Layer_Index:

                                active_layer = obj.data.Pseudo_Bone_Layer[obj.data.Pseudo_Bone_Layer_Index]
                                box.template_list("BONERA_UL_PBL_Layer", "", active_layer, "bones", active_layer, "bone_index")

                                box.operator("bonera_pbl.add_bone_name_slot", text="Add By Name")

                                row = box.row(align=True)
                                row.operator("bonera_pbl.clear_missing_bone", text="Clear Missing Bone")
                                row.operator("bonera_pbl.batch_rename_layer", icon="SORTALPHA").index = index

                        else:
                            row = box.row(align=True)
                            row.alignment = "LEFT"
                            row.prop(preferences, "show_bone_list", text="Show Bone List", emboss=False, icon="TRIA_RIGHT")

                # PBL_Draw_Icon(self, context, layout)
            else:
                layout.label(text="Select a Armature", icon="INFO")
        else:
            layout.label(text="Select a Armature", icon="INFO")




classes=[BONERA_PT_Pseudo_Layer_Panel, BONERA_PBL_OT_Key_Bone, BONERA_PBL_OT_Add_Bone_Name_Slot, BONERA_PBL_OT_Batch_Rename_Layer, BONERA_PBL_OT_Select_Slot_Bone, BONERA_PBL_OT_Edit_Bone_Name, BONERA_PBL_OT_Clear_Missing_Bone, BONERA_PBL_Layer, BONERA_UL_Bone_Pseudo_Bone_Layer, BONERA_PBL_List_Operator, BONERA_Pseudo_Bone_Layer, BONERA_UL_PBL_Layer, BONERA_PBL_OT_Unassign_Bone_From_Layer]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.Object.Pseudo_Bone_Layer = bpy.props.CollectionProperty(type=BONAD_Pseudo_Bone_Layer)
    # bpy.types.Object.Pseudo_Bone_Layer_Index = bpy.props.IntProperty()

    bpy.types.Armature.Pseudo_Bone_Layer = bpy.props.CollectionProperty(type=BONERA_Pseudo_Bone_Layer)
    bpy.types.Armature.Pseudo_Bone_Layer_Index = bpy.props.IntProperty()


def unregister():

    # del bpy.types.Object.Pseudo_Bone_Layer
    # del bpy.types.Object.Pseudo_Bone_Layer_Index

    del bpy.types.Armature.Pseudo_Bone_Layer
    del bpy.types.Armature.Pseudo_Bone_Layer_Index

    # del bpy.types.Scene.Bone_Suffix_List
    # del bpy.types.Scene.Pseudo_Bone_Layer_Index

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
