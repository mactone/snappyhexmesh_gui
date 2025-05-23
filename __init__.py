# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "SnappyHexMesh GUI-mactone",
    "author": "Orig: Tuomo Keskitalo Modification: mactone hsieh",
    "version": (1, 9),
    "blender": (2, 80, 0),
    "location": "3D View > SnappyHexMesh GUI",
    "description": "GUI for OpenFOAM SnappyHexMesh volume mesh generation tool",
    "wiki_url": "https://github.com/tkeskita/snappyhexmesh_gui",
    "tracker_url": "https://github.com/tkeskita/snappyhexmesh_gui/issues",
    "support": 'COMMUNITY',
    "category": "Object",
    }

if "bpy" in locals():
    import importlib
    importlib.reload(op_gen)
    importlib.reload(op_export)
    importlib.reload(op_object)
else:
    import bpy
    import os.path
    from sys import float_info
    import math
    from . import (
        op_gen,
        op_export,
        op_object,
        )
    

# Common settings as property group
class SnappyHexMeshGUI_Settings(bpy.types.PropertyGroup):
    openfoam_framework: bpy.props.EnumProperty(
        name="Fork",
        description="OpenFOAM Fork Name for Compatibility of Generated Files",
        items={
            ('openfoam.org', 'openfoam.org', 'openfoam.org', 0),
            ('openfoam.com', 'openfoam.com', 'openfoam.com', 1)},
        default='openfoam.com',
    )
    snappy_template_path: bpy.props.StringProperty(
        name="Template Path",
        description="Path to SnappyHexMeshDict Template",
        default=os.path.join(os.path.dirname(__file__), 'skel', 'snappyHexMeshDictTemplate'),
        maxlen=1024,
        subtype="FILE_PATH",
    )
    block_mesh_template_path: bpy.props.StringProperty(
        name="Block Mesh Template Path",
        description="Path to BlockMeshDict Template",
        default=os.path.join(os.path.dirname(__file__), 'skel', 'blockMeshDictTemplate'),
        maxlen=1024,
        subtype="FILE_PATH",
    )
    surface_features_template_path: bpy.props.StringProperty(
        name="Surface Features Template Path",
        description="Path to surfaceFeaturesDictTemplate Template",
        default=os.path.join(os.path.dirname(__file__), 'skel', 'surfaceFeaturesDictTemplate'),
        maxlen=1024,
        subtype="FILE_PATH",
    )
    decomposepardict_template_path: bpy.props.StringProperty(
        name="decomposeParDict Template Path",
        description="Path to decomposeParDict Template",
        default=os.path.join(os.path.dirname(__file__), 'skel', 'decomposeParDictTemplate'),
        maxlen=1024,
        subtype="FILE_PATH",
    )
    createbafflesdict_template_path: bpy.props.StringProperty(
        name="createBafflesDict Template Path",
        description="Path to createBafflesDict Template",
        default=os.path.join(os.path.dirname(__file__), 'skel', 'createBafflesDictTemplate'),
        maxlen=1024,
        subtype="FILE_PATH",
    )
    meshqualitydict_template_path: bpy.props.StringProperty(
        name="meshQualityDict Template Path",
        description="Path to meshQualityDict Template",
        default=os.path.join(os.path.dirname(__file__), 'skel', 'meshQualityDictTemplate'),
        maxlen=1024,
        subtype="FILE_PATH",
    )
    export_path: bpy.props.StringProperty(
        name="Export Path",
        description="Path to Export Case Files. '//' means the folder where Blender file is saved",
        default="//",
        maxlen=1024,
        subtype="DIR_PATH",
    )
    export_stl_ascii: bpy.props.BoolProperty(
        name="ASCII STL",
        description="Export STL files in ASCII instead of Binary Format",
        default=False,
    )
    number_of_cpus: bpy.props.IntProperty(
        name="CPUs",
        description="Number of CPUs for decomposeParDict",
        default=1,
        min=1,
    )
    do_castellation: bpy.props.BoolProperty(
        name="Castellation Phase",
        description="Do Castellation Phase",
        default=True,
    )
    do_snapping: bpy.props.BoolProperty(
        name="Snapping Phase",
        description="Do Snapping Phase",
        default=True,
    )
    do_add_layers: bpy.props.BoolProperty(
        name="Add Layers Phase",
        description="Do Layer Addition Phase",
        default=False,
    )
    do_block_mesh: bpy.props.BoolProperty(
        name="Generate Block Mesh",
        description="Option to generate blockMeshDict (Cubic Cells for Whole Domain)",
        default=True,
    )
    export_scale: bpy.props.FloatProperty(
        name="Export Scale",
        description="Scaling Factor for Export",
        default=1.0,
        precision=4,
        min=float_info.min, max=float_info.max
    )
    cell_side_length: bpy.props.FloatProperty(
        name="Cell Side Length",
        description="Length of Base Block Mesh Cell Side",
        default=0.1,
        precision=4,
        min=float_info.min, max=float_info.max
    )
    block_mesh_min: bpy.props.FloatVectorProperty(
        name="Block Mesh Minimum Coordinates",
        description="Minimum Coordinates for Block Mesh",
        precision=6,
    )
    block_mesh_max: bpy.props.FloatVectorProperty(
        name="Block Mesh Maximum Coordinates",
        description="Maximum Coordinates for Block Mesh",
        precision=6,
    )
    block_mesh_delta: bpy.props.IntVectorProperty(
        name="Block Mesh Divisions",
        description="Block Mesh Division Counts in X, Y and Z Directions",
    )
    max_non_ortho: bpy.props.IntProperty(
        name="Max Non-Ortho",
        description="Maximum Allowed Non-Orthogonality. " \
        + "Small value generates better mesh for numerical solution, and " \
        + "large value better fit for surfaces and better layer addition",
        default=35,
        min=1, max=180,
    )
    relaxed_max_non_ortho: bpy.props.IntProperty(
        name="Relaxed Max Non-Ortho",
        description="Relaxed Maximum Allowed Non-Orthogonality for Layer Addition Phase",
        default=65,
        min=1, max=180,
    )
    surface_layer_feature_angle: bpy.props.IntProperty(
        name="Layer Feature Angle",
        description="Feature Angle for Addition of Layers. Small value avoids creating layers in corners, large value covers also corners",
        default=85,
        min=1, max=180
    )
    surface_layer_expansion_ratio: bpy.props.FloatProperty(
        name="Expansion Ratio",
        description="Layer Thickness Expansion Ratio",
        default=1.3,
        min=1e-2, max=1e2
    )
    surface_layer_final_thickness: bpy.props.FloatProperty(
        name="Final Thickness",
        description="Relative Thickness for Final Layer",
        default=0.6,
        min=1e-5, max=1.0
    )
    surface_layer_minimum_thickness: bpy.props.FloatProperty(
        name="Min Thickness",
        description="Relative Minimum Thickness for Layer",
        default=0.001,
        precision=5,
        min=1e-12, max=1.0
    )
    max_internal_skewness: bpy.props.FloatProperty(
        name="Max Internal Skewness",
        description="Maximum Skewness for Internal Faces (Decrease to Improve Solver Stability)",
        default=4.0,
        precision=2,
        min=0.01, max=20.0
    )
    min_twist: bpy.props.FloatProperty(
        name="Min Triangle Twist",
        description="Minimum Face Triangle Twist",
        default=0.6,
        min=1e-5, max=1.0
    )
    # Disabled relaxed min triangle twist for now. It does not seem to
    # play much role for layer addition.
    # relaxed_min_twist: bpy.props.FloatProperty(
    #     name="Relaxed Min Triangle Twist",
    #     description="Relaxed Minimum Face Triangle Twist for Layer Addition Phase",
    #     default=0.5,
    #     min=-1.0, max=1.0
    # )
    disable_quality_criteria: bpy.props.BoolProperty(
        name="Disable All Quality Criteria",
        description="Use Disabled Mesh Quality Criteria to Pass All Mesh Quality Checks. Creates Maximal Snapping and Layers, But Allows Extremely Low Quality Cells. For Debugging Purposes Only",
        default=False,
    )
    merge_distance_string: bpy.props.StringProperty(
        name="Merge Distance",
        description="Maximum Distance for Merging Closeby Vertices in Clean Mesh",
        default="1e-5"
    )
    merge_distance: bpy.props.FloatProperty(
        name="Merge Distance Float",
        description="Maximum Distance (as a float) for Merging Closeby Vertices in Clean Mesh",
        default=1e-5,
        min=0.0
    )
    feature_snap_iter: bpy.props.IntProperty(
        name="Feature Snap Iter",
        description="Number of Feature Edge Snapping Iterations (nFeatureSnapIter)",
        default=3,
        min=0, max=100,
    )

# Object specific parameters
bpy.types.Object.shmg_include_in_export = bpy.props.BoolProperty(
    name="Include in export",
    description="Include mesh in export (SnappyHexMesh GUI)",
    default=True,
)
bpy.types.Object.shmg_include_snapping = bpy.props.BoolProperty(
    name="Do Snap to Surface",
    description="Include Snapping to Surface. Required for cell/face zones",
    default=True,
)
bpy.types.Object.shmg_include_feature_extraction = bpy.props.BoolProperty(
    name="Do Feature Extraction",
    description="Include Extraction of Feature Edges from Surface",
    default=True,
)
bpy.types.Object.shmg_surface_min_level = bpy.props.IntProperty(
    name="Minimum Surface Refinement Level",
    description="Minimum Cell Refinement Level for Surface",
    default=0, min=0, max=10,
)
bpy.types.Object.shmg_surface_max_level = bpy.props.IntProperty(
    name="Maximum Surface Refinement Level",
    description="Maximum Cell Refinement Level for Surface",
    default=0, min=0, max=10,
)

bpy.types.Object.shmg_volume_refinement_gaplevels_min_level = bpy.props.IntProperty(
    name="Minimum Surface Refinement Level",
    description="Minimum Cell Refinement Level for Surface",
    default=0, min=0, max=10,
)

bpy.types.Object.shmg_volume_refinement_gaplevels_max_level = bpy.props.IntProperty(
    name="Minimum Surface Refinement Level",
    description="Minimum Cell Refinement Level for Surface",
    default=0, min=0, max=10,
)

bpy.types.Object.shmg_feature_edge_level = bpy.props.IntProperty(
    name="Feature Edge Refinement Level",
    description="Feature Edge (Sharp Edge) Refinement Level for Surface",
    default=0, min=0, max=10,
)
bpy.types.Object.shmg_surface_layers = bpy.props.IntProperty(
    name="Number of Surface Layers",
    description="Number of Surface Layers for Surface. Value -1 means Not Specified, 0 means No Layers Allowed",
    default=-1, min=-1, max=100,
)
bpy.types.Object.shmg_dict_number = bpy.props.IntProperty(
    name="Dict File Number",
    description="Specifies Which snappyHexMeshDict File This Layer is Added To. Value 1 means the default snappyHexMeshDict, value 2 creates snappyHexMeshDict2 etc",
    default=1, min=1, max=100,
)
bpy.types.Object.shmg_patch_info_type = bpy.props.EnumProperty(
    name="Surface Type",
    description="Patch Type for Surface",
    items={
        # Commented out basic types not supported by SnappyHexMesh
        # ('cyclic', 'cyclic', 'Conformal Cyclic Boundary', 0),
        # ('cyclicAMI', 'cyclicAMI', 'Non-conformal Cyclic Boundary', 1),
        # ('empty', 'empty', 'Empty (Ignored) Boundary', 2),
        ('patch', 'patch', 'Patch (General) Boundary', 3),
        # ('symmetry', 'symmetry', 'Patch (Possibly Non-Planar) Boundary', 4),
        # ('symmetryPlane', 'symmetryPlane', 'Planar Patch Boundary', 5),
        ('wall', 'wall', 'Wall Boundary', 6),
        # ('wedge', 'wedge', 'Wedge (2D Axisymmetric) Boundary', 7),
    },
    default='patch'
)
bpy.types.Object.shmg_face_zone_type = bpy.props.EnumProperty(
    name="Face Zone Type",
    description="Face Zone Type For Surface (Optional)",
    items={
        ('none', 'none', 'None', 0),
        ('internal', 'internal', 'Internal (Shared Internal Faces)', 1),
        ('baffle', 'baffle', 'Baffle (Overlapping Boundary Faces)', 2),
        ('boundary', 'boundary', 'Boundary (Separate Boundary Faces)', 3)},
    default='none'
)
bpy.types.Object.shmg_cell_zone_type = bpy.props.EnumProperty(
    name="Cell Zone Type",
    description="Cell Zone Type for Enclosed Volume (Optional)",
    items={
        ('none', 'none', 'None', 0),
        ('inside', 'inside', 'Create Zone Inside of Enclosed Volume', 1),
        ('outside', 'outside', 'Create Zone Outside of Enclosed Volume', 2)},
    default='none'
)

bpy.types.Object.shmg_volume_type_gapmode = bpy.props.EnumProperty(
    name="gapMode",
    description="set the gapMode inside volume refinement (Optional)",
    items={
        ('none', 'none', 'None', 0),
        ('inside', 'inside', 'gap inside the volume', 1),
        ('outside', 'outside', 'gap outside the volume', 2)},
    default='none'
) # mactone

bpy.types.Object.shmg_volume_level = bpy.props.IntProperty(
    name="Volume Refinement Level",
    description="Cell Refinement Level for Volume",
    default=0, min=0, max=10,
)
bpy.types.Object.shmg_volume_type = bpy.props.EnumProperty(
    name="Volume Refinement Type",
    description="Volume Refinement Type",
    items={
        ('none', 'none', 'None', 0),
        ('inside', 'inside', 'Refine Cells Inside of Enclosed Volume', 1),
        ('outside', 'outside', 'Refine Cells Outside of Enclosed Volume', 2)},
    default='none'
)
bpy.types.Object.shmg_slave_side_layers = bpy.props.BoolProperty(
    name="Slave Side Layers",
    description="Create Layers also on the Slave Side (For Baffle or Boundary Type Face Zones)",
    default=False,
)
bpy.types.Object.shmg_specify_object_layer_properties = bpy.props.BoolProperty(
    name="Object Specific Layer Settings",
    description="Enable Object Specific Layer Settings",
    default=False,
)
bpy.types.Object.shmg_obj_surface_layer_expansion_ratio = bpy.props.FloatProperty(
    name="Expansion Ratio",
    description="Layer Thickness Expansion Ratio",
    default=1.3,
    min=1e-2, max=1e2
)
bpy.types.Object.shmg_obj_surface_layer_final_thickness = bpy.props.FloatProperty(
    name="Final Thickness",
    description="Relative Thickness for Final Layer",
    default=0.6,
    min=1e-5, max=1.0
)
bpy.types.Object.shmg_obj_surface_layer_minimum_thickness = bpy.props.FloatProperty(
    name="Min Thickness",
    description="Relative Minimum Thickness for Layer",
    default=0.001,
    precision=5,
    min=1e-12, max=1.0
)
bpy.types.Object.shmg_buffer_layer = bpy.props.BoolProperty(
    name="Buffer Layer",
    description="Create a Buffer Layer for Object (OpenFOAM.com v2412 or later, enable for objects with layer addition)",
    default=False,
)


class SnappyHexMeshGUI_ToolBar:
    """Base Class for Add-on Tool Bar"""
    bl_label = "SnappyHexMesh GUI"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "SnappyHexMesh GUI"

    
class VIEW3D_PT_SnappyHexMeshGUI_Edit(bpy.types.Panel, SnappyHexMeshGUI_ToolBar):
    """Main Tool Bar in Edit Mode"""
    bl_idname = "VIEW3D_PT_snappyhexmeshgui_edit_mode"
    bl_context = "mesh_edit"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        col = box.column(align=True)
        col.label(text="Not available", icon='ERROR')
        col.label(text="in Edit Mode")

    
class VIEW3D_PT_SnappyHexMeshGUI_Object(bpy.types.Panel, SnappyHexMeshGUI_ToolBar):
    """Main Tool Bar in Object Mode"""
    bl_idname = "VIEW3D_PT_snappyhexmeshgui_object_mode"
    bl_context = "objectmode"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gui = scene.snappyhexmeshgui
        icon_names = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items.keys()

        col = layout.column()
        rowsub = col.row(align=True)
        rowsub.label(text="Options:")
        rowsub.prop(gui, "number_of_cpus", text="CPUs:")

        if 'MOD_MULTIRES' in icon_names:
            rowsub.prop(gui, "do_castellation", text="", icon='MOD_MULTIRES')
        else:
            rowsub = col.row(align=True)
            rowsub.prop(gui, "do_castellation", text="Do Castellation")

        if 'UV_VERTEXSEL' in icon_names:
            rowsub.prop(gui, "do_snapping", text="", icon='UV_VERTEXSEL')
        else:
            rowsub = col.row(align=True)
            rowsub.prop(gui, "do_snapping", text="Do Snapping")

        if 'HAIR' in icon_names:
            rowsub.prop(gui, "do_add_layers", text="", icon='HAIR')
        elif 'STRANDS' in icon_names:
            rowsub.prop(gui, "do_add_layers", text="", icon='STRANDS')
        else:
            rowsub = col.row(align=True)
            rowsub.prop(gui, "do_add_layers", text="Add Layers")

        rowsub = col.row()
        rowsub.prop(gui, "openfoam_framework")

        rowsub = col.row()
        rowsub.prop(gui, "export_scale")

        rowsub = col.row()
        rowsub.label(text="Export Path:")
        rowsub = col.row()
        rowsub.prop(gui, "export_path", text="")

        rowsub = col.row()
        rowsub.prop(gui, "do_block_mesh")

        if gui.do_block_mesh:
            rowsub = col.row()
            rowsub.label(text="Cell Length")
            rowsub.prop(gui, "cell_side_length", text="")

        rowsub = col.row()
        rowsub.prop(gui, "disable_quality_criteria")
        if not gui.disable_quality_criteria:
            rowsub = col.row()
            rowsub.label(text="Max Non-Ortho")
            rowsub.prop(gui, "max_non_ortho", text="")
            # Hide maxInternalSkewness for now, looks like it can be constant
            # rowsub = col.row()
            # rowsub.label(text="Max Internal Skewness")
            # rowsub.prop(gui, "max_internal_skewness", text="")
            rowsub = col.row()
            rowsub.label(text="Min Triangle Twist")
            rowsub.prop(gui, "min_twist", text="")
        rowsub = col.row()
        rowsub.label(text="Feature Snap Iter")
        rowsub.prop(gui, "feature_snap_iter", text="")

        if gui.do_add_layers:
            rowsub = col.row(align=True)
            rowsub.label(text="Layer Addition Global Options:")
            rowsub = col.row()
            if not gui.disable_quality_criteria:
                rowsub.label(text="Relaxed Max Non-Ortho")
                rowsub.prop(gui, "relaxed_max_non_ortho", text="")
            # Disabled relaxed min triangle twist for now. It does not seem to
            # play much role for layer addition.
            # rowsub = col.row()
            # rowsub.label(text="Relaxed Min Triangle Twist")
            # rowsub.prop(gui, "relaxed_min_twist", text="")
            rowsub = col.row()
            rowsub.label(text="Feature Angle")
            rowsub.prop(gui, "surface_layer_feature_angle", text="")
            rowsub = col.row()
            rowsub.label(text="Expansion Ratio")
            rowsub.prop(gui, "surface_layer_expansion_ratio", text="")
            rowsub = col.row()
            rowsub.label(text="Final Thickness")
            rowsub.prop(gui, "surface_layer_final_thickness", text="")
            rowsub = col.row()
            rowsub.label(text="Min Thickness")
            rowsub.prop(gui, "surface_layer_minimum_thickness", text="")

        row = layout.row()
        row.operator("object.snappyhexmeshgui_apply_locrotscale", text="Apply LocRotScale for All")

        row = layout.row(align=True)
        row.operator("object.snappyhexmeshgui_cleanup_meshes", text="Clean Mesh")
        row.prop(gui, "merge_distance_string", text="")

        row = layout.row()
        row.operator("object.snappyhexmeshgui_add_location_in_mesh_object", text="Add Location In Mesh Object")
        row = layout.row()
        row.operator("object.snappyhexmeshgui_clean_case_dir", text="Clean Case Dir")


        scaled_obs = op_object.get_scaled_object_names()
        if scaled_obs:
            row = layout.row()
            row.label(icon="ERROR", text="Found scaled objects: " + scaled_obs)

        if gui.feature_snap_iter > 0 and gui.do_add_layers:
            row = layout.row()
            row.label(icon="ERROR", text="Feature Snap Iters may create bad layers")

        if gui.disable_quality_criteria:
            row = layout.row()
            row.label(icon="ERROR", text="All Quality Criteria are Disabled!")
            col = layout.column()
            rowsub = col.row(align=True)
            rowsub.operator("object.snappyhexmeshgui_export", text="I understand, Export!")
        else:
            col = layout.column()
            rowsub = col.row(align=True)
            rowsub.operator("object.snappyhexmeshgui_export", text="Export")

        if 'FILE_TEXT' in icon_names:
            rowsub.prop(gui, "export_stl_ascii", text="", icon='FILE_TEXT')
        else:
            rowsub = col.row(align=True)
            rowsub.prop(gui, "export_stl_ascii", text="ASCII STL Format")


class VIEW3D_PT_SnappyHexMeshGUI_Object_Summary(bpy.types.Panel, SnappyHexMeshGUI_ToolBar):
    """Overall Summary Panel in Object Mode"""
    bl_idname = "VIEW3D_PT_snappyhexmeshgui_object_summary"
    bl_context = "objectmode"
    bl_label = "Export Summary"

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gui = scene.snappyhexmeshgui

        col = layout.column()

        # Global bounding box info
        bb_min, bb_max = op_object.get_global_bbox_coords()
        bb_min_str = "[%7.3f %7.3f %7.3f]" % (bb_min[0], bb_min[1], bb_min[2])
        bb_max_str = "[%7.3f %7.3f %7.3f]" % (bb_max[0], bb_max[1], bb_max[2])
        rowsub = col.row()
        rowsub.label(text="Global Bounds [min] [max]:")
        rowsub = col.row()
        rowsub.label(text=bb_min_str)
        rowsub = col.row()
        rowsub.label(text=bb_max_str)

        # Block mesh cell count
        if gui.do_block_mesh:
            bm_count = op_object.block_mesh_cell_count(bb_min, bb_max, gui)
            rowsub = col.row(align=True)
            rowsub.label(text="Block Mesh Count: %d" % bm_count)

        # List objects included in export
        rowsub = col.row(align=True)
        rowsub.label(text="Objects included:")
        for obj in bpy.data.objects:
            if obj.type != 'MESH':
                continue
            if not obj.shmg_include_in_export:
                continue
            rowsub = col.row(align=True)
            rowsub.label(text="    %r" % obj.name)

        
class VIEW3D_PT_SnappyHexMeshGUI_Object_Object(bpy.types.Panel, SnappyHexMeshGUI_ToolBar):
    """Object Setting Panel in Object Mode"""
    bl_idname = "VIEW3D_PT_snappyhexmeshgui_object_object"
    bl_context = "objectmode"
    bl_label = "Object Settings"
    
    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        gui = scene.snappyhexmeshgui
        obj = context.object

        col = layout.column()
        rowsub = col.row(align=True)
        rowsub.label(text="Object: %r" % obj.name)

        row = col.row()
        row.operator("object.snappyhexmeshgui_copy_settings_to_objects",
                     text="Copy Settings to Objects")

        # Bounding box info
        bb_min, bb_max = op_object.get_object_bbox_coords(obj)
        bb_min_str = "[%7.3f %7.3f %7.3f]" % (bb_min[0], bb_min[1], bb_min[2])
        bb_max_str = "[%7.3f %7.3f %7.3f]" % (bb_max[0], bb_max[1], bb_max[2])
        rowsub = col.row()
        rowsub.label(text="Object Bounds [min] [max]:")
        rowsub = col.row()
        rowsub.label(text=bb_min_str)
        rowsub = col.row()
        rowsub.label(text=bb_max_str)
        rowsub = col.row()
        rowsub.label(text="Area: %.4e" % op_object.get_surface_area(obj))

        rowsub = col.row()
        rowsub.prop(obj, "shmg_include_in_export", text="Inlcude in Export")

        rowsub = col.row()
        rowsub.alignment = 'RIGHT'
        rowsub.prop(obj, "shmg_patch_info_type", text="Type")
        rowsub = col.row()
        rowsub.prop(obj, "shmg_include_snapping", text="Enable Snapping")
        # rowsub = col.row()
        # rowsub.prop(obj, "shmg_buffer_layer", text="Enable Buffer Layer")
        rowsub = col.row()
        rowsub.label(text="Surface Refinement Levels:")
        rowsub = col.row()
        rowsub.prop(obj, "shmg_surface_min_level", text="Min")
        rowsub.prop(obj, "shmg_surface_max_level", text="Max")
        rowsub = col.row()
        rowsub.prop(obj, "shmg_include_feature_extraction", text="Extract Feature Edges")
        rowsub = col.row()
        rowsub.prop(obj, "shmg_feature_edge_level", text="Feature Edge Level")
        rowsub = col.row()
        rowsub.alignment = 'RIGHT'
        rowsub.prop(obj, "shmg_face_zone_type", text="Face Zone Type")
        rowsub = col.row()
        rowsub.alignment = 'RIGHT'
        rowsub.prop(obj, "shmg_cell_zone_type", text="Cell Zone Type")
        rowsub = col.row()
        rowsub.alignment = 'RIGHT'
        rowsub.prop(obj, "shmg_volume_type", text="Volume Refinement")
        rowsub = col.row()
        rowsub.alignment = 'RIGHT'
        rowsub.prop(obj, "shmg_volume_type_gapmode", text="gapMode")
        rowsub = col.row()
        rowsub.alignment = 'RIGHT'
        rowsub = col.row()
        rowsub.label(text="gapLevels:")
        rowsub = col.row()
        rowsub.prop(obj, "shmg_volume_type_gaplevels_min_level", text="Min")
        rowsub.prop(obj, "shmg_volume_type_gaplevels_max_level", text="Max")
        
        if obj.shmg_volume_type != "none":
            rowsub = col.row()
            rowsub.prop(obj, "shmg_volume_level", text="Volume Refinement Level")

        if gui.do_add_layers:
            rowsub = col.row()
            rowsub.label(text="Layer Addition Settings:")
            rowsub = col.row()
            rowsub.prop(obj, "shmg_dict_number")
            rowsub = col.row()
            rowsub.prop(obj, "shmg_surface_layers", text="Surface Layers")
            rowsub = col.row()
            rowsub.prop(obj, "shmg_slave_side_layers")
            rowsub = col.row()
            rowsub.prop(obj, "shmg_specify_object_layer_properties")
            if obj.shmg_specify_object_layer_properties:
                rowsub = col.row()
                rowsub.prop(obj, "shmg_obj_surface_layer_expansion_ratio")
                rowsub = col.row()
                rowsub.prop(obj, "shmg_obj_surface_layer_final_thickness")
                rowsub = col.row()
                rowsub.prop(obj, "shmg_obj_surface_layer_minimum_thickness")

        
# Registration

classes = (
    VIEW3D_PT_SnappyHexMeshGUI_Object,
    VIEW3D_PT_SnappyHexMeshGUI_Edit,
    VIEW3D_PT_SnappyHexMeshGUI_Object_Object,
    VIEW3D_PT_SnappyHexMeshGUI_Object_Summary,
    op_export.OBJECT_OT_snappyhexmeshgui_export,
    op_export.OBJECT_OT_snappyhexmeshgui_apply_locrotscale,
    op_export.OBJECT_OT_snappyhexmeshgui_add_location_in_mesh_object,
    op_export.OBJECT_OT_snappyhexmeshgui_cleanup_meshes,
    op_export.OBJECT_OT_snappyhexmeshgui_copy_settings_to_objects,
    op_export.OBJECT_OT_snappyhexmeshgui_clean_case_dir,
    
    SnappyHexMeshGUI_Settings,
)
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.snappyhexmeshgui = \
        bpy.props.PointerProperty(type = SnappyHexMeshGUI_Settings)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.snappyhexmeshgui

if __name__ == "__main__":
    register()
