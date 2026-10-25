import bmesh,random,math,json,os
random.seed(34127);results=[]
for case in range(200):
    n=4+case%8;points=[]
    for i in range(n):
        angle=2*math.pi*i/n;radius=random.uniform(.6,2)
        points.append((round(math.cos(angle)*radius,4),round(math.sin(angle)*radius,4),0))
    for method in ('BEAUTY','EAR_CLIP'):
        bm=bmesh.new();vertices=[bm.verts.new(p) for p in points];face=bm.faces.new(vertices);bm.normal_update()
        bmesh.ops.triangulate(bm,faces=[face],quad_method='BEAUTY',ngon_method=method)
        lookup={v:i for i,v in enumerate(vertices)};triangles=[]
        for face in bm.faces:
            indices=[lookup[v] for v in face.verts];start=indices.index(min(indices));triangles.append(indices[start:]+indices[:start])
        results.append(sorted(triangles));bm.free()
with open(os.environ['HB_TRIANGULATION_RESULTS'],'w') as output:json.dump(results,output)
