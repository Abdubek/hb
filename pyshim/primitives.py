"""Blender-referenced object-mode mesh primitives; records live in Rust."""
def _primitive_options(path,enter_editmode,align,location,rotation,scale):
    if enter_editmode or align!='WORLD':raise UnsupportedError(path,'Only object-mode WORLD-aligned creation is supported.')
    for value in (location,rotation,scale):
        if len(value)!=3:raise ValueError('Expected three transform components')
        if not all(math.isfinite(float(x)) for x in value):raise ValueError('Transform components must be finite')

def _primitive_mesh(name,vertices,edges,faces,uv,location,rotation):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,edges,faces)
    if uv is not None:mesh._set('uv_layers',[{'name':'UVMap','data':[[f32(x) for x in p] for p in uv]}])
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    obj.location=location;obj.rotation_euler=rotation
    select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
    return {'FINISHED'}

def _ring(n,radius,reverse=False):
    # Symmetric octants avoid trig residuals at the coordinate axes.
    result=[]
    for i in range(n):
        angle=2*math.pi*i/n
        x,y=math.sin(angle),math.cos(angle)
        if abs(x)<1e-15:x=0.
        if abs(y)<1e-15:y=0.
        result.append((f32(f32(-x if reverse else x)*radius),f32(f32(y)*radius)))
    return result

def primitive_plane_add(*,size=2.,calc_uvs=True,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.mesh.primitive_plane_add',enter_editmode,align,location,rotation,scale)
    s=f32(max(0.,min(1e12,float(size))))/2
    return _primitive_mesh('Plane',[(-s,-s,0),(s,-s,0),(-s,s,0),(s,s,0)],[],[(0,1,3,2)],[(0,0),(1,0),(1,1),(0,1)] if calc_uvs else None,location,rotation)

def primitive_circle_add(*,vertices=32,radius=1.,fill_type='NOTHING',calc_uvs=True,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.mesh.primitive_circle_add',enter_editmode,align,location,rotation,scale)
    if fill_type not in ('NOTHING','NGON','TRIFAN'):raise TypeError('Invalid fill_type')
    n=max(3,min(10000000,int(vertices)));r=f32(max(0.,min(1e12,float(radius))))
    ring=_ring(n,r,True);unit=_ring(n,1.,True)
    v=[(x,y,0) for x,y in ring];f=[];e=[]
    if fill_type=='TRIFAN':
        v.insert(0,(0,0,0));unit.insert(0,(0,0))
        f=[(0,i+1,(i+1)%n+1) for i in range(n)]
    elif fill_type=='NGON':f=[tuple(range(n))]
    else:e=[(i,(i+1)%n) for i in range(n)]
    uv=[(f32(.5+f32(unit[i][0]*.5)),f32(.5+f32(unit[i][1]*.5))) for face in f for i in face] if calc_uvs else None
    return _primitive_mesh('Circle',v,e,f,uv,location,rotation)

def primitive_cylinder_add(*,vertices=32,radius=1.,depth=2.,end_fill_type='NGON',calc_uvs=True,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.mesh.primitive_cylinder_add',enter_editmode,align,location,rotation,scale)
    if end_fill_type not in ('NOTHING','NGON','TRIFAN'):raise TypeError('Invalid end_fill_type')
    n=max(3,min(10000000,int(vertices)));r=f32(max(0.,min(1e12,float(radius))));d=f32(max(0.,min(1e12,float(depth))))/2
    if r==0:return _primitive_mesh('Cylinder',[(0.,0.,-d),(0.,0.,d)],[(1,0)],[],[] if calc_uvs else None,location,rotation)
    ring=_ring(n,r);unit=_ring(n,1.)
    v=[];f=[];uv=[];offset=2 if end_fill_type=='TRIFAN' else 0
    if offset:v=[(0,0,-d),(0,0,d)]
    for x,y in ring:v.extend([(x,y,-d),(x,y,d)])
    def cap(face,top):
        f.append(face)
        for ix in face:
            x,y=(0,0) if ix<offset else unit[(ix-offset)//2]
            uv.append((f32((.25 if top else .75)+f32(x*f32(.24))),f32(.25+f32(y*f32(.24)))))
    u=1.;step=f32(1/n)
    for i in range(n):
        a=offset+2*i;b=offset+2*((i+1)%n)
        if offset:
            cap([0,a,b],False);cap([1,b+1,a+1],True)
        if end_fill_type=='NGON' and i==max(2,n-2):cap([3,1]+list(range(2*n-1,3,-2)),True)
        f.append([a,a+1,b+1,b]);next_u=f32(u-step)
        v0=0. if end_fill_type=='NOTHING' else .5
        uv.extend([(u,v0),(u,1.),(next_u,1.),(next_u,v0)]);u=next_u
    if end_fill_type=='NGON':cap(list(range(0,2*n,2)),False)
    return _primitive_mesh('Cylinder',v,[],f,uv if calc_uvs else None,location,rotation)

bpy.ops.mesh._values.update(primitive_plane_add=primitive_plane_add,primitive_circle_add=primitive_circle_add,primitive_cylinder_add=primitive_cylinder_add)

def _construction_float(value):
    value=f32(value)
    if not math.isfinite(value):raise ValueError('Primitive dimensions must be finite')
    return value

def _sphere_sincos(k,n):
    # Rational octants keep axial and symmetric latitude coordinates exact.
    k%=n;quadrant=(4*k)//n;u=(4*k)%n
    if 2*u>n:
        angle=f32(f32(math.pi/2)*f32((n-u)/n));s=f32(math.cos(angle));c=f32(math.sin(angle))
    else:
        angle=f32(f32(math.pi/2)*f32(u/n));s=f32(math.sin(angle));c=f32(math.cos(angle))
    return ((s,c),(c,-s),(-s,-c),(-c,s))[quadrant]

# Construction indices are stable for UV spheres; see compat/DEVIATIONS.md.
def _sphere_geometry(n,rings,radius):
    if n*(rings-1)+2>100000:raise UnsupportedError('UV sphere','Construction limit is 100,000 vertices; reduce segment/ring counts.')
    if not math.isfinite(radius) or radius<=0:raise UnsupportedError('UV sphere radius','Use a positive radius; degenerate sphere merging is not supported.')
    profile=[(0.,f32(radius*_sphere_sincos(j,2*rings)[0]),f32(radius*_sphere_sincos(j,2*rings)[1])) for j in range(1,rings)]
    sine=f32(math.sin(f32(2*math.pi/n)));cosine=f32(math.cos(f32(2*math.pi/n)));rotated=[]
    for _ in range(n):
        profile=[(f32(f32(x*cosine)+f32(y*sine)),f32(f32(y*cosine)-f32(x*sine)),z) for x,y,z in profile]
        rotated.append(profile)
    # Closing the spin keeps the final ring, including its float32 roundoff.
    verts=[(0.,0.,radius)]+[v for ring in rotated[-1:]+rotated[:-1] for v in ring]
    south=len(verts);verts.append((0,0,-radius));faces=[];uv=[]
    def ix(i,j):return 1+(i%n)*(rings-1)+j-1
    offset=(3*n)//4
    for i in range(n):
        u0=((offset-i)%n)/n
        if u0==0:u0=1.
        u1=u0-1/n;mid=(u0+u1)/2
        faces.append([ix(i,1),0,ix(i+1,1)]);uv.extend([(u0,1-1/rings),(mid,1),(u1,1-1/rings)])
        for j in range(1,rings-1):
            faces.append([ix(i,j+1),ix(i,j),ix(i+1,j),ix(i+1,j+1)])
            uv.extend([(u0,1-(j+1)/rings),(u0,1-j/rings),(u1,1-j/rings),(u1,1-(j+1)/rings)])
        faces.append([south,ix(i,rings-1),ix(i+1,rings-1)]);uv.extend([(mid,0),(u0,1/rings),(u1,1/rings)])
    return verts,[],faces,uv

def primitive_uv_sphere_add(*,segments=32,ring_count=16,radius=1.,calc_uvs=True,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.mesh.primitive_uv_sphere_add',enter_editmode,align,location,rotation,scale)
    n=max(3,min(100000,int(segments)));rings=max(3,min(100000,int(ring_count)))
    r=max(0.,min(1e12,_construction_float(radius)))
    if r==0:
        if calc_uvs:raise UnsupportedError('UV sphere radius','Zero-radius Blender UVs are non-finite; use calc_uvs=False')
        if (n+1)*(rings+1)>100000:raise UnsupportedError('UV sphere','Degenerate construction is limited to 100,000 vertices')
        stride=rings+1;faces=[[i*stride+j,i*stride+j-1,(i+1)*stride+j-1,(i+1)*stride+j] for i in range(n) for j in range(1,stride)]
        return _primitive_mesh('Sphere',[(0.,0.,0.)]*((n+1)*stride),[],faces,None,location,rotation)
    verts,edges,faces,uv=_sphere_geometry(n,rings,r)
    if tuple(scale)!=(0.,0.,0.):verts=[tuple(f32(v[i]*scale[i]) for i in range(3)) for v in verts]
    return _primitive_mesh('Sphere',verts,edges,faces,uv if calc_uvs else None,location,rotation)

def _cone_geometry(n,r1,r2,depth,fill):
    if n>100000:raise UnsupportedError('Cone','Construction limit is 100,000 segments; reduce vertices.')
    if not all(math.isfinite(v) for v in (r1,r2,depth)):raise ValueError('Primitive dimensions must be finite')
    if r1==0 and r2==0:raise UnsupportedError('Cone radii','At least one radius must be positive; degenerate BMesh cone topology is unsupported.')
    half=f32(depth*.5);unit=_ring(n,1.);verts=[];radial=[];faces=[];uv=[]
    def vertex(p,xy):
        i=len(verts);verts.append(p);radial.append(xy);return i
    bottom_center=vertex((0,0,-half),(0,0)) if fill=='TRIFAN' and r1 else None
    top_center=vertex((0,0,half),(0,0)) if fill=='TRIFAN' and r2 else None
    lower=[];upper=[]
    if not r1:lower=[vertex((0,0,-half),(0,0))]*n
    for x,y in unit:
        if r1:lower.append(vertex((f32(x*r1),f32(y*r1),-half),(x,y)))
        if r2:upper.append(vertex((f32(x*r2),f32(y*r2),half),(x,y)))
    if not r2:upper=[vertex((0,0,half),(0,0))]*n
    def radial_face(face,top):
        faces.append(face)
        center=(.25 if top else .75) if fill!='NOTHING' else .5
        factor=f32(.24) if fill!='NOTHING' else .5
        for ix in face:
            x,y=radial[ix];uv.append((f32(center+f32(x*factor)),f32((.25 if fill!='NOTHING' else .5)+f32(y*factor))))
    u=1.;step=f32(1/n)
    for i in range(n):
        j=(i+1)%n
        if bottom_center is not None:radial_face([bottom_center,lower[i],lower[j]],False)
        if top_center is not None:radial_face([top_center,upper[j],upper[i]],True)
        if fill=='NGON' and i==(max(2,n-2) if r2 else n-2):
            if r2:radial_face([upper[1],upper[0]]+list(reversed(upper[2:])),True)
            elif r1:radial_face(lower[:],False)
        if not r1:radial_face([lower[i],upper[i],upper[j]],False)
        elif not r2:radial_face([lower[i],upper[i],lower[j]],True)
        else:
            faces.append([lower[i],upper[i],upper[j],lower[j]]);next_u=f32(u-step);v0=0. if fill=='NOTHING' else .5
            uv.extend([(u,v0),(u,1),(next_u,1),(next_u,v0)]);u=next_u
    if fill=='NGON' and r1 and r2:radial_face(lower[:],False)
    return verts,[],faces,uv

def primitive_cone_add(*,vertices=32,radius1=1.,radius2=0.,depth=2.,end_fill_type='NGON',calc_uvs=True,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.mesh.primitive_cone_add',enter_editmode,align,location,rotation,scale)
    if calc_uvs and tuple(scale) not in ((0.,0.,0.),(1.,1.,1.)):
        raise UnsupportedError('bpy.ops.mesh.primitive_cone_add(scale=...)','Generated UVs with a scaled cone are unsupported; use calc_uvs=False or set object.scale after creation.')
    if end_fill_type not in ('NOTHING','NGON','TRIFAN'):raise TypeError('Invalid end_fill_type')
    n=max(3,min(10000000,int(vertices)))
    r1,r2,d=[f32(max(0.,min(1e12,_construction_float(v)))) for v in (radius1,radius2,depth)]
    if r1==0 and r2==0:return _primitive_mesh('Cone',[(0.,0.,f32(-d*.5)),(0.,0.,f32(d*.5))],[(1,0)],[],[] if calc_uvs else None,location,rotation)
    v,e,f,uv=_cone_geometry(n,r1,r2,d,end_fill_type)
    if tuple(scale)!=(0.,0.,0.):v=[tuple(f32(p[i]*scale[i]) for i in range(3)) for p in v]
    return _primitive_mesh('Cone',v,e,f,uv if calc_uvs else None,location,rotation)

bpy.ops.mesh._values.update(primitive_uv_sphere_add=primitive_uv_sphere_add,primitive_cone_add=primitive_cone_add)


def primitive_torus_add(*,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),major_segments=48,minor_segments=12,mode='MAJOR_MINOR',major_radius=1.,minor_radius=.25,abso_major_rad=1.25,abso_minor_rad=.75,generate_uvs=True):
    _primitive_options('bpy.ops.mesh.primitive_torus_add',False,align,location,rotation,(1,1,1))
    if mode not in ('MAJOR_MINOR','EXT_INT'):raise TypeError('Invalid torus radius mode')
    n=max(3,min(256,int(major_segments)));m=max(3,min(256,int(minor_segments)))
    major,minor,outer,inner=[max(0.,min(10000.,_construction_float(v))) for v in (major_radius,minor_radius,abso_major_rad,abso_minor_rad)]
    if mode=='EXT_INT':
        minor=f32((outer-inner)/2);major=f32(outer-minor)
    if not 0<=minor<=major:raise UnsupportedError('bpy.ops.mesh.primitive_torus_add','Use a ring torus with 0 < minor_radius < major_radius (or outer radius > inner radius > 0). Degenerate and self-intersecting tori are unsupported.')
    verts=[];faces=[];uv=[]
    for i in range(n):
        # Blender's rotation matrix receives an angle wrapped with float32 arithmetic.
        angle=f32(f32(f32(2*math.pi*i/n)+f32(math.pi))%f32(2*math.pi)-f32(math.pi))
        c,s=f32(math.cos(angle)),f32(math.sin(angle))
        for j in range(m):
            a=2*math.pi*j/m;r=f32(major+minor*math.cos(a))
            verts.append((f32(r*c),f32(r*s),f32(minor*math.sin(a))))
            faces.append([i*m+j,((i+1)%n)*m+j,((i+1)%n)*m+(j+1)%m,i*m+(j+1)%m])
            u=((i+(n+1)//2)%n)/n;v=((j+(m+1)//2)%m)/m
            uv.extend([(u,v),(u+1/n,v),(u+1/n,v+1/m),(u,v+1/m)])
    return _primitive_mesh('Torus',verts,[],faces,uv if generate_uvs else None,location,rotation)

bpy.ops.mesh._values['primitive_torus_add']=primitive_torus_add

# Blender 4.5.9 base icosahedron and unfolded triangle UV coordinates,
# measured before implementation (compat/golden/m3_ico_sphere.py).
_ICO_VERTS = [[0.0, 0.0, -1.0], [0.7236, -0.52572, -0.447215], [-0.276385, -0.85064, -0.447215], [-0.894425, 0.0, -0.447215], [-0.276385, 0.85064, -0.447215], [0.7236, 0.52572, -0.447215], [0.276385, -0.85064, 0.447215], [-0.7236, -0.52572, 0.447215], [-0.7236, 0.52572, 0.447215], [0.276385, 0.85064, 0.447215], [0.894425, 0.0, 0.447215], [0.0, 0.0, 1.0]]
_ICO_FACES = [[0, 1, 2], [1, 0, 5], [0, 2, 3], [0, 3, 4], [0, 4, 5], [1, 5, 10], [2, 1, 6], [3, 2, 7], [4, 3, 8], [5, 4, 9], [1, 10, 6], [2, 6, 7], [3, 7, 8], [4, 8, 9], [5, 9, 10], [6, 10, 11], [7, 6, 11], [8, 7, 11], [9, 8, 11], [10, 9, 11]]
_ICO_UV = [[0.181819, 0.0], [0.272728, 0.157461], [0.09091, 0.157461], [0.272728, 0.157461], [0.363637, 0.0], [0.454546, 0.157461], [0.909091, 0.0], [1.0, 0.157461], [0.818182, 0.157461], [0.727273, 0.0], [0.818182, 0.157461], [0.636364, 0.157461], [0.545455, 0.0], [0.636364, 0.157461], [0.454546, 0.157461], [0.272728, 0.157461], [0.454546, 0.157461], [0.363637, 0.314921], [0.09091, 0.157461], [0.272728, 0.157461], [0.181819, 0.314921], [0.818182, 0.157461], [1.0, 0.157461], [0.909091, 0.314921], [0.636364, 0.157461], [0.818182, 0.157461], [0.727273, 0.314921], [0.454546, 0.157461], [0.636364, 0.157461], [0.545455, 0.314921], [0.272728, 0.157461], [0.363637, 0.314921], [0.181819, 0.314921], [0.09091, 0.157461], [0.181819, 0.314921], [0.0, 0.314921], [0.818182, 0.157461], [0.909091, 0.314921], [0.727273, 0.314921], [0.636364, 0.157461], [0.727273, 0.314921], [0.545455, 0.314921], [0.454546, 0.157461], [0.545455, 0.314921], [0.363637, 0.314921], [0.181819, 0.314921], [0.363637, 0.314921], [0.272728, 0.472382], [0.0, 0.314921], [0.181819, 0.314921], [0.09091, 0.472382], [0.727273, 0.314921], [0.909091, 0.314921], [0.818182, 0.472382], [0.545455, 0.314921], [0.727273, 0.314921], [0.636364, 0.472382], [0.363637, 0.314921], [0.545455, 0.314921], [0.454546, 0.472382]]

def primitive_ico_sphere_add(*,subdivisions=2,radius=1.,calc_uvs=True,enter_editmode=False,align='WORLD',location=(0.,0.,0.),rotation=(0.,0.,0.),scale=(0.,0.,0.)):
    _primitive_options('bpy.ops.mesh.primitive_ico_sphere_add',enter_editmode,align,location,rotation,scale)
    level=max(1,min(10,int(subdivisions)))
    if level>7:raise UnsupportedError('Ico sphere subdivisions','Use subdivisions 1..7; the construction limit is 100,000 vertices.')
    radius=f32(max(0.,min(1e12,_construction_float(radius))))
    n=1<<(level-1);vertices=[];faces=[];uv=[];indices={}
    for fi,base in enumerate(_ICO_FACES):
        grid={};tex={}
        for i in range(n+1):
            for j in range(n+1-i):
                weights=(n-i-j,i,j)
                key=tuple(sorted((v,w) for v,w in zip(base,weights) if w))
                if key not in indices:
                    point=[sum(_ICO_VERTS[v][axis]*w for v,w in zip(base,weights))/n for axis in range(3)]
                    length=math.sqrt(sum(x*x for x in point)) if level>1 else 1.
                    point=[f32(x*radius/length) for x in point]
                    if tuple(scale)!=(0.,0.,0.):point=[f32(x*s) for x,s in zip(point,scale)]
                    indices[key]=len(vertices);vertices.append(point)
                grid[i,j]=indices[key]
                tex[i,j]=tuple(f32(sum(_ICO_UV[3*fi+k][axis]*weights[k] for k in range(3))/n) for axis in range(2))
        def triangle(corners):
            faces.append([grid[c] for c in corners]);uv.extend(tex[c] for c in corners)
        for i in range(n):
            for j in range(n-i):
                triangle(((i,j),(i+1,j),(i,j+1)))
                if i+j<n-1:triangle(((i+1,j),(i+1,j+1),(i,j+1)))
    return _primitive_mesh('Icosphere',vertices,[],faces,uv if calc_uvs else None,location,rotation)

bpy.ops.mesh._values['primitive_ico_sphere_add']=primitive_ico_sphere_add
