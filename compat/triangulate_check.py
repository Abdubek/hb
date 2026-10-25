"""Oriented topology, UV and custom-normal comparison for TRIANGULATE.

Normals have a separate 1e-4 bound because Blender stores quantized corner-space
angles. hb stores float32 vectors. No existing golden tolerance is changed.
"""
def close(a,b,tolerance):
    if isinstance(a,list):
        assert len(a)==len(b),(len(a),len(b))
        for x,y in zip(a,b):close(x,y,tolerance)
    else:assert abs(a-b)<=tolerance,(a,b,tolerance)

def compare(reference,scene):
    objects={o['name']:o for o in scene['objects']}
    meshes={m['id']:m for m in scene['meshes']}
    for name,expected in reference.items():
        mesh=meshes[objects[name]['data']['id']]
        close(expected['vertices'],mesh['vertices'],1e-5)
        assert expected['has_custom_normals']==bool(mesh['loop_normals']),name
        def records(faces,uv,normals):
            result={};at=0
            for face in faces:
                shift=min(range(len(face)),key=lambda i:tuple(face[i:]+face[:i]))
                key=tuple(face[shift:]+face[:shift])
                assert key not in result
                indices=list(range(at+shift,at+len(face)))+list(range(at,at+shift))
                result[key]=([uv[i] for i in indices],[normals[i] for i in indices] if normals else [])
                at+=len(face)
            return result
        a=records(expected['faces'],expected['uv'],expected['normals'] if expected['has_custom_normals'] else [])
        b=records(mesh['faces'],mesh['uv_layers'][0]['data'],mesh['loop_normals'])
        assert a.keys()==b.keys(),(name,'indexed oriented triangles',a.keys(),b.keys())
        for face in a:
            close(a[face][0],b[face][0],1e-5)
            close(a[face][1],b[face][1],1e-4)
