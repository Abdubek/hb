"""Legacy POLY/BEZIER control data, evaluated into the shared surface representation."""
_CURVE_DIRTY=set()

def _curve_number(value,minimum=-10000.,maximum=10000.):
    value=f32(value)
    if not math.isfinite(value) or not f32(minimum)<=value<=f32(maximum):raise UnsupportedError('bpy.types.Curve','Finite curve values must remain within the documented bounds')
    return value

class Curve(DataBlock):
    _kind='meshes';_path='bpy.types.Curve'
    def _curve(self):return DataBlock._read(self,'curve')
    def _read(self,field):
        if field in ('name','materials','material_indices','vertices','faces'):return DataBlock._read(self,field)
        return self._curve()[field]
    def _set(self,field,value):
        if field in ('name','materials','material_indices'):return DataBlock._set(self,field,value)
        record=self._curve();record[field]=value;DataBlock._set(self,'curve',record);_CURVE_DIRTY.add(self._id)
    dimensions=prop('dimensions',str,choices=('3D',))
    fill_mode=prop('fill_mode',str,choices=('FULL',))
    twist_mode=prop('twist_mode',str,choices=('MINIMUM',))
    bevel_mode=prop('bevel_mode',str,choices=('ROUND',))
    resolution_u=prop('resolution_u',int,1,1024)
    bevel_resolution=property(lambda self:self._read('bevel_resolution'),lambda self,v:self._set('bevel_resolution',int(_curve_number(int(v),0,8))))
    bevel_depth=property(lambda self:self._read('bevel_depth'),lambda self,v:self._set('bevel_depth',_curve_number(v,0,100)))
    extrude=property(lambda self:0.,lambda self,v:self._constant('extrude',v,0.))
    use_fill_caps=property(lambda self:self._curve().get('use_fill_caps',False),lambda self,v:self._set('use_fill_caps',bool(v)))
    def _constant(self,name,value,expected):
        if value!=expected:raise UnsupportedError(self._path+'.'+name,'This curve option is outside the bounded POLY/round-bevel subset')
    @property
    def splines(self):return CurveSplines(self)
    @property
    def materials(self):return CurveMaterials(self)

class CurveMaterials(Materials):
    _path='bpy.types.Curve.materials'
    def clear(self):
        self._mesh._set('materials',[])
        for spline in self._mesh.splines:spline.material_index=0
    def pop(self,*,index=-1):
        ids=self._ids();i=index if index>=0 else len(ids)+index;key=ids.pop(index);self._mesh._set('materials',ids)
        for spline in self._mesh.splines:
            if spline.material_index>=i:spline.material_index=max(0,spline.material_index-1)
        return wrap('materials',key)

class CurveSpline(Strict):
    _path='bpy.types.Spline'
    def __init__(self,curve,index):self._curve,self._index=curve,index
    def _read(self,field):return self._curve._read('splines')[self._index][field]
    def _set(self,field,value):
        splines=self._curve._read('splines');splines[self._index][field]=value;self._curve._set('splines',splines)
    type=property(lambda self:self._curve._read('splines')[self._index].get('type','POLY'))
    use_cyclic_u=prop('use_cyclic_u',bool)
    use_smooth=prop('use_smooth',bool)
    material_index=prop('material_index',int,0,32767)
    @property
    def points(self):
        if self.type!='POLY':raise UnsupportedError(self._path+'.points','Use bezier_points for BEZIER splines')
        return CurvePoints(self)
    @property
    def bezier_points(self):
        if self.type!='BEZIER':raise UnsupportedError(self._path+'.bezier_points','Use points for POLY splines')
        return BezierPoints(self)

class CurveSplines(Strict):
    _path='bpy.types.Curve.splines'
    def __init__(self,curve):self._curve=curve
    def __len__(self):return len(self._curve._read('splines'))
    def __iter__(self):return (self[i] for i in range(len(self)))
    def __getitem__(self,index):
        if index<0:index+=len(self)
        if not 0<=index<len(self):raise IndexError('Spline index out of range')
        return CurveSpline(self._curve,index)
    def new(self,type):
        if type not in ('POLY','BEZIER'):raise UnsupportedError(self._path+'.new','Supported splines are POLY and BEZIER')
        if len(self)>=64:raise UnsupportedError(self._path,'At most 64 splines per curve')
        point=_bezier_point() if type=='BEZIER' else dict(co=[0.,0.,0.,1.],radius=1.,tilt=0.)
        splines=self._curve._read('splines');splines.append(dict(type=type,points=[point],use_cyclic_u=False,use_smooth=True,material_index=0));self._curve._set('splines',splines)
        return self[-1]
    def clear(self):self._curve._set('splines',[])

class CurvePoint(Strict):
    _path='bpy.types.SplinePoint'
    def __init__(self,spline,index):self._spline,self._index=spline,index
    def _read(self,field):return self._spline._read('points')[self._index][field]
    def _set(self,field,value):
        points=self._spline._read('points');points[self._index][field]=value;self._spline._set('points',points)
    def _co(self,value):
        value=[_curve_number(v) for v in value]
        if len(value)!=4:raise ValueError('POLY point coordinates have four components')
        self._set('co',value)
    co=property(lambda self:VectorView(lambda:self._read('co'),self._co,self._path+'.co'),_co)
    radius=property(lambda self:self._read('radius'),lambda self,v:self._set('radius',_curve_number(v,0,100)))
    tilt=property(lambda self:self._read('tilt'),lambda self,v:self._set('tilt',_curve_number(v,-100,100)))

class CurvePoints(Strict):
    _path='bpy.types.Spline.points'
    def __init__(self,spline):self._spline=spline
    def __len__(self):return len(self._spline._read('points'))
    def __iter__(self):return (self[i] for i in range(len(self)))
    def __getitem__(self,index):
        if index<0:index+=len(self)
        if not 0<=index<len(self):raise IndexError('Point index out of range')
        return CurvePoint(self._spline,index)
    def add(self,count):
        count=int(count)
        if count<0 or len(self)+count>4096:raise UnsupportedError(self._path+'.add','Each spline has at most 4096 points')
        points=self._spline._read('points');points += [dict(co=[0.,0.,0.,1.],radius=1.,tilt=0.) for _ in range(count)];self._spline._set('points',points)

def _bezier_point():
    return dict(co=[0.,0.,0.,1.],radius=1.,tilt=0.,handle_left=[0.,0.,0.],handle_right=[0.,0.,0.],handle_left_type='FREE',handle_right_type='FREE')

class BezierPoint(CurvePoint):
    _path='bpy.types.BezierSplinePoint'
    def _co(self,value):
        value=[_curve_number(v) for v in value]
        if len(value)!=3:raise ValueError('Bezier coordinates have three components')
        points=self._spline._read('points');point=points[self._index];delta=[value[i]-point['co'][i] for i in range(3)]
        point['co']=value+[1.]
        for field in ('handle_left','handle_right'):point[field]=[_curve_number(point[field][i]+delta[i]) for i in range(3)]
        self._spline._set('points',points)
    co=property(lambda self:VectorView(lambda:self._read('co')[:3],self._co,self._path+'.co'),_co)
    def _effective_handle(self,side):
        if self._read('handle_'+side+'_type') in ('FREE','ALIGNED'):return self._read('handle_'+side)
        spline=self._spline._curve._read('splines')[self._spline._index]
        return list(_bezier_handles(spline)[self._index][0 if side=='left' else 1])
    def _handle(self,side,value):
        value=[_curve_number(v) for v in value]
        if len(value)!=3:raise ValueError('Bezier handles have three components')
        points=self._spline._read('points');point=points[self._index];field='handle_'+side;point[field]=value
        other='handle_'+('right' if side=='left' else 'left');delta=Vector(value)-Vector(point['co'][:3])
        if point[other+'_type']=='ALIGNED' and point[field+'_type']!='FREE' and delta.length>1e-8:
            size=(Vector(point[other])-Vector(point['co'][:3])).length
            point[other]=[_curve_number(v) for v in Vector(point['co'][:3])-delta.normalized()*size]
        self._spline._set('points',points)
    handle_left=property(lambda self:VectorView(lambda:self._effective_handle('left'),lambda v:self._handle('left',v),self._path+'.handle_left'),lambda self,v:self._handle('left',v))
    handle_right=property(lambda self:VectorView(lambda:self._effective_handle('right'),lambda v:self._handle('right',v),self._path+'.handle_right'),lambda self,v:self._handle('right',v))
    handle_left_type=prop('handle_left_type',str,choices=('FREE','VECTOR','AUTO','ALIGNED'))
    handle_right_type=prop('handle_right_type',str,choices=('FREE','VECTOR','AUTO','ALIGNED'))

class BezierPoints(CurvePoints):
    _path='bpy.types.Spline.bezier_points'
    def __getitem__(self,index):
        if index<0:index+=len(self)
        if not 0<=index<len(self):raise IndexError('Bezier point index out of range')
        return BezierPoint(self._spline,index)
    def add(self,count):
        count=int(count)
        if count<0 or len(self)+count>4096:raise UnsupportedError(self._path+'.add','Each spline has at most 4096 control points')
        points=self._spline._read('points');points += [_bezier_point() for _ in range(count)];self._spline._set('points',points)

def _sample_bezier(spline,resolution):
    controls=spline['points'];count=len(controls);cyclic=spline['use_cyclic_u']
    if count<2:return controls
    if (count if cyclic else count-1)*resolution+1>100000:raise UnsupportedError('bpy.types.Curve','Bezier sampling exceeds 100000 points; reduce resolution_u')
    coordinates=[Vector(p['co'][:3]) for p in controls]
    handles=_bezier_handles(spline)
    sampled=[]
    for i in range(count if cyclic else count-1):
        j=(i+1)%count;a=coordinates[i];b=handles[i][1];c=handles[j][0];d=coordinates[j]
        linear=controls[i]['handle_right_type']=='VECTOR' and controls[j]['handle_left_type']=='VECTOR'
        steps=1 if linear else resolution
        for step in range(steps):
            t=step/steps;u=1-t;co=a*(u*u*u)+b*(3*u*u*t)+c*(3*u*t*t)+d*(t*t*t)
            sampled.append(dict(co=list(co)+[1.],radius=controls[i]['radius']*u+controls[j]['radius']*t,tilt=controls[i]['tilt']*u+controls[j]['tilt']*t))
    if not cyclic:sampled.append(dict(co=list(coordinates[-1])+[1.],radius=controls[-1]['radius'],tilt=controls[-1]['tilt']))
    return sampled

def _bezier_handles(spline):
    controls=spline['points'];count=len(controls);cyclic=spline['use_cyclic_u']
    if count<2:return [[Vector(p['handle_left']),Vector(p['handle_right'])] for p in controls]
    coordinates=[Vector(p['co'][:3]) for p in controls];handles=[]
    for i,point in enumerate(controls):
        co=coordinates[i];previous=coordinates[(i-1)%count] if cyclic or i else co*2-coordinates[1]
        following=coordinates[(i+1)%count] if cyclic or i<count-1 else co*2-coordinates[-2]
        before=co-previous;after=following-co
        if before.length<1e-6 or after.length<1e-6:raise UnsupportedError('bpy.types.BezierSplinePoint','Adjacent control points must be separated by at least 1e-6')
        tangent=before.normalized()+after.normalized()
        if tangent.length<1e-6 and 'AUTO' in (point['handle_left_type'],point['handle_right_type']):raise UnsupportedError('bpy.types.BezierSplinePoint','Reversing automatic tangents are unsupported')
        # Ordinary 3D AUTO handles follow the neighboring chord bisector, with
        # lengths capped relative to the shorter adjacent chord. These numeric
        # semantics are independently checked against Blender 4.5.9 probes.
        left_length=min(before.length,5*after.length)
        right_length=min(after.length,5*left_length)
        tangent=tangent.normalized();pair=[]
        for side,sign,neighbor,distance in (('left',-1,previous,left_length),('right',1,following,right_length)):
            kind=point['handle_'+side+'_type']
            if kind=='VECTOR':handle=co+(neighbor-co)/3
            elif kind=='AUTO':handle=co+tangent*(sign*distance/2.5614)
            else:handle=Vector(point['handle_'+side])
            pair.append(handle)
        handles.append(pair)
    return handles

class CurveDatabase(Database):
    def __init__(self):
        self._kind='meshes';Sequence.__init__(self,'bpy.data.curves',lambda:[wrap('meshes',k) for k in request('list',kind='meshes') if request('get',kind='meshes',id=k).get('curve') is not None])
    def new(self,name,type):
        if type not in ('CURVE','FONT'):raise UnsupportedError(self._path+'.new','Use the declared CURVE or FONT subset')
        record=dict(type=type,dimensions='2D',fill_mode='FULL',twist_mode='MINIMUM',bevel_mode='ROUND',resolution_u=12,bevel_resolution=4,bevel_depth=0.,use_fill_caps=False,splines=[])
        if type=='FONT':record.update(body='',font=None,size=1.,space_line=1.,align_x='LEFT',align_y='TOP_BASELINE')
        key=request('new',kind='meshes',name=name,extra={'curve':record});_cache[('meshes',key)]=(TextCurve if type=='FONT' else Curve)(key);_CURVE_DIRTY.add(key);return _cache[('meshes',key)]
    def remove(self,datablock,**kwargs):
        if not isinstance(datablock,Curve):raise TypeError('Expected Curve')
        super().remove(datablock,**kwargs);_CURVE_DIRTY.discard(datablock._id)

bpy.data._values['curves']=CurveDatabase()
bpy.data.meshes._values=lambda:[wrap('meshes',k) for k in request('list',kind='meshes') if request('get',kind='meshes',id=k).get('curve') is None]

def _curve_surface(record):
    if record['type']=='FONT':return _text_surface(record)
    vertices=[];edges=[];faces=[];uv=[];smooth=[];indices=[]
    depth=record['bevel_depth'];segments=4+2*record['bevel_resolution']
    if record['dimensions']!='3D' and record['splines']:raise UnsupportedError('bpy.types.Curve.dimensions','Set dimensions="3D"; planar fill is outside this subset')
    for spline in record['splines']:
        if spline.get('type','POLY')=='BEZIER':spline={**spline,'points':_sample_bezier(spline,record['resolution_u'])}
        points=[Vector(p['co'][:3]) for p in spline['points']];count=len(points);cyclic=spline['use_cyclic_u']
        if count<2:continue
        if cyclic and count<3:raise UnsupportedError('bpy.types.Spline','Cyclic curves require at least three distinct points')
        directions=[points[(i+1)%count]-points[i] for i in range(count if cyclic else count-1)]
        if any(v.length<1e-6 for v in directions):raise UnsupportedError('bpy.types.Spline','Consecutive points must be separated by at least 1e-6')
        directions=[v.normalized() for v in directions]
        base=len(vertices);steps=count if cyclic else count-1
        projected=count*(segments if depth else 1)
        if len(vertices)+projected>100000 or len(faces)+steps*segments+(2 if record.get('use_fill_caps',False) and not cyclic else 0)>100000:raise UnsupportedError('bpy.types.Curve','Evaluated curves are limited to 100000 vertices/faces')
        if not depth:
            vertices += [list(p) for p in points];edges += [[base+i,base+(i+1)%count] for i in range(steps)];continue
        spatial_cycle=cyclic and any(abs(p.z-points[0].z)>1e-6 for p in points)
        tangents=[]
        for i in range(count):
            tangent=directions[0] if i==0 and not cyclic else directions[-1] if i==count-1 and not cyclic else directions[i-1]+directions[i]
            if tangent.length<1e-6:raise UnsupportedError('bpy.types.Spline','Reversing cusps are outside the round-bevel subset')
            tangents.append(tangent.normalized())
        tangent=tangents[0]
        radial=Vector((0,0,1))-tangent*tangent.z
        radial=Vector((0,-1,0)) if radial.length<1e-6 else radial.normalized()
        frames=None
        if spatial_cycle:
            # Parallel transport around the complete loop, then distribute the
            # closure rotation by arc length so the seam has no unique twist.
            def transport(radial,previous,tangent):
                axis=previous.cross(tangent);sine=axis.length;cosine=max(-1.,min(1.,previous.dot(tangent)))
                if sine>1e-7:
                    axis=axis/sine
                    radial=radial*cosine+axis.cross(radial)*sine+axis*axis.dot(radial)*(1-cosine)
                elif cosine<0:raise UnsupportedError('bpy.types.Spline','Opposite tangents are outside the round-bevel subset')
                return (radial-tangent*radial.dot(tangent)).normalized()
            frames=[radial];distances=[0.]
            for i in range(1,count):
                frames.append(transport(frames[-1],tangents[i-1],tangents[i]))
                distances.append(distances[-1]+(points[i]-points[i-1]).length)
            end=transport(frames[-1],tangents[-1],tangents[0])
            correction=math.atan2(tangents[0].dot(end.cross(frames[0])),end.dot(frames[0]))
            total=distances[-1]+(points[0]-points[-1]).length
            frames=[frame*math.cos(correction*d/total)+tangent.cross(frame)*math.sin(correction*d/total) for frame,tangent,d in zip(frames,tangents,distances)]
        for i,(point,tangent) in enumerate(zip(points,tangents)):
            if frames is not None:
                radial=frames[i]
            elif i:
                previous=tangents[i-1];axis=previous.cross(tangent);sine=axis.length;cosine=max(-1.,min(1.,previous.dot(tangent)))
                if sine>1e-7:
                    axis=axis/sine;radial=radial*cosine+axis.cross(radial)*sine+axis*axis.dot(radial)*(1-cosine)
                elif cosine<0:raise UnsupportedError('bpy.types.Spline','Opposite tangents are outside the round-bevel subset')
            side=tangent.cross(radial);radius=depth*spline['points'][i]['radius'];tilt=spline['points'][i]['tilt']
            step=f32(2*math.pi/segments);profile_angle=f32(-(segments-1)*step)
            for j in range(segments):
                angle=profile_angle-math.pi/2+tilt;vertices.append(list(point+(radial*math.cos(angle)+side*math.sin(angle))*radius));profile_angle=f32(profile_angle+step)
        for i in range(steps):
            for j in range(segments):
                a=base+i*segments;b=base+((i+1)%count)*segments;k=(j-1)%segments
                faces.append([a+j,b+j,b+k,a+k]);u=i/steps;next_u=(i+1)/steps;v=j/segments if j else 1.;previous_v=k/segments
                uv += [[u,v],[next_u,v],[next_u,previous_v],[u,previous_v]]
                smooth.append(spline['use_smooth']);indices.append(spline['material_index'])
        if record.get('use_fill_caps',False) and not cyclic:
            if spline['points'][0]['radius']<=0 or spline['points'][-1]['radius']<=0:raise UnsupportedError('bpy.types.Curve.use_fill_caps','End caps require positive endpoint radii')
            for ring,reverse in ((0,True),(count-1,False)):
                # The side profile order has normal +tangent; reverse the start.
                order=list(range(segments))
                if reverse:order.reverse()
                faces.append([base+ring*segments+j for j in order])
                uv += [[.5+.5*math.cos(2*math.pi*j/segments),.5+.5*math.sin(2*math.pi*j/segments)] for j in order]
                smooth.append(False);indices.append(spline['material_index'])
        if len(vertices)>100000 or len(faces)>100000:raise UnsupportedError('bpy.types.Curve','Evaluated curves are limited to 100000 vertices/faces')
    return dict(vertices=vertices,edges=edges,faces=faces,uv_layers=[dict(name='UVMap',data=uv)] if faces else [],active_uv=0,loop_normals=[],colors=[],smooth=smooth,material_indices=indices)

def _evaluate_curves():
    for key in list(_CURVE_DIRTY):
        data=request('get',kind='meshes',id=key);surface=_curve_surface(data['curve'])
        request('bmesh_publish',id=key,mesh=surface);_CURVE_DIRTY.discard(key)

_old_update=bpy.context.view_layer._values['update']
def _curve_update():_evaluate_curves();return _old_update()
bpy.context.view_layer._values['update']=_curve_update
