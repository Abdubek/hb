"""Static TrueType text; explicit font loading keeps the default Bfont out of the binary."""
class VectorFont(DataBlock):
    _kind='fonts';_path='bpy.types.VectorFont'
CLASSES['fonts']=VectorFont

class Fonts(Strict):
    _path='bpy.data.fonts'
    def load(self,filepath,*,check_existing=False):
        if check_existing:raise UnsupportedError(self._path+'.load','Font-cache identity is outside this subset; use check_existing=False')
        with open(str(filepath),'rb') as file:data=file.read(4*1024*1024+1)
        if len(data)>4*1024*1024:raise UnsupportedError(self._path+'.load','TrueType files are limited to 4 MiB')
        try:
            record=_read_truetype(data,str(filepath).replace('\\','/').rsplit('/',1)[-1]);name=record.pop('name')
            return wrap('fonts',request('new',kind='fonts',name=name,extra=record))
        except (IndexError,KeyError,struct.error,ValueError) as exc:raise UnsupportedError(self._path+'.load','Malformed or unsupported static TrueType font: '+str(exc))
bpy.data._values['fonts']=Fonts()

def _read_truetype(data,name):
    def u16(offset):return struct.unpack_from('>H',data,offset)[0]
    def s16(offset):return struct.unpack_from('>h',data,offset)[0]
    def u32(offset):return struct.unpack_from('>I',data,offset)[0]
    if data[:4] not in (b'\x00\x01\x00\x00',b'true'):raise ValueError('Expected a glyf-based sfnt file')
    count=u16(4)
    if not 1<=count<=128:raise ValueError('Invalid table count')
    tables={}
    for i in range(count):
        pos=12+16*i;tag=data[pos:pos+4].decode('ascii');offset=u32(pos+8);length=u32(pos+12)
        if offset+length>len(data):raise ValueError('Truncated table')
        tables[tag]=(offset,length)
    if 'fvar' in tables or 'CFF ' in tables or 'CFF2' in tables:raise ValueError('Variable and CFF fonts are excluded')
    head=tables['head'][0];hhea=tables['hhea'][0];maxp=tables['maxp'][0];loca=tables['loca'][0];glyf=tables['glyf'][0];hmtx=tables['hmtx'][0];cmap=tables['cmap'][0]
    glyph_count=u16(maxp+4);metric_count=u16(hhea+34);loc_format=s16(head+50)
    if not 0<metric_count<=glyph_count or loc_format not in (0,1):raise ValueError('Invalid glyph metrics')
    height=s16(head+42)-s16(head+38);asc=s16(hhea+4);desc=s16(hhea+6)
    if height<=0 or asc<=desc:raise ValueError('Invalid font height')
    scale=f32(1/height);subtable=None
    for i in range(u16(cmap+2)):
        pos=cmap+4+8*i;platform=u16(pos);encoding=u16(pos+2);offset=cmap+u32(pos+4)
        if platform in (0,3) and u16(offset)==4:
            subtable=offset
            if platform==3 and encoding==1:break
    if subtable is None:raise ValueError('A Unicode format-4 cmap is required')
    segment_count=u16(subtable+6)//2
    if not 1<=segment_count<=8192:raise ValueError('Invalid cmap segment count')
    ends=subtable+14;starts=ends+2*segment_count+2;deltas=starts+2*segment_count;ranges=deltas+2*segment_count
    def glyph_id(code):
        for i in range(segment_count):
            if u16(starts+2*i)<=code<=u16(ends+2*i):
                delta=s16(deltas+2*i);offset=u16(ranges+2*i)
                gid=(code+delta)&65535 if not offset else u16(ranges+2*i+offset+2*(code-u16(starts+2*i)))
                if offset and gid:gid=(gid+delta)&65535
                if gid>=glyph_count:raise ValueError('Invalid glyph index')
                return gid
        return 0
    def location(gid):return (u16(loca+2*gid)*2) if loc_format==0 else u32(loca+4*gid)
    glyphs={}
    for code in range(32,127):
        gid=glyph_id(code)
        if gid==0:glyphs[chr(code)]=None;continue
        begin=location(gid);end=location(gid+1);advance=u16(hmtx+4*min(gid,metric_count-1));contours=[]
        if end<begin or end>tables['glyf'][1]:raise ValueError('Invalid glyph extent')
        if begin!=end:
            pos=glyf+begin;n=s16(pos)
            if n<0:
                # Exclude only the affected character; other simple ASCII glyphs remain useful.
                glyphs[chr(code)]=None;continue
            if n>128:raise ValueError('Too many contours')
            ends_list=[u16(pos+10+2*i) for i in range(n)];total=ends_list[-1]+1 if n else 0
            if total>8192:raise ValueError('Too many glyph points')
            cursor=pos+10+2*n;cursor+=2+u16(cursor);flags=[]
            while len(flags)<total:
                flag=data[cursor];cursor+=1;repeat=1
                if flag&8:repeat+=data[cursor];cursor+=1
                flags += [flag]*repeat
            if len(flags)!=total:raise ValueError('Invalid repeated flags')
            axes=[]
            for short,same in ((2,16),(4,32)):
                values=[];value=0
                for flag in flags:
                    if flag&short:delta=data[cursor]*(1 if flag&same else -1);cursor+=1
                    elif flag&same:delta=0
                    else:delta=s16(cursor);cursor+=2
                    value+=delta;values.append(value)
                axes.append(values)
            if cursor>glyf+end:raise ValueError('Truncated glyph')
            start=0
            for last in ends_list:
                contours.append([[axes[0][i],axes[1][i],bool(flags[i]&1)] for i in range(start,last+1)]);start=last+1
        glyphs[chr(code)]=dict(advance=f32(advance*scale),contours=contours)
    if 'name' in tables:
        names={};base=tables['name'][0];strings=base+u16(base+4)
        for i in range(u16(base+2)):
            pos=base+6+12*i;platform=u16(pos);ident=u16(pos+6);length=u16(pos+8);offset=u16(pos+10)
            if platform in (0,3) and ident in (1,2):names[ident]=data[strings+offset:strings+offset+length].decode('utf-16-be')
        if 1 in names:name=names[1]+(' '+names[2] if names.get(2) else '')
    return dict(name=name,scale=scale,ascender=f32(asc*scale),descender=f32(desc*scale),glyphs=glyphs)

class TextMaterials(Materials):
    _path='bpy.types.TextCurve.materials'
    def clear(self):
        self._mesh._set('materials',[])
        self._mesh._set('material_indices',[0]*len(self._mesh._read('faces')))

class TextCurve(Curve):
    _path='bpy.types.TextCurve'
    def _body(self,value):
        if not isinstance(value,str):raise TypeError('Text body must be a string')
        if len(value)>256 or any(c!='\n' and not 32<=ord(c)<=126 for c in value):raise UnsupportedError(self._path+'.body','At most 256 printable ASCII characters and newlines')
        self._set('body',value)
    body=property(lambda self:self._read('body'),_body)
    def _font(self,value):
        if not isinstance(value,VectorFont):raise TypeError('Expected a loaded VectorFont')
        self._set('font',value._id)
    font=property(lambda self:wrap('fonts',self._read('font')) if self._read('font') is not None else Namespace('bpy.types.VectorFont',name='Bfont'),_font)
    size=property(lambda self:self._read('size'),lambda self,v:self._set('size',_curve_number(v,.0001,100)))
    space_character=property(lambda self:1.,lambda self,v:self._constant('space_character',v,1.))
    space_word=property(lambda self:1.,lambda self,v:self._constant('space_word',v,1.))
    space_line=property(lambda self:self._read('space_line'),lambda self,v:self._set('space_line',_curve_number(v,0,10)))
    align_x=prop('align_x',str,choices=('LEFT','CENTER','RIGHT'))
    align_y=prop('align_y',str,choices=('TOP_BASELINE',))
    resolution_u=property(lambda self:self._read('resolution_u'),lambda self,v:self._set('resolution_u',int(_curve_number(int(v),1,32))))
    bevel_depth=property(lambda self:0.,lambda self,v:self._constant('bevel_depth',v,0.))
    extrude=property(lambda self:self._curve().get('extrude',0.),lambda self,v:self._set('extrude',_curve_number(v,0,100)))
    offset=property(lambda self:0.,lambda self,v:self._constant('offset',v,0.))
    @property
    def materials(self):return TextMaterials(self)
    @property
    def splines(self):raise UnsupportedError(self._path+'.splines','FONT curve control splines are not editable through this API')


def _text_contour(points,resolution,scale):
    expanded=[]
    for i,p in enumerate(points):
        expanded.append(p)
        following=points[(i+1)%len(points)]
        if not p[2] and not following[2]:expanded.append([(p[0]+following[0])/2,(p[1]+following[1])/2,True])
    if not expanded:return []
    start=next((i for i,p in enumerate(expanded) if p[2]),None)
    if start is None:raise ValueError('Missing on-curve point')
    expanded=expanded[start:]+expanded[:start];output=[];i=0
    while i<len(expanded):
        a=expanded[i];b=expanded[(i+1)%len(expanded)]
        if b[2]:output.append([f32(a[0]*scale),f32(a[1]*scale)]);i+=1
        else:
            c=expanded[(i+2)%len(expanded)]
            for step in range(resolution):
                t=step/resolution;output.append([f32(((1-t)**2*a[k]+2*t*(1-t)*b[k]+t*t*c[k])*scale) for k in range(2)])
            i+=2
    return output

def _text_contour_groups(contours):
    # Filled display-list components are emitted in reverse component order.
    # Touching/overlapping bounds share one component, including nested holes.
    bounds=[(min(p[0] for p in c),min(p[1] for p in c),max(p[0] for p in c),max(p[1] for p in c)) for c in contours]
    roots=list(range(len(contours)))
    def root(i):
        while roots[i]!=i:i=roots[i]
        return i
    for i,a in enumerate(bounds):
        for j,b in enumerate(bounds[:i]):
            if a[0]<=b[2] and b[0]<=a[2] and a[1]<=b[3] and b[1]<=a[3]:roots[root(i)]=root(j)
    groups={}
    for i,c in enumerate(contours):groups.setdefault(root(i),[]).append(c)
    return [c for group in reversed(list(groups.values())) for c in group]

def _text_surface(record):
    font=request('get',kind='fonts',id=record['font']) if record['font'] is not None else None;body=record['body'];vertices=[];faces=[];uv=[]
    if body.strip() and font is None:raise UnsupportedError('bpy.types.TextCurve.font','Assign an explicitly loaded static TrueType font; bundled Bfont geometry is outside this contract')
    if not font:return dict(vertices=[],edges=[],faces=[],uv_layers=[],active_uv=0,loop_normals=[],colors=[],smooth=[],material_indices=[])
    size=record['size'];resolution=record['resolution_u']
    for line_number,line in enumerate(body.split('\n')):
        glyphs=[font['glyphs'][character] for character in line]
        if any(g is None for g in glyphs):raise UnsupportedError('bpy.types.TextCurve.body','The selected font contains an unsupported composite ASCII glyph')
        width=sum(g['advance'] for g in glyphs);offset=-width*(.5 if record['align_x']=='CENTER' else 1 if record['align_x']=='RIGHT' else 0)
        for glyph in glyphs:
            contours=[_text_contour(c,resolution,font['scale']) for c in glyph['contours']]
            if contours:
                # The triangulator accepts oriented outer boundaries and holes; TrueType winds oppositely.
                contours=_text_contour_groups([c for c in contours if len(c)>=3]);total=sum(map(len,contours));mapping=[];start=0
                for contour in contours:mapping += list(reversed(range(start,start+len(contour))));start+=len(contour)
                contours=[list(reversed(c)) for c in contours]
                result=request('text_triangulate',contours=contours);base=len(vertices)
                points=[point for contour in contours for point in contour]
                vertices += [[f32((point[0]+offset)*size),f32((point[1]-line_number*record['space_line'])*size),0.] for point in points]
                faces += [[base+i for i in triangle] for triangle in result]
                uv += [[f32(mapping[i]/max(1,total-1)),0.] for triangle in result for i in triangle]
            offset=f32(offset+glyph['advance'])
    if record.get('extrude',0.) and faces:
        depth=record['extrude'];count=len(vertices);flat_faces=faces;flat_uv=uv;faces=[];uv=[]
        # Use actual triangulated boundaries, including holes, so omitted collinear
        # outline samples cannot leave T-junctions between caps and side walls.
        boundary={}
        for face in flat_faces:
            for a,b in zip(face,face[1:]+face[:1]):
                if (b,a) in boundary:del boundary[(b,a)]
                elif (a,b) in boundary:raise UnsupportedError('bpy.types.TextCurve.extrude','Text triangulation has overlapping oriented boundaries')
                else:boundary[(a,b)]=True
        if 2*count>100000 or 2*len(flat_faces)+len(boundary)>100000:raise UnsupportedError('bpy.types.TextCurve','Extruded text is limited to 100000 evaluated vertices/faces; reduce body length or resolution_u')
        vertices=[[p[0],p[1],-depth] for p in vertices]+[[p[0],p[1],depth] for p in vertices]
        cursor=0
        for face in flat_faces:
            cap_uv=flat_uv[cursor:cursor+len(face)];cursor+=len(face)
            faces.append(list(reversed(face)));uv+=list(reversed(cap_uv))
            faces.append([i+count for i in face]);uv+=cap_uv
        for a,b in boundary:
            faces.append([a,b,b+count,a+count])
            distance=(Vector(vertices[b])-Vector(vertices[a])).length
            uv += [[0.,0.],[distance,0.],[distance,2*depth],[0.,2*depth]]
        # Cap triangulation may discard redundant contour vertices. Compact them
        # without merging separate glyphs, contours or coincident components.
        used=sorted({v for face in faces for v in face});mapping={v:i for i,v in enumerate(used)}
        vertices=[vertices[v] for v in used];faces=[[mapping[v] for v in face] for face in faces]
    if len(vertices)>100000 or len(faces)>100000:raise UnsupportedError('bpy.types.TextCurve','Text is limited to 100000 evaluated vertices/faces')
    return dict(vertices=vertices,edges=[],faces=faces,uv_layers=[dict(name='UVMap',data=uv)] if faces else [],active_uv=0,loop_normals=[],colors=[],smooth=[False]*len(faces),material_indices=[0]*len(faces))


def text_add(*,enter_editmode=False,align='WORLD',location=None,rotation=None,scale=(1.,1.,1.)):
    if enter_editmode or align not in ('WORLD','CURSOR') or tuple(scale)!=(1.,1.,1.):raise UnsupportedError('bpy.ops.object.text_add','Use object mode, WORLD/CURSOR alignment and unit construction scale')
    curve=bpy.data.curves.new('Text','FONT');curve.body='Text'
    obj=bpy.data.objects.new('Text',curve);bpy.context.collection.objects.link(obj)
    for old in bpy.context.selected_objects:old.select_set(False)
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    obj.location=tuple(_CONSTRUCTION_CURSOR.location) if location is None else location
    obj.rotation_euler=(tuple(_CONSTRUCTION_CURSOR.rotation_euler) if align=='CURSOR' else (0.,0.,0.)) if rotation is None else rotation
    return {'FINISHED'}
bpy.ops.object._values['text_add']=_object_mode_operation('text_add',text_add)
