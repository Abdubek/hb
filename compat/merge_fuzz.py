"""Deterministic remove_doubles representative differential workload."""
import bmesh,json,os,random
rng=random.Random(271828)
results=[]
for case in range(400):
    points=[]
    for i in range(1+case%53):
        points.append(tuple(rng.randrange(-4,5)*.1+(rng.random()*.003 if case%2 else 0) for _ in range(3)))
    distance=(0,.1,.15,.3)[case%4]
    bm=bmesh.new();vertices=[bm.verts.new(point) for point in points]
    selected=vertices if case%3 else vertices[::2]
    bmesh.ops.remove_doubles(bm,verts=selected,dist=distance)
    results.append([i for i,v in enumerate(vertices) if v.is_valid]);bm.free()
with open(os.environ['HB_MERGE_RESULTS'],'w') as output:json.dump(results,output)
