"""Bijection, oriented faces and edge multiplicity for mixed extrusion."""
from collections import Counter

def compare(refs,scene):
    meshes={m['id']:m for m in scene['meshes']};fail=[]
    def cycle(f):return min(tuple(f[i:]+f[:i]) for i in range(len(f)))
    for o in scene['objects']:
        m=meshes[o['data']['id']];r=refs[o['name']]
        try:
            assert len(m['vertices'])==len(r['vertices']),('vertex count',len(m['vertices']),len(r['vertices']))
            mapping=[]
            for v in m['vertices']:
                matches=[i for i,w in enumerate(r['vertices']) if max(abs(a-b) for a,b in zip(v,w))<=1e-5]
                assert len(matches)==1,('bijection',v,matches);mapping.append(matches[0])
            assert len(set(mapping))==len(mapping)
            assert Counter(cycle([mapping[i] for i in f]) for f in m['faces'])==Counter(cycle(f) for f in r['faces']),'oriented faces'
            assert Counter(tuple(sorted(mapping[i] for i in e)) for e in m['edges'])==Counter(tuple(sorted(e)) for e in r['edges']),'edge multiplicity'
        except Exception as e:fail.append((o['name'],str(e)))
    assert not fail,fail
