"""The sphere comparator must preserve geometry, orientation and corner meaning."""
import copy,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'compat'))
from equivalent import align
class Equivalence(unittest.TestCase):
    def scene(self):
        mesh=dict(name='Sphere',vertices=[[0,0,0],[1,0,0],[0,1,0]],faces=[[0,1,2]],uv=[[0,0],[1,0],[0,1]])
        return dict(objects=[dict(name='Sphere',mesh=mesh)],meshes=[dict(name='Sphere',material_indices=[2],smooth=[True],uv_layers=[dict(name='UV',data=mesh['uv'])])])
    def test_reindexing_only(self):
        ref=self.scene();got=copy.deepcopy(ref);m=got['objects'][0]['mesh'];m['vertices']=[m['vertices'][2],m['vertices'][0],m['vertices'][1]];m['faces']=[[1,2,0]]
        self.assertEqual(align(ref,got,('Sphere',)),ref)
    def test_geometry_winding_and_counts_cannot_escape(self):
        for change in ('position','winding','count','duplicate'):
            with self.subTest(change=change):
                ref=self.scene();got=copy.deepcopy(ref);m=got['objects'][0]['mesh']
                if change=='position':m['vertices'][0][0]=.01
                if change=='winding':m['faces'][0].reverse()
                if change=='count':m['vertices'].append([2,2,2])
                if change=='duplicate':m['faces'].append([0,1,2])
                with self.assertRaises(AssertionError):align(ref,got,('Sphere',))
    def test_attributes_remain_visible_to_comparison(self):
        ref=self.scene();got=copy.deepcopy(ref);got['objects'][0]['mesh']['uv'][0]=[.5,.5]
        self.assertNotEqual(align(ref,got,('Sphere',)),ref)
        self.assertEqual(align(ref,got,()),got)

class FaceOrder(unittest.TestCase):
    def scene(self):
        s=Equivalence().scene();m=s['objects'][0]['mesh'];m['name']='Extrude'
        m['vertices'].append([1,1,0]);m['faces'].append([1,3,2]);m['uv'] += [[1,0],[1,1],[0,1]]
        r=s['meshes'][0];r.update(name='Extrude',material_indices=[2,3],smooth=[True,False]);r['uv_layers'][0]['data']=m['uv'][:]
        return s
    def test_only_face_order_and_corner_starts_change(self):
        from equivalent import align_faces
        ref=self.scene();got=copy.deepcopy(ref);m=got['objects'][0]['mesh']
        m['faces']=[[3,2,1],[2,0,1]];indices=[4,5,3,2,0,1]
        m['uv']=[m['uv'][i] for i in indices]
        r=got['meshes'][0];r['material_indices'].reverse();r['smooth'].reverse();r['uv_layers'][0]['data']=m['uv'][:]
        self.assertEqual(align_faces(ref,got,('Extrude',)),ref)
        self.assertEqual(align_faces(ref,got,()),got)
    def test_winding_counts_and_duplicates_are_rejected(self):
        from equivalent import align_faces
        for kind in ('winding','count','duplicate'):
            ref=self.scene();got=copy.deepcopy(ref);m=got['objects'][0]['mesh']
            if kind=='winding':m['faces'][0].reverse()
            if kind=='count':m['vertices'].append([0,0,1])
            if kind=='duplicate':m['faces'][1]=m['faces'][0][:]
            with self.assertRaises(AssertionError):align_faces(ref,got,('Extrude',))
    def test_positions_and_attributes_cannot_be_hidden(self):
        from equivalent import align_faces
        for field in ('position','material','smooth','uv'):
            ref=self.scene();got=copy.deepcopy(ref)
            if field=='position':got['objects'][0]['mesh']['vertices'][0][0]=1
            if field=='material':got['meshes'][0]['material_indices'][0]=9
            if field=='smooth':got['meshes'][0]['smooth'][0]=False
            if field=='uv':got['objects'][0]['mesh']['uv'][0]=[.5,.5]
            self.assertNotEqual(align_faces(ref,got,('Extrude',)),ref)
