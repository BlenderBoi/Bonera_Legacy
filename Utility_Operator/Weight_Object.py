import bpy

from Bonera_Toolkit import Utility_Functions

ENUM_Mode = [("BONE","Bone","Bone"),("NAME","Object Name","Object Name"), ("STRING", "String", "String")]

class BONERA_Weight_Object(bpy.types.Operator):
    """Create Vertex Group for Object from Bones
    Object Only"""
    bl_idname = "bonera.weight_object"
    bl_label = "Weight Object To Bones"
    bl_options = {'UNDO', 'REGISTER'}

    Mode: bpy.props.EnumProperty(items=ENUM_Mode) 
    Bone: bpy.props.StringProperty()
    Name: bpy.props.StringProperty()
    Add_Armature_Modifier: bpy.props.BoolProperty(default=False)
    Weight: bpy.props.FloatProperty(default=1.0, min=0.0)

    def invoke(self, context, event):

    

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):

        data = context.scene.Bonera_Scene_Data

        layout = self.layout
        layout.prop(self, "Mode", text="Mode", expand=True)
        layout.prop(self, "Weight", text="Weight")
        if self.Mode == "STRING":
            layout.prop(self, "Name", text="String")

        layout.prop(self, "Add_Armature_Modifier", text="Add Armature Modifier")
        
        if self.Mode == "BONE":
            layout.prop(data, "Armature_Picker", text="Armature")
            if data.Armature_Picker:
               layout.prop_search(self, "Bone", data.Armature_Picker.data, "bones", text="Bone")
        else:
            if self.Add_Armature_Modifier:
                layout.prop(data, "Armature_Picker", text="Armature")



    @classmethod
    def poll(cls, context):
        if context.mode == "OBJECT":
            return True

    def execute(self, context):

        objects = context.selected_objects

        data = context.scene.Bonera_Scene_Data

        context.view_layer.update()


        for object in objects:
            if object.type == "MESH":

                name = object.name                
                valid = False
                if self.Mode == "NAME":
                    name = object.name
                    valid = True
                if self.Mode == "STRING":
                    name = self.Name
                    valid = True
                if self.Mode == "BONE":
                    name = self.Bone
                    if data.Armature_Picker:
                        if data.Armature_Picker.type == "ARMATURE":
                            if data.Armature_Picker.data.bones.get(self.Bone):
                                valid = True

                if valid:
                    
                    group = None

                    if name:
                        group = object.vertex_groups.get(name)
                        
                    if not group:
                        group = object.vertex_groups.new(name = name)

                    vertex_indices = [vertex.index for vertex in object.data.vertices]
                    group.add( vertex_indices, self.Weight, 'REPLACE' )

                    if self.Add_Armature_Modifier:
                        if data.Armature_Picker:
                            New_Modifier = Utility_Functions.Add_Armature_Modifier(object, data.Armature_Picker)

        data.Armature_Picker = None

        return {'FINISHED'}

classes = [BONERA_Weight_Object]

def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
