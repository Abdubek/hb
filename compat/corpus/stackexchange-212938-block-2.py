import bpy

tests = (
    (0, (1, 1, 1)),
    (1, (0, 0, 0)),
    (1, (1, 1, 1)),
    (1, (2, 2, 2)),
    (2, (1, 1, 1)),
    (2, (2, 2, 2)),
    (1, (1, 1, 4)),
    (2, (1, 1, 4)),
    (2, (2, 2, 8)),
    )

x = 0    
for i, (size, scale) in enumerate(tests):
    # Create the default cube
    bpy.ops.mesh.primitive_cube_add(
        size=size,
        scale=scale,
        location = (x, 0, 0),
        )
    cube = bpy.context.object
    cube.name = f"Test{i}_{size}_{scale}"
    print(size, scale, cube.dimensions[:])
    x += cube.dimensions.x
