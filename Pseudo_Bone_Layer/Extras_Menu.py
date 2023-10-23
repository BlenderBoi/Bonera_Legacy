import bpy
from Bonera_Toolkit import Utility_Functions

class BONERA_MT_PBL_Icon_Expose_Menu(bpy.types.Menu):
    bl_label = "Pseudo Bone Layer Icon Expose Menu"
    bl_idname = "BONERA_MT_pbl_icon_expose"

    def draw(self, context):

        scn = context.scene
        obj = context.object
        layout = self.layout

        preferences = Utility_Functions.get_addon_preferences()

        options = [
            ("ICON_PBL_Key_Bone", "Key Bone", "KEYTYPE_KEYFRAME_VEC"),                      #
            ("ICON_PBL_Mute_Constraint", "Mute Constraint", "CONSTRAINT"),
            ("ICON_PBL_Solo", "Solo", "SOLO_ON"),
            ("ICON_PBL_Visibility", "Hide or Unhide", "HIDE_OFF"),                      #
            ("ICON_PBL_Select", "Select", "RESTRICT_SELECT_OFF"),                      #
            ("ICON_PBL_Deform", "Set Deform", "OUTLINER_OB_ARMATURE"),                      #
            ("ICON_PBL_Remove", "Remove", "X"),                      #
        ]


        for option in options:

            if option[2]:

                row = layout.row(align=True)
                row.label(text="", icon=option[2])
                row.prop(preferences, option[0], text=option[1], icon=option[2])
                row.separator()
            else:
                row = layout.row(align=True)
                row.label(text="", icon="DOT")
                row.prop(preferences, option[0], text=option[1])
                row.separator()



classes = [BONERA_MT_PBL_Icon_Expose_Menu]



def register():

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
