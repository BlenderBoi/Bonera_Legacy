import bpy
from .. import Utility_Functions
import mathutils

OPERATOR_POLL_CONTEXT = ["OBJECT","EDIT_MESH","EDIT_CURVE","EDIT_ARMATURE", "POSE", "EDIT_LATTICE"]
bezier_point_type = ["BEZIER"]
point_type = ["POLY", "NURBS"]


# Constraint Object


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

    if self.Mode == "INDIVIDUAL":
        ENUM_Items = [("OFFSET_GLOBAL","Offset Tail from Head (Global)","Offset Tail from Head (Global)"),("OFFSET_LOCAL","Offset Tail from Head (Local)","Offset Tail from Head (Local)")]

    if self.Mode == "MEDIAN":
        ENUM_Items = [("OFFSET_GLOBAL","Offset Tail from Head (Global)","Offset Tail from Head (Global)")]

    if context.mode == "EDIT_MESH" and self.Mode == "INDIVIDUAL":
        ENUM_Items.append(("NORMAL","Normal","Normal"))

    if context.mode in ["EDIT_ARMATURE", "POSE"] and self.Mode == "INDIVIDUAL":
        ENUM_Items.append(("ROLL","Roll","Roll"))

    if context.mode in ["EDIT_ARMATURE"] and self.Mode == "INDIVIDUAL":
        ENUM_Items.append(("BONE","Extend","Extend"))

    ENUM_Items.append(("CURSOR", "3D Cursor", "3D Cursor"))

    return ENUM_Items

def ENUM_Bind_Mode(self, context):

    if context.mode == "OBJECT":

        ENUM_Items = [("NONE","None","None"),("WEIGHT","Weight","Weight"),("PARENT_BONE","Parent Bone","Parent Bone")]

    else:

        if context.mode == "EDIT_MESH":
            ENUM_Items =  [("NONE","None","None"),("WEIGHT","Weight","Weight"), ("CONSTRAINT_BONE_TO_SELECTED", "Constraint Bone To Selected", "Constraint Bone To Selected")]
        else:
            ENUM_Items =  [("NONE","None","None"),("WEIGHT","Weight","Weight")]

    # if self.Mode == "MEDIAN":
    #     ENUM_Items = [("NONE","None","None"),("WEIGHT","Weight","Weight"),("PARENT_BONE","Parent Bone","Parent Bone")]
    #
    # if self.Mode == "INDIVIDUAL":
    #     ENUM_Items =  [("NONE","None","None"),("WEIGHT","Weight","Weight"),("PARENT_BONE","Parent Bone","Parent Bone")]



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

def Reset_Default(self, context):
    if self.Reset_To_Default:
        self.Reset_To_Default = False


    self.Base_Name = "Bone"
    self.Prefix="NONE"
    self.Suffix="NONE"

    self.Mode="INDIVIDUAL"

    self.Position_Mode = "ORIGIN"
    self.Use_Deform = True

    self.Bind_Mode = "WEIGHT"

    self.SHOW_Weight_Option=False

    self.BIND_Add_Armature_Modifier=True
    self.BIND_Parent_Non_Mesh=True
    self.BIND_Parent_To_Armature=True

    self.SHOW_Tail=False

    self.Tail_Mode = "OFFSET_GLOBAL"
    self.Tail_Offset_Amount=(0, 0, 0.5)
    self.Flip_Bone = False

    self.Hook = True

    self.SHOW_Armature = False

    self.New_Armature_Name = "Armature"
    self.Choice_Armature = "NEW"

    self.ARMATURE_Parent_Bone = True

    # self.Armature_Update = True

    if context.mode == "EDIT_MESH":
        self.ELEM_Mesh = "VERTEX"

    if context.mode in ["EDIT_MESH", "POSE"]:
        self.ELEM_Armature = "HEAD"

    self.ELEM_Handle = False

    self.To_Active_Armature = True
    self.Use_Self_Armature = True

    if context.mode in ["EDIT_ARMATURE", "POSE"]:
        self.Target_Armature_Mode = "SELF_ARMATURE"
    else:
        self.Target_Armature_Mode = "CHOOSE_ARMATURE"

    self.Use_Only_Orphan = False
    self.Use_Hierarchy = True

    self.Parent_Bone = False





ENUM_Constraint_Type = [("COPY_LOCATION","Copy Location","Copy Location"), ("COPY_TRANSFORMS","Copy Transforms","Copy Transforms")]







class BONERA_OP_Create_Bones_From_Selected(bpy.types.Operator):
    """Create Bones from Selected Objects or Elements
    Object | Edit Mesh | Edit Curve | Edit Armature | Pose"""
    bl_idname = "bonera.create_bones_from_selected"
    bl_label = "Create Bones From Selected"
    bl_options = {'UNDO', 'REGISTER'}

    Base_Name: bpy.props.StringProperty(default="Bone")
    name: bpy.props.StringProperty(default="Bone")

    Reset_To_Default: bpy.props.BoolProperty(default=False, update=Reset_Default)

    Prefix: bpy.props.EnumProperty(items=ENUM_Prefix)
    Suffix: bpy.props.EnumProperty(items=ENUM_Suffix)

    Mode: bpy.props.EnumProperty(items=ENUM_Mode)

    Position_Mode: bpy.props.EnumProperty(items=ENUM_Position_Mode)
    Use_Deform: bpy.props.BoolProperty(default=True)

    Bind_Mode: bpy.props.EnumProperty(items=ENUM_Bind_Mode, default=1)
    Constraint_Type: bpy.props.EnumProperty(items=ENUM_Constraint_Type)

    SHOW_Weight_Option: bpy.props.BoolProperty(default=False)

    BIND_Add_Armature_Modifier: bpy.props.BoolProperty(default=True)
    BIND_Parent_Non_Mesh: bpy.props.BoolProperty(default=True)
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

    ARMATURE_Parent_Bone: bpy.props.BoolProperty(default=True)

    Armature_Update: bpy.props.BoolProperty(default=False)

    ELEM_Mesh: bpy.props.EnumProperty(default="VERTEX", items=ENUM_ELEM_Mesh)
    ELEM_Armature: bpy.props.EnumProperty(default="HEAD", items=ENUM_ELEM_Armature)
    ELEM_Handle: bpy.props.BoolProperty(default=False)

    To_Active_Armature: bpy.props.BoolProperty(default=True)
    Use_Self_Armature: bpy.props.BoolProperty(default=True)

    Target_Armature_Mode: bpy.props.EnumProperty(items=ENUM_Target_Armature_Mode)

    Use_Only_Orphan: bpy.props.BoolProperty(default=False)
    Use_Hierarchy: bpy.props.BoolProperty(default=True)

    Parent_Bone: bpy.props.BoolProperty(default=False)


    child_bone_pair = []
    armature_obj_pair = []


    @classmethod
    def poll(cls, context):
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
            # row.prop(self, "Base_Name", text="")
            row.prop(self, "name", text="")
            row.scale_x = 2
            row.prop(self, "Suffix", text="")
        else:
            layout.prop(self, "Base_Name", text="Bone Name")

    def draw_general(self, context, layout):

        row = layout.row()
        row.prop(self, "Mode", expand=True)

        if context.mode == "OBJECT":
            row = layout.row()
            row.prop(self, "Position_Mode", text="")
            if self.Mode == "INDIVIDUAL":
                row = layout.row()
                row.prop(self, "Use_Hierarchy", text="Use Hierarchy")

    def draw_weight_options(self, context, layout):

        if not context.mode in ["EDIT_ARMATURE", "POSE"]:

            if Utility_Functions.draw_subpanel(self, self.SHOW_Weight_Option, "SHOW_Weight_Option", "Bind Option", layout):

                if context.mode in ["EDIT_MESH", "OBJECT"]:
                    col = layout.column(align=True)

                    col.prop(self, "Bind_Mode", text="")

                    if self.Bind_Mode == "WEIGHT":

                        col.prop(self, "BIND_Add_Armature_Modifier", text="Add Armature Modifier")
                        col.prop(self, "BIND_Parent_To_Armature", text="Parent To Armature")
                        col.prop(self, "BIND_Parent_Non_Mesh", text="Parent Non Mesh")

                    if self.Bind_Mode == "CONSTRAINT_BONE_TO_SELECTED":
                        row = col.row()
                        row.prop(self, "Constraint_Type", expand=True)


                        # col.prop(self, "BIND_Clear_Vertex_Group", text="Clear Vertex Group")

                if context.mode in ["EDIT_CURVE","EDIT_LATTICE"]:
                    layout.prop(self, "Hook", text="Hook")

    def draw_elements(self, context, layout):

        if self.Mode == "INDIVIDUAL":

            if context.mode == "EDIT_MESH":

                layout.prop(self, "ELEM_Mesh", text="")

            if context.mode == "EDIT_CURVE":

                layout.prop(self, "ELEM_Handle", text="Bezier Handle")

        if context.mode in ["EDIT_ARMATURE", "POSE"]:

            layout.prop(self, "ELEM_Armature", text="")

        # if context.mode == "EDIT_ARMATURE" and self.Mode == "INDIVIDUAL":
        #     layout.prop(self, "ARMATURE_Parent_Bone", text="Parent Bone")

    def draw_tail(self, context, layout):

        if Utility_Functions.draw_subpanel(self, self.SHOW_Tail, "SHOW_Tail", "Tail Option", layout):

            col = layout.column(align=True)
            col.prop(self, "Tail_Mode", text="")

            row = col.row(align=True)
            if not self.Tail_Mode == "CURSOR":
                row.prop(self, "Tail_Offset_Amount", text="")
            col.prop(self, "Flip_Bone", text="Flip Bone")

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

                    # if self.Choice_Armature == "NEW":
                    #     col.prop(self, "Armature_Update", text="Update")


        else:
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

        preferences = Utility_Functions.get_addon_preferences()

        if preferences.Reset_Button:
            row = layout.row()
            row.alignment = "RIGHT"
            row.prop(self, "Reset_To_Default", text="Reset Settings", icon="FILE_REFRESH")

        col = layout.column(align=True)
        self.draw_name(context, col)
        col.prop(self, "Use_Deform", text="Use Deform")

        col.separator()

        self.draw_general(context, col)
        self.draw_elements(context, col)

        if self.Target_Armature_Mode == "SELF_ARMATURE":

            col.prop(self, "Parent_Bone", text="Parent Bone")


        # if context.mode == "OBJECT":
        #     col.prop(self, "Use_Only_Orphan", text="Use Only Orphan")

        layout.separator()

        self.draw_weight_options(context, layout)
        self.draw_tail(context, layout)
        self.draw_armature(context, layout)



    def Armature_Check(self, context):

        scn = context.scene
        armature_object = None

        if self.Choice_Armature == "NEW":
            armature_object = Create_Armature(self.New_Armature_Name)
            armature_object.show_in_front = True
            return armature_object
        else:
            armature_object = scn.Bonera_Scene_Data.Bone_From_Selection_Armature
            return armature_object


        if not armature_object:
            armature_object = Create_Armature(self.New_Armature_Name)
            armature_object.show_in_front = True
            return armature_object
        else:
            if context.view_layer.objects.get(armature_object.name):
                pass
            else:
                armature_object = Create_Armature(self.New_Armature_Name)
                armature_object.show_in_front = True
                return armature_object

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


        if self.name == "":
            self.Base_Name = self.name
        else:
            self.Base_Name = self.name + "_"


        self.child_bone_pair.clear()
        self.armature_obj_pair.clear()

        mode = context.mode

        Tail_Mode = self.Tail_Mode
        bind_mode = self.Bind_Mode

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

            if self.Mode == "MEDIAN":

                binding_objects = []
                points = []

                for object in selected_objects:

                    indices = []

                    if mode == "OBJECT":

                        if self.Position_Mode == "ORIGIN":

                            points.append(object.matrix_world.to_translation())

                            if object.type == "MESH":
                                for vertex in object.data.vertices:
                                    indices.append(vertex.index)

                        if self.Position_Mode in ["CENTER", "BOUNDING_BOX"]:

                            if object.type == "MESH":
                                for vertex in object.data.vertices:
                                    points.append(object.matrix_world @ vertex.co)
                                    indices.append(vertex.index)

                            else:
                                points.append(object.matrix_world.to_translation())

                        binding_object = {"object": object, "indices": indices}
                        binding_objects.append(binding_object)

                    if mode == "EDIT_MESH":

                        Utility_Functions.object_switch_mode(object, "OBJECT")

                        if object.type == "MESH":
                            for vertex in object.data.vertices:

                                if vertex.select:

                                    points.append(object.matrix_world @ vertex.co)
                                    indices.append(vertex.index)

                            binding_object = {"object": object, "indices": indices}
                            binding_objects.append(binding_object)

                    if mode == "EDIT_LATTICE":

                        Utility_Functions.object_switch_mode(object, "OBJECT")

                        if object.type == "LATTICE":
                            

                            for i, point in enumerate(object.data.points):

                                if point.select:
                                    points.append(object.matrix_world @ point.co)
                                    indices.append(i)

                            binding_object = {"object": object, "indices": indices}
                            binding_objects.append(binding_object)

                    if mode == "EDIT_CURVE":

                        if object.type == "CURVE":

                            counter = -1

                            for spline in object.data.splines:

                                if spline.type in bezier_point_type:

                                    for bezier_point in spline.bezier_points:

                                        counter += 1
                                        index_handle_left = counter
                                        counter += 1
                                        index_point = counter
                                        counter += 1
                                        index_handle_right = counter

                                        if bezier_point.select_control_point:
                                            points.append(object.matrix_world @ bezier_point.co)

                                            indices.append(index_handle_left)
                                            indices.append(index_point)
                                            indices.append(index_handle_right)

                                if spline.type in point_type:

                                    for point in spline.points:
                                        counter += 1
                                        index_nurbs_point = counter

                                        if point.select:
                                            points.append(object.matrix_world @ point.co.xyz)
                                            indices.append(index_nurbs_point)

                            binding_object = {"object": object, "indices": indices}
                            binding_objects.append(binding_object)

                    if mode == "EDIT_ARMATURE":

                        if object.type == "ARMATURE":
                            for bone in object.data.edit_bones:

                                if bone.select:
                                    if self.ELEM_Armature == "HEAD":

                                        points.append(object.matrix_world @ bone.head)

                                    if self.ELEM_Armature == "TAIL":

                                        points.append(object.matrix_world @ bone.tail)

                                    if self.ELEM_Armature == "CENTER":

                                        points.append(object.matrix_world @ bone.head)
                                        points.append(object.matrix_world @ bone.tail)

                            binding_object = {"object": object, "indices": indices}
                            binding_objects.append(binding_object)

                    if mode == "POSE":

                        if object.type == "ARMATURE":
                            for bone in object.pose.bones:

                                if bone.bone.select:
                                    if self.ELEM_Armature == "HEAD":

                                        points.append(object.matrix_world @ bone.head)

                                    if self.ELEM_Armature == "TAIL":

                                        points.append(object.matrix_world @ bone.tail)

                                    if self.ELEM_Armature == "CENTER":

                                        points.append(object.matrix_world @ bone.head)
                                        points.append(object.matrix_world @ bone.tail)

                            binding_object = {"object": object, "indices": indices}
                            binding_objects.append(binding_object)

                if self.Position_Mode == "CENTER":
                    mid_point = Utility_Functions.midpoint(points, "CENTER")

                if self.Position_Mode == "BOUNDING_BOX":
                    mid_point = Utility_Functions.midpoint(points, "BOUNDING_BOX")

                if self.Position_Mode == "ORIGIN":
                    mid_point = Utility_Functions.midpoint(points, "BOUNDING_BOX")

                Create_Item = {"location": mid_point, "name": self.Base_Name, "binding_objects": binding_objects}

                Utility_Functions.object_switch_mode(Armature_Object, "EDIT")

                Edit_Bones = Armature_Object.data.edit_bones

                mid_point = Create_Item["location"]

                if mid_point:
                    name = Create_Item["name"]

                    if preferences.Enable_Affixes:
                        bone_name = self.Generate_Bone_Name(context, name)
                    else:
                        bone_name = name

                    bone_head = Armature_Object.matrix_world.inverted() @ mid_point
                    bone_tail = Armature_Object.matrix_world.inverted() @ self.Offset_From_Head(context, mid_point)

                    if Tail_Mode == "CURSOR":
                        bone_tail = Armature_Object.matrix_world.inverted() @ context.scene.cursor.location

                    if Tail_Mode == "OFFSET_GLOBAL":
                        bone_tail = Armature_Object.matrix_world.inverted() @ self.Offset_From_Head(context, mid_point)

                    New_Bone = Utility_Functions.create_bone(Armature_Object, bone_name, bone_head, bone_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                    New_Bone_Name = New_Bone.name

                    Create_Item["bone_name"] = New_Bone_Name

                    Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")

                    for binding_object in Create_Item["binding_objects"]:

                        obj = binding_object["object"]
                        indices = binding_object["indices"]
                        bone_name = Create_Item["bone_name"]

                        # if self.Bind_Mode == "PARENT_BONE":
                        if bind_mode == "PARENT_BONE":

                            mw = obj.matrix_world.copy()

                            obj.parent = Armature_Object
                            obj.parent_type = "BONE"
                            obj.parent_bone = bone_name

                            obj.matrix_world = mw

                        # if self.Bind_Mode == "WEIGHT":
                        if bind_mode == "WEIGHT":

                            if obj.type == "MESH":

                                New_Vertex_Group = Utility_Functions.Add_Weight(obj, bone_name, indices)

                                if self.BIND_Add_Armature_Modifier:
                                    New_Modifier = Utility_Functions.Add_Armature_Modifier(obj, Armature_Object)

                                if self.BIND_Parent_To_Armature:
                                    mw = obj.matrix_world.copy()
                                    obj.parent = Armature_Object
                                    obj.matrix_world = mw

                            else:
                                if mode == "OBJECT":
                                    if self.BIND_Parent_Non_Mesh:

                                        mw = obj.matrix_world.copy()

                                        if not obj == Armature_Object:

                                            obj.parent = Armature_Object
                                            obj.parent_type = "BONE"
                                            obj.parent_bone = bone_name

                                            obj.matrix_world = mw

                        if mode in ["EDIT_CURVE", "EDIT_LATTICE"]:
                            if self.Hook:
                                if obj.type in ["CURVE", "LATTICE"]:
                                    Utility_Functions.Hook_Vertex_Bone(obj, Armature_Object, indices, New_Bone_Name, name=New_Bone_Name)

            if self.Mode == "INDIVIDUAL":

                if mode == "OBJECT" and self.Use_Hierarchy and self.Mode == "INDIVIDUAL":

                    Selected_Root = [object for object in selected_objects]

                    for obj in selected_objects:
                        for child in obj.children:
                            if child in Selected_Root:
                                Selected_Root.remove(child)

                    Utility_Functions.object_switch_mode(Armature_Object, "EDIT")
                    Edit_Bones = Armature_Object.data.edit_bones

                    for obj in Selected_Root:

                        if preferences.Enable_Affixes:

                            # bone_name = self.Generate_Bone_Name(context, self.Base_Name + "_" +  obj.name)
                            bone_name = self.Generate_Bone_Name(context, self.Base_Name + obj.name)
                        else:
                            # bone_name = self.Base_Name + "_" +  obj.name
                            bone_name = self.Base_Name + obj.name

                        bone_head_local = Utility_Functions.get_object_center(obj, self.Position_Mode)
                        bone_head = Armature_Object.matrix_world.inverted() @ obj.matrix_world @ bone_head_local
                        bone_tail = Armature_Object.matrix_world.inverted() @ ((obj.matrix_world @ bone_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                        if Tail_Mode == "CURSOR":
                            bone_tail = Armature_Object.matrix_world.inverted() @ context.scene.cursor.location

                        if Tail_Mode == "OFFSET_GLOBAL":
                            bone_tail = Armature_Object.matrix_world.inverted() @ ((obj.matrix_world @ bone_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                        if Tail_Mode == "OFFSET_LOCAL":
                            bone_tail = Armature_Object.matrix_world.inverted() @ obj.matrix_world @ self.Offset_From_Head(context, bone_head_local)

                        New_Bone = Utility_Functions.create_bone(Armature_Object, bone_name, bone_head, bone_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                        New_Bone_Name = New_Bone.name

                        # if self.Bind_Mode == "WEIGHT":
                        if bind_mode == "WEIGHT":

                            if obj.type == "MESH":

                                indices = [vertex.index for vertex in obj.data.vertices]

                                if indices is not None:
                                    New_Vertex_Group = Utility_Functions.Add_Weight(obj, New_Bone_Name, indices)

                                if self.BIND_Add_Armature_Modifier:
                                    New_Modifier = Utility_Functions.Add_Armature_Modifier(obj, Armature_Object)

                                if self.BIND_Parent_To_Armature:
                                    self.armature_obj_pair.append(obj)

                            else:

                                if self.BIND_Parent_Non_Mesh:

                                    self.child_bone_pair.append({"child": obj, "bone_name": New_Bone_Name})

                        # if self.Bind_Mode == "PARENT_BONE":
                        if bind_mode == "PARENT_BONE":

                            self.child_bone_pair.append({"child": obj, "bone_name": New_Bone_Name})






                        if len(obj.children) > 0:



                            for child in obj.children:

                                if child in selected_objects and obj in selected_objects:


                                    if preferences.Enable_Affixes:
                                        cob_name = self.Generate_Bone_Name(context, self.Base_Name +  child.name)
                                    else:
                                        cob_name = self.Base_Name + child.name

                                    cob_head_local = Utility_Functions.get_object_center(child, self.Position_Mode)
                                    cod_head = Armature_Object.matrix_world.inverted() @ child.matrix_world @ cob_head_local

                                    if Tail_Mode == "CURSOR":
                                        cob_tail = Armature_Object.matrix_world.inverted() @ context.scene.cursor.location

                                    if Tail_Mode == "OFFSET_GLOBAL":
                                        cob_tail = Armature_Object.matrix_world.inverted() @ ((child.matrix_world @ cob_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                                    if Tail_Mode == "OFFSET_LOCAL":
                                        cob_tail = Armature_Object.matrix_world.inverted() @ child.matrix_world @ self.Offset_From_Head(context, cob_head_local)

                                    cob_Bone = Utility_Functions.create_bone(Armature_Object, cob_name, cod_head, cob_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                                    cob_Bone_name = cob_Bone.name

                                    cob_Bone.parent = New_Bone




                                    # if self.Bind_Mode == "WEIGHT":
                                    if bind_mode == "WEIGHT":

                                        if child.type == "MESH":

                                            indices = [vertex.index for vertex in child.data.vertices]

                                            if indices is not None:
                                                New_Vertex_Group = Utility_Functions.Add_Weight(child, cob_Bone_name, indices)

                                            if self.BIND_Add_Armature_Modifier:
                                                New_Modifier = Utility_Functions.Add_Armature_Modifier(child, Armature_Object)

                                            if self.BIND_Parent_To_Armature:
                                                self.armature_obj_pair.append(child)

                                        else:

                                            if self.BIND_Parent_Non_Mesh:

                                                self.child_bone_pair.append({"child": child, "bone_name": cob_Bone.name})

                                    # if self.Bind_Mode == "PARENT_BONE":
                                    if bind_mode == "PARENT_BONE":

                                        self.child_bone_pair.append({"child": child, "bone_name": cob_Bone.name})







                                    self.recursive_object_find(context, Armature_Object, child, cob_Bone, selected_objects, Tail_Mode, bind_mode)






                else:

                    Create_Lists = []

                    if mode == "OBJECT":

                        for object in selected_objects:

                            Create_Lists = [{"location": Utility_Functions.get_object_center(object, self.Position_Mode), "name": self.Base_Name + object.name, "object": object , "indices": Utility_Functions.get_object_indices(object)} for object in selected_objects]

                    if mode == "EDIT_LATTICE":

                        for object in selected_objects:

                            Utility_Functions.object_switch_mode(object, "OBJECT")

                            if object.type == "LATTICE":


                                point_counter = -1

                                for count, point in enumerate(object.data.points):
                                    if point.select:
                                        point_counter += 1
                                        Create_Lists.append({"location": point.co, "name": self.Base_Name + object.name + "_LATTICE_" + str(point_counter), "object": object, "indices": [count]})


                    if mode == "EDIT_MESH":

                        for object in selected_objects:

                            Utility_Functions.object_switch_mode(object, "OBJECT")

                            if object.type == "MESH":

                                if self.ELEM_Mesh == "VERTEX":

                                    vert_counter = -1

                                    for count, vertex in enumerate(object.data.vertices):
                                        if vertex.select:
                                            vert_counter += 1
                                            Create_Lists.append({"location": vertex.co, "name": self.Base_Name + object.name + "_VERTEX_" + str(vertex.index), "object": object, "normal": vertex.normal, "indices": [vertex.index]})

                                if self.ELEM_Mesh == "EDGES":

                                    edge_counter = -1

                                    for count, edge in enumerate(object.data.edges):
                                        if edge.select:
                                            edge_counter += 1

                                            edge_center = Utility_Functions.midpoint([object.data.vertices[vertex_index].co for vertex_index in edge.vertices], "CENTER")
                                            average_normal = Utility_Functions.Average_Normals([object.data.vertices[vertex_index].normal for vertex_index in edge.vertices])
                                            Create_Lists.append({"location": edge_center, "name": self.Base_Name + object.name + "_EDGES_" + str(edge.index), "object": object, "normal": average_normal, "indices": edge.vertices})

                                if self.ELEM_Mesh == "FACE":

                                    face_counter = -1

                                    for count, face in enumerate(object.data.polygons):
                                        if face.select:
                                            face_counter += 1
                                            Create_Lists.append({"location": face.center, "name": self.Base_Name + object.name + "_FACE_" + str(face.index), "object": object, "normal": face.normal, "indices": face.vertices})

                    if mode == "EDIT_CURVE":

                        for object in selected_objects:

                            Utility_Functions.object_switch_mode(object, "OBJECT")

                            if object.type == "CURVE":

                                counter = -1

                                for spline_count, spline in enumerate(object.data.splines):

                                    indices = []

                                    if spline.type in bezier_point_type:

                                        bp_counter = -1

                                        for count, bezier_point in enumerate(spline.bezier_points):

                                            bezier_point.handle_left_type = "FREE"
                                            bezier_point.handle_right_type = "FREE"

                                            counter += 1
                                            index_handle_left = counter
                                            counter += 1
                                            index_point = counter
                                            counter += 1
                                            index_handle_right = counter

                                            if bezier_point.select_control_point:

                                                bp_counter += 1
                                                if self.ELEM_Handle:
                                                    Handle_Create = []
                                                    Handle_Create.append({"location": bezier_point.handle_left, "name": self.Base_Name + object.name + "_SPLINE_" + str(spline_count) +"_HANDLE_LEFT_" + str(count), "object": object, "indices": [index_handle_left]})
                                                    Handle_Create.append({"location": bezier_point.handle_right, "name": self.Base_Name + object.name + "_SPLINE_" + str(spline_count) +"_HANDLE_RIGHT_" + str(count), "object": object, "indices": [index_handle_right]})
                                                    Create_Lists.append({"location": bezier_point.co.xyz, "name": self.Base_Name + object.name + "_SPLINE_" + str(spline_count) + "_BEZIER_POINT_" + str(count), "object": object, "indices": [index_point], "handle_create": Handle_Create})
                                                else:
                                                    Create_Lists.append({"location": bezier_point.co.xyz, "name": self.Base_Name + object.name + "_SPLINE_" + str(spline_count) + "_BEZIER_POINT_" + str(count), "object": object, "indices": [index_handle_left, index_point, index_handle_right], "handle_create": []})

                                    if spline.type in point_type:

                                        np_counter = -1

                                        for count, point in enumerate(spline.points):

                                            counter += 1
                                            index_nurbs_point = counter

                                            if point.select:

                                                np_counter += 1

                                                Create_Lists.append({"location": point.co.xyz, "name": self.Base_Name + object.name + "_SPLINE_" + str(spline_count) +"_NURB_POINT_" + str(count), "object": object, "indices": [index_nurbs_point], "handle_create": []})

                    if mode in ["EDIT_ARMATURE", "POSE"]:

                        for object in selected_objects:

                            if object.type == "ARMATURE":

                                if mode == "EDIT_ARMATURE":
                                    bones = object.data.edit_bones
                                if mode == "POSE":
                                    bones = object.pose.bones

                                for count, bone in enumerate(bones):

                                    if self.ELEM_Armature == "CENTER":

                                        center = Utility_Functions.midpoint([bone.head, bone.tail], "CENTER")

                                        if Utility_Functions.check_bone_select(bone, mode):

                                            Offset_Head = bone.matrix @ mathutils.Vector(self.Tail_Offset_Amount)
                                            Offset_Vector = bone.head - Offset_Head
                                            Offset_Matrix = mathutils.Matrix.Translation(mathutils.Vector(Offset_Vector))

                                            Create_Lists.append({"location": center, "name": self.Base_Name + object.name + "_Bone_" + bone.name, "object": object, "bone_matrix": Offset_Matrix, "normal": None, "indices": [], "parent_bone": bone.name})

                                    if self.ELEM_Armature == "HEAD":

                                        if Utility_Functions.check_bone_select(bone, mode):

                                            Offset_Head = bone.matrix @ mathutils.Vector(self.Tail_Offset_Amount)
                                            Offset_Vector = bone.head - Offset_Head
                                            Offset_Matrix = mathutils.Matrix.Translation(mathutils.Vector(Offset_Vector))

                                            Create_Lists.append({"location": bone.head, "name": self.Base_Name + object.name + "_Head_" + bone.name, "object": object, "bone_matrix": Offset_Matrix, "normal": None, "indices": [], "parent_bone": bone.name})

                                    if self.ELEM_Armature == "TAIL":

                                        if Utility_Functions.check_bone_select(bone, mode):

                                            Offset_Head = bone.matrix @ mathutils.Vector(self.Tail_Offset_Amount)
                                            Offset_Vector = bone.head - Offset_Head
                                            Offset_Matrix = mathutils.Matrix.Translation(mathutils.Vector(Offset_Vector))

                                            Create_Lists.append({"location": bone.tail, "name": self.Base_Name + object.name + "_Tail_" + bone.name, "object": object,"bone_matrix": Offset_Matrix, "normal": None, "indices": [], "parent_bone": bone.name})

                    if Create_Lists is not None:

                        Utility_Functions.object_switch_mode(Armature_Object, "EDIT")



                        Edit_Bones = Armature_Object.data.edit_bones

                        Weight_Pair_List = []




                        for Create in Create_Lists:

                            if preferences.Enable_Affixes:
                                bone_name = self.Generate_Bone_Name(context, Create["name"])
                            else:
                                bone_name = Create["name"]

                            bone_head_local = Create["location"]

                            object_ref = Create["object"]

                            if self.Target_Armature_Mode == "SELF_ARMATURE" and mode in ["EDIT_ARMATURE", "POSE"]:
                                Armature_Object = object_ref

                            bone_head = Armature_Object.matrix_world.inverted() @ object_ref.matrix_world @ bone_head_local

                            bone_tail = Armature_Object.matrix_world.inverted() @ self.Offset_From_Head(context, bone_head_local)

                            if Tail_Mode == "CURSOR":
                                bone_tail = Armature_Object.matrix_world.inverted() @ context.scene.cursor.location

                            if Tail_Mode == "OFFSET_GLOBAL":
                                bone_tail = Armature_Object.matrix_world.inverted() @ ((object_ref.matrix_world @ bone_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                            if Tail_Mode == "OFFSET_LOCAL":
                                bone_tail = Armature_Object.matrix_world.inverted() @ Create["object"].matrix_world @ self.Offset_From_Head(context, bone_head_local)

                            if Tail_Mode == "NORMAL":
                                bone_tail = Armature_Object.matrix_world.inverted() @ object_ref.matrix_world @ self.Offset_From_Head_NORMAL(context, object_ref, bone_head_local, Create["normal"])

                            if Tail_Mode == "ROLL":
                                bone_tail = Armature_Object.matrix_world.inverted() @ object_ref.matrix_world @ Create["bone_matrix"] @ bone_head_local




                            # SELF_ARMATURE



                            New_Bone = Utility_Functions.create_bone(Armature_Object, bone_name, bone_head, bone_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                            New_Bone_Name = New_Bone.name

                            if Tail_Mode == "BONE":
                                if "parent_bone" in Create:
                                    New_Bone.align_orientation(Armature_Object.data.edit_bones.get(Create["parent_bone"]))


                            if self.Target_Armature_Mode == "SELF_ARMATURE" and mode in ["EDIT_ARMATURE"]:
                                if self.Parent_Bone:
                                    if "parent_bone" in Create:
                                        New_Bone.parent = Armature_Object.data.edit_bones.get(Create["parent_bone"])



                            obj = Create["object"]
                            indices = Create["indices"]

                            Weight_Pair = {"object": obj, "indices": indices, "bone_name": New_Bone_Name}
                            Weight_Pair_List.append(Weight_Pair)


                            if mode == "EDIT_CURVE":
                                if object_ref.type == "CURVE":

                                    handles = Create["handle_create"]

                                    for handle in handles:

                                        if preferences.Enable_Affixes:
                                            handle_bone_name = self.Generate_Bone_Name(context, handle["name"])
                                        else:
                                            handle_bone_name = handle["name"]

                                        handle_bone_head_local = handle["location"]
                                        handle_bone_head = Armature_Object.matrix_world.inverted() @ object_ref.matrix_world @ handle_bone_head_local
                                        handle_bone_tail = self.Offset_From_Head(context, handle_bone_head)

                                        if Tail_Mode == "CURSOR":
                                            handle_bone_tail = Armature_Object.matrix_world.inverted() @ context.scene.cursor.location

                                        if Tail_Mode == "OFFSET_GLOBAL":
                                            handle_bone_tail = self.Offset_From_Head(context, handle_bone_head)

                                        if Tail_Mode == "OFFSET_LOCAL":
                                            handle_bone_tail = handle["object"].matrix_world @ self.Offset_From_Head(context, handle_bone_head_local)

                                        Handle_New_Bone = Utility_Functions.create_bone(Armature_Object, handle_bone_name, handle_bone_head, handle_bone_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                                        Handle_New_Bone_Name = Handle_New_Bone.name

                                        Handle_New_Bone.parent = New_Bone

                                        handle_obj = handle["object"]
                                        handle_indices = handle["indices"]

                                        Handle_Weight_Pair = {"object": handle_obj, "indices": handle_indices, "bone_name": Handle_New_Bone_Name}
                                        Weight_Pair_List.append(Handle_Weight_Pair)

                        Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")

                        for Weight_Pair in Weight_Pair_List:

                            obj = Weight_Pair["object"]
                            indices = Weight_Pair["indices"]
                            Bone_Name = Weight_Pair["bone_name"]

                            if mode == "EDIT_CURVE":
                                if self.Hook:
                                    if obj.type == "CURVE":
                                        Utility_Functions.Hook_Vertex_Bone(obj, Armature_Object, indices, Bone_Name, name=Bone_Name)



                            if mode == "EDIT_LATTICE":
                                if self.Hook:
                                    if obj.type == "LATTICE":
                                        Utility_Functions.Hook_Vertex_Bone(obj, Armature_Object, indices, Bone_Name, name=Bone_Name)

                            # if self.Bind_Mode in ["WEIGHT", "CONSTRAINT_BONE_TO_SELECTED"]:
                            if bind_mode in ["WEIGHT", "CONSTRAINT_BONE_TO_SELECTED"]:

                                if obj.type == "MESH":


                                    if indices is not None:
                                        New_Vertex_Group = Utility_Functions.Add_Weight(obj, Bone_Name, indices)


                                    # if self.Bind_Mode == "WEIGHT":
                                    if bind_mode == "WEIGHT":


                                        if self.BIND_Add_Armature_Modifier:
                                            New_Modifier = Utility_Functions.Add_Armature_Modifier(obj, Armature_Object)

                                        if self.BIND_Parent_To_Armature:

                                            mw = obj.matrix_world.copy()
                                            obj.parent = Armature_Object
                                            obj.matrix_world = mw

                                    # if self.Bind_Mode == "CONSTRAINT_BONE_TO_SELECTED":
                                    if bind_mode == "CONSTRAINT_BONE_TO_SELECTED":

                                        constraint_bone = Armature_Object.pose.bones.get(Bone_Name)

                                        if constraint_bone is not None:
                                            constraint = constraint_bone.constraints.new(self.Constraint_Type)
                                            # constraint = constraint_bone.constraints.new("COPY_LOCATION")
                                            constraint.target = obj
                                            constraint.subtarget = New_Vertex_Group.name
                                            mode = "OBJECT"





                                else:
                                    if mode == "OBJECT":
                                        if self.BIND_Parent_Non_Mesh:

                                            mw = obj.matrix_world.copy()
                                            if not obj == Armature_Object:
                                                obj.parent = Armature_Object
                                                obj.parent_type = "BONE"
                                                obj.parent_bone = Bone_Name

                                                obj.matrix_world = mw

                            if mode == "OBJECT":
                                # if self.Bind_Mode == "PARENT_BONE":
                                if bind_mode == "PARENT_BONE":

                                    mw = obj.matrix_world.copy()

                                    obj.parent = Armature_Object
                                    obj.parent_type = "BONE"
                                    obj.parent_bone = Bone_Name

                                    obj.matrix_world = mw

            Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")

            for cbp in self.child_bone_pair:

                bone_name = cbp["bone_name"]
                child = cbp["child"]

                if child:
                    mw = child.matrix_world.copy()

                    child.parent = Armature_Object
                    child.parent_type = "BONE"
                    child.parent_bone = bone_name
                    child.matrix_world = mw

            self.child_bone_pair.clear()

            if self.BIND_Parent_To_Armature:

                for arm_obj in self.armature_obj_pair:

                    mw = arm_obj.matrix_world.copy()
                    arm_obj.parent = Armature_Object
                    arm_obj.matrix_world = mw

            self.armature_obj_pair.clear()





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

        self.child_bone_pair.clear()
        self.armature_obj_pair.clear()

        return {'FINISHED'}


    def recursive_object_find(self, context, Armature_Object, object, prev_cob_bone, selected, Tail_Mode, bind_mode):


        preferences = Utility_Functions.get_addon_preferences()
        edit_bones = Armature_Object.data.edit_bones

        if len(object.children) > 0:

            for child in object.children:

                if child in selected and object in selected:



                    if preferences.Enable_Affixes:
                        cob_name = self.Generate_Bone_Name(context, self.Base_Name + child.name)
                    else:
                        cob_name = self.Base_Name +  child.name

                    cob_head_local = Utility_Functions.get_object_center(child, self.Position_Mode)
                    cod_head = Armature_Object.matrix_world.inverted() @ child.matrix_world @ cob_head_local

                    if Tail_Mode == "CURSOR":
                        cob_tail = Armature_Object.matrix_world.inverted() @ context.scene.cursor.location

                    if Tail_Mode == "OFFSET_GLOBAL":
                        cob_tail = Armature_Object.matrix_world.inverted() @ ((child.matrix_world @ cob_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                    if Tail_Mode == "OFFSET_LOCAL":
                        cob_tail = Armature_Object.matrix_world.inverted() @ child.matrix_world @ self.Offset_From_Head(context, cob_head_local)

                    cob_Bone = Utility_Functions.create_bone(Armature_Object, cob_name, cod_head, cob_tail, self.Use_Deform, Flip_Bone = self.Flip_Bone)
                    cob_Bone_name = cob_Bone.name

                    cob_Bone.parent = prev_cob_bone

                    self.recursive_object_find(context, Armature_Object, child, cob_Bone, selected, Tail_Mode, bind_mode)



                    # if self.Bind_Mode == "WEIGHT":
                    if bind_mode == "WEIGHT":

                        if child.type == "MESH":

                            indices = [vertex.index for vertex in child.data.vertices]

                            if indices is not None:
                                New_Vertex_Group = Utility_Functions.Add_Weight(child, cob_Bone_name, indices)

                            if self.BIND_Add_Armature_Modifier:
                                New_Modifier = Utility_Functions.Add_Armature_Modifier(child, Armature_Object)

                            if self.BIND_Parent_To_Armature:
                                self.armature_obj_pair.append(child)

                        else:

                            if self.BIND_Parent_Non_Mesh:

                                self.child_bone_pair.append({"child": child, "bone_name": cob_Bone.name})

                    # if self.Bind_Mode == "PARENT_BONE":
                    if bind_mode == "PARENT_BONE":

                        self.child_bone_pair.append({"child": child, "bone_name": cob_Bone.name})









classes = [BONERA_OP_Create_Bones_From_Selected]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
