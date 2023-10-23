import bpy
from .. import Utility_Functions
import mathutils

OPERATOR_POLL_CONTEXT = ["OBJECT"]

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

    ENUM_Items =  [("NONE","None","None"),("WEIGHT","Weight","Weight"),("PARENT_BONE","Parent Bone","Parent Bone")]

    return ENUM_Items

ENUM_Position_Mode = [("ORIGIN","Origin","Origin"),("CENTER","Geometry","Geometry"),("BOUNDING_BOX","Bounding Box","Bounding Box")]

ENUM_Choice_Armature = [("NEW","New","New"),("EXIST","Existing","Existing")]

#---------------------ENUM AREA---------------------

def Create_Armature(name):

    armature = bpy.data.armatures.new(name)
    object = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(object)

    return object

class BONERA_OP_Create_Bone_Chain_From_Object_Hierarchy(bpy.types.Operator):
    """Create Bone Chain from Object Hierarchy
    Object Only"""
    bl_idname = "bonera.create_bone_chain_from_object_hierarchy"
    bl_label = "Create Bone Chain from Object Hierarchy"
    bl_options = {'UNDO', 'REGISTER'}

    Base_Name: bpy.props.StringProperty(default="Bone")

    Prefix: bpy.props.EnumProperty(items=ENUM_Prefix)
    Suffix: bpy.props.EnumProperty(items=ENUM_Suffix)

    Only_Selected: bpy.props.BoolProperty(default=True)

    Position_Mode: bpy.props.EnumProperty(items=ENUM_Position_Mode)
    Use_Deform: bpy.props.BoolProperty(default=True)

    Bind_Mode: bpy.props.EnumProperty(items=ENUM_Bind_Mode, default=1)

    SHOW_Weight_Option: bpy.props.BoolProperty(default=False)

    BIND_Add_Armature_Modifier: bpy.props.BoolProperty(default=True)
    BIND_Parent_Non_Mesh: bpy.props.BoolProperty(default=True)
    BIND_Parent_To_Armature: bpy.props.BoolProperty(default=False)

    SHOW_Tail: bpy.props.BoolProperty(default=False)

    Tail_Mode: bpy.props.EnumProperty(items=ENUM_Tail_Mode)
    Tail_Offset_Amount: bpy.props.FloatVectorProperty(default=(0, 0, 0.5))

    SHOW_Armature: bpy.props.BoolProperty(default=False)

    New_Armature_Name: bpy.props.StringProperty(default="Armature")
    Choice_Armature: bpy.props.EnumProperty(default="NEW", items=ENUM_Choice_Armature)

    Armature_Update: bpy.props.BoolProperty(default=False)


    Def_Prefix: bpy.props.EnumProperty(items=ENUM_Prefix)


    Chain_Prefix: bpy.props.StringProperty(default="Chain_")
    Deform_Prefix: bpy.props.StringProperty(default="Def_")


    Generate_Connect: bpy.props.BoolProperty(default=True)
    Generate_Deform: bpy.props.BoolProperty(default=False)
    Def_Use_Deform: bpy.props.BoolProperty(default=True)

    SHOW_Individual_Deform_Bone: bpy.props.BoolProperty(default=False)

    Align_Roll: bpy.props.BoolProperty(default=True)
    Connect_Bone: bpy.props.BoolProperty(default=True)


    Realign_bone_list = []
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

        layout.prop(self, "Chain_Prefix", text="Prefix")

    def draw_general(self, context, layout):


        row = layout.row()
        if context.mode == "OBJECT":
            row = layout.row()
            row.prop(self, "Position_Mode", text="")
            row = layout.row()
            # row.separator()
            # row = layout.row()
            # row.prop(self, "Only_Selected", text="Only Selected")

    def draw_weight_options(self, context, layout):

        if not context.mode in ["EDIT_ARMATURE", "POSE"]:

            if Utility_Functions.draw_subpanel(self, self.SHOW_Weight_Option, "SHOW_Weight_Option", "Bind Option", layout):

                col = layout.column(align=True)

                col.prop(self, "Bind_Mode", text="")

                if self.Bind_Mode == "WEIGHT":

                    col.prop(self, "BIND_Add_Armature_Modifier", text="Add Armature Modifier")
                    col.prop(self, "BIND_Parent_To_Armature", text="Parent To Armature")
                    col.prop(self, "BIND_Parent_Non_Mesh", text="Parent Non Mesh")

    def draw_tail(self, context, layout):

        if Utility_Functions.draw_subpanel(self, self.SHOW_Tail, "SHOW_Tail", "Tail Option", layout):

            col = layout.column(align=True)
            col.prop(self, "Tail_Mode", text="")

            row = col.row(align=True)

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

        col = layout.column(align=True)
        self.draw_name(context, col)

        col.separator()

        self.draw_general(context, col)

        layout.prop(self, "Align_Roll", text="Recalculate Bone Roll")
        layout.prop(self, "Connect_Bone", text="Connect Bone")

        if Utility_Functions.draw_subpanel(self, self.SHOW_Individual_Deform_Bone, "SHOW_Individual_Deform_Bone", "Bone Settings", layout):

            if self.Generate_Deform:
                layout.prop(self, "Deform_Prefix", text="Prefix")
            layout.prop(self, "Generate_Deform", text="Individual Deform Bone")

            layout.prop(self, "Generate_Connect", text="Sub Connect Bone")


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

        self.child_bone_pair.clear()
        self.armature_obj_pair.clear()
        self.Realign_bone_list.clear()

        mode = context.mode

        Tail_Mode = self.Tail_Mode

        selected_objects = [object for object in context.selected_objects]
        active_object = context.object

        preferences = Utility_Functions.get_addon_preferences()

        Armature_Object = self.Set_Up_Armature(context)

        context.view_layer.update()

        chain_bone = None

        if Armature_Object:

            Selected_Root = [object for object in selected_objects]

            for obj in selected_objects:

                if self.Only_Selected:
                    child_select_check = [child_obj for child_obj in obj.children if child_obj in selected_objects]
                else:
                    child_select_check = obj.children


                for child in child_select_check:
                    if child in Selected_Root:
                        Selected_Root.remove(child)

            Utility_Functions.object_switch_mode(Armature_Object, "EDIT")
            Edit_Bones = Armature_Object.data.edit_bones


            for obj in Selected_Root:

                if self.Only_Selected:
                    child_select_check = [child_obj for child_obj in obj.children if child_obj in selected_objects]
                else:
                    child_select_check = obj.children

                if len(child_select_check) > 0:


                    child_center = Armature_Object.matrix_world.inverted() @ mathutils.Vector(Utility_Functions.midpoint([c.matrix_world @ Utility_Functions.get_object_center(c, self.Position_Mode) for c in child_select_check], "BOUNDING_BOX"))

                    chain_head = Utility_Functions.get_object_center(obj, self.Position_Mode)
                    chain_tail = child_center
                    chain_head = Armature_Object.matrix_world.inverted() @ obj.matrix_world @ chain_head
                    # chain_tail = Armature_Object.matrix_world.inverted() @ chain_tail

                    chain_name = self.Chain_Prefix + obj.name

                    chain_bone = Utility_Functions.create_bone(Armature_Object, chain_name, chain_head, chain_tail, self.Use_Deform, Flip_Bone = False)

                    self.Realign_bone_list.append(chain_bone.name)

                    if not self.Generate_Deform:
                        if self.Bind_Mode == "WEIGHT":

                            if obj.type == "MESH":

                                indices = [vertex.index for vertex in obj.data.vertices]

                                if indices is not None:
                                    New_Vertex_Group = Utility_Functions.Add_Weight(obj, chain_bone.name, indices)

                                if self.BIND_Add_Armature_Modifier:
                                    New_Modifier = Utility_Functions.Add_Armature_Modifier(obj, Armature_Object)

                                if self.BIND_Parent_To_Armature:

                                    self.armature_obj_pair.append(obj)

                            else:

                                if self.BIND_Parent_Non_Mesh:

                                    self.child_bone_pair.append({"child": obj, "bone_name": chain_bone.name})

                        if self.Bind_Mode == "PARENT_BONE":

                            self.child_bone_pair.append({"child": obj, "bone_name": chain_bone.name})





                    for child in child_select_check:

                        Connect_bone = None

                        if len(child_select_check) > 1 and self.Generate_Connect:

                            Connect_head = chain_tail
                            Connect_tail_local = Utility_Functions.get_object_center(child, self.Position_Mode)
                            Connect_tail = Armature_Object.matrix_world.inverted() @ child.matrix_world @ Connect_tail_local

                            Connect_name = self.Chain_Prefix + obj.name + "_" + child.name

                            Connect_bone = Utility_Functions.create_bone(Armature_Object, Connect_name, Connect_head, Connect_tail, self.Use_Deform, Flip_Bone = False)
                            self.Realign_bone_list.append(Connect_bone.name)
                            Connect_bone.parent = chain_bone

                            if self.Connect_Bone:
                                if Connect_bone.head == chain_bone.tail:
                                    Connect_bone.use_connect = True

                        if Connect_bone:
                            Pass_Chain_Bone = Connect_bone
                        else:
                            Pass_Chain_Bone = chain_bone

                        self.recursive_object_find(context, Armature_Object, child, Pass_Chain_Bone, selected_objects, Tail_Mode)


                # else:
                if len(child_select_check) == 0 or self.Generate_Deform:

                    tip_head_local = Utility_Functions.get_object_center(obj, self.Position_Mode)

                    tip_head = Armature_Object.matrix_world.inverted() @ obj.matrix_world @ tip_head_local


                    if Tail_Mode == "OFFSET_GLOBAL":
                        tip_tail = Armature_Object.matrix_world.inverted() @ ((obj.matrix_world @ tip_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

                    if Tail_Mode == "OFFSET_LOCAL":
                        tip_tail = Armature_Object.matrix_world.inverted() @ obj.matrix_world @ self.Offset_From_Head(context, tip_head_local)


                    if self.Generate_Deform:
                        tip_name = self.Deform_Prefix + obj.name
                    else:
                        tip_name = self.Chain_Prefix + obj.name

                    tip_bone = Utility_Functions.create_bone(Armature_Object, tip_name, tip_head, tip_tail, self.Use_Deform, Flip_Bone = False)
                    self.Realign_bone_list.append(tip_bone.name)
                    tip_bone.parent = chain_bone

                    if self.Connect_Bone:
                        if chain_bone and tip_bone:
                            if tip_bone.head == chain_bone.tail:
                                tip_bone.use_connect = True

                    if self.Bind_Mode == "WEIGHT":

                        if obj.type == "MESH":

                            indices = [vertex.index for vertex in obj.data.vertices]

                            if indices is not None:
                                New_Vertex_Group = Utility_Functions.Add_Weight(obj, tip_bone.name, indices)

                            if self.BIND_Add_Armature_Modifier:
                                New_Modifier = Utility_Functions.Add_Armature_Modifier(obj, Armature_Object)

                            if self.BIND_Parent_To_Armature:
                                self.armature_obj_pair.append(obj)

                        else:

                            if self.BIND_Parent_Non_Mesh:

                                self.child_bone_pair.append({"child": obj, "bone_name": tip_bone.name})

                    if self.Bind_Mode == "PARENT_BONE":

                        self.child_bone_pair.append({"child": obj, "bone_name": tip_bone.name})






            Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")



            for cbp in self.child_bone_pair:

                bone_name = cbp["bone_name"]
                child = cbp["child"]

                if child:
                    mw = child.matrix_world.copy()

                    if not child == Armature_Object:

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

        if self.Align_Roll:
            Utility_Functions.object_switch_mode(Armature_Object, "EDIT")
            for bone_name in self.Realign_bone_list:

                bone = Armature_Object.data.edit_bones.get(bone_name)
                if bone:
                    bone.align_roll((0, 0, 1))

            Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")

        self.child_bone_pair.clear()
        self.armature_obj_pair.clear()
        self.Realign_bone_list.clear()


        return {'FINISHED'}

    def recursive_object_find(self, context, Armature_Object, object, prev_chain_bone, selected, Tail_Mode):

        preferences = Utility_Functions.get_addon_preferences()
        edit_bones = Armature_Object.data.edit_bones

        chain_bone = None


        if self.Only_Selected:
            child_select_check = [child_obj for child_obj in object.children if child_obj in selected]
        else:
            child_select_check = object.children


        if len(child_select_check) > 0:


            child_center = Armature_Object.matrix_world.inverted() @ mathutils.Vector(Utility_Functions.midpoint([c.matrix_world @ Utility_Functions.get_object_center(c, self.Position_Mode) for c in child_select_check], "BOUNDING_BOX"))

            chain_head = Utility_Functions.get_object_center(object, self.Position_Mode)
            chain_tail = child_center
            chain_head = Armature_Object.matrix_world.inverted() @ object.matrix_world @ chain_head
            # chain_tail = Armature_Object.matrix_world.inverted() @ chain_tail

            chain_name = self.Chain_Prefix + object.name

            chain_bone = Utility_Functions.create_bone(Armature_Object, chain_name, chain_head, chain_tail, self.Use_Deform, Flip_Bone = False)
            self.Realign_bone_list.append(chain_bone.name)
            Connect_bone = None

            # if len(child_select_check) == 1:
            #
            #     if chain_tail and chain_head:
            #
            #         chain_bone = Utility_Functions.create_bone(Armature_Object, chain_name, chain_head, chain_tail, self.Use_Deform, Flip_Bone = False)


            chain_bone.parent = prev_chain_bone

            if self.Connect_Bone:
                if chain_bone.head == prev_chain_bone.tail:
                    chain_bone.use_connect = True


            if not self.Generate_Deform:
                if self.Bind_Mode == "WEIGHT":

                    if object.type == "MESH":


                        indices = [vertex.index for vertex in object.data.vertices]

                        if indices is not None:
                            New_Vertex_Group = Utility_Functions.Add_Weight(object, chain_bone.name, indices)

                        if self.BIND_Add_Armature_Modifier:
                            New_Modifier = Utility_Functions.Add_Armature_Modifier(object, Armature_Object)

                        if self.BIND_Parent_To_Armature:
                            self.armature_obj_pair.append(object)

                    else:

                        if self.BIND_Parent_Non_Mesh:

                            self.child_bone_pair.append({"child": object, "bone_name": chain_bone.name})

                if self.Bind_Mode == "PARENT_BONE":

                    self.child_bone_pair.append({"child": object, "bone_name": chain_bone.name})

            for child in child_select_check:
                if child in selected and object in selected:



                    Connect_bone = None

                    if len(child_select_check) > 1 and self.Generate_Connect:

                        Connect_head = chain_tail
                        Connect_tail_local = Utility_Functions.get_object_center(child, self.Position_Mode)
                        Connect_tail = Armature_Object.matrix_world.inverted() @ child.matrix_world @ Connect_tail_local

                        Connect_name = self.Chain_Prefix + object.name + "_" + child.name

                        Connect_bone = Utility_Functions.create_bone(Armature_Object, Connect_name, Connect_head, Connect_tail, self.Use_Deform, Flip_Bone = False)
                        self.Realign_bone_list.append(Connect_bone.name)
                        Connect_bone.parent = chain_bone

                        if self.Connect_Bone:
                            if Connect_bone.head == chain_bone.tail:
                                Connect_bone.use_connect = True


                    if Connect_bone:
                        Pass_Chain_Bone = Connect_bone
                    else:
                        Pass_Chain_Bone = chain_bone

                    self.recursive_object_find(context, Armature_Object, child, Pass_Chain_Bone, selected, Tail_Mode)

        # else:
        if len(child_select_check) == 0 or self.Generate_Deform:

            tip_head_local = Utility_Functions.get_object_center(object, self.Position_Mode)

            tip_head = Armature_Object.matrix_world.inverted() @ object.matrix_world @ tip_head_local


            if Tail_Mode == "OFFSET_GLOBAL":
                tip_tail = Armature_Object.matrix_world.inverted() @ ((object.matrix_world @ tip_head_local) + mathutils.Vector(self.Tail_Offset_Amount))

            if Tail_Mode == "OFFSET_LOCAL":
                tip_tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ self.Offset_From_Head(context, tip_head_local)

            # tip_name = self.Chain_Prefix + object.name

            if self.Generate_Deform:
                tip_name = self.Deform_Prefix + object.name
            else:
                tip_name = self.Chain_Prefix + object.name


            tip_bone = Utility_Functions.create_bone(Armature_Object, tip_name, tip_head, tip_tail, self.Use_Deform, Flip_Bone = False)
            self.Realign_bone_list.append(tip_bone.name)
            # tip_bone.parent = prev_chain_bone

            if chain_bone:
                tip_bone.parent = chain_bone

                if self.Connect_Bone:
                    if tip_bone.head == chain_bone.tail:
                        tip_bone.use_connect = True


            else:
                tip_bone.parent = prev_chain_bone

                if self.Connect_Bone:
                    if tip_bone.head == prev_chain_bone.tail:
                        tip_bone.use_connect = True


            if self.Bind_Mode == "WEIGHT":

                if object.type == "MESH":

                    indices = [vertex.index for vertex in object.data.vertices]

                    if indices is not None:
                        New_Vertex_Group = Utility_Functions.Add_Weight(object, tip_bone.name, indices)

                    if self.BIND_Add_Armature_Modifier:
                        New_Modifier = Utility_Functions.Add_Armature_Modifier(object, Armature_Object)

                    if self.BIND_Parent_To_Armature:

                        self.armature_obj_pair.append(object)

                else:

                    if self.BIND_Parent_Non_Mesh:

                        self.child_bone_pair.append({"child": object, "bone_name": tip_bone.name})

            if self.Bind_Mode == "PARENT_BONE":

                self.child_bone_pair.append({"child": object, "bone_name": tip_bone.name})








classes = [BONERA_OP_Create_Bone_Chain_From_Object_Hierarchy]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
