import bpy
from Bonera_Toolkit import Utility_Functions
import mathutils

OPERATOR_POLL_CONTEXT = ["OBJECT", "EDIT_CURVE"]
bezier_point_type = ["BEZIER"]
point_type = ["POLY", "NURBS"]

#---------------------ENUM AREA---------------------

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

def ENUM_Tail_Mode(self, context):

    ENUM_Items = [("OFFSET_GLOBAL","Offset Tail from Head (Global)","Offset Tail from Head (Global)"),("OFFSET_LOCAL","Offset Tail from Head (Local)","Offset Tail from Head (Local)")]

    return ENUM_Items

def ENUM_Bind_Mode(self, context):

    if self.Mode == "MEDIAN":
        ENUM_Items = [("NONE","None","None"),("WEIGHT","Weight","Weight"),("PARENT_BONE","Parent Bone","Parent Bone")]

    if self.Mode == "INDIVIDUAL":
        ENUM_Items =  [("NONE","None","None"),("WEIGHT","Weight","Weight"),("PARENT_BONE","Parent Bone","Parent Bone")]

    return ENUM_Items

def ENUM_Target_Armature_Mode(self, context):

    ENUM_Items = []

    if context.mode in ["EDIT_ARMATURE", "POSE"]:

        if self.Mode == "INDIVIDUAL":
            ENUM_Items.append(("SELF_ARMATURE","Own Armature","Own Armature"))

        ENUM_Items.append(("ACTIVE_ARMATURE","Active Armature","Active Armature"))

    ENUM_Items.append(("CHOOSE_ARMATURE","Choose Armature","Choose Armature"))

    return ENUM_Items

ENUM_Mode = [("INDIVIDUAL","Individual","Individual"),("MEDIAN","Median","Median")]

ENUM_Position_Mode = [("ORIGIN","Origin","Origin"),("CENTER","Geometry","Geometry"),("BOUNDING_BOX","Bounding Box","Bounding Box")]

# ENUM_Bind_Mode = [("NONE","None","None"),("WEIGHT","Weight","Weight"),("PARENT_BONE","Parent Bone","Parent Bone")]

# ENUM_Tail_Mode = [("OFFSET_GLOBAL","Offset Tail from Head (Global)","Offset Tail from Head (Global)"),("OFFSET_LOCAL","Offset Tail from Head (Local)","Offset Tail from Head (Local)"),("CURSOR", "3D Cursor", "3D Cursor")]

ENUM_Choice_Armature = [("NEW","New","New"),("EXIST","Existing","Existing")]

ENUM_ELEM_Mesh = [("VERTEX","Vertices","Vertices"),("EDGES","Edges","Edges"),("FACE","Faces","Faces")]

ENUM_ELEM_Armature = [("CENTER","Center","Center"),("HEAD","Head","Head"),("TAIL","Tail","Tail")]

#---------------------ENUM AREA---------------------

def Create_Armature(name):

    armature = bpy.data.armatures.new(name)
    object = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(object)

    return object

class BONERA_OP_Create_Bone_Chain_From_Curve(bpy.types.Operator):
    """Create Bone Chain from Curve
    Curve Object Only
        Object: All Curve Points
        Edit Curve: Selected Curve points"""

    bl_idname = "bonera.create_bone_chain_from_curve"
    bl_label = "Create Bone Chain From Curve"
    bl_options = {'UNDO', 'REGISTER'}

    Base_Name: bpy.props.StringProperty(default="Bone")

    Prefix: bpy.props.EnumProperty(items=ENUM_Prefix)
    Suffix: bpy.props.EnumProperty(items=ENUM_Suffix)

    Mode: bpy.props.EnumProperty(items=ENUM_Mode)

    Position_Mode: bpy.props.EnumProperty(items=ENUM_Position_Mode)
    Use_Deform: bpy.props.BoolProperty(default=True)

    Bind_Mode: bpy.props.EnumProperty(items=ENUM_Bind_Mode, default=1)

    SHOW_Weight_Option: bpy.props.BoolProperty(default=False)

    BIND_Parent_To_Armature: bpy.props.BoolProperty(default=True)
    # BIND_Clear_Vertex_Group: bpy.props.BoolProperty(default=False)

    SHOW_Tail: bpy.props.BoolProperty(default=False)

    Tail_Mode: bpy.props.EnumProperty(items=ENUM_Tail_Mode)
    Tail_Offset_Amount: bpy.props.FloatVectorProperty(default=(0, 0, 0.5))
    Flip_Bone: bpy.props.BoolProperty(default=False)

    Hook: bpy.props.BoolProperty(default=True)

    SHOW_Armature: bpy.props.BoolProperty(default=False)

    New_Armature_Name: bpy.props.StringProperty(default="Armature")
    Choice_Armature: bpy.props.EnumProperty(default="NEW", items=ENUM_Choice_Armature)

    Armature_Update: bpy.props.BoolProperty(default=False)

    ELEM_Handle: bpy.props.BoolProperty(default=False)

    To_Active_Armature: bpy.props.BoolProperty(default=True)
    Use_Self_Armature: bpy.props.BoolProperty(default=True)

    Target_Armature_Mode: bpy.props.EnumProperty(items=ENUM_Target_Armature_Mode)
    Use_Connect : bpy.props.BoolProperty(default=True)

    armature_obj_pair = []
    hook_pairs = []

    @classmethod
    def poll(cls, context):
        if context.object:
            
            if context.object.type == "CURVE":
                if context.mode in OPERATOR_POLL_CONTEXT:
                    return True

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def draw_name(self, context, layout):

        preferences = Utility_Functions.get_addon_preferences()

        if preferences.Enable_Affixes:
            row = layout.row(align=True)
            row.scale_x = 2
            row.prop(self, "Prefix", text="")
            row.scale_x = 6
            row.prop(self, "Base_Name", text="")
            row.scale_x = 2
            row.prop(self, "Suffix", text="")
        else:
            layout.prop(self, "Base_Name", text="Bone Name")

    def draw_tail(self, context, layout):

        if Utility_Functions.draw_subpanel(self, self.SHOW_Tail, "SHOW_Tail", "Tail Option", layout):

            col = layout.column(align=True)
            col.prop(self, "Tail_Mode", text="")

            row = col.row(align=True)
            if not self.Tail_Mode == "CURSOR":
                row.prop(self, "Tail_Offset_Amount", text="")

    def draw_armature(self, context, layout):

        scn = context.scene

        col = layout.column(align=True)

        if Utility_Functions.draw_subpanel(self, self.SHOW_Armature, "SHOW_Armature", "Armature", col):

            if self.Choice_Armature == "EXIST":
                col.prop(scn.Bonera_Scene_Data, "Bone_From_Selection_Armature", text="")

            if self.Choice_Armature == "NEW":
                col.prop(self, "New_Armature_Name", text="")

            row = col.row(align=True)
            row.prop(self, "Choice_Armature", expand=True)

            # if self.Choice_Armature == "NEW":
            #     col.prop(self, "Armature_Update", text="Update")

    def draw(self, context):

        layout = self.layout

        self.draw_name(context, layout)

        layout.prop(self, "Use_Deform", text="Use Deform")
        layout.prop(self, "Use_Connect", text="Connect Bone")
        layout.prop(self, "ELEM_Handle", text="Bezier Handle")


        row = layout.row(align=True)
        row.prop(self, "Hook", text="Hook")
        row.prop(self, "BIND_Parent_To_Armature", text="Parent to Armature")

        self.draw_tail(context, layout)
        self.draw_armature(context, layout)

    def Armature_Check(self, context):

        scn = context.scene
        armature_object = None

        if self.Choice_Armature == "NEW":
            armature_object = Create_Armature(self.New_Armature_Name)
            armature_object.show_in_front = True
        else:
            armature_object = scn.Bonera_Scene_Data.Bone_From_Selection_Armature

        if not armature_object:
            armature_object = Create_Armature(self.New_Armature_Name)
            armature_object.show_in_front = True
        else:
            if context.view_layer.objects.get(armature_object.name):
                pass
            else:
                armature_object = Create_Armature(self.New_Armature_Name)
                armature_object.show_in_front = True

        context.view_layer.update()

        return armature_object

    def Update_Armature(self, context, armature_object):

        if armature_object:

            scn = context.scene

            if self.Armature_Update:
                scn.Bonera_Scene_Data.Bone_From_Selection_Armature = armature_object
                self.Choice_Armature = "EXIST"

    def Set_Up_Armature(self, context):

        Armature_Object = self.Armature_Check(context)
        self.Update_Armature(context, Armature_Object)

        return Armature_Object

    def Offset_From_Head(self, context, head_position):

        Offset_Amount = self.Tail_Offset_Amount

        return head_position + mathutils.Vector(Offset_Amount)

    def Generate_Bone_Name(self, context, basename):

        if self.Prefix == "NONE":
            Prefix = ""
        else:
            Prefix = self.Prefix

        if self.Suffix == "NONE":
            Suffix = ""
        else:
            Suffix = self.Suffix

        name = Prefix + basename + Suffix

        return name

    def execute(self, context):

        self.armature_obj_pair.clear()
        self.hook_pairs.clear()

        mode = context.mode

        Tail_Mode = self.Tail_Mode

        selected_objects = [object for object in context.selected_objects]
        active_object = context.object

        preferences = Utility_Functions.get_addon_preferences()

        Armature_Object = self.Set_Up_Armature(context)
        Utility_Functions.object_switch_mode(Armature_Object, "EDIT")
        context.view_layer.update()

        if Armature_Object:

            Create_Lists = []



            if mode in ["EDIT_CURVE", "OBJECT"]:

                for object in selected_objects:

                    Utility_Functions.object_switch_mode(object, "OBJECT")

                    if object.type == "CURVE":


                        if self.BIND_Parent_To_Armature:
                            mw = object.matrix_world.copy()
                            object.parent = Armature_Object
                            object.matrix_world = mw

                        counter = -1

                        for spline_count, spline in enumerate(object.data.splines):

                            indices = []

                            if spline.type in bezier_point_type:

                                bp_counter = -1

                                prev_bone = None

                                for count, bezier_point in enumerate(spline.bezier_points):

                                    bezier_point.handle_left_type = "FREE"
                                    bezier_point.handle_right_type = "FREE"


                                    counter += 1
                                    index_handle_left = counter
                                    counter += 1
                                    index_point = counter
                                    counter += 1
                                    index_handle_right = counter

                                    # if bezier_point.select_control_point:
                                    if (mode == "EDIT_CURVE" and bezier_point.select_control_point) or (mode == "OBJECT"):

                                        name = self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) + "_BEZIER_POINT_" + str(count)

                                        if preferences.Enable_Affixes:

                                            bone_name = self.Generate_Bone_Name(context, name)
                                        else:
                                            bone_name = name

                                        bone_head_local = bezier_point.co.xyz
                                        bone_head = Armature_Object.matrix_world.inverted() @ object.matrix_world @ bone_head_local
                                        bone_tail = Armature_Object.matrix_world.inverted() @ self.Offset_From_Head(context, bone_head_local)

                                        if Tail_Mode == "OFFSET_GLOBAL":
                                            bone_tail = Armature_Object.matrix_world.inverted() @ ((object.matrix_world @ bone_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                                        if Tail_Mode == "OFFSET_LOCAL":
                                            bone_tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ self.Offset_From_Head(context, bone_head_local)

                                        if len(spline.bezier_points) > count + 1:
                                            bone_tail_local = spline.bezier_points[count+1].co.xyz
                                            bone_tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ bone_tail_local

                                        New_Bone = Utility_Functions.create_bone(Armature_Object, bone_name, bone_head, bone_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                                        New_Bone_Name = New_Bone.name

                                        if prev_bone:
                                            New_Bone.parent = prev_bone


                                            if self.Use_Connect:
                                                if New_Bone.head == prev_bone.tail:
                                                    New_Bone.use_connect = True

                                        prev_bone = New_Bone

                                        if self.ELEM_Handle:


                                            handle_left_head_local = bezier_point.handle_left
                                            handle_left_head = Armature_Object.matrix_world.inverted() @ object.matrix_world @ handle_left_head_local
                                            hl_name = self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) +"_HANDLE_LEFT_" + str(count)

                                            if preferences.Enable_Affixes:

                                                handle_left_name = self.Generate_Bone_Name(context, hl_name)
                                            else:
                                                handle_left_name = name

                                            if Tail_Mode == "OFFSET_GLOBAL":
                                                handle_left_tail = Armature_Object.matrix_world.inverted() @ ((object.matrix_world @ handle_left_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                                            if Tail_Mode == "OFFSET_LOCAL":
                                                handle_left_tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ self.Offset_From_Head(context, handle_left_head_local)

                                            Handle_Left_Bone = Utility_Functions.create_bone(Armature_Object, handle_left_name, handle_left_head, handle_left_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                                            Handle_Left_Bone.parent = New_Bone



                                            handle_right_head_local = bezier_point.handle_right
                                            handle_right_head = Armature_Object.matrix_world.inverted() @ object.matrix_world @ handle_right_head_local
                                            hr_name = self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) +"_HANDLE_RIGHT_" + str(count)

                                            if preferences.Enable_Affixes:

                                                handle_right_name = self.Generate_Bone_Name(context, hr_name)
                                            else:
                                                handle_right_name = name

                                            if Tail_Mode == "OFFSET_GLOBAL":
                                                handle_right_tail = Armature_Object.matrix_world.inverted() @ ((object.matrix_world @ handle_right_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                                            if Tail_Mode == "OFFSET_LOCAL":
                                                handle_right_tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ self.Offset_From_Head(context, handle_right_head_local)

                                            Handle_Right_Bone = Utility_Functions.create_bone(Armature_Object, handle_right_name, handle_right_head, handle_right_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                                            Handle_Right_Bone.parent = New_Bone

                                        if self.ELEM_Handle:

                                            indices = [index_point]
                                            hook_pair = {"object": object, "indices": indices, "bone_name": New_Bone.name}
                                            self.hook_pairs.append(hook_pair)

                                            indices = [index_handle_left]
                                            hook_pair = {"object": object, "indices": indices, "bone_name": Handle_Left_Bone.name}
                                            self.hook_pairs.append(hook_pair)

                                            indices = [index_handle_right]
                                            hook_pair = {"object": object, "indices": indices, "bone_name": Handle_Right_Bone.name}
                                            self.hook_pairs.append(hook_pair)

                                        else:

                                            indices = [index_handle_left, index_point, index_handle_right]
                                            hook_pair = {"object": object, "indices": indices, "bone_name": New_Bone.name}
                                            self.hook_pairs.append(hook_pair)




                            if spline.type in point_type:

                                np_counter = -1

                                prev_nurb_bone = None

                                for count, point in enumerate(spline.points):

                                    counter += 1
                                    index_nurbs_point = counter

                                    if (mode == "EDIT_CURVE" and point.select) or (mode == "OBJECT"):

                                        np_counter += 1



                                        name = self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) +"_NURB_POINT_" + str(count)

                                        if preferences.Enable_Affixes:

                                            bone_name = self.Generate_Bone_Name(context, name)
                                        else:
                                            bone_name = name


                                        bone_head_local = point.co.xyz
                                        bone_head = Armature_Object.matrix_world.inverted() @ object.matrix_world @ bone_head_local
                                        bone_tail = Armature_Object.matrix_world.inverted() @ self.Offset_From_Head(context, bone_head_local)

                                        if Tail_Mode == "OFFSET_GLOBAL":
                                            bone_tail = Armature_Object.matrix_world.inverted() @ ((object.matrix_world @ bone_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                                        if Tail_Mode == "OFFSET_LOCAL":
                                            bone_tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ self.Offset_From_Head(context, bone_head_local)

                                        if len(spline.points) > count + 1:
                                            bone_tail_local = spline.points[count+1].co.xyz
                                            bone_tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ bone_tail_local

                                        New_Bone = Utility_Functions.create_bone(Armature_Object, bone_name, bone_head, bone_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                                        New_Bone_Name = New_Bone.name

                                        if prev_nurb_bone:
                                            New_Bone.parent = prev_nurb_bone


                                            if self.Use_Connect:
                                                if New_Bone.head == prev_nurb_bone.tail:
                                                    New_Bone.use_connect = True

                                        prev_nurb_bone = New_Bone


                                        indices = [index_nurbs_point]
                                        hook_pair = {"object": object, "indices": indices, "bone_name": New_Bone.name}
                                        self.hook_pairs.append(hook_pair)

                if self.Hook:

                    Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")
                    context.view_layer.update()

                    for hook_pair in self.hook_pairs:

                        object = hook_pair["object"]
                        indices = hook_pair["indices"]
                        bone_name = hook_pair["bone_name"]

                        Utility_Functions.Hook_Vertex_Bone(object, Armature_Object, indices, bone_name, name=bone_name)

                    self.hook_pairs.clear()
        ############################################################

        Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")

        if mode in ["EDIT_CURVE"]:

            for object in selected_objects:
                if object.type in ["MESH", "CURVE", "ARMATURE"]:
                    Utility_Functions.object_switch_mode(object, "EDIT")


        context.view_layer.objects.active = active_object

        self.armature_obj_pair.clear()

        return {'FINISHED'}

classes = [BONERA_OP_Create_Bone_Chain_From_Curve]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
