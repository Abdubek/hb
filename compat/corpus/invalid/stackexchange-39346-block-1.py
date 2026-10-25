import bpy

# get the current scene
scn = bpy.context.scene

# create a mesh data block
mymesh = bpy.data.meshes.new('mymesh')

# define some vertices
verts = [Vector((-1,  1, 0)),
         Vector(( 1,  1, 0)),
         Vector(( 1, -1, 0)),
         Vector((-1, -1, 0)),
        ]

edges = []
faces = [[0, 1, 2, 3]]
# add the vertices to the mesh
mymesh.from_pydata(verts, edges, faces)

# create an object that uses the mesh data
myobj = bpy.data.objects.new('myobject', mymesh)

# link the object to the scene
scn.objects.link(myobj)
