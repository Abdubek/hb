"""Compare oriented planar patches, retaining holes, seams and corner attributes.

Different solvers partition planar holes and retain collinear vertices differently.
Cancel only internal edges with matching attributes, then compare patch planes,
areas and oriented boundaries. Existing MANIFOLD goldens remain unchanged.
"""
import math

def records(mesh):
    result=[];start=0
    for face in mesh['faces']:
        corners=[]
        for i,v in enumerate(face):
            record={'position':mesh['vertices'][v]}
            for field in ('uv','normals','colors'):
                if mesh.get(field):record[field]=mesh[field][start+i]
            corners.append(record)
        start+=len(face)
        changed=True
        while changed and len(corners)>3:
            changed=False
            for i,c in enumerate(corners):
                a=corners[i-1]['position'];b=c['position'];d=corners[(i+1)%len(corners)]['position']
                x=[b[k]-a[k] for k in range(3)];y=[d[k]-b[k] for k in range(3)]
                cross=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]]
                if sum(v*v for v in cross)<=1e-10*sum(v*v for v in x)*sum(v*v for v in y) and sum(x[k]*y[k] for k in range(3))>=0:
                    corners.pop(i);changed=True;break
        result.append(corners)
    return result

def compare(expected,actual):
    a,b=records(expected),records(actual)
    assert len(a)==len(b),('face count',len(a),len(b))
    used=set()
    def near(x,y,tolerance):return len(x)==len(y) and all(abs(u-v)<=tolerance for u,v in zip(x,y))
    for face in a:
        found=None
        for j,other in enumerate(b):
            if j in used or len(face)!=len(other):continue
            for shift in range(len(face)):
                rotated=other[shift:]+other[:shift]
                if all(near(x['position'],y['position'],1e-5) for x,y in zip(face,rotated)):
                    found=(j,rotated);break
            if found:break
        assert found,('oriented boundary',face)
        used.add(found[0])
        for x,y in zip(face,found[1]):
            for field in ('uv','colors','normals'):
                if field in x:
                    assert field in y,('missing attribute',field)
                    assert near(x[field],y[field],1e-4 if field=='normals' else 1e-5),(field,x[field],y[field])

def actual_mesh(scene,name):
    obj=next(o for o in scene['objects'] if o['name']==name)
    m=next(m for m in scene['meshes'] if m['id']==obj['data']['id'])
    return dict(vertices=m['vertices'],faces=m['faces'],uv=m['uv_layers'][0]['data'] if m['uv_layers'] else [],normals=m['loop_normals'],colors=m['colors'])

# Different Boolean algorithms can bridge a planar face with a hole differently.
# Cancel only oppositely directed edges with matching corner attributes. Seams,
# hole winding and boundary coordinates remain observable and must match.
def patches(mesh):
    groups=[]
    def near(a,b,tol=1e-5):return len(a)==len(b) and all(abs(x-y)<=tol for x,y in zip(a,b))
    def same(a,b):return a.keys()==b.keys() and all(near(a[k],b[k],1e-4 if k=='normals' else 1e-5) for k in a)
    for face in records(mesh):
        normal=[0.,0.,0.]
        for a,b in zip(face,face[1:]+face[:1]):
            a,b=a['position'],b['position']
            for k in range(3):normal[k]+=a[(k+1)%3]*b[(k+2)%3]-a[(k+2)%3]*b[(k+1)%3]
        length=math.sqrt(sum(x*x for x in normal));assert length>1e-10
        normal=[x/length for x in normal];distance=sum(x*y for x,y in zip(normal,face[0]['position']))
        group=next((g for g in groups if near(g[0],normal) and abs(g[1]-distance)<=1e-5),None)
        if group is None:group=[normal,distance,[],0.];groups.append(group)
        group[3]+=length/2
        edges=group[2]
        for a,b in zip(face,face[1:]+face[:1]):
            reverse=next((i for i,(x,y) in enumerate(edges) if same(a,y) and same(b,x)),None)
            if reverse is None:edges.append((a,b))
            else:edges.pop(reverse)
    for _,_,edges,_ in groups:
        changed=True
        while changed:
            changed=False
            for i,(a,b) in enumerate(edges):
                following=[j for j,(x,_) in enumerate(edges) if same(b,x)]
                previous=[j for j,(_,y) in enumerate(edges) if same(b,y)]
                if len(following)!=1 or len(previous)!=1:continue
                j=following[0];d=edges[j][1]
                x=[b['position'][k]-a['position'][k] for k in range(3)];y=[d['position'][k]-b['position'][k] for k in range(3)]
                lx=math.sqrt(sum(v*v for v in x));ly=math.sqrt(sum(v*v for v in y))
                if not lx or not ly:continue
                cross=[x[1]*y[2]-x[2]*y[1],x[2]*y[0]-x[0]*y[2],x[0]*y[1]-x[1]*y[0]]
                if math.sqrt(sum(v*v for v in cross))>1e-5*(lx+ly) or sum(x[k]*y[k] for k in range(3))<0:continue
                if any(not near(b[k],[(u*ly+v*lx)/(lx+ly) for u,v in zip(a[k],d[k])],1e-4 if k=='normals' else 1e-5) for k in b if k!='position'):continue
                for index in sorted((i,j),reverse=True):edges.pop(index)
                edges.append((a,d));changed=True;break
    return groups

compare_faces=compare
def compare(expected,actual):
    a,b=patches(expected),patches(actual)
    assert len(a)==len(b),('oriented planes',len(a),len(b))
    def near(x,y,tol=1e-5):return len(x)==len(y) and all(abs(u-v)<=tol for u,v in zip(x,y))
    used=set()
    for normal,distance,edges,area in a:
        choices=[(j,g) for j,g in enumerate(b) if j not in used and near(normal,g[0]) and abs(distance-g[1])<1e-5]
        assert len(choices)==1,('plane',normal,distance)
        index,group=choices[0];used.add(index)
        assert abs(area-group[3])<=1e-5*max(1,area),('planar area',area,group[3])
        assert len(edges)==len(group[2]),('boundary/seam edges',len(edges),len(group[2]))
        matched=set()
        for edge in edges:
            choices=[(j,other) for j,other in enumerate(group[2]) if j not in matched and all(near(x['position'],y['position']) for x,y in zip(edge,other))]
            assert choices,('oriented boundary edge',edge)
            index,other=choices[0];matched.add(index)
            for x,y in zip(edge,other):
                for field in x:
                    assert field in y,('missing attribute',field)
                    assert near(x[field],y[field],1e-4 if field=='normals' else 1e-5),(field,x[field],y[field])
