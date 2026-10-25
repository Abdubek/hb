import bpy

C = bpy.context

# Iterate through all objects in selection
for ob in C.selected_objects:
    if ob.type not in ('LIGHTS', 'CAMERA', 'VOLUME'): # OPTIONAL
        # Iterate through all material slots
        for slot in ob.material_slots:
            if slot.material is not None:
                # Set the property
                slot.material.show_transparent_back = False
                slot.material.diffuse_color = (1.0, 0.0, 0.0, 1.0)
                slot.material.use_backface_culling = True
                # ... whatever
