# Fill in some info for this add on 
bl_info = {
    "name": "CommonUI",
    "author": "Tim",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "View3D > Tool Shelf > CommonUI",
    "description": "A bunch of common UI examples for add on",
    "category": "Object",
}

import bpy
import os
from bpy.props import EnumProperty, FloatVectorProperty

"""------------------------------------------------------------------------
Functions
------------------------------------------------------------------------"""
# Function to apply changes to the selected object's scale
def update_scale(context):
    obj = context.active_object
    props = context.scene.my_scale_props
    if obj and obj.type == 'MESH':
        obj.scale.x = props.scale_x
        obj.scale.y = props.scale_y
        obj.scale.z = props.scale_z


"""------------------------------------------------------------------------
Properties
------------------------------------------------------------------------"""
#Store XYZ scale inputs Property Group
class ScaleProperties(bpy.types.PropertyGroup):
    scale_x: bpy.props.FloatProperty(name="X", default=1.0, update=lambda self, context: update_scale(context))
    scale_y: bpy.props.FloatProperty(name="Y", default=1.0, update=lambda self, context: update_scale(context))
    scale_z: bpy.props.FloatProperty(name="Z", default=1.0, update=lambda self, context: update_scale(context))


class LightCreatorProperties(bpy.types.PropertyGroup):
    #Create a light enum
    light_type: bpy.props.EnumProperty(
        name="Type",
        description="Choose type of light to create",
        items=[
            ('POINT', "Point Light", "Create a Point Light"),
            ('SPOT', "Spot Light", "Create a Spot Light"),
            ('AREA', "Area Light", "Create an Area Light"),
        ],
        default='POINT',
    )
    #Create a light color
    light_color: FloatVectorProperty(
        name="Light Color",
        description="Color of the light",
        subtype='COLOR',
        default=(1.0, 1.0, 1.0),
        min=0.0,
        max=1.0
    )

"""------------------------------------------------------------------------
Create Operator
------------------------------------------------------------------------"""
#Add Suzan mesh to the scene
class OBJECT_OT_add_suzan(bpy.types.Operator):
    bl_idname = "object.add_suzan"
    bl_label = "Add Suzan"
    bl_description = "Add Suzan to the scene"
    bl_options = {'REGISTER', 'UNDO'}
    # The actual action. Add monkey mesh
    def execute(self, context):
        bpy.ops.mesh.primitive_monkey_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        return {'FINISHED'}

#Add Sphere mesh to the scene
class OBJECT_OT_add_sphere(bpy.types.Operator):
    bl_idname = "object.add_sphere"
    bl_label = "Add Sphere"
    bl_description = "Add a sphere to the scene"
    bl_options = {'REGISTER', 'UNDO'}
    # The actual action. Add UV Sphere
    def execute(self, context):
        bpy.ops.mesh.primitive_uv_sphere_add()
        return {'FINISHED'}

#Create light based on the chosen enum type
class LIGHTCREATOR_OT_create_light(bpy.types.Operator):
    bl_idname = "lightcreator.create_light"
    bl_label = "Create Light"
    bl_description = "Create the selected type of light"
    bl_options = {'REGISTER', 'UNDO'}
    # The actual action. Add light
    def execute(self, context):
        props = context.scene.light_creator_props
        #light_type = context.scene.light_creator_props.light_type
        #bpy.ops.object.light_add(type=light_type, align='WORLD', location=(0, 0, 2))
        
        # Create the light data
        light_data = bpy.data.lights.new(name="New_Light", type=props.light_type)
        light_data.color = props.light_color
        
    
        # Create the light object
        light_object = bpy.data.objects.new(name="New_Light", object_data=light_data)
        
        # Link light object to the scene
        collection = context.collection
        collection.objects.link(light_object)
        
        # Set the light at the 3D cursor location
        light_object.location = context.scene.cursor.location
        return {'FINISHED'}

# Subdivide and add shade smooth to the selected object
class SmoothObject_OT_smooth_object(bpy.types.Operator):
    bl_label = "Smooth Object"
    bl_idname = "mesh.smooth_object_button"
    bl_description = "Smooth the chosen object"
    bl_options = {'REGISTER', 'UNDO'}
    # The actual action. Add subdivide modifier and shade smooth
    def execute(self, context):
        obj = bpy.context.active_object
        subsurf_mod = obj.modifiers.new(name="Subdivision",type='SUBSURF')
        subsurf_mod.levels = 2
        subsurf_mod.render_levels = 2
        bpy.ops.object.shade_smooth()
        return {'FINISHED'}
   
# Batch export all selected meshes
class BATCHEXPORT_OT_batch_export(bpy.types.Operator):
    bl_label = "Batch Export"
    bl_idname = "mesh.batch_export_button"
    bl_description = "Batch export selected meshes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0))
        # export to blend file location
        basedir = os.path.dirname(bpy.data.filepath)

        if not basedir:
            raise Exception("Blend file is not saved")

        view_layer = bpy.context.view_layer

        obj_active = view_layer.objects.active
        selection = bpy.context.selected_objects

        bpy.ops.object.select_all(action='DESELECT')

        for obj in selection:
            obj.select_set(True)
            # some exporters only use the active object
            view_layer.objects.active = obj
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(basedir, name)
            bpy.ops.export_scene.fbx(filepath=fn + ".fbx", use_selection=True)
            # Can be used for multiple formats
            # bpy.ops.export_scene.x3d(filepath=fn + ".x3d", use_selection=True)
            obj.select_set(False)
            print("written:", fn)


        view_layer.objects.active = obj_active

        for obj in selection:
            obj.select_set(True)

        return {'FINISHED'}
    
    
"""------------------------------------------------------------------------
Create UI for running Operator
------------------------------------------------------------------------"""        
class VIEW3D_PT_add_mesh_panel(bpy.types.Panel):
    bl_label = "Common UI"
    bl_idname = "VIEW3D_PT_add_mesh" 
    #Show up in 3D viewport. Can be switched to other viewport like Shader Editor or Compositor
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Commom UI"
    bl_context = "objectmode" #Only show up in object more

    def draw(self, context):
        layout = self.layout
        layout.label(text="Add Mesh:")
        row = layout.row() #create first row
        row.operator("object.add_suzan", icon='MONKEY') #link Operator with UI button
        row = layout.row() #create second row
        row.operator("object.add_sphere", icon='SPHERE') #link Operator with UI button

        layout.label(text="Subdivide:")
        row = layout.row()
        row.operator("mesh.smooth_object_button", icon='MESH_CIRCLE')
        
        layout.label(text="Scaling:")
        ScaleProps = context.scene.my_scale_props #create scale input
        layout.prop(ScaleProps, "scale_x") #link Property with UI button
        layout.prop(ScaleProps, "scale_y") #link Property with UI button
        layout.prop(ScaleProps, "scale_z") #link Property with UI button

class VIEW3D_PT_add_lighting_panel(bpy.types.Panel):
    bl_label = "Lighting"
    bl_idname = "VIEW3D_PT_add_light"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Commom UI"
    bl_context = "objectmode" #Only show up in object more
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.light_creator_props
        
        layout.prop(props, "light_type")
        layout.prop(props, "light_color")
        layout.operator("lightcreator.create_light", text="Create Light")
        
        
        #LightProps = context.scene.light_creator_props
        #layout.prop(LightProps, "light_type")#create light enum
        #layout.operator("lightcreator.create_light", text="Create Light")#create light

class VIEW3D_PT_add_output_panel(bpy.types.Panel):
    bl_label = "Output"
    bl_idname = "VIEW3D_PT_output"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Commom UI"
    bl_context = "objectmode" #Only show up in object more
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("mesh.batch_export_button", icon='FILEBROWSER')
        # Big render button
        row = layout.row()
        row.scale_y = 2.0
        row.operator("render.render", icon='SCENE')#Actual render

"""------------------------------------------------------------------------
Register
------------------------------------------------------------------------""" 
# Register and unregister UI Panel and Operator
classes = [
    OBJECT_OT_add_suzan, 
    OBJECT_OT_add_sphere, 
    SmoothObject_OT_smooth_object, 
    BATCHEXPORT_OT_batch_export, 
    ScaleProperties, 
    LIGHTCREATOR_OT_create_light, 
    LightCreatorProperties, 
    VIEW3D_PT_add_mesh_panel, 
    VIEW3D_PT_add_lighting_panel, 
    VIEW3D_PT_add_output_panel
    ]
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    #linked to custom properties
    bpy.types.Scene.my_scale_props = bpy.props.PointerProperty(type=ScaleProperties)
    bpy.types.Scene.light_creator_props = bpy.props.PointerProperty(type=LightCreatorProperties)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.my_scale_props


if __name__ == "__main__":
    register()