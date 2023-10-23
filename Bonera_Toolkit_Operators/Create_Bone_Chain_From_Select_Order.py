
import bpy
import bmesh
import numpy
import mathutils

from .. import Utility_Functions


OPERATOR_POLL_CONTEXT = ["EDIT_MESH"]




def set_mode(obj, mode="EDIT"):
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode=mode, toggle=False)


ENUM_Choice_Armature = [("NEW","New","New"),("EXIST","Existing","Existing")]




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





class BONERA_OT_Create_Bone_Chain_From_Select_Order(bpy.types.Operator):
    """Create Bone Chain From Select Order
    Edit Mesh Only"""

    bl_idname = "bonera.create_bone_chain_from_select_order"
    bl_label = "Create Bone Chain From Select Order"
    bl_options = {'UNDO', 'REGISTER'}

    name: bpy.props.StringProperty(default="Bone")
    apply_weight: bpy.props.BoolProperty(default=True)
    preclear_weight: bpy.props.BoolProperty(default=True)

    connect_bone: bpy.props.BoolProperty(default=True)
    align_roll: bpy.props.BoolProperty(default=True)

    add_armature_modifier: bpy.props.BoolProperty(default=True)
    parent_to_armature: bpy.props.BoolProperty(default=True)


    Prefix: bpy.props.EnumProperty(items=ENUM_Prefix)
    Suffix: bpy.props.EnumProperty(items=ENUM_Suffix)

    SHOW_Armature: bpy.props.BoolProperty(default=False)
    New_Armature_Name: bpy.props.StringProperty(default="Armature")
    Choice_Armature: bpy.props.EnumProperty(default="NEW", items=ENUM_Choice_Armature)



    @classmethod
    def poll(cls, context):

        if context.mode in OPERATOR_POLL_CONTEXT:
            return True

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)




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

    def draw_name(self, context, layout):

        preferences = Utility_Functions.get_addon_preferences()

        if preferences.Enable_Affixes:
            row = layout.row(align=True)
            row.scale_x = 2
            row.prop(self, "Prefix", text="")
            row.scale_x = 6
            row.prop(self, "name", text="")
            row.scale_x = 2
            row.prop(self, "Suffix", text="")
        else:
            layout.prop(self, "name", text="Bone Name")





    def draw(self, context):

        layout = self.layout
        self.draw_name(context, layout)
        layout.label(text="Set Weight")
        layout.prop(self, "apply_weight", text="Apply Weight")

        # if self.apply_weight:
        #     layout.prop(self, "preclear_weight", text="Preclear Weight")

        layout.prop(self, "connect_bone", text="Connect Bone")

        layout.separator()
        layout.prop(self, "add_armature_modifier", text="Add Armature Modifier")

        if self.add_armature_modifier:
            layout.prop(self, "parent_to_armature", text="Parent To Armature")

        self.draw_armature(context, layout)


    def Armature_Check(self, context):

        scn = context.scene
        armature_object = None

        if self.Choice_Armature == "NEW":
            armature_object = Utility_Functions.Create_Armature(self.New_Armature_Name)
            armature_object.show_in_front = True
            return armature_object
        else:
            armature_object = scn.Bonera_Scene_Data.Bone_From_Selection_Armature
            return armature_object

        if not armature_object:
            armature_object = Utility_Functions.Create_Armature(self.New_Armature_Name)
            armature_object.show_in_front = True
            return armature_object
        else:
            if context.view_layer.objects.get(armature_object.name):
                pass
            else:
                armature_object = Utility_Functions.Create_Armature(self.New_Armature_Name)
                armature_object.show_in_front = True
                return armature_object

        context.view_layer.update()

        return armature_object

    def Update_Armature(self, context, armature_object):

        pass
        # if armature_object:
        #
        #     scn = context.scene

            # scn.Bonera_Scene_Data.Bone_From_Selection_Armature = armature_object
            # self.Choice_Armature = "EXIST"

    def Set_Up_Armature(self, context):

        Armature_Object = self.Armature_Check(context)
        self.Update_Armature(context, Armature_Object)

        return Armature_Object


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

        obj = bpy.context.object

        name = self.name

        armature = self.Set_Up_Armature(context)

        if self.Choice_Armature == "NEW":
            self.Choice_Armature = "EXIST"

            context.scene.Bonera_Scene_Data.Bone_From_Selection_Armature = armature



        preferences = Utility_Functions.get_addon_preferences()



        for obj in context.selected_editable_objects:

            if obj.type == "MESH":


                vertex_groups_create = []

                if self.add_armature_modifier:
                    Utility_Functions.Add_Armature_Modifier(obj, armature)

                    mw = obj.matrix_world.copy()

                    if self.parent_to_armature:
                        obj.parent = armature
                        obj.matrix_world = mw

                if bpy.context.mode == "EDIT_MESH":

                    me = obj.data
                    bm = bmesh.from_edit_mesh(me)

                    bm.verts.layers.deform.verify()
                    deform = bm.verts.layers.deform.active


                    set_mode(armature, mode="EDIT")

                    indices = []

                    previous_bone = None

                    for index, select_element in enumerate(bm.select_history):

                        next_index = index + 1
                        head_co = None
                        tail_co = None

                        if type(select_element) == bmesh.types.BMVert:

                            head_co = select_element.co
                            indices = [select_element.index]


                        if type(select_element) == bmesh.types.BMEdge:

                            edge_verts = [vert.co for vert in select_element.verts]
                            edge_mid = numpy.sum(edge_verts, axis=0) / len(edge_verts)

                            head_co = edge_mid

                            indices = [vert.index for vert in select_element.verts]


                        if type(select_element) == bmesh.types.BMFace:

                            head_co = select_element.calc_center_median()

                            indices = [vert.index for vert in select_element.verts]


                        if len(bm.select_history) > next_index:

                            next_select_element = bm.select_history[next_index]


                            if type(next_select_element) == bmesh.types.BMVert:

                                tail_co = next_select_element.co


                            if type(next_select_element) == bmesh.types.BMEdge:

                                edge_verts = [vert.co for vert in next_select_element.verts]
                                edge_mid = numpy.sum(edge_verts, axis=0) / len(edge_verts)

                                tail_co = edge_mid

                            if type(next_select_element) == bmesh.types.BMFace:

                                tail_co = next_select_element.calc_center_median()







                        if head_co is not None:
                        # if head_co is not None:


                            if tail_co is not None:



                                bone_name = name + str(index)

                                if preferences.Enable_Affixes:
                                    bone_name = self.Generate_Bone_Name(context, bone_name)


                                bone = armature.data.edit_bones.new(bone_name)
                                bone.head = obj.matrix_world @ armature.matrix_world.inverted() @ mathutils.Vector(head_co)
                                bone.tail = obj.matrix_world @ armature.matrix_world.inverted() @ mathutils.Vector(tail_co)

                            else:

                                bone = previous_bone



                            if bone is not None:


                                vg_create = [bone.name, indices]
                                vertex_groups_create.append(vg_create)


                                if previous_bone is not None:
                                    bone.parent = previous_bone

                                    if self.connect_bone:
                                        if previous_bone.tail == bone.head:
                                            bone.use_connect = True

                                previous_bone = bone



                    set_mode(armature, mode="OBJECT")
                    bmesh.update_edit_mesh(me, loop_triangles=True)
                    set_mode(obj, mode="OBJECT")

                    if self.apply_weight:
                        for vg_create in vertex_groups_create:

                            bone_name = vg_create[0]
                            vg_indices = vg_create[1]

                            # if self.preclear_weight:
                            # vg = obj.vertex_groups.get(bone_name)
                            # if vg is not None:
                            #     obj.vertex_groups.remove(vg)

                            New_Vertex_Group = Utility_Functions.Add_Weight(obj, bone_name, vg_indices)



                    set_mode(obj, mode="EDIT")




































        context.view_layer.update()


        return {'FINISHED'}


classes = [BONERA_OT_Create_Bone_Chain_From_Select_Order]

def register():



    for cls in classes:
        bpy.utils.register_class(cls)



def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
