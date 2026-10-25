import bpy
from random import uniform
from mathutils import Matrix
from math import pi
n=25

T = Matrix.Translation((2, 0, 0))
R = Matrix.Rotation(4 * pi / n, 4, 'Z')
#M = R @ T

ob = bpy.context.object
ob.data.transform(T) # like an edit mode transform

coll = bpy.context.collection

for i in range(1, n+1):
    copy = ob.copy() # copy object
    copy.color = (uniform(0, 1), uniform(0, 1), uniform(0, 1), 1)
    copy.matrix_world @= R
    coll.objects.link(copy) # link to context collection
    ob = copy
