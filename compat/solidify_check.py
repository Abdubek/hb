"""Compare preserved SOLIDIFY probes with oriented topology and weight checks.

NON_MANIFOLD allocates radial fans in a different order. Find an explicit vertex
bijection, including coincident clamped/zero-weight vertices, then compare indexed
oriented faces. EXTRUDE retains the exact original vertex order.
"""
from collections import Counter

def canonical(face):
    return min(tuple(face[i:]+face[:i]) for i in range(len(face)))

def compare(reference, actual):
    assert reference.keys()==actual.keys(), 'SOLIDIFY probe population changed'
    for name, expected in reference.items():
        observed=actual[name]
        rv=expected['vertices'];nv=observed['vertices']
        assert len(rv)==len(nv),(name,'vertex count')
        assert len(expected['faces'])==len(observed['faces']),(name,'face count')
        target=Counter(canonical(f) for f in expected['faces'])
        def matches(i,j):
            if any(abs(a-b)>1e-5 for a,b in zip(nv[i],rv[j])):return False
            a=observed['weights'][i];b=expected['weights'][j]
            return len(a)==len(b) and all(x[0]==y[0] and abs(x[1]-y[1])<=1e-6 for x,y in zip(a,b))
        if name.startswith('EXTRUDE'):
            assert all(matches(i,i) for i in range(len(rv))),(name,'indexed positions/weights')
            assert Counter(canonical(f) for f in observed['faces'])==target,(name,'oriented faces')
            continue
        def incidence(faces,n):
            counts=[Counter() for _ in range(n)];neighbors=[set() for _ in range(n)]
            for face in faces:
                for i,v in enumerate(face):
                    counts[v][len(face)]+=1
                    neighbors[v].update((face[i-1],face[(i+1)%len(face)]))
            return counts,neighbors
        rc,rn=incidence(expected['faces'],len(rv));nc,nn=incidence(observed['faces'],len(nv))
        candidates={i:[j for j in range(len(rv)) if matches(i,j) and nc[i]==rc[j]] for i in range(len(nv))}
        assert all(candidates.values()),(name,'positions/weights/incidence')
        order=sorted(candidates,key=lambda i:len(candidates[i]));mapping={};used=set();attempts=0
        def search(at):
            nonlocal attempts
            attempts+=1
            assert attempts<=100000,(name,'ambiguous probe exceeds matching bound')
            if at==len(order):return Counter(canonical([mapping[i] for i in f]) for f in observed['faces'])==target
            i=order[at]
            for j in candidates[i]:
                if j in used or any((v in nn[i])!=(mapped in rn[j]) for v,mapped in mapping.items()):continue
                mapping[i]=j;used.add(j)
                if search(at+1):return True
                del mapping[i];used.remove(j)
            return False
        assert search(0),(name,'indexed connectivity/winding')
