import bpy

# Callback function for location changes
def obj_location_callback(ob):
    # Do something here
    print('Object "{}" changed its location to: {}: '.format(
        ob.name, ob.location)
        )


# Subscribe to the context object (mesh)
def subscribe_to_obj_loc(ob):
    if ob.type != 'MESH':
        return

    subscribe_to = ob.path_resolve("location", False)

    bpy.msgbus.subscribe_rna(
        key=subscribe_to,
        # owner of msgbus subcribe (for clearing later)
        owner=ob,
        # Args passed to callback function (tuple)
        args=(ob,),
        # Callback function for property update
        notify=obj_location_callback,
    )

# Ensure only meshes are passed to this function
subscribe_to_obj_loc(bpy.context.object)
