import bmesh

bm=bmesh.new()
verts=[bm.verts.new(co) for co in ((0,0,0),(1,0,0),(0,1,0),(0,-1,0),(0,0,1),(2,0,0),(9,9,9))]
faces=[bm.faces.new(tuple(verts[i] for i in ids)) for ids in ((0,1,2),(1,0,3),(0,1,4))]
wire=bm.edges.new((verts[1],verts[5]))
shared=next(edge for edge in bm.edges if set(edge.verts)=={verts[0],verts[1]})
linked_edges=verts[0].link_edges
linked_faces=verts[0].link_faces
radial_faces=shared.link_faces
assert len(linked_edges)==4 and set(linked_faces)==set(faces)
assert set(radial_faces)==set(faces)  # Three faces share this nonmanifold edge.
assert len(wire.link_faces)==0 and len(verts[6].link_edges)==len(verts[6].link_faces)==0
assert all(len(edge.link_faces)==(0 if edge==wire else 3 if edge==shared else 1) for edge in bm.edges)
assert all(verts[0] in edge.verts for edge in linked_edges)
assert all(verts[0] in face.verts for face in linked_faces)
assert faces[0] in linked_faces and wire not in linked_edges and 3 not in linked_faces
assert linked_faces[:]==list(linked_faces)
assert linked_faces[-1]==list(linked_faces)[-1]
try:linked_faces[::2]
except TypeError:pass
else:raise AssertionError('Stepped adjacency slice accepted')

# Keep the views while the underlying topology changes.
bm.faces.remove(faces[1])
assert set(linked_faces)==set(radial_faces)=={faces[0],faces[2]}
assert len(linked_edges)==4
bm.edges.remove(shared)
assert len(linked_faces)==0 and len(linked_edges)==3
replacement=bm.faces.new((verts[0],verts[2],verts[4]))
assert list(linked_faces)==[replacement]
assert len(linked_edges)==3

# Use the new adjacency to select actual geometry for an existing operator.
selected={vertex for face in linked_faces for vertex in face.verts}
bmesh.ops.translate(bm,verts=list(selected),vec=(0,0,2))
assert tuple(verts[0].co)==(0,0,2)
assert tuple(verts[2].co)==(0,1,2) and tuple(verts[4].co)==(0,0,3)
assert tuple(verts[1].co)==(1,0,0) and tuple(verts[6].co)==(9,9,9)
bm.free()
