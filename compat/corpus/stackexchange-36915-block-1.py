import bpy
import bmesh
import numpy as np

## ------- part 1 --- do this once.
sig = 0.3
n_frames = 101
bpy.context.scene.frame_end = n_frames

pi = np.pi
make_ico = bpy.ops.mesh.primitive_ico_sphere_add
make_ico(subdivisions=3, radius = 2.0, location = (0,0,3))
obj = bpy.context.active_object
me = obj.data

ico0 = np.array([v.co for v in me.vertices]) # get ico vertices
zmin, zmax = ico0[:,2].min(), ico0[:,2].max()
zc = np.linspace(zmin, zmax, n_frames)
ico = np.zeros_like(ico0)
data = []

for i in range(n_frames):
    ico[:,:2] = (1.0 + np.exp(-(ico0[:,2] - zc[i])**2/(2.*sig**2)))[:,None] * ico0[:,:2]
    ico[:,2] = ico0[:,2]
    data.append(ico.copy())
