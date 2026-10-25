import bpy

# Get the object reference
obj = bpy.context.object

# Get the material via active slot 
mat = obj.active_material 
# or: bpy.data.materials.get("MaterialName")

if hasattr(mat, 'node_tree'):
    # Get the principled bsdf
    prince = mat.node_tree.nodes.get('Principled BSDF') 
    if prince:
        # Get the base color of the principled bsdf
        r, g, b, a = prince.inputs['Base Color'].default_value
        print(r, g, b, a)
