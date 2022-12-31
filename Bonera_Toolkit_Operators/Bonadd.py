import bpy
from Bonera_Toolkit import Utility_Functions
import mathutils

OPERATOR_POLL_CONTEXT = ["EDIT_MESH","EDIT_CURVE"]
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



def ENUM_Target_Armature_Mode(self, context):

    ENUM_Items = []

    if context.mode in ["EDIT_ARMATURE", "POSE"]:

        ENUM_Items.append(("ACTIVE_ARMATURE","Active Armature","Active Armature"))

    ENUM_Items.append(("CHOOSE_ARMATURE","Choose Armature","Choose Armature"))

    return ENUM_Items

# ENUM_Mode = [("INDIVIDUAL","Individual","Individual"),("MEDIAN","Median","Median")]

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

class BONERA_OP_Bonadd(bpy.types.Operator):
    """Experimental Operator that create bone using 3D Cursor and Selected Elements
    Object | Edit Mesh | Edit Curve | Edit Armature | Pose"""
    bl_idname = "bonera.bonadd"
    bl_label = "Bonadd"
    bl_options = {'UNDO', 'REGISTER'}

    Base_Name: bpy.props.StringProperty(default="Bone")

    Prefix: bpy.props.EnumProperty(items=ENUM_Prefix)
    Suffix: bpy.props.EnumProperty(items=ENUM_Suffix)

    # Mode: bpy.props.EnumProperty(items=ENUM_Mode)

    Use_Deform: bpy.props.BoolProperty(default=True)


    SHOW_Weight_Option: bpy.props.BoolProperty(default=False)

    BIND_Add_Armature_Modifier: bpy.props.BoolProperty(default=True)
    BIND_Parent_Non_Mesh: bpy.props.BoolProperty(default=True)
    BIND_Parent_To_Armature: bpy.props.BoolProperty(default=True)
    # BIND_Clear_Vertex_Group: bpy.props.BoolProperty(default=False)

    SHOW_Tail: bpy.props.BoolProperty(default=False)



    Hook: bpy.props.BoolProperty(default=True)

    SHOW_Armature: bpy.props.BoolProperty(default=False)

    New_Armature_Name: bpy.props.StringProperty(default="Armature")
    Choice_Armature: bpy.props.EnumProperty(default="NEW", items=ENUM_Choice_Armature)

    ARMATURE_Parent_Bone: bpy.props.BoolProperty(default=True)

    Armature_Update: bpy.props.BoolProperty(default=True)

    ELEM_Mesh: bpy.props.EnumProperty(default="VERTEX", items=ENUM_ELEM_Mesh)
    ELEM_Armature: bpy.props.EnumProperty(default="HEAD", items=ENUM_ELEM_Armature)
    ELEM_Handle: bpy.props.BoolProperty(default=False)

    To_Active_Armature: bpy.props.BoolProperty(default=True)
    Use_Self_Armature: bpy.props.BoolProperty(default=True)

    Target_Armature_Mode: bpy.props.EnumProperty(items=ENUM_Target_Armature_Mode)

    Use_Only_Orphan: bpy.props.BoolProperty(default=False)

    Move_3D_Cursor: bpy.props.BoolProperty(default=True)

    @classmethod
    def poll(cls, context):

        preferences = Utility_Functions.get_addon_preferences()

        if not preferences.DISABLE_Bonadd:
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

    def draw_armature(self, context, layout):

        scn = context.scene

        if context.mode in ["EDIT_ARMATURE", "POSE"]:
            col = layout.column(align=True)
            # col.prop(self, "To_Active_Armature", text="Use Active Armature")



            # if not self.To_Active_Armature:

            if Utility_Functions.draw_subpanel(self, self.SHOW_Armature, "SHOW_Armature", "Armature", col):

                col.prop(self, "Target_Armature_Mode", text="")

                # if self.Target_Armature_Mode == "SELF_ARMATURE":
                #     col.prop(self, "Parent_Bone", text="Parent Bone")

                col = layout.column(align=True)

                if self.Target_Armature_Mode == "CHOOSE_ARMATURE":
                    if self.Choice_Armature == "EXIST":
                        col.prop(scn.Bonera_Scene_Data, "Bone_From_Selection_Armature", text="")

                    if self.Choice_Armature == "NEW":
                        col.prop(self, "New_Armature_Name", text="")

                    row = col.row(align=True)
                    row.prop(self, "Choice_Armature", expand=True)

                    if self.Choice_Armature == "NEW":
                        col.prop(self, "Armature_Update", text="Update")


        else:
            col = layout.column(align=True)

            if Utility_Functions.draw_subpanel(self, self.SHOW_Armature, "SHOW_Armature", "Armature", col):

                if self.Choice_Armature == "EXIST":
                    col.prop(scn.Bonera_Scene_Data, "Bone_From_Selection_Armature", text="")

                if self.Choice_Armature == "NEW":
                    col.prop(self, "New_Armature_Name", text="")

                row = col.row(align=True)
                row.prop(self, "Choice_Armature", expand=True)

                if self.Choice_Armature == "NEW":
                    col.prop(self, "Armature_Update", text="Update")

    def draw(self, context):

        layout = self.layout

        col = layout.column(align=True)
        self.draw_name(context, col)
        col.prop(self, "Use_Deform", text="Use Deform")
        col.prop(self, "Move_3D_Cursor", text="Move 3D Cursor")
        col.separator()

        layout.separator()

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

    def Offset_From_Head_NORMAL(self, context, object, location, normal):

        return Utility_Functions.Normal_To_Offset(object, location, normal, self.Tail_Offset_Amount)

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

        mode = context.mode

        selected_objects = [object for object in context.selected_objects]
        active_object = context.object

        preferences = Utility_Functions.get_addon_preferences()

        if mode in ["EDIT_ARMATURE", "POSE"] and self.Target_Armature_Mode in ["ACTIVE_ARMATURE", "SELF_ARMATURE"]:

            if context.object.type == "ARMATURE":
                Armature_Object = context.object
            else:
                Armature_Object = self.Set_Up_Armature(context)

        else:
            Armature_Object = self.Set_Up_Armature(context)

        context.view_layer.update()

        if Armature_Object:



            mid_point = None

            Points = []

            if mode == "EDIT_MESH":
                for object in selected_objects:

                    Utility_Functions.object_switch_mode(object, "OBJECT")

                    if object.type == "MESH":
                        for vertex in object.data.vertices:
                            if vertex.select:
                                Points.append(object.matrix_world @ vertex.co)



            if mode == "EDIT_CURVE":
                for object in selected_objects:

                    Utility_Functions.object_switch_mode(object, "OBJECT")

                    if object.type == "CURVE":
                        for spline in object.data.splines:
                            for point in spline.points:
                                if point.select:
                                    Points.append(object.matrix_world @ point.co.xyz)

                            for bezier_point in spline.bezier_points:
                                if bezier_point.select_control_point:
                                    Points.append(object.matrix_world @ bezier_point.co.xyz)

            if len(Points) > 0:
                mid_point = Utility_Functions.midpoint(Points, "BOUNDING_BOX")

            if mid_point:

                Utility_Functions.object_switch_mode(Armature_Object, "EDIT")
                Edit_Bones = Armature_Object.data.edit_bones

                if preferences.Enable_Affixes:
                    bone_name = self.Generate_Bone_Name(context, self.Base_Name)
                else:
                    bone_name = self.Base_Name

                bone_head = Armature_Object.matrix_world.inverted() @ context.scene.cursor.location
                bone_tail = Armature_Object.matrix_world.inverted() @ mid_point

                if self.Move_3D_Cursor:
                    context.scene.cursor.location = mid_point

                New_Bone = Utility_Functions.create_bone(Armature_Object, bone_name, bone_head, bone_tail, self.Use_Deform, Flip_Bone = False)
                New_Bone_Name = New_Bone.name

                Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")


            Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")




        ############################################################



        if mode in ["EDIT_MESH", "EDIT_CURVE", "EDIT_ARMATURE"]:

            for object in selected_objects:
                if object.type in ["MESH", "CURVE", "ARMATURE"]:
                    Utility_Functions.object_switch_mode(object, "EDIT")

        if mode in ["POSE"]:

            for object in selected_objects:
                if object.type in ["ARMATURE"]:
                    Utility_Functions.object_switch_mode(object, "POSE")

        context.view_layer.objects.active = active_object



        return {'FINISHED'}








classes = [BONERA_OP_Bonadd]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
