import bpy
import os
import rna_keymap_ui

from .. import Utility_Functions
from .. import Pair_List_Renamer
from .. import Pseudo_Bone_Layer
from .. import Bone_Slider_Generator
from .. import Bonera_Toolkit_Operators
from .. import Hierarchy_Template
from . import Affixes_Preset_List


#---------------------ENUM AREA---------------------

ENUM_Preferences_Tabs = [("GENERAL","General","General"), ("AFFIXES","Affixes List","Affixes List"), ("BONE_SHAPE","Bone Shape","Bone Shape"),("DEFAULT_NAME","Default Name","Default Name"), ("HOTKEY", "Hotkey", "Hotkey")]


#---------------------ENUM AREA---------------------

def get_pie_menu(km, operator, menu):
    for idx, kmi in enumerate(km.keymap_items):
        if km.keymap_items.keys()[idx] == operator:
            if km.keymap_items[idx].properties.name == menu:
                return kmi
    return None


def append_panel_class(panels, cls, category, label):
    panel = cls
    item = [panel, category, label]
    panels.append(item)

    return panels



def update_panel(self, context):

    addon_preferences = Utility_Functions.get_addon_preferences()
    message = ": Updating Panel locations has failed"

    panels = []



    panel_class = Pseudo_Bone_Layer.Pseudo_Bone_Layer.BONERA_PT_Pseudo_Layer_Panel
    category = addon_preferences.PANEL_Pseudo_Bone_Layer_Category
    label = addon_preferences.PANEL_Pseudo_Bone_Layer_Label
    panels = append_panel_class(panels, panel_class, category, label)


    panel_class = Bonera_Toolkit_Operators.Bonera_Toolkit_Panel.BONERA_PT_Bonera_Toolkit_Panel
    category = addon_preferences.PANEL_Bonera_Toolkit_Category
    label = addon_preferences.PANEL_Bonera_Toolkit_Label
    panels = append_panel_class(panels, panel_class, category, label)


    panel_class = Pair_List_Renamer.Pair_List_Renamer_Panel.BONERA_PT_Pair_List_Renamer
    category = addon_preferences.PANEL_Pair_List_Renamer_Category
    label = addon_preferences.PANEL_Pair_List_Renamer_Label
    panels = append_panel_class(panels, panel_class, category, label)


    panel_class = Bone_Slider_Generator.Bone_Slider_Generator_Panel.BONERA_ARMATURE_PT_BONE_UI_Generator
    category = addon_preferences.PANEL_Bone_Slider_Generator_Category
    label = addon_preferences.PANEL_Bone_Slider_Generator_Label
    panels = append_panel_class(panels, panel_class, category, label)


    panel_class = Hierarchy_Template.Hierarchy_Template_Panel.BONERA_ARMATURE_PT_Hierarchy_Template
    category = addon_preferences.PANEL_Hierarchy_Template_Category
    label = addon_preferences.PANEL_Hierarchy_Template_Label
    panels = append_panel_class(panels, panel_class, category, label)


    try:
        pass
        for item in panels:

            panel = item[0]
            category = item[1]
            label = item[2]

            if "bl_rna" in panel.__dict__:
                bpy.utils.unregister_class(panel)


            panel.bl_category = category
            panel.bl_label = label
            bpy.utils.register_class(panel)

    except Exception as e:
        print("\n[{}]\n{}\n\nError:\n{}".format(__name__, message, e))
        pass




class BONERA_user_preferences(bpy.types.AddonPreferences):

    bl_idname = Utility_Functions.get_addon_name()


    ENUM_Preferences_Tabs: bpy.props.EnumProperty(items=ENUM_Preferences_Tabs)

    #AFFIXES SETTING

    Enable_Affixes: bpy.props.BoolProperty(default=True)

    Prefix_List : bpy.props.CollectionProperty(type=Affixes_Preset_List.BONERA_Prefix)
    Prefix_List_Index: bpy.props.IntProperty()

    Suffix_List : bpy.props.CollectionProperty(type=Affixes_Preset_List.BONERA_Suffix)
    Suffix_List_Index: bpy.props.IntProperty()

    #GENERAL SETTING

    # Panel_Name: bpy.props.StringProperty(default="Bonera", update=update_panel)

    SECTION_Bonera_Toolkit: bpy.props.BoolProperty(default=True)
    PANEL_Bonera_Toolkit_Label: bpy.props.StringProperty(default="Bonera Toolkit", update=update_panel)
    PANEL_Bonera_Toolkit_Category: bpy.props.StringProperty(default="Bonera", update=update_panel)


    SECTION_Bonera_Pseudo_Layers: bpy.props.BoolProperty(default=True)
    PANEL_Pseudo_Bone_Layer_Label: bpy.props.StringProperty(default="Pseudo Bone Layer", update=update_panel)
    PANEL_Pseudo_Bone_Layer_Category: bpy.props.StringProperty(default="Bonera", update=update_panel)


    SECTION_Bonera_Pair_Renamer: bpy.props.BoolProperty(default=True)
    PANEL_Pair_List_Renamer_Label: bpy.props.StringProperty(default="Pair List Renamer", update=update_panel)
    PANEL_Pair_List_Renamer_Category: bpy.props.StringProperty(default="Bonera", update=update_panel)



    SECTION_Bonera_UI_Bone_Generator: bpy.props.BoolProperty(default=True)
    PANEL_Bone_Slider_Generator_Label: bpy.props.StringProperty(default="Bone UI Slider Generator", update=update_panel)
    PANEL_Bone_Slider_Generator_Category: bpy.props.StringProperty(default="Bonera", update=update_panel)


    SECTION_Hierarchy_Template: bpy.props.BoolProperty(default=True)
    PANEL_Hierarchy_Template_Label: bpy.props.StringProperty(default="Hierarchy Template", update=update_panel)
    PANEL_Hierarchy_Template_Category: bpy.props.StringProperty(default="Bonera", update=update_panel)



    CTRL_Pole_Suffix: bpy.props.StringProperty(default="CTRL_POLE_")
    CTRL_IK_Suffix: bpy.props.StringProperty(default="CTRL_IK_")

    CTRL_Hydraulic_Prefix: bpy.props.StringProperty(default="TGT_")

    show_RENAMER_List: bpy.props.BoolProperty(default=False)
    show_display_settings: bpy.props.BoolProperty(default=False)

    show_PBL_Bone_Layer_Icon: bpy.props.BoolProperty(default=False)
    ICON_PBL_Visibility: bpy.props.BoolProperty(default=True)
    ICON_PBL_Select: bpy.props.BoolProperty(default=True)
    ICON_PBL_Solo : bpy.props.BoolProperty(default=True)
    ICON_PBL_Remove: bpy.props.BoolProperty(default=True)
    ICON_PBL_Mute_Constraint: bpy.props.BoolProperty(default=False)


    ICON_PBL_Deform: bpy.props.BoolProperty(default=True)

    ICON_PBL_Key_Bone: bpy.props.BoolProperty(default=True)

    show_bone_list: bpy.props.BoolProperty(default=False)

    DISABLE_Bonadd: bpy.props.BoolProperty(default=True)
    Reset_Button: bpy.props.BoolProperty(default=False)

    constraint_toogle_use_selected: bpy.props.BoolProperty(default=False)
    header_toogle_constraints: bpy.props.BoolProperty(default=True)

    def draw_affixes_lists_operators(self, context, affix, layout):

        col = layout.column(align=True)

        operator = col.operator("bonera.affixes_list_operator", text="", icon="ADD")
        operator.list = affix
        operator.operation = "ADD"

        operator = col.operator("bonera.affixes_list_operator", text="", icon="REMOVE")
        operator.list = affix
        operator.operation = "REMOVE"

        col.separator()

        operator = col.operator("bonera.affixes_list_operator", text="", icon="TRIA_UP")
        operator.list = affix
        operator.operation = "UP"

        operator = col.operator("bonera.affixes_list_operator", text="", icon="TRIA_DOWN")
        operator.list = affix
        operator.operation = "DOWN"

    def draw_prefix_list(self, context, layout):

        col = layout.column(align=True)

        col.label(text="Prefix")

        row = col.row(align=True)

        row.template_list("BONERA_UL_Affixes_List", "", self, "Prefix_List", self, "Prefix_List_Index")
        self.draw_affixes_lists_operators(context, "PREFIX", row)

    def draw_suffix_list(self, context, layout):

        col = layout.column(align=True)

        col.label(text="Suffix")

        row = col.row(align=True)
        row.template_list("BONERA_UL_Affixes_List", "", self, "Suffix_List", self, "Suffix_List_Index")
        self.draw_affixes_lists_operators(context, "SUFFIX", row)

    def draw_affixes_lists(self, context, layout):

        layout.prop(self, "Enable_Affixes", text="Enable Affixes for Bone Name")



        if self.Enable_Affixes:
            layout.operator("bonera.load_reccommended", text="Load Reccomended")
            row = layout.row(align=True)
            self.draw_prefix_list(context, row)
            self.draw_suffix_list(context, row)

    def draw_hotkey(self, context, layout):


        layout.label(text="3D View")
        kc = context.window_manager.keyconfigs.user # addon
        km = kc.keymaps['3D View'] #
        keymap_items = km.keymap_items

        kmi = get_pie_menu(km, 'wm.call_menu', 'POSE_MT_bonera_toolkit_menu')
        kmi.show_expanded = False
        #col.context_pointer_set("keymap", km)
        rna_keymap_ui.draw_kmi([], kc, km, kmi, layout, 0)



    def draw_general(self, context, layout):

        # layout.prop(self, "Panel_Name", text="Panel Name")
        #
        # layout.separator()

        layout.label(text="Panels: ")

        layout.prop(self, "SECTION_Bonera_Toolkit", text="Bonera Toolkit")

        if self.SECTION_Bonera_Toolkit:
            box = layout.box()
            box.prop(self, "PANEL_Bonera_Toolkit_Category", text="Category")
            box.prop(self, "PANEL_Bonera_Toolkit_Label", text="Label")



        layout.prop(self, "SECTION_Bonera_Pseudo_Layers", text="Bonera Pseudo Layer")

        if self.SECTION_Bonera_Pseudo_Layers:
            box = layout.box()
            box.prop(self, "PANEL_Pseudo_Bone_Layer_Category", text="Category")
            box.prop(self, "PANEL_Pseudo_Bone_Layer_Label", text="Label")


        layout.prop(self, "SECTION_Bonera_Pair_Renamer", text="Pair Renamer")

        if self.SECTION_Bonera_Pair_Renamer:
            box = layout.box()
            box.prop(self, "PANEL_Pair_List_Renamer_Category", text="Category")
            box.prop(self, "PANEL_Pair_List_Renamer_Label", text="Label")


        layout.prop(self, "SECTION_Bonera_UI_Bone_Generator", text="UI Bone Generator")

        if self.SECTION_Bonera_UI_Bone_Generator:
            box = layout.box()
            box.prop(self, "PANEL_Bone_Slider_Generator_Category", text="Category")
            box.prop(self, "PANEL_Bone_Slider_Generator_Label", text="Label")


        layout.prop(self, "SECTION_Hierarchy_Template", text="Hierarchy Template")

        if self.SECTION_Hierarchy_Template:
            box = layout.box()
            box.prop(self, "PANEL_Hierarchy_Template_Category", text="Category")
            box.prop(self, "PANEL_Hierarchy_Template_Label", text="Label")











        layout.separator()
        layout.prop(self , "header_toogle_constraints", text="Toogle Constraint Buttons on Viewport (Pose Mode)")

        layout.label(text="Operators: ")
        layout.prop(self, "DISABLE_Bonadd", text="Disable Bonadd")
        layout.prop(self, "Reset_Button", text="Enable Reset Parameter Button")


    def draw_default_name(self, context, layout):

        col = layout.column(align=True)
        col.label(text="Generate IK Settings: ")
        col.prop(self, "CTRL_Pole_Suffix", text="Pole Bone Prefix")
        col.prop(self, "CTRL_IK_Suffix", text="IK Bone Prefix")

        col = layout.column(align=True)
        col.label(text="Hydraulic Settings: ")
        col.prop(self, "CTRL_Hydraulic_Prefix", text="Hydraulic Bone Prefix")

    def draw_bone_shape(self, context, layout):
        layout.label(text="Bone Shapes", icon="BONE_DATA")
        row = layout.row(align=True)
        row.operator("bonera.open_bone_shape_folder", text="Open Bone Shape Folder", icon="FILE_FOLDER")
        row.operator("bonera.reload_bone_shapes", text="Reload bone shapes", icon="FILE_REFRESH")

    def draw(self, context):
        layout = self.layout

        Main_Column = layout.column(align=True)
        row = Main_Column.row()
        row.prop(self, "ENUM_Preferences_Tabs", expand=True)
        box = Main_Column.box()

        if self.ENUM_Preferences_Tabs == "GENERAL":
            self.draw_general(context, box)

        if self.ENUM_Preferences_Tabs == "BONE_SHAPE":
            self.draw_bone_shape(context, box)

        if self.ENUM_Preferences_Tabs == "AFFIXES":
            self.draw_affixes_lists(context, box)

        if self.ENUM_Preferences_Tabs == "DEFAULT_NAME":
            self.draw_default_name(context, box)

        if self.ENUM_Preferences_Tabs == "HOTKEY":
            self.draw_hotkey(context, box)



classes = [BONERA_user_preferences]



def register():
    for cls in classes:

        bpy.utils.register_class(cls)

    update_panel(None, bpy.context)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
