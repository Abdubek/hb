import bpy

scene = bpy.context.scene

obs = []
for ob in scene.objects:
    # whatever objects you want to join...
    if ob.type == 'MESH':
        obs.append(ob)

ctx = bpy.context.copy()

# one of the objects to join
ctx['active_object'] = obs[0]

ctx['selected_objects'] = obs
# In Blender 2.8x this needs to be the following instead:
#ctx['selected_editable_objects'] = obs

# We need the scene bases as well for joining.
# Remove this line in Blender >= 2.80!
ctx['selected_editable_bases'] = [scene.object_bases[ob.name] for ob in obs]

bpy.ops.object.join(ctx)
