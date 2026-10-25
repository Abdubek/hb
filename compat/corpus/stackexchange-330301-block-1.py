import bpy
from math import radians, degrees
from mathutils import Matrix, Euler, Vector
from datetime import datetime
from bpy_extras.node_shader_utils import PrincipledBSDFWrapper


def convert_euler_zyx_to_yxz(rotation_zyx):
    euler_zyx = Euler((radians(rotation_zyx[0]), radians(rotation_zyx[1]), radians(rotation_zyx[2])), 'XYZ')
    rot_mat = euler_zyx.to_matrix()

    
    rot_yxz = rot_mat.to_euler('ZXY')
    print('\n')
    print(f'%.4f %.4f %.4f' % (degrees(euler_zyx.x), degrees(euler_zyx.y), degrees(euler_zyx.z)))
    print(f'%.4f %.4f %.4f' % (degrees(rot_yxz.x), degrees(rot_yxz.y), degrees(rot_yxz.z)))


rot_zyx = (119.878, -11.9565, 138.127)  # Rotación en grados en orden ZYX
convert_euler_zyx_to_yxz(rot_zyx)

