import bpy
from math import radians
from mathutils import Vector
import bmesh
import idprop
import rna_prop_ui

def Create_Text_Object(name, text, width):
    font_curve = bpy.data.curves.new(type="FONT", name=name)
    font_curve.body = text
    font_obj = bpy.data.objects.new(name=name, object_data=font_curve)
    WGT_Collection(font_obj)

    font_curve.overflow = "SCALE"
    font_curve.text_boxes[0].width = width
    # bpy.context.scene.collection.objects.link(font_obj)
    font_obj.show_bounds=True
    font_obj.hide_render = True

    return font_obj

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

def WGT_Collection(object, collection_name = "WGT_Collection"):

    if bpy.data.collections.get(collection_name):
        tiles_collection =  bpy.data.collections[collection_name]
    else:
        tiles_collection =  bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(tiles_collection)

    if tiles_collection:
        tiles_collection.objects.link(object)

    # tiles_collection.hide_viewport = True
    tiles_collection.hide_render = True

    return tiles_collection

def WGT_Slider_Create(thickness=0.05, height = 0.2):

    name = "WGT_Slider"
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
    object.hide_render= True
    return object

def WGT_Bar_Create(thickness = 0.2, min=0.0, max=1.0):

    name = "WGT_Bar"
    mesh = bpy.data.meshes.new(name)
    object = bpy.data.objects.new(name, mesh)
    WGT_Collection(object)
    # bpy.context.collection.objects.link(object)

    bm = bmesh.new()
    bm.from_mesh(mesh)

    points = []

    points.append((min, 0.0000, -thickness))
    points.append((min, max, -thickness))
    points.append((min, max, thickness))
    points.append((min, 0.0000, thickness))

    for point in points:
        vertex = bm.verts.new(point)

    bm.faces.new(bm.verts)

    bm.to_mesh(mesh)
    bm.free()
    object.hide_render= True
    return object

def Create_Armature(context, name):

    Armature = bpy.data.armatures.new(name)
    Armature_Object = bpy.data.objects.new(name, Armature)
    context.collection.objects.link(Armature_Object)

    return Armature_Object

def ENUM_Source_Mode(self, context):

    items = []

    object = context.view_layer.objects.get(self.Source_Object)

    if object:
        if object.type == "MESH":
            item = ("SHAPEKEYS","Shapekeys","Shapekeys")
            items.append(item)

        item = ("CUSTOM_PROPERTIES","Custom Properties","Custom Properties")
        items.append(item)


    if len(items) == 0:
        item = ("NONE","None","None")
        items.append(item)

    return items

def ENUM_Properties_Mode(self, context):

    items = [("OBJECT","Object","Object"),("DATA","Data","data")]

    object = context.view_layer.objects.get(self.Source_Object)

    if object:
        if object.type == "ARMATURE":
            item = ("BONE","Pose Bone","Bone")
            items.append(item)

    return items


ENUM_Data_Path = [("LOC_X","Location X","Location X"),("LOC_Y","Location Y","Location Y"),("LOC_Z","Location Z","Location Z"), ("ROT_X","Rotation X","Rotation X"),("ROT_Y","Rotation Y","Location Y"),("ROT_Z","Rotation Z","Location Z"), ("SCALE_X","Scale X","Scale X"),("SCALE_Y","Scale Y","Scale Y"),("SCALE_Z","Scale Z","Scale Z")]
ENUM_Transform_Space = [("WORLD_SPACE","World Space","World Space"),("TRANSFORM_SPACE","Transform_Space","Transfom Space"),("LOCAL_SPACE","Local Space","Local Space")]
ENUM_Layout_Mode =  [("COLUMN","Max Column","Column"),("ROW","Max Row","Row")]
ENUM_Limit_Location_Axis = [("X", "X", "x"),("Y","Y","y"),("Z","Z","z")]

class BONERA_OT_Generate_Driver_Bone(bpy.types.Operator):
    """Generate Driver Bone"""
    bl_idname = "bonera.generate_driver_bone"
    bl_label = "Generate Driver Bone"
    bl_options = {'UNDO', 'REGISTER'}

    Source_Mode: bpy.props.EnumProperty(items=ENUM_Source_Mode)
    Source_Object: bpy.props.StringProperty()
    Source_SubTarget: bpy.props.StringProperty()


    Data_Path: bpy.props.EnumProperty(items=ENUM_Data_Path)
    Transform_Space: bpy.props.EnumProperty(default="LOCAL_SPACE", items=ENUM_Transform_Space)
    New_Armature: bpy.props.BoolProperty(default=True)
    Armature_Name: bpy.props.StringProperty(default="Armature")
    Armature_Object: bpy.props.StringProperty()

    Use_Degree: bpy.props.BoolProperty(default=False)

    Limit_Max: bpy.props.FloatProperty(default=1.0)
    Limit_Min: bpy.props.FloatProperty(default=0.0)

    Use_Limit_Constraint: bpy.props.BoolProperty(default=True)
    Use_Lock_Transform: bpy.props.BoolProperty(default=True)

    Map_Value: bpy.props.BoolProperty(default=True)

    Properties_Mode: bpy.props.EnumProperty(items=ENUM_Properties_Mode)

    show_UI_Setup: bpy.props.BoolProperty()

    Generate_UI_Bone: bpy.props.BoolProperty(default=True)

    Generate_Label: bpy.props.BoolProperty(default=True)
    Label_Offset: bpy.props.FloatVectorProperty(default=(0, 0, 0.5))
    Generate_Bar: bpy.props.BoolProperty(default=True)
    Generate_Slider_Shape: bpy.props.BoolProperty(default=True)
    Bar_Thickness: bpy.props.FloatProperty(default=0.03)

    layout_mode: bpy.props.EnumProperty(default="COLUMN", items=ENUM_Layout_Mode)
    layout_align_amount: bpy.props.IntProperty(default=5, min=1)
    layout_offset_horizontal: bpy.props.FloatProperty(default=0.5)
    layout_offset_vertical: bpy.props.FloatProperty(default=1)

    SHOW_Drivers: bpy.props.BoolProperty(default=False)
    SHOW_Limits: bpy.props.BoolProperty(default=False)
    SHOW_Layout: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        bonera_data = scn.Bonera_Scene_Data

        layout.label(text="Armature")

        if self.New_Armature:
            layout.prop(self, "Armature_Name", text="")
        else:
            layout.prop(bonera_data, "BUIG_Armature_Picker", text="")

        layout.prop(self, "New_Armature", text="New Armature")

        layout.separator()


        col = layout.column(align=True)

        col.label(text="Driven Properties")

        col.prop(self, "Source_Mode", text="")

        if self.Source_Mode == "CUSTOM_PROPERTIES":
            row = col.row(align=True)
            row.prop(self, "Properties_Mode", text="Properties", expand=True)

        col.separator()
        col.separator()
        col.prop_search(self, "Source_Object", context.view_layer, "objects", text="Object")

        object = context.view_layer.objects.get(self.Source_Object)

        if object:
            if object.type == "ARMATURE":
                if self.Properties_Mode == "BONE":
                    col.prop_search(self, "Source_SubTarget", object.data, "bones", text="Bone")


        layout.separator()
        layout.separator()


        if self.SHOW_Layout:
            ICON_SHOW = "TRIA_DOWN"
        else:
            ICON_SHOW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_Layout", text="Layout Option", emboss=False, icon=ICON_SHOW)

        if self.SHOW_Layout:

            layout.separator()

            col = layout.column(align=True)

            col.prop(self, "layout_mode", text="")
            if self.layout_mode == "COLUMN":
                col.prop(self, "layout_align_amount", text="Max Column")
            if self.layout_mode == "ROW":
                col.prop(self, "layout_align_amount", text="Max Row")

            col.label(text="Layout Offset")
            row = col.row(align=True)
            row.prop(self, "layout_offset_horizontal", text="Vertical")
            row.prop(self, "layout_offset_vertical", text="Horizontal")


        if self.SHOW_Drivers:
            ICON_SHOW = "TRIA_DOWN"
        else:
            ICON_SHOW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_Drivers", text="Drivers Option", emboss=False, icon=ICON_SHOW)

        if self.SHOW_Drivers:

            layout.separator()

            col = layout.column(align=True)

            col.prop(self, "Data_Path", text="Driver")
            col.prop(self, "Transform_Space", text="Space")


            layout.separator()


        if self.SHOW_Limits:
            ICON_SHOW = "TRIA_DOWN"
        else:
            ICON_SHOW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_Limits", text="Limits Option", emboss=False, icon=ICON_SHOW)

        if self.SHOW_Limits:

            layout.separator()
            layout.separator()

            col = layout.column(align=True)

            row = col.row(align=True)
            row.prop(self, "Use_Limit_Constraint", text="Limit Constraints")
            col.prop(self, "Use_Lock_Transform", text="Lock Transform", icon="LOCKED")

            if self.Use_Limit_Constraint:


                row = col.row(align=True)
                row.prop(self, "Limit_Min", text="Limit Min")
                row.prop(self, "Limit_Max", text="Limit Max")
                col.prop(self, "Map_Value", text="Map Value to Min Max")


            layout.separator()




        layout.separator()
        layout.separator()

        if self.Data_Path == "LOC_X":

            layout.prop(self, "Generate_UI_Bone", text="Generate UI Bone")

            if self.Generate_UI_Bone:

                if self.show_UI_Setup:
                    SHOWICON = "TRIA_DOWN"
                else:
                    SHOWICON = "TRIA_RIGHT"

                row = layout.row(align=True)
                row.alignment = "LEFT"
                row.prop(self, "show_UI_Setup", text="UI Settings", emboss=False, icon=SHOWICON)

                if self.show_UI_Setup:

                    box = layout.box()

                    box.prop(self, "Generate_Label", text="Label Bone")

                    if self.Generate_Label:
                        row = box.row()
                        row.prop(self, "Label_Offset", text="")
                    box.prop(self, "Generate_Bar", text="Slider Bar")

                    if self.Generate_Bar:
                        box.prop(self, "Bar_Thickness", text="")

                    box.prop(self, "Generate_Slider_Shape", text="Slider Shape")

    def invoke(self, context, event):


        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        scn = context.scene
        bonera_data = scn.Bonera_Scene_Data

        if not self.Data_Path == "LOC_X":
            self.Generate_UI_Bone = False

        object = context.view_layer.objects.get(self.Source_Object)

        if not self.New_Armature:
            if bonera_data.BUIG_Armature_Picker:
                self.Armature_Object = bonera_data.BUIG_Armature_Picker.name

        armature_object = None
        WGT_SLIDER = None
        WGT_BAR = None

        if object:

            if self.Generate_UI_Bone:

                if self.Generate_Bar:
                    WGT_BAR = WGT_Bar_Create(thickness = self.Bar_Thickness, min=self.Limit_Min, max=self.Limit_Max)

                if self.Generate_Slider_Shape:
                    WGT_SLIDER = WGT_Slider_Create(thickness=0.08, height = 0.2)


            if not self.New_Armature:
                armature_object = context.view_layer.objects.get(self.Armature_Object)

            if not armature_object:
                armature_object = Create_Armature(context, self.Armature_Name)

            if object and armature_object:

                bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
                context.view_layer.objects.active = armature_object
                bpy.ops.object.mode_set(mode="EDIT", toggle=False)

                edit_bones = armature_object.data.edit_bones


                layout_mode = self.layout_mode
                layout_max = self.layout_align_amount -1

                position_x = 0
                position_y = 0

                if self.Source_Mode == "CUSTOM_PROPERTIES":

                    bone_prop_pair = []
                    if self.Properties_Mode == "OBJECT":
                        Source = object

                    if self.Properties_Mode == "DATA":
                        Source = object.data

                    if self.Properties_Mode == "BONE":
                        Source = object.pose.bones.get(self.Source_SubTarget)



                    if Source:

                        src_type = type(Source)
                        type_dict = dir(src_type)
                        for k, v in Source.items():

                            if k in type_dict:

                                tmp = getattr(src_type, k)

                                if isinstance(tmp, bpy.props._PropertyDeferred):
                                    continue

                            if not isinstance(v, (int, float)):
                                continue

                            skip = False


                            #Check if Property have Drivers

                            if Source.id_data.animation_data:

                                for d in Source.id_data.animation_data.drivers:

                                    source_path = ""

                                    if self.Properties_Mode == "BONE":
                                        if type(Source) == bpy.types.PoseBone:
                                            source_path = Source.path_from_id()
                                    else:
                                        source_path = ""

                                    if d.data_path == source_path + rna_prop_ui.rna_idprop_quote_path(k):
                                        skip = True
                                        break



                            if not skip:
                                # bone = edit_bones.new(Source.name + "_" + property)
                                bone = edit_bones.new(Source.name + "_" + k)

                                bone.head = armature_object.matrix_world.inverted() @ context.scene.cursor.location
                                bone.head.x += position_x
                                bone.head.z += position_y


                                bone.tail = bone.head
                                bone.tail.z += 1

                                Label_Bone = None
                                Bar_Bone = None

                                Bar_Bone_Name = None
                                Label_Bone_Name = None
                                text_object = None

                                if self.Generate_UI_Bone:

                                    if self.Generate_Bar:
                                        # Bar_Bone = edit_bones.new("UI_BAR_" + Source.name + "_" + property)
                                        Bar_Bone = edit_bones.new("UI_BAR_" + Source.name + "_" + k)
                                        Bar_Bone.head = bone.head
                                        Bar_Bone.head.x += self.Limit_Min

                                        Bar_Bone.tail = bone.head
                                        Bar_Bone.tail.x += self.Limit_Max

                                        Bar_Bone_Name = Bar_Bone.name

                                    if self.Generate_Label:

                                        # Label_Bone = edit_bones.new("UI_LABEL_" + Source.name + "_" + property)
                                        Label_Bone = edit_bones.new("UI_LABEL_" + Source.name + "_" + k)
                                        Label_Bone.head = Vector(bone.head) + Vector(self.Label_Offset)

                                        Label_Bone.tail = Label_Bone.head
                                        Label_Bone.tail.z += 1

                                        Label_Bone_Name = Label_Bone.name

                                        # text_object = Create_Text_Object("WGT_" + Label_Bone_Name, property, abs(self.Limit_Min) + self.Limit_Max)
                                        text_object = Create_Text_Object("WGT_" + Label_Bone_Name, k, abs(self.Limit_Min) + self.Limit_Max)
                                        # text_object.matrix_world = object.matrix_world @ Label_Bone.matrix
                                        text_object.matrix_world = armature_object.matrix_world @ Label_Bone.matrix

                                        if Bar_Bone:
                                            Bar_Bone.parent = Label_Bone
                                            bone.parent = Label_Bone


                                # data_path = '["{}"]'.format(property)
                                # data_path = '["{}"]'.format(k)
                                data_path = rna_prop_ui.rna_idprop_quote_path(k)
                                # data_path = property

                                bone_prop_pair.append([bone.name, Source, data_path, Label_Bone_Name, Bar_Bone_Name, text_object])

                                if self.layout_mode == "ROW":
                                    if position_x == layout_max * (abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal):
                                        position_x = 0
                                        position_y -=  self.layout_offset_vertical
                                    else:
                                        position_x +=  abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal

                                if self.layout_mode == "COLUMN":

                                    if position_y == -layout_max * self.layout_offset_vertical:
                                        position_y = 0
                                        position_x +=  abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal
                                    else:
                                        position_y -=  self.layout_offset_vertical

                if self.Source_Mode == "SHAPEKEYS":

                    bone_prop_pair = []

                    if object.type == "MESH":

                        if object.data.shape_keys:
                            for shapekey in object.data.shape_keys.key_blocks:

                                skip = False

                                if object.data.shape_keys.animation_data:
                                    for d in object.data.shape_keys.animation_data.drivers:

                                        if d.data_path == shapekey.path_from_id("value"):

                                            skip = True

                                if not skip:
                                    if not shapekey.name == "Basis":

                                        bone = edit_bones.new(shapekey.name)

                                        bone.head = armature_object.matrix_world.inverted() @ context.scene.cursor.location
                                        bone.head.x += position_x
                                        bone.head.z += position_y

                                        bone.tail = bone.head
                                        bone.tail.z += 1

                                        Label_Bone = None
                                        Bar_Bone = None

                                        Bar_Bone_Name = None
                                        Label_Bone_Name = None
                                        text_object = None

                                        if self.Generate_UI_Bone:

                                            if self.Generate_Bar:
                                                Bar_Bone = edit_bones.new("UI_BAR_" + shapekey.name)
                                                Bar_Bone.head = bone.head
                                                Bar_Bone.head.x += self.Limit_Min

                                                Bar_Bone.tail = bone.head
                                                Bar_Bone.tail.x += self.Limit_Max

                                                # Bar_Bone.hide_select = True

                                                Bar_Bone_Name = Bar_Bone.name

                                            if self.Generate_Label:

                                                Label_Bone = edit_bones.new("UI_LABEL_" + shapekey.name)
                                                Label_Bone.head = Vector(bone.head) + Vector(self.Label_Offset)

                                                Label_Bone.tail = Label_Bone.head
                                                Label_Bone.tail.z += 1

                                                Label_Bone_Name = Label_Bone.name

                                                text_object = Create_Text_Object("WGT_" + Label_Bone_Name, shapekey.name, abs(self.Limit_Min) + self.Limit_Max)
                                                # text_object.matrix_world = Label_Bone.matrix
                                                text_object.matrix_world = armature_object.matrix_world @ Label_Bone.matrix


                                                # Label_Bone.hide_select = False
                                                if Bar_Bone:
                                                    Bar_Bone.parent = Label_Bone
                                                    bone.parent = Label_Bone



                                        data_path = "value"

                                        bone_prop_pair.append([bone.name, shapekey, "value", Label_Bone_Name, Bar_Bone_Name, text_object])
                                        # position_x +=  abs(self.Limit_Min) + self.Limit_Max + 0.5
                                        # position_y +=  1


                                        if self.layout_mode == "ROW":
                                            if position_x == layout_max * (abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal):
                                                position_x = 0
                                                position_y -=  self.layout_offset_vertical
                                            else:
                                                position_x +=  abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal

                                        if self.layout_mode == "COLUMN":

                                            if position_y == -layout_max * self.layout_offset_vertical:
                                                position_y = 0
                                                position_x +=  abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal
                                            else:
                                                position_y -=  self.layout_offset_vertical




                bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

                for pair in bone_prop_pair:

                    bone = armature_object.pose.bones.get(pair[0])
                    BAR_BONE = None
                    LABEL_BONE = None


                    if self.Generate_UI_Bone:

                        if pair[3]:
                            LABEL_BONE = armature_object.pose.bones.get(pair[3])
                            if LABEL_BONE:

                                text_object = pair[5]
                                LABEL_BONE.custom_shape = text_object

                            lock_bone(LABEL_BONE, state=True)
                        if pair[4]:
                            BAR_BONE = armature_object.pose.bones.get(pair[4])
                            lock_bone(BAR_BONE, state=True)

                        if BAR_BONE:
                            BAR_BONE.custom_shape = WGT_BAR
                            BAR_BONE.use_custom_shape_bone_size = False

                        if WGT_SLIDER:
                            bone.custom_shape = WGT_SLIDER

                    #Fix
                    driver = pair[1].driver_add(pair[2]).driver


                    if self.Use_Lock_Transform:
                        bone.lock_location[0] = True
                        bone.lock_location[1] = True
                        bone.lock_location[2] = True

                        bone.lock_rotation_w = True
                        bone.lock_rotation[0] = True
                        bone.lock_rotation[1] = True
                        bone.lock_rotation[2] = True

                        bone.lock_scale[0] = True
                        bone.lock_scale[1] = True
                        bone.lock_scale[2] = True

                        if self.Data_Path == "ROT_X":
                            bone.lock_rotation_w = False
                            bone.lock_rotation[0] = False

                        if self.Data_Path == "ROT_Y":
                            bone.lock_rotation_w = False
                            bone.lock_rotation[1] = False

                        if self.Data_Path == "ROT_Z":
                            bone.lock_rotation_w = False
                            bone.lock_rotation[2] = False

                        if self.Data_Path == "LOC_X":
                            bone.lock_location[0] = False

                        if self.Data_Path == "LOC_Y":
                            bone.lock_location[1] = False

                        if self.Data_Path == "LOC_Z":
                            bone.lock_location[2] = False

                        if self.Data_Path == "SCALE_X":
                            bone.lock_scale[0] = False

                        if self.Data_Path == "SCALE_Y":
                            bone.lock_scale[1] = False

                        if self.Data_Path == "SCALE_Z":
                            bone.lock_scale[2] = False


                    if driver:

                        v = driver.variables.new()
                        v.name = "value"
                        v.targets[0].id = armature_object
                        v.targets[0].bone_target = pair[0]

                        v.type = "TRANSFORMS"

                        v.targets[0].transform_space = self.Transform_Space
                        v.targets[0].transform_type = self.Data_Path


                        driver.expression = v.name

                        if self.Use_Limit_Constraint:
                            if self.Map_Value:
                                if self.Data_Path in ["ROT_X", "ROT_Y", "ROT_Z"]:
                                    driver.expression = "({expr}-{min})/({max}-{min})".format(expr = driver.expression, min = str(radians(self.Limit_Min)), max = str(radians(self.Limit_Max)))
                                else:
                                    driver.expression = "({expr}-{min})/({max}-{min})".format(expr = driver.expression, min = str(self.Limit_Min), max = str(self.Limit_Max))


                    if self.Use_Limit_Constraint:
                        if self.Data_Path in ["LOC_X", "LOC_Y", "LOC_Z"]:
                            constraint = bone.constraints.new("LIMIT_LOCATION")

                        if self.Data_Path in ["ROT_X", "ROT_Y", "ROT_Z"]:
                            constraint = bone.constraints.new("LIMIT_ROTATION")

                        if self.Data_Path in ["SCALE_X", "SCALE_Y", "SCALE_Z"]:
                            constraint = bone.constraints.new("LIMIT_SCALE")


                        constraint.use_transform_limit = True
                        constraint.owner_space = "LOCAL"

                        if self.Data_Path in ["LOC_X", "SCALE_X"]:
                            constraint.use_min_x = True
                            constraint.use_max_x = True

                            constraint.min_x =self.Limit_Min
                            constraint.max_x =self.Limit_Max

                        if self.Data_Path in ["LOC_Y", "SCALE_Y"]:
                            constraint.use_min_y = True
                            constraint.use_max_y = True

                            constraint.min_y =self.Limit_Min
                            constraint.max_y =self.Limit_Max

                        if self.Data_Path in ["LOC_Z", "SCALE_Z"]:
                            constraint.use_min_z = True
                            constraint.use_max_z = True

                            constraint.min_z =self.Limit_Min
                            constraint.max_z =self.Limit_Max

                        if self.Data_Path == "ROT_X":
                            constraint.use_limit_x = True


                            constraint.min_x = radians(self.Limit_Min)
                            constraint.max_x = radians(self.Limit_Max)


                        if self.Data_Path == "ROT_Y":
                            constraint.use_limit_y = True


                            constraint.min_y =radians(self.Limit_Min)
                            constraint.max_y =radians(self.Limit_Max)


                        if self.Data_Path == "ROT_Z":
                            constraint.use_limit_z = True


                            constraint.min_z =radians(self.Limit_Min)
                            constraint.max_z =radians(self.Limit_Max)



        if WGT_SLIDER:
            WGT_SLIDER.hide_viewport = True
            WGT_SLIDER.hide_render = True
        if WGT_BAR:
            WGT_BAR.hide_viewport = True
            WGT_BAR.hide_render = True


        return {'FINISHED'}

class BONERA_OT_Generate_Driver_Bone_From_List(bpy.types.Operator):
    """Generate Driver Bones from List
    Edit Armature | Pose"""
    bl_idname = "bonera.generate_driver_bone_from_list"
    bl_label = "Generate"
    bl_options = {'UNDO', "REGISTER"}


    Use_Degree: bpy.props.BoolProperty(default=False)

    Limit_Max: bpy.props.FloatProperty(default=1.0)
    Limit_Min: bpy.props.FloatProperty(default=0.0)

    Use_Limit_Constraint: bpy.props.BoolProperty(default=True)
    Use_Lock_Transform: bpy.props.BoolProperty(default=True)

    Map_Value: bpy.props.BoolProperty(default=True)

    Properties_Mode: bpy.props.EnumProperty(items=ENUM_Properties_Mode)

    show_UI_Setup: bpy.props.BoolProperty()

    Generate_Label: bpy.props.BoolProperty(default=True)
    Label_Offset: bpy.props.FloatVectorProperty(default=(0, 0, 0.5))
    Generate_Bar: bpy.props.BoolProperty(default=True)
    Generate_Slider_Shape: bpy.props.BoolProperty(default=True)
    Bar_Thickness: bpy.props.FloatProperty(default=0.03)

    layout_mode: bpy.props.EnumProperty(default="COLUMN", items=ENUM_Layout_Mode)
    layout_align_amount: bpy.props.IntProperty(default=5, min=1)
    layout_offset_horizontal: bpy.props.FloatProperty(default=0.5)
    layout_offset_vertical: bpy.props.FloatProperty(default=1)

    extras: bpy.props.BoolProperty(default=False)

    SHOW_Drivers: bpy.props.BoolProperty(default=False)
    SHOW_Limits: bpy.props.BoolProperty(default=False)
    SHOW_Layout: bpy.props.BoolProperty(default=False)

    @classmethod
    def poll(cls, context):
        object = context.object

        armature_objects = [object.type for object in context.view_layer.objects]
        if "ARMATURE" in armature_objects:
            return True
        # if object.type == "ARMATURE":
        #     return True

    def draw(self, context):

        layout = self.layout
        scn= context.scene

        bonera_data = scn.Bonera_Scene_Data


        if self.SHOW_Layout:
            ICON_SHOW = "TRIA_DOWN"
        else:
            ICON_SHOW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_Layout", text="Layout Option", emboss=False, icon=ICON_SHOW)

        if self.SHOW_Layout:

            col = layout.column(align=True)

            col.prop(self, "layout_mode", text="")
            if self.layout_mode == "COLUMN":
                col.prop(self, "layout_align_amount", text="Max Column")
            if self.layout_mode == "ROW":
                col.prop(self, "layout_align_amount", text="Max Row")

            col.label(text="Layout Offset")
            row = col.row(align=True)
            row.prop(self, "layout_offset_horizontal", text="Vertical")
            row.prop(self, "layout_offset_vertical", text="Horizontal")





        if self.SHOW_Limits:
            ICON_SHOW = "TRIA_DOWN"
        else:
            ICON_SHOW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_Limits", text="Limits Option", emboss=False, icon=ICON_SHOW)

        if self.SHOW_Limits:

            layout.separator()

            col = layout.column(align=True)

            row = col.row(align=True)
            row.prop(self, "Use_Limit_Constraint", text="Limit Constraints")
            col.prop(self, "Use_Lock_Transform", text="Lock Transform", icon="LOCKED")

            if self.Use_Limit_Constraint:


                row = col.row(align=True)
                row.prop(self, "Limit_Min", text="Limit Min")
                row.prop(self, "Limit_Max", text="Limit Max")
                # col.prop(self, "Map_Value", text="Map Value to Min Max")


            layout.separator()






        if self.show_UI_Setup:
            SHOWICON = "TRIA_DOWN"
        else:
            SHOWICON = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "show_UI_Setup", text="UI Settings", emboss=False, icon=SHOWICON)

        if self.show_UI_Setup:

            box = layout.box()

            box.prop(self, "Generate_Label", text="Label Bone")

            if self.Generate_Label:
                row = box.row()
                row.prop(self, "Label_Offset", text="")
            box.prop(self, "Generate_Bar", text="Slider Bar")

            if self.Generate_Bar:
                box.prop(self, "Bar_Thickness", text="")

            box.prop(self, "Generate_Slider_Shape", text="Slider Shape")



    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):


        armature_objects = [object for object in context.view_layer.objects if object.type == "ARMATURE"]

        for object in armature_objects:
            if object.type == "ARMATURE":

                armature_object = object

                WGT_SLIDER = None
                WGT_BAR = None

                scn = context.scene
                bonera_data = scn.Bonera_Scene_Data

                item_list = bonera_data.BUIG
                item_index = bonera_data.BUIG_Index

                if self.Generate_Bar:
                    WGT_BAR = WGT_Bar_Create(thickness = self.Bar_Thickness, min=self.Limit_Min, max=self.Limit_Max)

                if self.Generate_Slider_Shape:
                    WGT_SLIDER = WGT_Slider_Create(thickness=0.08, height = 0.2)

                if armature_object.type == "ARMATURE":

                    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
                    context.view_layer.objects.active = armature_object
                    bpy.ops.object.mode_set(mode="EDIT", toggle=False)

                    edit_bones = armature_object.data.edit_bones


                    layout_mode = self.layout_mode
                    layout_max = self.layout_align_amount -1

                    position_x = 0
                    position_y = 0


                    bone_prop_pair = []



                    for item in item_list:

                        item_name = item.label

                        bone = edit_bones.new(item_name)

                        bone.head = armature_object.matrix_world.inverted() @ context.scene.cursor.location
                        bone.head.x += position_x
                        bone.head.z += position_y

                        bone.tail = bone.head
                        bone.tail.z += 1

                        Label_Bone = None
                        Bar_Bone = None

                        Bar_Bone_Name = None
                        Label_Bone_Name = None
                        text_object = None


                        if self.Generate_Bar:
                            Bar_Bone = edit_bones.new("UI_BAR_" + item_name)
                            Bar_Bone.head = bone.head
                            Bar_Bone.head.x += self.Limit_Min

                            Bar_Bone.tail = bone.head
                            Bar_Bone.tail.x += self.Limit_Max

                            # Bar_Bone.hide_select = True

                            Bar_Bone_Name = Bar_Bone.name

                        if self.Generate_Label:

                            Label_Bone = edit_bones.new("UI_LABEL_" + item_name)
                            Label_Bone.head = Vector(bone.head) + Vector(self.Label_Offset)

                            Label_Bone.tail = Label_Bone.head
                            Label_Bone.tail.z += 1

                            Label_Bone_Name = Label_Bone.name

                            text_object = Create_Text_Object("WGT_" + Label_Bone_Name, item_name, abs(self.Limit_Min) + self.Limit_Max)
                            text_object.matrix_world = armature_object.matrix_world @ Label_Bone.matrix
                            text_object.parent = armature_object
                            text_object.matrix_parent_inverse = armature_object.matrix_world.inverted()
                            # Label_Bone.hide_select = False
                            if Bar_Bone:
                                Bar_Bone.parent = Label_Bone
                                bone.parent = Label_Bone

                            driver_object = armature_object
                            data_path = "value"


                            bone_prop_pair.append([bone.name, driver_object, data_path, Label_Bone_Name, Bar_Bone_Name, text_object])



                            if self.layout_mode == "ROW":
                                if position_x == layout_max * (abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal):
                                    position_x = 0
                                    position_y -=  self.layout_offset_vertical
                                else:
                                    position_x +=  abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal

                            if self.layout_mode == "COLUMN":

                                if position_y == -layout_max * self.layout_offset_vertical:
                                    position_y = 0
                                    position_x +=  abs(self.Limit_Min) + self.Limit_Max + self.layout_offset_horizontal
                                else:
                                    position_y -=  self.layout_offset_vertical




                    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

                    for pair in bone_prop_pair:

                        bone = armature_object.pose.bones.get(pair[0])
                        BAR_BONE = None
                        LABEL_BONE = None

                        if pair[3]:
                            LABEL_BONE = armature_object.pose.bones.get(pair[3])
                            if LABEL_BONE:

                                text_object = pair[5]
                                LABEL_BONE.custom_shape = text_object

                            lock_bone(LABEL_BONE, state=True)
                        if pair[4]:
                            BAR_BONE = armature_object.pose.bones.get(pair[4])
                            lock_bone(BAR_BONE, state=True)

                        if BAR_BONE:
                            BAR_BONE.custom_shape = WGT_BAR
                            BAR_BONE.use_custom_shape_bone_size = False

                        if WGT_SLIDER:
                            bone.custom_shape = WGT_SLIDER

                        if self.Use_Lock_Transform:
                            bone.lock_location[0] = True
                            bone.lock_location[1] = True
                            bone.lock_location[2] = True

                            bone.lock_rotation_w = True
                            bone.lock_rotation[0] = True
                            bone.lock_rotation[1] = True
                            bone.lock_rotation[2] = True

                            bone.lock_scale[0] = True
                            bone.lock_scale[1] = True
                            bone.lock_scale[2] = True

                            bone.lock_location[0] = False

                        if self.Use_Limit_Constraint:

                            constraint = bone.constraints.new("LIMIT_LOCATION")
                            constraint.use_transform_limit = True
                            constraint.owner_space = "LOCAL"


                            constraint.use_min_x = True
                            constraint.use_max_x = True

                            constraint.min_x =self.Limit_Min
                            constraint.max_x =self.Limit_Max




                if WGT_SLIDER:
                    WGT_SLIDER.hide_viewport = True
                    WGT_SLIDER.hide_render = True
                if WGT_BAR:
                    WGT_BAR.hide_viewport = True
                    WGT_BAR.hide_render = True

        return {'FINISHED'}

def ENUM_Custom_Property_Picker(self, context):

    items = []
    source = None

    object = context.view_layer.objects.get(self.Source_Object)

    if self.Properties_Mode == "OBJECT":
        source = object
    if self.Properties_Mode == "DATA":
        source = object.data
    if self.Properties_Mode == "BONE":
        if self.Source_SubTarget:
            source = object.pose.bones.get(self.Source_SubTarget)



    if source:
        src_type = type(source)
        type_dict = dir(src_type)



        for k, v in source.items():



            if k in type_dict:

                tmp = getattr(src_type, k)

                if isinstance(tmp, bpy.props._PropertyDeferred):
                    continue

            if not isinstance(v, (int, float)):
                continue


            item = (k, k, k)
            items.append(item)

        # if source.get("_RNA_UI"):
        #     for prop in source["_RNA_UI"]:
        #         item = (prop, prop, prop)
        #         items.append(item)

    if len(items) == 0:
        items = [("NONE","None","None")]


    return items

class BONERA_OT_Create_Single_Driver_Bone(bpy.types.Operator):
    """Create Single Driver Bone
    Edit Armature Only"""
    bl_idname = "bonera.create_single_driver_bone"
    bl_label = "Create Single Driver Bone"
    bl_options = {'UNDO'}

    Source_Mode: bpy.props.EnumProperty(items=ENUM_Source_Mode)
    Source_Object: bpy.props.StringProperty()
    Source_SubTarget: bpy.props.StringProperty()

    Data_Path: bpy.props.EnumProperty(items=ENUM_Data_Path)
    Transform_Space: bpy.props.EnumProperty(default="LOCAL_SPACE", items=ENUM_Transform_Space)
    New_Armature: bpy.props.BoolProperty(default=True)
    Armature_Name: bpy.props.StringProperty(default="Armature")
    Armature_Object: bpy.props.StringProperty()

    Use_Degree: bpy.props.BoolProperty(default=False)

    Limit_Max: bpy.props.FloatProperty(default=1.0)
    Limit_Min: bpy.props.FloatProperty(default=0.0)

    Use_Limit_Constraint: bpy.props.BoolProperty(default=True)
    Use_Lock_Transform: bpy.props.BoolProperty(default=True)

    Map_Value: bpy.props.BoolProperty(default=True)

    Properties_Mode: bpy.props.EnumProperty(items=ENUM_Properties_Mode)

    show_UI_Setup: bpy.props.BoolProperty()

    Generate_UI_Bone: bpy.props.BoolProperty(default=True)

    Generate_Label: bpy.props.BoolProperty(default=True)
    Label_Offset: bpy.props.FloatVectorProperty(default=(0, 0, 0.5))
    Generate_Bar: bpy.props.BoolProperty(default=True)
    Generate_Slider_Shape: bpy.props.BoolProperty(default=True)
    Bar_Thickness: bpy.props.FloatProperty(default=0.03)

    Driven_Property: bpy.props.StringProperty()
    Custom_Property_Picker: bpy.props.EnumProperty(items=ENUM_Custom_Property_Picker)

    SHOW_Drivers: bpy.props.BoolProperty(default=False)
    SHOW_Limits: bpy.props.BoolProperty(default=False)



    @classmethod
    def poll(cls, context):

        if context.mode:
            if context.mode == "EDIT_ARMATURE":
                return True

    def draw(self, context):

        layout = self.layout
        object = context.view_layer.objects.get(self.Source_Object)

        col = layout.column(align=True)

        col.label(text="Driven Property: ")

        col.prop(self, "Source_Mode", text="")
        if self.Source_Mode == "CUSTOM_PROPERTIES":
            row = col.row(align=True)
            row.prop(self, "Properties_Mode", text="Properties", expand=True)

        object = context.view_layer.objects.get(self.Source_Object)
        col.separator()
        col.separator()
        col.prop_search(self, "Source_Object", context.view_layer, "objects", text="Object")
        if object:
            if object.type == "ARMATURE":
                if self.Properties_Mode == "BONE":
                    col.prop_search(self, "Source_SubTarget", object.data, "bones", text="Bone")

        if self.Source_Mode == "SHAPEKEYS":
            if object.type == "MESH":
                if object.data.shape_keys:
                    col.prop_search(self, "Driven_Property", object.data.shape_keys, "key_blocks",text="Shapekeys")

        if self.Source_Mode == "CUSTOM_PROPERTIES":

            col.prop(self, "Custom_Property_Picker", text="Properties")

        layout.separator()
        layout.separator()


        if self.SHOW_Drivers:
            ICON_SHOW = "TRIA_DOWN"
        else:
            ICON_SHOW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_Drivers", text="Driver Option", emboss=False, icon=ICON_SHOW)

        if self.SHOW_Drivers:


            col = layout.column(align=True)
            col.prop(self, "Data_Path", text="Driver")
            col.prop(self, "Transform_Space", text="Space")

        if self.SHOW_Limits:
            ICON_SHOW = "TRIA_DOWN"
        else:
            ICON_SHOW = "TRIA_RIGHT"

        row = layout.row(align=True)
        row.alignment = "LEFT"
        row.prop(self, "SHOW_Limits", text="Limits Option", emboss=False, icon=ICON_SHOW)

        if self.SHOW_Limits:

            layout.prop(self, "Use_Limit_Constraint", text="Limit Constraints")

            col = layout.column(align=True)

            col.prop(self, "Use_Lock_Transform", text="Lock Transform", icon="LOCKED")

            if self.Use_Limit_Constraint:


                row = col.row(align=True)
                row.prop(self, "Limit_Min", text="Limit Min")
                row.prop(self, "Limit_Max", text="Limit Max")
                col.prop(self, "Map_Value", text="Map Value to Min Max")

        layout.separator()
        layout.separator()

        if self.Data_Path == "LOC_X":
            layout.prop(self, "Generate_UI_Bone", text="Generate UI Bone")

            if self.Generate_UI_Bone:

                if self.show_UI_Setup:
                    SHOWICON = "TRIA_DOWN"
                else:
                    SHOWICON = "TRIA_RIGHT"

                row = layout.row(align=True)
                row.alignment = "LEFT"
                row.prop(self, "show_UI_Setup", text="UI Settings", emboss=False, icon=SHOWICON)

                if self.show_UI_Setup:

                    box = layout.box()

                    box.prop(self, "Generate_Label", text="Label Bone")

                    if self.Generate_Label:
                        row = box.row()
                        row.prop(self, "Label_Offset", text="")
                    box.prop(self, "Generate_Bar", text="Slider Bar")

                    if self.Generate_Bar:
                        box.prop(self, "Bar_Thickness", text="")

                    box.prop(self, "Generate_Slider_Shape", text="Slider Shape")

    def invoke(self, context, event):

        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        if not self.Data_Path == "LOC_X":
            self.Generate_UI_Bone = False

        object = context.view_layer.objects.get(self.Source_Object)
        armature_object = context.object

        Hide_Widgets = []

        WGT_SLIDER = None
        WGT_BAR = None


        if object:

            if self.Generate_UI_Bone:
                if self.Generate_Bar:
                    WGT_BAR = WGT_Bar_Create(thickness = self.Bar_Thickness, min=self.Limit_Min, max=self.Limit_Max)
                    Hide_Widgets.append(WGT_BAR)

                if self.Generate_Slider_Shape:
                    WGT_SLIDER = WGT_Slider_Create(thickness=0.08, height = 0.2)
                    Hide_Widgets.append(WGT_SLIDER)

            if object and armature_object:

                bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
                context.view_layer.objects.active = armature_object
                bpy.ops.object.mode_set(mode="EDIT", toggle=False)

                edit_bones = armature_object.data.edit_bones

                bone_prop_pair = []

                # position = 0
                if self.Custom_Property_Picker != "NONE":
                    if self.Source_Mode == "CUSTOM_PROPERTIES":

                        bone_prop_pair = []
                        if self.Properties_Mode == "OBJECT":
                            Source = object

                        if self.Properties_Mode == "DATA":
                            Source = object.data

                        if self.Properties_Mode == "BONE":
                            # Source = object.pose.bones.get(self.Source_SubTarget)
                            Source = object.pose.bones.get(self.Source_SubTarget)

                        if Source:


                            if Source.id_data.animation_data:
                                for d in Source.id_data.animation_data.drivers:
                                    source_path = ""

                                    if self.Properties_Mode == "BONE":
                                        if type(Source) == bpy.types.PoseBone:
                                            source_path = Source.path_from_id()
                                    else:
                                        source_path = ""

                                    if d.data_path == source_path + rna_prop_ui.rna_idprop_quote_path(self.Custom_Property_Picker):
                                        Source.id_data.animation_data.drivers.remove(d)

                                        break




                        #     property = Source.get(self.Custom_Property_Picker)
                        #
                        # if property:
                        #



                            bone = edit_bones.new(Source.name + "_" + self.Custom_Property_Picker)
                            bone.head = armature_object.matrix_world.inverted() @ context.scene.cursor.location
                            bone.tail = bone.head
                            bone.tail.z += 1

                            Label_Bone = None
                            Bar_Bone = None

                            Bar_Bone_Name = None
                            Label_Bone_Name = None
                            text_object = None

                            if self.Generate_UI_Bone:

                                if self.Generate_Bar:
                                    Bar_Bone = edit_bones.new("UI_BAR_" + Source.name + "_" + self.Custom_Property_Picker)
                                    Bar_Bone.head = bone.head
                                    Bar_Bone.head.x += self.Limit_Min

                                    Bar_Bone.tail = bone.head
                                    Bar_Bone.tail.x += self.Limit_Max

                                    Bar_Bone_Name = Bar_Bone.name

                                if self.Generate_Label:

                                    Label_Bone = edit_bones.new("UI_LABEL_" + Source.name + "_" + self.Custom_Property_Picker)
                                    Label_Bone.head = Vector(bone.head) + Vector(self.Label_Offset)

                                    Label_Bone.tail = Label_Bone.head
                                    Label_Bone.tail.z += 1

                                    Label_Bone_Name = Label_Bone.name

                                    text_object = Create_Text_Object("WGT_" + Label_Bone_Name, self.Custom_Property_Picker, abs(self.Limit_Min) + self.Limit_Max)
                                    text_object.matrix_world = armature_object.matrix_world @ Label_Bone.matrix
                                    Hide_Widgets.append(text_object)

                                    if Bar_Bone:
                                        Bar_Bone.parent = Label_Bone
                                        bone.parent = Label_Bone

                            data_path = rna_prop_ui.rna_idprop_quote_path(self.Custom_Property_Picker)
                            # data_path = '["{}"]'.format(property.name)

                            # data_path = property

                            bone_prop_pair.append([bone.name, Source, data_path, Label_Bone_Name, Bar_Bone_Name, text_object])

                            # position +=  abs(self.Limit_Min) + self.Limit_Max + 0.5


                if self.Source_Mode == "SHAPEKEYS":

                    bone_prop_pair = []

                    if object.type == "MESH":

                        if object.data.shape_keys:
                            # for shapekey in object.data.shape_keys.key_blocks:
                                # if not shapekey.name == "Basis":
                            shapekey = object.data.shape_keys.key_blocks.get(self.Driven_Property)

                            if shapekey:


                                if object.data.shape_keys:
                                    if object.data.shape_keys.animation_data:
                                        for d in object.data.shape_keys.animation_data.drivers:
                                            if d.data_path == shapekey.path_from_id("value"):

                                                object.data.shape_keys.animation_data.drivers.remove(d)
                                                break

                                bone = edit_bones.new(shapekey.name)
                                bone.head = armature_object.matrix_world.inverted() @ context.scene.cursor.location
                                bone.tail = bone.head
                                bone.tail.z += 1

                                Label_Bone = None
                                Bar_Bone = None

                                Bar_Bone_Name = None
                                Label_Bone_Name = None
                                text_object = None

                                if self.Generate_UI_Bone:

                                    if self.Generate_Bar:
                                        Bar_Bone = edit_bones.new("UI_BAR_" + shapekey.name)
                                        Bar_Bone.head = bone.head
                                        Bar_Bone.head.x += self.Limit_Min

                                        Bar_Bone.tail = bone.head
                                        Bar_Bone.tail.x += self.Limit_Max

                                        # Bar_Bone.hide_select = True

                                        Bar_Bone_Name = Bar_Bone.name

                                    if self.Generate_Label:

                                        Label_Bone = edit_bones.new("UI_LABEL_" + shapekey.name)
                                        Label_Bone.head = Vector(bone.head) + Vector(self.Label_Offset)

                                        Label_Bone.tail = Label_Bone.head
                                        Label_Bone.tail.z += 1

                                        Label_Bone_Name = Label_Bone.name

                                        text_object = Create_Text_Object("WGT_" + Label_Bone_Name, shapekey.name, abs(self.Limit_Min) + self.Limit_Max)
                                        text_object.matrix_world = armature_object.matrix_world @ Label_Bone.matrix

                                        Hide_Widgets.append(text_object)
                                        # Label_Bone.hide_select = False
                                        if Bar_Bone:
                                            Bar_Bone.parent = Label_Bone
                                            bone.parent = Label_Bone



                                data_path = "value"

                                bone_prop_pair.append([bone.name, shapekey, "value", Label_Bone_Name, Bar_Bone_Name, text_object])
                                # position +=  abs(self.Limit_Min) + self.Limit_Max + 0.5

                bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

                for pair in bone_prop_pair:

                    bone = armature_object.pose.bones.get(pair[0])
                    BAR_BONE = None
                    LABEL_BONE = None


                    if self.Generate_UI_Bone:

                        if pair[3]:
                            LABEL_BONE = armature_object.pose.bones.get(pair[3])
                            if LABEL_BONE:

                                text_object = pair[5]
                                LABEL_BONE.custom_shape = text_object

                            # lock_bone(LABEL_BONE, state=True)
                        if pair[4]:
                            BAR_BONE = armature_object.pose.bones.get(pair[4])
                            lock_bone(BAR_BONE, state=True)

                        if BAR_BONE:
                            BAR_BONE.custom_shape = WGT_BAR
                            BAR_BONE.use_custom_shape_bone_size = False

                        if WGT_SLIDER:
                            bone.custom_shape = WGT_SLIDER

                    driver = pair[1].driver_add(pair[2]).driver


                    if self.Use_Lock_Transform:
                        bone.lock_location[0] = True
                        bone.lock_location[1] = True
                        bone.lock_location[2] = True

                        bone.lock_rotation_w = True
                        bone.lock_rotation[0] = True
                        bone.lock_rotation[1] = True
                        bone.lock_rotation[2] = True

                        bone.lock_scale[0] = True
                        bone.lock_scale[1] = True
                        bone.lock_scale[2] = True

                        if self.Data_Path == "ROT_X":
                            bone.lock_rotation_w = False
                            bone.lock_rotation[0] = False

                        if self.Data_Path == "ROT_Y":
                            bone.lock_rotation_w = False
                            bone.lock_rotation[1] = False

                        if self.Data_Path == "ROT_Z":
                            bone.lock_rotation_w = False
                            bone.lock_rotation[2] = False

                        if self.Data_Path == "LOC_X":
                            bone.lock_location[0] = False

                        if self.Data_Path == "LOC_Y":
                            bone.lock_location[1] = False

                        if self.Data_Path == "LOC_Z":
                            bone.lock_location[2] = False

                        if self.Data_Path == "SCALE_X":
                            bone.lock_scale[0] = False

                        if self.Data_Path == "SCALE_Y":
                            bone.lock_scale[1] = False

                        if self.Data_Path == "SCALE_Z":
                            bone.lock_scale[2] = False


                    if driver:

                        v = driver.variables.new()
                        v.name = "value"
                        v.targets[0].id = armature_object
                        v.targets[0].bone_target = pair[0]

                        v.type = "TRANSFORMS"

                        v.targets[0].transform_space = self.Transform_Space
                        v.targets[0].transform_type = self.Data_Path


                        driver.expression = v.name

                        if self.Use_Limit_Constraint:
                            if self.Map_Value:
                                if self.Data_Path in ["ROT_X", "ROT_Y", "ROT_Z"]:
                                    driver.expression = "({expr}-{min})/({max}-{min})".format(expr = driver.expression, min = str(radians(self.Limit_Min)), max = str(radians(self.Limit_Max)))
                                else:
                                    driver.expression = "({expr}-{min})/({max}-{min})".format(expr = driver.expression, min = str(self.Limit_Min), max = str(self.Limit_Max))


                    if self.Use_Limit_Constraint:
                        if self.Data_Path in ["LOC_X", "LOC_Y", "LOC_Z"]:
                            constraint = bone.constraints.new("LIMIT_LOCATION")

                        if self.Data_Path in ["ROT_X", "ROT_Y", "ROT_Z"]:
                            constraint = bone.constraints.new("LIMIT_ROTATION")

                        if self.Data_Path in ["SCALE_X", "SCALE_Y", "SCALE_Z"]:
                            constraint = bone.constraints.new("LIMIT_SCALE")


                        constraint.use_transform_limit = True
                        constraint.owner_space = "LOCAL"

                        if self.Data_Path in ["LOC_X", "SCALE_X"]:
                            constraint.use_min_x = True
                            constraint.use_max_x = True

                            constraint.min_x =self.Limit_Min
                            constraint.max_x =self.Limit_Max

                        if self.Data_Path in ["LOC_Y", "SCALE_Y"]:
                            constraint.use_min_y = True
                            constraint.use_max_y = True

                            constraint.min_y =self.Limit_Min
                            constraint.max_y =self.Limit_Max

                        if self.Data_Path in ["LOC_Z", "SCALE_Z"]:
                            constraint.use_min_z = True
                            constraint.use_max_z = True

                            constraint.min_z =self.Limit_Min
                            constraint.max_z =self.Limit_Max

                        if self.Data_Path == "ROT_X":
                            constraint.use_limit_x = True


                            constraint.min_x = radians(self.Limit_Min)
                            constraint.max_x = radians(self.Limit_Max)


                        if self.Data_Path == "ROT_Y":
                            constraint.use_limit_y = True


                            constraint.min_y =radians(self.Limit_Min)
                            constraint.max_y =radians(self.Limit_Max)


                        if self.Data_Path == "ROT_Z":
                            constraint.use_limit_z = True


                            constraint.min_z =radians(self.Limit_Min)
                            constraint.max_z =radians(self.Limit_Max)


        for Widget in Hide_Widgets:
            if Widget:
                Widget.hide_viewport = True

        bpy.ops.object.mode_set(mode="EDIT", toggle=False)
        return {'FINISHED'}





classes = [BONERA_OT_Generate_Driver_Bone, BONERA_OT_Create_Single_Driver_Bone, BONERA_OT_Generate_Driver_Bone_From_List]

def register():


    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
