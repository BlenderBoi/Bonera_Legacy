import bpy
from .. import Utility_Functions
import mathutils

ENUM_Choice_Armature = [("NEW","New","New"),("EXIST","Existing","Existing")]

def ENUM_Tail_Mode(self, context):

    ENUM_Items = [("OFFSET_GLOBAL","Offset Tail from Head (Global)","Offset Tail from Head (Global)"),("OFFSET_LOCAL","Offset Tail from Head (Local)","Offset Tail from Head (Local)")]

    return ENUM_Items

def ENUM_Bind_Mode(self, context):

    ENUM_Items =  [("NONE","None","None"),("WEIGHT","Weight","Weight")]

    return ENUM_Items

ENUM_Position_Mode = [("CENTER","Geometry","Geometry"),("BOUNDING_BOX","Bounding Box","Bounding Box")]

# ENUM_Position_Mode = [("WEIGHT","Weight","Weight"), ("CENTER","Geometry","Geometry"),("BOUNDING_BOX","Bounding Box","Bounding Box")]


def Create_Armature(name):

    armature = bpy.data.armatures.new(name)
    object = bpy.data.objects.new(name, armature)
    bpy.context.collection.objects.link(object)

    return object


class BONERA_OP_Create_Bone_From_Vertex_Group(bpy.types.Operator):
    """Create Bone from Vertex Group
    Mesh Object Only"""
    bl_idname = "bonera.create_bone_from_vertex_group"
    bl_label = "Create Bone from Vertex Group"
    bl_options = {'REGISTER', 'UNDO'}

    Vertex_Group: bpy.props.StringProperty()
    Use_All: bpy.props.BoolProperty(default=True)
    Use_Deform: bpy.props.BoolProperty(default=True)

    SHOW_Armature: bpy.props.BoolProperty(default=False)

    New_Armature_Name: bpy.props.StringProperty(default="Armature")
    Choice_Armature: bpy.props.EnumProperty(default="NEW", items=ENUM_Choice_Armature)

    Armature_Update: bpy.props.BoolProperty(default=False)




    SHOW_Weight_Option: bpy.props.BoolProperty(default=False)

    BIND_Add_Armature_Modifier: bpy.props.BoolProperty(default=True)
    BIND_Parent_To_Armature: bpy.props.BoolProperty(default=False)

    SHOW_Tail: bpy.props.BoolProperty(default=False)

    Tail_Mode: bpy.props.EnumProperty(items=ENUM_Tail_Mode)
    Tail_Offset_Amount: bpy.props.FloatVectorProperty(default=(0, 0, 0.5))

    Position_Mode: bpy.props.EnumProperty(items=ENUM_Position_Mode)


    @classmethod
    def poll(cls, context):
        object = context.object
        if object:
            if object.type == "MESH":
                return True

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

    def draw_weight_options(self, context, layout):

        if not context.mode in ["EDIT_ARMATURE", "POSE"]:

            if Utility_Functions.draw_subpanel(self, self.SHOW_Weight_Option, "SHOW_Weight_Option", "Bind Option", layout):

                col = layout.column(align=True)


                col.prop(self, "BIND_Add_Armature_Modifier", text="Add Armature Modifier")
                col.prop(self, "BIND_Parent_To_Armature", text="Parent To Armature")

    def draw_tail(self, context, layout):

        if Utility_Functions.draw_subpanel(self, self.SHOW_Tail, "SHOW_Tail", "Tail Option", layout):

            col = layout.column(align=True)
            col.prop(self, "Tail_Mode", text="")

            row = col.row(align=True)

            row.prop(self, "Tail_Offset_Amount", text="")

    def draw(self, context):

        obj = context.object

        layout = self.layout

        if not self.Use_All:
            layout.prop_search(self, "Vertex_Group", obj, "vertex_groups", text="")

        layout.prop(self, "Use_All", text="All Vertex Groups")

        layout.prop(self, "Position_Mode", text="Head")

        layout.prop(self, "Use_Deform", text="Use Deform")

        self.draw_weight_options(context, layout)
        self.draw_tail(context, layout)

        self.draw_armature(context, layout)


    def Offset_From_Head(self, context, head_position):

        Offset_Amount = self.Tail_Offset_Amount

        return head_position + mathutils.Vector(Offset_Amount)

    def Update_Armature(self, context, armature_object):

        if armature_object:

            scn = context.scene

            if self.Armature_Update:
                scn.Bonera_Scene_Data.Bone_From_Selection_Armature = armature_object
                self.Choice_Armature = "EXIST"

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

    def Set_Up_Armature(self, context):

        Armature_Object = self.Armature_Check(context)
        self.Update_Armature(context, Armature_Object)

        return Armature_Object

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):


        object = context.object
        Tail_Mode = self.Tail_Mode
        Armature_Object = self.Set_Up_Armature(context)
        context.view_layer.update()


        mode = context.mode

        Utility_Functions.object_switch_mode(Armature_Object, "EDIT")
        Edit_Bones = Armature_Object.data.edit_bones

        for vertex_group in object.vertex_groups:

            vg_vertices = []

            if self.Use_All:

                for v in object.data.vertices:
                    for vg in v.groups:
                        if vertex_group.index == vg.group:

                            vg_vertices.append(v.co)

            else:

                if vertex_group.name == self.Vertex_Group:

                    for v in object.data.vertices:
                        for vg in v.groups:
                            if vertex_group.index == vg.group:

                                vg_vertices.append(v.co)

                                # if self.Bind_Mode == "WEIGHT":
                                #     vg_vertices.append(v.co + (vg.weight * v.co))
                                # else:
                                #     vg_vertices.append(v.co)

            midpoint = Utility_Functions.midpoint(vg_vertices, self.Position_Mode)

            if midpoint:

                Bone_Head_Local = midpoint
                Bone_Head = Armature_Object.matrix_world.inverted() @ object.matrix_world @ Bone_Head_Local
                Bone_Name = vertex_group.name

                if Tail_Mode == "OFFSET_GLOBAL":
                    Bone_Tail = Armature_Object.matrix_world.inverted() @ ((object.matrix_world @ Bone_Head_Local) + mathutils.Vector(self.Tail_Offset_Amount))

                if Tail_Mode == "OFFSET_LOCAL":
                    Bone_Tail = Armature_Object.matrix_world.inverted() @ object.matrix_world @ self.Offset_From_Head(context, Bone_Head_Local)

                Bone = Utility_Functions.create_bone(Armature_Object, Bone_Name, Bone_Head, Bone_Tail, self.Use_Deform, Flip_Bone = False)

                if object.type == "MESH":

                    if self.BIND_Add_Armature_Modifier:
                        New_Modifier = Utility_Functions.Add_Armature_Modifier(object, Armature_Object)

                    if self.BIND_Parent_To_Armature:

                        mw = object.matrix_world.copy()
                        object.parent = Armature_Object
                        object.matrix_world = mw

        Utility_Functions.object_switch_mode(Armature_Object, "OBJECT")

        if mode == "OBJECT":
            Utility_Functions.object_switch_mode(object, "OBJECT")
        if mode == "EDIT_MESH":
            Utility_Functions.object_switch_mode(object, "EDIT")

        context.view_layer.objects.active = object




        return {'FINISHED'}






classes = [BONERA_OP_Create_Bone_From_Vertex_Group]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
