import bpy

bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0.5))
cube = bpy.context.object
cube.name = "Blue cube"
cube.scale = (0.5, 0.5, 0.5)

material = bpy.data.materials.new("Blue paint")
material.diffuse_color = (0.08, 0.25, 0.65, 1)
cube.data.materials.append(material)
