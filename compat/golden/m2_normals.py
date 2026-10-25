"""Closed-solid winding repair; run in Blender before exposing the operator."""
HB_SYMBOLS={
'bmesh.types.BMFace.index':'Read or write a valid face index; normal repair refreshes sequential indices without reordering faces',
'bmesh.types.BMEdge.index':'Read or write a valid edge index; normal repair refreshes sequential indices without reordering edges',
}
import bpy,bmesh,math

cube_points=((-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1))
cube_faces=((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7))
cube_normals=((0,0,-1),(0,0,1),(0,-1,0),(1,0,0),(0,1,0),(-1,0,0))

def append(bm,points,outward,mask):
    verts=[bm.verts.new(p) for p in points];faces=[]
    for i,indices in enumerate(outward):
        if mask & (1<<i):indices=(indices[0],)+tuple(reversed(indices[1:]))
        face=bm.faces.new([verts[j] for j in indices]);face.material_index=i%2;face.smooth=bool(i%2)
        faces.append(face)
    return faces

def repair(bm,verts,faces,outward):
    edges=list(bm.edges);before=[tuple(e.verts) for e in edges]
    bm.faces.ensure_lookup_table();bm.faces.index_update()
    for i,f in enumerate(bm.faces):f.index=100+i
    for i,e in enumerate(bm.edges):e.index=100+i
    for i,v in enumerate(bm.verts):v.index=100+i
    assert bmesh.ops.recalc_face_normals(bm,faces=faces[::-1]) is None
    for i,f in enumerate(faces):
        assert tuple(f.verts)==tuple(verts[j] for j in outward[i])
        assert f.is_valid
        assert f.material_index==i%2 and f.smooth==bool(i%2)
        assert abs(f.normal.length-1)<1e-5
        # Face edge loops track the corrected corners; edge endpoint order stays intact.
        for k,e in enumerate(f.edges):
            assert set(e.verts)=={f.verts[k],f.verts[(k+1)%len(f.verts)]}
    assert list(bm.edges)==edges and [tuple(e.verts) for e in edges]==before
    assert [f.index for f in bm.faces]==list(range(len(bm.faces)))
    assert [e.index for e in bm.edges]==list(range(len(bm.edges)))
    assert [v.index for v in bm.verts]==list(range(len(bm.verts)))
    assert all(bm.faces[i] is f for i,f in enumerate(list(bm.faces)))
    assert bmesh.ops.recalc_face_normals(bm,faces=faces) is None
    assert all(tuple(f.verts)==tuple(verts[j] for j in outward[i]) for i,f in enumerate(faces))

def publish(bm):
    mesh=bpy.data.meshes.new('Repaired');bm.to_mesh(mesh)
    obj=bpy.data.objects.new('Repaired',mesh);bpy.context.collection.objects.link(obj);bm.free()

# Every possible reversal of a six-face box, including entirely inside-out.
for mask in range(64):
    bm=bmesh.new();faces=append(bm,cube_points,cube_faces,mask);verts=list(bm.verts)
    repair(bm,verts,faces,cube_faces)
    for f,normal in zip(faces,cube_normals):assert all(abs(a-b)<1e-5 for a,b in zip(f.normal,normal))
    publish(bm)

# Slanted faces and a concave L profile; no face-order comparison relaxation.
tetra_points=((0,0,0),(3,0,0),(0,2,0),(.2,.3,4))
tetra_faces=((0,2,1),(0,1,3),(1,2,3),(2,0,3))
outline=((0,0),(3,0),(3,1),(1,1),(1,3),(0,3))
prism_points=tuple((x,y,z) for z in (0,2) for x,y in outline)
prism_faces=((0,5,4,3,2,1),(6,7,8,9,10,11))+tuple((i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6))
for points,faces,mask in ((tetra_points,tetra_faces,10),(prism_points,prism_faces,173)):
    bm=bmesh.new();created=append(bm,points,faces,mask);repair(bm,list(bm.verts),created,faces);publish(bm)

# A closed annular solid has a through-hole, so convex-only orientation is insufficient.
n=8
annulus_points=tuple((r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for z in (0,1) for r in (2,1) for i in range(n))
annulus_faces=[]
for i in range(n):
    j=(i+1)%n
    annulus_faces.extend(((i,j,j+2*n,i+2*n),(n+j,n+i,3*n+i,3*n+j),(2*n+i,2*n+j,3*n+j,3*n+i),(j,i,n+i,n+j)))
bm=bmesh.new();annular=append(bm,annulus_points,annulus_faces,0xA357C41B)
repair(bm,list(bm.verts),annular,annulus_faces);publish(bm)

# Whole disconnected components can be selected independently, including nested shells.
bm=bmesh.new();fa=append(bm,cube_points,cube_faces,21);a=list(bm.verts)
fb=append(bm,[tuple(x*.3 for x in p) for p in cube_points],cube_faces,42);b=list(bm.verts)[8:]
untouched=[tuple(f.verts) for f in fb]
repair(bm,a,fa,cube_faces)
assert [tuple(f.verts) for f in fb]==untouched
repair(bm,b,fb,cube_faces);publish(bm)
for scale,offset in ((.001,0),(2,10000)):
    bm=bmesh.new();scaled_faces=append(bm,[tuple(x*scale+offset for x in p) for p in cube_points],cube_faces,35);v=list(bm.verts)
    repair(bm,v,scaled_faces,cube_faces);publish(bm)

bm=bmesh.new();empty_faces=append(bm,cube_points,cube_faces,63)
before=[tuple(face.verts) for face in empty_faces]
try:bmesh.ops.recalc_face_normals(bm,faces=empty_faces+empty_faces[:1])
except ValueError:pass
else:raise AssertionError('Duplicate handles must fail')
assert bmesh.ops.recalc_face_normals(bm) is None
assert [tuple(face.verts) for face in empty_faces]==before
bm.free()

# Even an empty selection refreshes existing face normals.
bm=bmesh.new();v=[bm.verts.new(p) for p in ((10,0,0),(11,0,0),(10,1,0))]
face=bm.faces.new(v);assert tuple(face.normal)==(0,0,0)
assert bmesh.ops.recalc_face_normals(bm) is None
assert tuple(face.normal)==(0,0,1)
closed=append(bm,cube_points,cube_faces,5)
for vertex in v:vertex.co.z=vertex.co.x-10
assert bmesh.ops.recalc_face_normals(bm,faces=closed) is None
assert abs(face.normal.x+2**-.5)<1e-5 and abs(face.normal.z-2**-.5)<1e-5
publish(bm)
