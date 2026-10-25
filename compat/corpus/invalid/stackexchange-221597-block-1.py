import bpy, bmesh, random
from mathutils import Vector

num_points = 1000


def point_on_triangle(face):
    a, b, c = map(lambda v: v.co, face.verts)
    a2b = b - a  # vector from a to b
    a2c = c - a  
    height = random.triangular(low=0.0, high=1.0, mode=0.0)
    return a + a2c*height + a2b*(1-height)*random.random()


def main():
    me = bpy.context.active_object.data
    bm = bmesh.from_edit_mesh(me)
    temp_geom = bmesh.ops.duplicate(bm, geom=[bm.select_history.active])
    temp_face = next(el for el in temp_geom['geom'] if isinstance(el, bmesh.types.BMFace))
    triangles = bmesh.ops.triangulate(bm, faces=[temp_face])['faces']
    surfaces = map(lambda t: t.calc_area(), triangles)
    choices = random.choices(population=triangles, weights=surfaces, k=num_points)
    points = map(point_on_triangle, choices)
    temp_verts = list({v for tri in triangles for v in tri.verts})
    
    for point in points:
        bm.verts.new(point)
    bmesh.ops.delete(bm, geom=temp_verts)
    bmesh.update_edit_mesh(me)
    
    
if __name__ == "__main__":
    main()
