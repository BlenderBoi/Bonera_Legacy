import bpy
from Bonera_Toolkit import Utility_Functions
import mathutils

OPERATOR_POLL_CONTEXT = ["OBJECT","EDIT_MESH","EDIT_CURVE","EDIT_ARMATURE", "POSE"]
bezier_point_type = ["BEZIER"]
point_type = ["POLY", "NURBS"]


#Fix Naming for some Operator
#Fix Hook Median Edit Mode


#---------------------ENUM AREA---------------------


def ENUM_Orientation_Mode(self, context):

    ENUM_Items = [("GLOBAL","Global","Global")]



    if self.Mode == "INDIVIDUAL":

        ENUM_Items.append(("LOCAL","Local","Local"))

        if context.mode == "EDIT_MESH":
            ENUM_Items.append(("NORMAL" ,"Normal" ,"Normal"))

        if context.mode in ["EDIT_ARMATURE", "POSE"]:
            ENUM_Items.append(("ROLL" ,"Roll" ,"Roll"))

    ENUM_Items.append(("CURSOR","3D Cursor","3D Cursor"))

    return ENUM_Items

def ENUM_Bind_Mode(self, context):

    if self.Mode == "MEDIAN":

        if context.mode == "OBJECT":
            ENUM_Items = [("NONE", "None", "None"),("PARENT","Parent","Parent")]

        if context.mode in ["EDIT_ARMATURE", "POSE"]:
            ENUM_Items = [("NONE", "None", "None"),("PARENT","Parent to Bone","Parent")]

        if context.mode == "EDIT_MESH":
            ENUM_Items = [("NONE", "None", "None"),("HOOK","Hook","Hook")]

        if context.mode == "EDIT_CURVE":
            ENUM_Items = [("NONE", "None", "None"),("HOOK","Hook","Hook")]

    if self.Mode == "INDIVIDUAL":

        if context.mode == "OBJECT":
            # ENUM_Items = [("NONE", "None", "None"),("PARENT","Parent","Parent"),("CHILD","Child","Child")]
            ENUM_Items = [("NONE", "None", "None"),("PARENT","Parent","Parent")]

        if context.mode in ["EDIT_ARMATURE", "POSE"]:
            ENUM_Items = [("NONE", "None", "None"),("PARENT","Parent to Bone","Parent")]

        if context.mode == "EDIT_MESH":
            if self.ELEM_Mesh == "VERTEX":
                ENUM_Items = [("NONE", "None", "None"),("HOOK","Hook","Hook"), ("PARENT_VERTEX","Parent to Vertex","Parent to Vertex")]
                # ENUM_Items = [("NONE", "None", "None"),("HOOK","Hook","Hook")]
            else:
                ENUM_Items = [("NONE", "None", "None"),("HOOK","Hook","Hook")]

        if context.mode == "EDIT_CURVE":
            # ENUM_Items = [("NONE", "None", "None"),("HOOK","Hook","Hook"), ("PARENT_VERTEX","Parent to Vertex","Parent to Vertex")]
            ENUM_Items = [("NONE", "None", "None"),("HOOK","Hook","Hook")]

    return ENUM_Items

ENUM_Mode = [("INDIVIDUAL","Individual","Individual"),("MEDIAN","Median","Median")]

ENUM_Position_Mode = [("ORIGIN","Origin","Origin"),("CENTER","Geometry","Geometry"),("BOUNDING_BOX","Bounding Box","Bounding Box")]

ENUM_ELEM_Mesh = [("VERTEX","Vertices","Vertices"),("EDGES","Edges","Edges"),("FACE","Faces","Faces")]

ENUM_ELEM_Armature = [("CENTER","Center","Center"),("HEAD","Head","Head"),("TAIL","Tail","Tail")]

ENUM_Empty_Shapes = [('PLAIN_AXES', 'Plain Axes', 'Plain Axes', "EMPTY_AXIS", 1), ('ARROWS', 'Arrows', 'Arrows', "EMPTY_ARROWS", 2), ('SINGLE_ARROW', 'Single Arrow', 'Single Arrow', "EMPTY_SINGLE_ARROW", 3), ('CIRCLE', "Circle", "Circle", "MESH_CIRCLE", 4), ('CUBE', "Cube", "Cube", "CUBE", 5), ('SPHERE', "Sphere", "Sphere", "SPHERE", 6), ('CONE', "Cone", "Cone", "CONE", 7), ('IMAGE',  "Image", "Image", "IMAGE_DATA", 8)]

#---------------------ENUM AREA---------------------

def Create_Armature(name):

    armature = bpy.data.armatures.new(name)
    object = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(object)

    return object






def Reset_Default(self, context):
    if self.Reset_To_Default:
        self.Reset_To_Default = False


    self.Base_Name="Empty"

    self.Mode="INDIVIDUAL"
    self.Position_Mode="ORIGIN"

    if context.mode == "OBJECT":
        self.Bind_Mode="PARENT"

    if context.mode in ["EDIT_ARMATURE", "POSE"]:
        self.Bind_Mode="PARENT"

    if context.mode == "EDIT_MESH":
        if self.ELEM_Mesh == "VERTEX":
            self.Bind_Mode="HOOK"
        else:
            self.Bind_Mode="HOOK"

    if context.mode == "EDIT_CURVE":

        self.Bind_Mode="HOOK"





    self.Use_Only_Orphan=False


    self.Empty_Shape="PLAIN_AXES"
    self.Empty_Display_Size=0.3

    self.Orientation="GLOBAL"

    self.ELEM_Mesh="VERTEX"
    self.ELEM_Armature="HEAD"
    self.ELEM_Handle=False

    self.Parent_To_Object=True

    self.Use_Hierarchy=True















class BONERA_OP_Create_Empties_From_Selected(bpy.types.Operator):
    """Create Empties from Selected Objects or Elements
    Object | Edit Mesh | Edit Curve | Edit Armature | Pose"""
    bl_idname = "bonera.create_empties_from_selected"
    bl_label = "Create Empties From Selected"
    bl_options = {'UNDO', 'REGISTER'}

    Reset_To_Default: bpy.props.BoolProperty(default=False, update=Reset_Default)

    Base_Name: bpy.props.StringProperty(default="Empty")

    Mode: bpy.props.EnumProperty(items=ENUM_Mode)

    Position_Mode: bpy.props.EnumProperty(items=ENUM_Position_Mode)

    Bind_Mode: bpy.props.EnumProperty(items=ENUM_Bind_Mode, default=1)

    Use_Only_Orphan: bpy.props.BoolProperty(default=False)

    #if Hook, Parent Object
    #Object Hierarchy
    Empty_Shape: bpy.props.EnumProperty(items=ENUM_Empty_Shapes)
    Empty_Display_Size: bpy.props.FloatProperty(default=0.3)

    Orientation: bpy.props.EnumProperty(items=ENUM_Orientation_Mode)

    ELEM_Mesh: bpy.props.EnumProperty(default="VERTEX", items=ENUM_ELEM_Mesh)
    ELEM_Armature: bpy.props.EnumProperty(default="HEAD", items=ENUM_ELEM_Armature)
    ELEM_Handle: bpy.props.BoolProperty(default=False)

    Parent_To_Object: bpy.props.BoolProperty(default=True)

    Use_Hierarchy: bpy.props.BoolProperty(default=True)

    child_bone_pair = []

    @classmethod
    def poll(cls, context):
        if context.mode in OPERATOR_POLL_CONTEXT:
            return True

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def draw_name(self, context, layout):
        layout.prop(self, "Base_Name", text="Name")

    def draw_general(self, context, layout):

        row = layout.row()
        row.prop(self, "Mode", expand=True)

        if context.mode == "OBJECT":
            row = layout.row()
            row.prop(self, "Position_Mode", text="")
            # if self.Mode == "INDIVIDUAL":
            #     row = layout.row()
            #     row.prop(self, "Use_Hierarchy", text="Use Hierarchy")
            #

    def draw_weight_options(self, context, layout):

        if context.mode in ["EDIT_MESH", "EDIT_CURVE" , "OBJECT", "EDIT_ARMATURE"]:
            col = layout.column(align=True)
            col.prop(self, "Bind_Mode", text="Bind: ")

    def draw_elements(self, context, layout):

        if self.Mode == "INDIVIDUAL":

            if context.mode == "EDIT_MESH":

                layout.prop(self, "ELEM_Mesh", text="")

            if context.mode == "EDIT_CURVE":

                layout.prop(self, "ELEM_Handle", text="Bezier Handle")

        if context.mode in ["EDIT_ARMATURE", "POSE"]:

            layout.prop(self, "ELEM_Armature", text="")

    def draw(self, context):

        layout = self.layout

        preferences = Utility_Functions.get_addon_preferences()

        if preferences.Reset_Button:
            row = layout.row()
            row.alignment = "RIGHT"
            row.prop(self, "Reset_To_Default", text="Reset Settings", icon="FILE_REFRESH")

        col = layout.column(align=True)
        self.draw_name(context, col)

        row = col.row(align=True)
        row.scale_x = 0.7
        row.prop(self, "Empty_Shape", text="")
        row.scale_x = 0.3
        row.prop(self, "Empty_Display_Size", text="Size")

        col.separator()

        self.draw_general(context, col)

        self.draw_elements(context, col)

        if context.mode == "OBJECT":
            col.prop(self, "Use_Only_Orphan", text="Use Only Orphan")

        if context.mode in ["EDIT_MESH"]:
            col.prop(self, "Parent_To_Object", text="Parent To Object")


        layout.separator()

        layout.prop(self, "Orientation", text="Orientation")

        self.draw_weight_options(context, layout)

    def execute(self, context):

        self.child_bone_pair.clear()

        mode = context.mode

        orientation = self.Orientation
        bind_mode = self.Bind_Mode

        selected_objects = context.selected_objects
        active_object = context.object

        preferences = Utility_Functions.get_addon_preferences()

        context.view_layer.update()

        if self.Mode == "MEDIAN":

            binding_objects = []
            points = []

            for object in selected_objects:

                indices = []

                if mode == "OBJECT":

                    Orphan_Bool = True

                    if self.Use_Only_Orphan:

                        if object.parent:
                            Orphan_Bool = False
                        else:
                            Orphan_Bool = True

                    if Orphan_Bool:

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

            mid_point = Create_Item["location"]

            if mid_point:
                name = Create_Item["name"]

                # if orientation == "GLOBAL":
                #     rotation = context.scene.cursor.location
                rotation_quaternion = (0, 0, 0, 0)
                rotation_euler = (0, 0, 0)


                if orientation == "CURSOR":
                    rotation_quaternion = context.scene.cursor.rotation_quaternion
                    rotation_euler = context.scene.cursor.rotation_euler


                New_Empty = Utility_Functions.Create_Empty(name)
                New_Empty.location = mid_point
                New_Empty.rotation_quaternion = rotation_quaternion
                New_Empty.rotation_euler = rotation_euler

                New_Empty.empty_display_type = self.Empty_Shape
                New_Empty.empty_display_size = self.Empty_Display_Size

                New_Empty.show_in_front = True

                context.view_layer.update()

                for binding_object in Create_Item["binding_objects"]:

                    obj = binding_object["object"]
                    indices = binding_object["indices"]

                    if mode == "EDIT_MESH":
                        if self.Parent_To_Object:
                            context.view_layer.update()
                            mw = New_Empty.matrix_world.copy()
                            New_Empty.parent = obj
                            New_Empty.matrix_world = mw

                    if mode == "OBJECT":
                        if bind_mode == "PARENT":

                            mw = obj.matrix_world.copy()
                            obj.parent = New_Empty
                            obj.matrix_world = mw

                    if mode in ["EDIT_MESH", "EDIT_CURVE"]:
                        if bind_mode == "HOOK":

                            if obj.type in ["CURVE", "MESH"]:

                                Utility_Functions.Hook_Vertex_Empty(obj, New_Empty, indices, name=name)

        if self.Mode == "INDIVIDUAL":

            Create_Lists = []

            if mode == "OBJECT":

                for object in selected_objects:

                    Orphan_Bool = True

                    if self.Use_Only_Orphan:

                        if object.parent:
                            Orphan_Bool = False
                        else:
                            Orphan_Bool = True

                    if Orphan_Bool:
                        Create_Lists.append({"location": Utility_Functions.get_object_center(object, self.Position_Mode), "name": self.Base_Name + "_" + object.name, "object": object , "indices": Utility_Functions.get_object_indices(object)})
                    # Create_Lists = [{"location": Utility_Functions.get_object_center(object, self.Position_Mode), "name": self.Base_Name + "_" + object.name, "object": object , "indices": Utility_Functions.get_object_indices(object)} for object in selected_objects]

            if mode == "EDIT_MESH":

                for object in selected_objects:

                    Utility_Functions.object_switch_mode(object, "OBJECT")

                    if object.type == "MESH":

                        if self.ELEM_Mesh == "VERTEX":

                            vert_counter = -1

                            for count, vertex in enumerate(object.data.vertices):
                                if vertex.select:
                                    vert_counter += 1
                                    Create_Lists.append({"location": vertex.co, "name": self.Base_Name + "_" + object.name + "_VERTEX_" + str(vertex.index), "object": object, "normal": vertex.normal, "indices": [vertex.index]})

                        if self.ELEM_Mesh == "EDGES":

                            edge_counter = -1

                            for count, edge in enumerate(object.data.edges):
                                if edge.select:
                                    edge_counter += 1

                                    edge_center = Utility_Functions.midpoint([object.data.vertices[vertex_index].co for vertex_index in edge.vertices], "CENTER")
                                    average_normal = Utility_Functions.Average_Normals([object.data.vertices[vertex_index].normal for vertex_index in edge.vertices])
                                    Create_Lists.append({"location": edge_center, "name": self.Base_Name + "_" + object.name + "_EDGES_" + str(edge.index), "object": object, "normal": average_normal, "indices": edge.vertices})

                        if self.ELEM_Mesh == "FACE":

                            face_counter = -1

                            for count, face in enumerate(object.data.polygons):
                                if face.select:
                                    face_counter += 1
                                    Create_Lists.append({"location": face.center, "name": self.Base_Name + "_" + object.name + "_FACE_" + str(face.index), "object": object, "normal": face.normal, "indices": face.vertices})

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
                                            Handle_Create.append({"location": bezier_point.handle_left, "name": self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) +"_HANDLE_LEFT_" + str(count), "object": object, "indices": [index_handle_left]})
                                            Handle_Create.append({"location": bezier_point.handle_right, "name": self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) +"_HANDLE_RIGHT_" + str(count), "object": object, "indices": [index_handle_right]})
                                            Create_Lists.append({"location": bezier_point.co.xyz, "name": self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) + "_BEZIER_POINT_" + str(count), "object": object, "indices": [index_point], "handle_create": Handle_Create})
                                        else:
                                            Create_Lists.append({"location": bezier_point.co.xyz, "name": self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) + "_BEZIER_POINT_" + str(count), "object": object, "indices": [index_handle_left, index_point, index_handle_right], "handle_create": []})

                            if spline.type in point_type:

                                np_counter = -1

                                for count, point in enumerate(spline.points):

                                    counter += 1
                                    index_nurbs_point = counter

                                    if point.select:

                                        np_counter += 1

                                        Create_Lists.append({"location": point.co.xyz, "name": self.Base_Name + "_" + object.name + "_SPLINE_" + str(spline_count) +"_NURB_POINT_" + str(count), "object": object, "indices": [index_nurbs_point], "handle_create": []})

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

                                    # Offset_Head = bone.matrix @ mathutils.Vector(self.Tail_Offset_Amount)
                                    # Offset_Vector = bone.head - Offset_Head
                                    # Offset_Matrix = mathutils.Matrix.Translation(mathutils.Vector(Offset_Vector))
                                    bone_matrix = bone.matrix
                                    Create_Lists.append({"location": center, "name": self.Base_Name + "_" + object.name + "_Bone_" + bone.name, "object": object, "bone_matrix": bone_matrix, "normal": None, "indices": [], "parent_bone": bone.name})
                                    # Create_Lists.append({"location": center, "name": self.Base_Name + "_" + object.name + "_Bone_" + bone.name, "object": object, "normal": None, "indices": [], "parent_bone": bone.name})

                            if self.ELEM_Armature == "HEAD":

                                if Utility_Functions.check_bone_select(bone, mode):

                                    # Offset_Head = bone.matrix @ mathutils.Vector(self.Tail_Offset_Amount)
                                    # Offset_Vector = bone.head - Offset_Head
                                    # Offset_Matrix = mathutils.Matrix.Translation(mathutils.Vector(Offset_Vector))
                                    bone_matrix = bone.matrix
                                    Create_Lists.append({"location": bone.head, "name": self.Base_Name + "_" + object.name + "_Head_" + bone.name, "object": object, "bone_matrix": bone_matrix, "normal": None, "indices": [], "parent_bone": bone.name})
                                    # Create_Lists.append({"location": bone.head, "name": self.Base_Name + "_" + object.name + "_Head_" + bone.name, "object": object, "normal": None, "indices": [], "parent_bone": bone.name})

                            if self.ELEM_Armature == "TAIL":

                                if Utility_Functions.check_bone_select(bone, mode):

                                    # Offset_Head = bone.matrix @ mathutils.Vector(self.Tail_Offset_Amount)
                                    # Offset_Vector = bone.head - Offset_Head
                                    # Offset_Matrix = mathutils.Matrix.Translation(mathutils.Vector(Offset_Vector))
                                    bone_matrix = bone.matrix
                                    Create_Lists.append({"location": bone.tail, "name": self.Base_Name + "_" + object.name + "_Tail_" + bone.name, "object": object,"bone_matrix": bone_matrix, "normal": None, "indices": [], "parent_bone": bone.name})
                                    # Create_Lists.append({"location": bone.tail, "name": self.Base_Name + "_" + object.name + "_Tail_" + bone.name, "object": object, "normal": None, "indices": [], "parent_bone": bone.name})

            if Create_Lists is not None:

                Weight_Pair_List = []

                for Create in Create_Lists:

                    name = Create["name"]

                    loc_local = Create["location"]

                    object_ref = Create["object"]

                    loc = object_ref.matrix_world @ loc_local

                    rotation_quaternion = (0, 0, 0, 0)
                    rotation_euler = (0, 0, 0)

                    if orientation == "GLOBAL":
                        rotation_quaternion = (0, 0, 0, 0)

                    if orientation == "LOCAL":
                        rotation_quaternion = object_ref.matrix_world.to_quaternion()
                        rotation_euler = object_ref.matrix_world.to_euler()

                    if orientation == "CURSOR":
                        rotation_quaternion = context.scene.cursor.rotation_quaternion
                        rotation_euler = context.scene.cursor.rotation_euler

                    if orientation == "NORMAL":
                        normal = Create["normal"]
                        rotation_quaternion = Utility_Functions.Normal_To_Orientation(object_ref, loc, normal).to_quaternion()
                        rotation_euler = Utility_Functions.Normal_To_Orientation(object_ref, loc, normal).to_euler()

                    if orientation == "ROLL":
                        bone_matrix = object_ref.matrix_world @ Create["bone_matrix"]

                        rotation_quaternion = bone_matrix.to_quaternion()
                        rotation_euler = bone_matrix.to_euler()


                    New_Empty = Utility_Functions.Create_Empty(name)
                    New_Empty.location = loc
                    New_Empty.rotation_quaternion = rotation_quaternion
                    New_Empty.rotation_euler = rotation_euler

                    New_Empty.empty_display_type = self.Empty_Shape
                    New_Empty.empty_display_size = self.Empty_Display_Size
                    New_Empty.show_in_front = True

                    obj = Create["object"]
                    indices = Create["indices"]

                    if "parent_bone" in Create:
                        parent_bone = Create["parent_bone"]
                    else:
                        parent_bone = None

                    Weight_Pair = {"object": obj, "indices": indices, "empty_object": New_Empty, "parent_bone": parent_bone}
                    Weight_Pair_List.append(Weight_Pair)


                    if mode == "EDIT_MESH":
                        if self.Parent_To_Object:
                            context.view_layer.update()
                            mw = New_Empty.matrix_world.copy()
                            New_Empty.parent = obj
                            New_Empty.matrix_world = mw

                    if mode == "EDIT_CURVE":
                        if object_ref.type == "CURVE":

                            handles = Create["handle_create"]

                            for handle in handles:

                                handle_empty_name = handle["name"]

                                handle_loc_local = handle["location"]
                                handle_loc = object_ref.matrix_world @ handle_loc_local

                                Handle_New_Empty = Utility_Functions.Create_Empty(handle_empty_name)
                                Handle_New_Empty.location = handle_loc
                                context.view_layer.update()

                                mw = Handle_New_Empty.matrix_world.copy()
                                Handle_New_Empty.parent = New_Empty
                                Handle_New_Empty.matrix_world = mw

                                Handle_New_Empty.empty_display_type = self.Empty_Shape
                                Handle_New_Empty.empty_display_size = self.Empty_Display_Size
                                Handle_New_Empty.show_in_front = True

                                handle_obj = handle["object"]
                                handle_indices = handle["indices"]

                                Handle_Weight_Pair = {"object": handle_obj, "indices": handle_indices, "empty_object": Handle_New_Empty}
                                Weight_Pair_List.append(Handle_Weight_Pair)

                context.view_layer.update()

                for Weight_Pair in Weight_Pair_List:

                    obj = Weight_Pair["object"]
                    indices = Weight_Pair["indices"]
                    Empty_Object = Weight_Pair["empty_object"]

                    if self.Bind_Mode == "PARENT":
                        if mode in ["EDIT_ARMATURE"]:

                            if obj.type in ["ARMATURE"]:

                                bone_name = Weight_Pair["parent_bone"]

                                mw = Empty_Object.matrix_world.copy()

                                Empty_Object.parent = obj
                                Empty_Object.parent_type = "BONE"
                                Empty_Object.parent_bone = bone_name

                                Empty_Object.matrix_world = mw

                    # bone_name = Weight_Pair["bone_name"]
                    # if mode in ["EDIT_ARMATURE", "POSE"]:
                    #     if obj.type in ["ARMATURE"]:
                    #
                    #         mw = Empty_Object.matrix_world.copy()
                    #
                    #         Empty_Object.parent = obj
                    #         Empty_Object.parent_type = "BONE"
                    #         Empty_Object.parent_bone = bone_name
                    #
                    #         Empty_Object.matrix_world = mw

                    if mode in ["EDIT_CURVE", "EDIT_MESH"]:

                        if bind_mode == "HOOK":

                            if obj.type in ["CURVE", "MESH"]:

                                Utility_Functions.Hook_Vertex_Empty(obj, Empty_Object, indices, name=Empty_Object.name)

                    
                        if mode == "EDIT_MESH":

                            if bind_mode == "PARENT_VERTEX":

                                if obj.type in ["CURVE", "MESH"]:

                                    mw = Empty_Object.matrix_world.copy()
                                    Empty_Object.location = (0, 0, 0)

                                    Empty_Object.parent = obj
                                    Empty_Object.parent_type = "VERTEX"
                                    Empty_Object.parent_vertices = (indices[0], indices[0], indices[0])

                                    # Empty_Object.matrix_world = mw



                    if mode == "OBJECT":
                        if bind_mode == "PARENT":

                            mw = obj.matrix_world.copy()

                            obj.parent = Empty_Object
                            obj.matrix_world = mw

                        # if bind_mode == "CHILD":

                        #     mw = Empty_Object.matrix_world.copy()
                        #     Empty_Object.parent = obj
                        #     Empty_Object.matrix_world = mw

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




classes = [BONERA_OP_Create_Empties_From_Selected]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
