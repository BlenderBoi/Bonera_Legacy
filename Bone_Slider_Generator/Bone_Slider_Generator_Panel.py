import bpy
from Bonera_Toolkit import Utility_Functions
import bmesh

#Grid Setting

def WGT_Collection(object, collection_name = "WGT_BUIG"):

    if bpy.data.collections.get(collection_name):
        tiles_collection =  bpy.data.collections[collection_name]
    else:
        tiles_collection =  bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(tiles_collection)

    if tiles_collection:
        tiles_collection.objects.link(object)

    tiles_collection.hide_viewport = True
    tiles_collection.hide_render = True

    return tiles_collection

def WGT_Slider_Create(thickness=0.05, height = 0.2):

    name = "WGT_BUIG_Slider"
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)
    # bpy.context.collection.objects.link(object)
    WGT_Collection(object)

    bm = bmesh.new()
    bm.from_mesh(mesh)

    points = []
    points.append((-thickness, -height, 0.0000))
    points.append((thickness, -height, 0.0000))
    points.append((thickness, height, 0.0000))
    points.append((-thickness, height, 0.0000))

    for point in points:
        vertex = bm.verts.new(point)

    bm.faces.new(bm.verts)

    bm.to_mesh(mesh)
    bm.free()

    return object

def WGT_Bar_Create(thickness = 0.2):

    name = "WGT_BUIG_Bar"
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)
    WGT_Collection(object)
    # bpy.context.collection.objects.link(object)

    bm = bmesh.new()
    bm.from_mesh(mesh)

    points = []
    points.append((0.0000, -thickness, 0.0000))
    points.append((2.0000, -thickness, 0.0000))
    points.append((2.0000, thickness, 0.0000))
    points.append((0.0000, thickness, 0.0000))

    for point in points:
        vertex = bm.verts.new(point)

    bm.faces.new(bm.verts)

    bm.to_mesh(mesh)
    bm.free()

    return object

ENUM_Driven_Property_Type = []

ENUM_Driven_Property_Type.append(("CUSTOM_PROPERTY", "Custom Property", "Custom Property"))
ENUM_Driven_Property_Type.append(("SHAPEKEY", "Shapekey", "Shapekey"))
ENUM_Driven_Property_Type.append(("TRANSFORM", "Transform", "Transform"))
ENUM_Driven_Property_Type.append(("PATH", "Path", "Path"))

def lock_bone(bone, state=True):

    bone.lock_location[0] = state
    bone.lock_location[1] = state
    bone.lock_location[2] = state

    bone.lock_rotation_w = state
    bone.lock_rotation[0] = state
    bone.lock_rotation[1] = state
    bone.lock_rotation[2] = state

    bone.lock_scale[0] = state
    bone.lock_scale[1] = state
    bone.lock_scale[2] = state

def Create_Text_Object(name, text):
    font_curve = bpy.data.curves.new(type="FONT", name=name)
    font_curve.body = text
    font_obj = bpy.data.objects.new(name=name, object_data=font_curve)
    WGT_Collection(font_obj)
    # bpy.context.scene.collection.objects.link(font_obj)

    return font_obj

class BONERA_UL_BUIG(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        layout.prop(item, "label", text="", emboss=False)




class BONERA_ARMATURE_PT_BONE_UI_Generator(bpy.types.Panel):

    bl_label = "Bone UI Slider Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Bonera"
    bl_options =  {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):

        preferences = Utility_Functions.get_addon_preferences()
        if preferences.SECTION_Bonera_UI_Bone_Generator:
            return True

    def draw(self, context):

        scn = context.scene
        layout = self.layout


        armature_objects = [object.type for object in context.view_layer.objects]
        if "ARMATURE" in armature_objects:

            object = context.object
            if object:

                if object.type == "ARMATURE":

                    bonera_data = scn.Bonera_Scene_Data
                    active_index = bonera_data.BUIG_Index

                    row = layout.row(align=False)

                    row.template_list("BONERA_UL_BUIG", "", bonera_data, "BUIG", bonera_data, "BUIG_Index")

                    col = row.column(align=True)

                    operator = col.operator("bonera.buig_list_operator", text="", icon="ADD")
                    operator.operation = "ADD"
                    operator.index = active_index

                    operator = col.operator("bonera.buig_list_operator", text="", icon="REMOVE")
                    operator.operation = "REMOVE"
                    operator.index = active_index

                    col.separator()

                    operator = col.operator("bonera.buig_list_operator", text="", icon="TRIA_UP")
                    operator.operation = "UP"
                    operator.index = active_index

                    operator = col.operator("bonera.buig_list_operator", text="", icon="TRIA_DOWN")
                    operator.operation = "DOWN"
                    operator.index = active_index

                    layout.operator("bonera.generate_driver_bone_from_list", text="Generate Blank Slider")


            else:
                layout.label(text="Select an Armature", icon="INFO")
        else:
            layout.label(text="Select an Armature", icon="INFO")



class BONERA_BUIG_Load_Shapekey(bpy.types.Operator):

    bl_idname = "bonera.buig_load_shapekey"
    bl_label = "Load Shapekey"

    def execute(self, context):
        pass

class BONERA_BUIG_Generate_UI_Slider_Bone(bpy.types.Operator):
    """Generate UI Bone from List"""
    bl_idname = "bonera.buig_generate"
    bl_label = "Generate"
    bl_options = {'UNDO', 'REGISTER'}

    column: bpy.props.IntProperty(default=3)
    margin: bpy.props.FloatProperty(default=1.3)
    slider_offset: bpy.props.FloatProperty(default=0.3)
    slider_bar_thickness: bpy.props.FloatProperty(default=0.04)

    new_armature: bpy.props.BoolProperty()
    armauture: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        if context.mode in ["POSE", "EDIT_ARMATURE"]:
            return True

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        scn = context.scene

        bonera_data = scn.Bonera_Scene_Data
        items = bonera_data.BUIG

        object = context.object
        bones = object.data.edit_bones

        column = self.column
        margin = self.margin
        slider_offset = self.slider_offset

        counter_x = -1
        counter_y = 0

        WGT_Bar = WGT_Bar_Create(thickness = self.slider_bar_thickness)
        WGT_Slider = WGT_Slider_Create(thickness=0.1, height = 0.2)

        for item in items:

            counter_x += 1

            if counter_x >= column:
                counter_x = 0
                counter_y -= 1

            bpy.ops.object.mode_set(mode='EDIT', toggle=False)

            name = "WGT_BUIG_" + item.label
            text = item.label
            Text_Object = Create_Text_Object(name, text)

            LABEL_bone_name = "UI_label_" + item.label
            LABEL_bone = bones.new(LABEL_bone_name)
            LABEL_bone.head.x = counter_x * margin
            LABEL_bone.head.y = counter_y * margin
            LABEL_bone.tail = LABEL_bone.head
            LABEL_bone.tail.x += 0.5
            LABEL_bone_find = LABEL_bone.name

            SLIDER_bone_name = "UI_slider_" + item.label
            SLIDER_bone = bones.new(LABEL_bone_name)
            SLIDER_bone.head.x = counter_x * margin - slider_offset
            SLIDER_bone.head.y = (counter_y * margin)
            SLIDER_bone.tail = SLIDER_bone.head
            SLIDER_bone.tail.x += 0.5
            SLIDER_bone_find = SLIDER_bone.name

            BAR_bone_name = "UI_bar_" + item.label
            BAR_bone = bones.new(BAR_bone_name)
            BAR_bone.head.x = counter_x * margin - slider_offset
            BAR_bone.head.y = (counter_y * margin)
            BAR_bone.tail = BAR_bone.head
            BAR_bone.tail.x += 0.5
            BAR_bone_find = BAR_bone.name

            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

            LABEL_pose_bone = object.pose.bones.get(LABEL_bone_find)
            LABEL_pose_bone.custom_shape = Text_Object
            LABEL_pose_bone.custom_shape_scale = 0.5
            lock_bone(LABEL_pose_bone)


            BAR_pose_bone = object.pose.bones.get(BAR_bone_find)
            BAR_pose_bone.custom_shape = WGT_Bar
            lock_bone(BAR_pose_bone)

            SLIDER_pose_bone = object.pose.bones.get(SLIDER_bone_find)
            SLIDER_pose_bone.custom_shape = WGT_Slider
            constraint = SLIDER_pose_bone.constraints.new(type="LIMIT_LOCATION")

            constraint.use_max_x = True
            constraint.use_max_y = True
            constraint.use_max_z = True

            constraint.max_x = 1

            constraint.use_min_x = True
            constraint.use_min_y = True
            constraint.use_min_z = True

            constraint.owner_space = "LOCAL"
            constraint.use_transform_limit = True

            constraint = SLIDER_pose_bone.constraints.new(type="LIMIT_ROTATION")

            constraint.use_limit_x = True
            constraint.use_limit_y = True
            constraint.use_limit_z = True

            constraint.owner_space = "LOCAL"
            constraint.use_transform_limit = True

            constraint = SLIDER_pose_bone.constraints.new(type="LIMIT_SCALE")

            constraint.use_max_x = True
            constraint.use_max_y = True
            constraint.use_max_z = True

            constraint.max_x = 1
            constraint.max_y = 1
            constraint.max_z = 1

            constraint.use_min_x = True
            constraint.use_min_y = True
            constraint.use_min_z = True

            constraint.min_x = 1
            constraint.min_y = 1
            constraint.min_z = 1

            constraint.use_transform_limit = True
            constraint.owner_space = "LOCAL"

        return {'FINISHED'}


ENUM_list_operation = [("ADD","Add","Add"),("REMOVE","Remove","Remove"),("UP","Up","Up"),("DOWN","Down","Down")]


class BONERA_BUIG_List_Operator(bpy.types.Operator):

    bl_idname = "bonera.buig_list_operator"
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

        self.name = "Parameter_" + str(len(bonera_data.BUIG))

        if self.operation in ["ADD"]:
            return context.window_manager.invoke_props_dialog(self)
        else:
            return self.execute(context)


    def execute(self, context):

        # obj = context.object
        # data = obj.data

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        item_list = bonera_data.BUIG
        item_index = bonera_data.BUIG_Index

        if self.operation == "REMOVE":
            item_list.remove(self.index)

            if len(item_list) == bonera_data.BUIG_Index:
                bonera_data.BUIG_Index = len(item_list) - 1
            Utility_Functions.update_UI()
            return {'FINISHED'}

        if self.operation == "ADD":

            item = item_list.add()
            item.label = self.name
            bonera_data.BUIG_Index = len(item_list) - 1
            Utility_Functions.update_UI()
            return {'FINISHED'}

        if self.operation == "UP":
            if item_index >= 1:
                item_list.move(item_index, item_index-1)
                bonera_data.BUIG_Index -= 1
                return {'FINISHED'}

        if self.operation == "DOWN":
            if len(item_list)-1 > item_index:
                item_list.move(item_index, item_index+1)
                bonera_data.BUIG_Index += 1
                return {'FINISHED'}

        Utility_Functions.update_UI()
        return {'FINISHED'}



classes=[BONERA_ARMATURE_PT_BONE_UI_Generator, BONERA_UL_BUIG, BONERA_BUIG_List_Operator]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # bpy.types.Scene.BUIG_Armature_Picker = bpy.props.PointerProperty(type=bpy.types.Object, poll=Armature_Picker_Poll)
    # bpy.types.Scene.BUIG = bpy.props.CollectionProperty(type=BONERA_BUIG)
    # bpy.types.Scene.BUIG_Index = bpy.props.IntProperty()


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    # del bpy.types.Scene.BUIG
    # del bpy.types.Scene.BUIG_Index

if __name__ == "__main__":
    register()
