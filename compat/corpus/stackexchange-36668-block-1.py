import bpy
from math import radians
from mathutils import Euler, Matrix

euler = Euler(map(radians, (0, 0, 45)), 'XYZ')

ob = bpy.context.object

loc, rot, scale = ob.matrix_world.decompose()

smat = Matrix()
for i in range(3):
    smat[i][i] = scale[i]

mat = Matrix.Translation(loc) * euler.to_matrix().to_4x4() * smat

ob.matrix_world = mat
