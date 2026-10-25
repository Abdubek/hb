"""Normalize native scene records to the independent Blender observer format."""
import json,zlib,base64
from png import rgba
from pathlib import Path

def revision(path):
    p=Path(path);head=json.loads(p.read_text())
    if head['format']=='hb-head-v1':
        data=Path(str(p)+'.revisions').joinpath(head['revision']+'.hbr').read_bytes()
        return json.loads(zlib.decompress(data[4:]))
    return head

def normalize(s):
    db={kind:{x['id']:x for x in s.get(kind,[])} for kind in ('objects','meshes','materials','cameras','lights','collections','images','textures','worlds')}
    def name(kind,key):return None if key is None else db[kind][key]['name']
    linked=set()
    def walk(k):
        c=db['collections'][k];linked.update(c['objects'])
        for k in c['children']:walk(k)
    walk(0)
    objects=[]
    for o in sorted(s['objects'],key=lambda o:o['name']):
        d=o['data'];kind=d['kind'] if d else None;mesh=None
        if kind=='meshes' and not db[kind][d['id']].get('curve'):
            m=db[kind][d['id']];mesh={k:m[k] for k in ('name','vertices','faces')};mesh['uv']=m['uv_layers'][m['active_uv']]['data'] if m['uv_layers'] else []
        objects.append(dict(name=o['name'],type={'meshes':'MESH','cameras':'CAMERA','lights':'LIGHT',None:'EMPTY'}[kind],parent=name('objects',o['parent']),data=name(kind,d['id']) if d else None,location=o['location'],rotation_euler=o['rotation_euler'],scale=o['scale'],selected=o['selected'] if o['id'] in linked else False,linked=o['id'] in linked,mesh=mesh))
        if kind=='meshes' and db[kind][d['id']].get('curve'):objects[-1]['type']=db[kind][d['id']]['curve']['type']
        if o.get('vertex_groups'):objects[-1]['vertex_groups']=[g['name'] for g in o['vertex_groups']]
        objects[-1]['modifiers']=[{k:v for k,v in m.items() if not k.startswith('_')} for m in o.get('modifiers',[])]
    for o in objects:
        for m in o['modifiers']:
            if m['type']=='BOOLEAN':
                m['object']=name('objects',m['object'])
                if 'collection' in m:m['collection']=name('collections',m['collection'])
            if m['type']=='SUBSURF' and not m.get('use_custom_normals'):m.pop('use_custom_normals',None)
            if m['type']=='DISPLACE':m['texture']=name('textures',m['texture'])
    materials=[]
    for m in sorted(s['materials'],key=lambda m:m['name']):
        v={k:m[k] for k in ('name','diffuse_color','metallic','roughness','use_nodes')};v['nodes']=[]
        for n in m['nodes'] or []:
            inputs={k:n['inputs'][k] for k in ('Base Color','Metallic','Roughness','Alpha','Emission Color','Emission Strength','Normal')} if n['type']=='ShaderNodeBsdfPrincipled' else n['inputs']
            v['nodes'].append(dict(name=n['name'],type=n['type'],inputs=inputs,image=name('images',n.get('image'))))
        materials.append(v)
    meshes=[]
    for m in sorted(s['meshes'],key=lambda m:m['name']):
        if m.get('curve'):continue
        v={k:m[k] for k in ('name','material_indices','smooth','uv_layers')};v['materials']=[name('materials',k) for k in m['materials']];meshes.append(v)
        if m.get('deform_weights'):v['deform_weights']=m['deform_weights']
    cameras=[{k:c[k] for k in ('name','type','lens','sensor_width','sensor_height','sensor_fit','clip_start','clip_end','ortho_scale','shift_x','shift_y')} for c in sorted(s['cameras'],key=lambda c:c['name'])]
    lights=[]
    for l in sorted(s['lights'],key=lambda l:l['name']):
        d={k:l[k] for k in ('name','type','energy','color')}
        d['use_shadow']=l.get('use_shadow',True)
        if l['type']=='AREA':d.update(shape=l.get('shape','SQUARE'),size_y=l.get('size_y',.25))
        for field,types in [('shadow_soft_size',('POINT','SPOT')),('size',('AREA',)),('spot_size',('SPOT',)),('spot_blend',('SPOT',))]:
            if l['type'] in types:d[field]=l[field]
        lights.append(d)
    collections=[dict(name=c['name'],objects=sorted(name('objects',k) for k in c['objects']),children=sorted(name('collections',k) for k in c['children'])) for c in sorted(s['collections'],key=lambda c:c['name']) if c['id']!=0]
    images=[]
    for i in sorted(s['images'],key=lambda i:i['name']):
        if i.get('encoded'):
            _,_,rows=rgba(base64.b64decode(i['encoded']));pixels=[v/255 for row in reversed(rows) for pixel in row for v in pixel]
        else:pixels=i['pixels']*(i['width']*i['height']) if i.get('solid') else i['pixels']
        images.append(dict(name=i['name'],size=[i['width'],i['height']],pixels=pixels,colorspace=i['colorspace']))
    textures=[{k:t[k] for k in ('name','type','noise_basis','noise_scale','noise_depth','noise_type','cloud_type','intensity','contrast')} for t in sorted(s.get('textures',[]),key=lambda t:t['name'])]
    worlds=[dict(name=w['name'],color=w['color'],use_nodes=w['use_nodes']) for w in sorted(s.get('worlds',[]),key=lambda w:w['name'])]
    return dict(worlds=worlds,world=name('worlds',s.get('scene_world')),objects=objects,meshes=meshes,materials=materials,cameras=cameras,lights=lights,collections=collections,images=images,textures=textures,camera=name('objects',s['camera']))
