import bpy

bpy.ops.mesh.primitive_cube_add()
obj=bpy.context.object
material=bpy.data.materials.new('Paint');material.use_nodes=True
p=material.node_tree.nodes['Principled BSDF']

faces=[p for p in obj.data.polygons if not p.use_smooth]
indices={p.index for p in obj.data.polygons if not p.use_smooth}
flags={p.index:p.use_smooth for p in obj.data.polygons}
face_set={p for p in obj.data.polygons};face_set.add(next(iter(face_set)))
assert len(face_set.copy())==6
generator=(p for p in obj.data.polygons)
assert not next(generator).use_smooth
generator.close()
assert len(faces)==len(indices)==len(flags)==6
assert not any(p.use_smooth for p in obj.data.polygons)

# The leftmost iterable sees the outer p; nested expressions have private p's.
assert len([p.inputs for p in [p]])==1
assert len([p.inputs for p in [p] if all(not p.use_smooth for p in obj.data.polygons)])==1
assert len([q for p in [obj] for q in p.data.polygons if not q.use_smooth])==6

def enclosing_global():
    values=[p.use_smooth for p in obj.data.polygons]
    p.inputs['Base Color'].default_value=(.25,.5,.75,1)
    return values

def enclosing_argument(p):
    values={p.index:p.use_smooth for p in obj.data.polygons}
    p.inputs['Base Color'].default_value=(.25,.5,.75,1)
    return values

def enclosing_walrus():
    # This p is function-local, unlike the comprehension's polygon target.
    values=[(p:=polygon) for polygon in obj.data.polygons]
    assert not p.use_smooth
    return len(values)

assert len(enclosing_global())==len(enclosing_argument(p))==enclosing_walrus()==6
p.inputs['Base Color'].default_value=(.25,.5,.75,1)
obj.data.materials.append(material)
