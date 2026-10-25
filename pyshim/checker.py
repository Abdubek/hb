"""Scope-aware preflight for the declared subset, with conservative API flow.

This checks API availability, not arbitrary Python correctness or termination.
Unresolved API values in helper functions fail closed instead of being ignored.
"""

def check(source,filename):
    try:tree=ast.parse(source,filename)
    except SyntaxError as exc:
        return [dict(code='SYNTAX_ERROR',message=exc.msg,location=f'{filename}:{exc.lineno}',suggestion='Correct the Python syntax.',doc='docs/compatibility.md#static-checker')]
    # Give each lexical binding a unique name before the original path validator.
    # No user code is executed. Locations remain those of the source file.
    counter=[0];functions={}
    class Scope(ast.NodeTransformer):
        def __init__(self,parent=None):self.parent=parent;self.names={};self.prefix=''
        def find(self,name):
            if name in self.names:return self.names[name]
            return self.parent.find(name) if self.parent else name
        def visit_Name(self,node):node.id=self.find(node.id);return node
        def visit_Global(self,node):
            for name in node.names:self.names[name]=name
            return node
        def visit_Nonlocal(self,node):
            for name in node.names:self.names[name]=self.parent.find(name) if self.parent else name
            return node
        def visit_FunctionDef(self,node):
            original=node.name;node.name=self.find(original)
            child=Scope(self);counter[0]+=1;prefix=f'_hb_scope_{counter[0]}_'
            # Collect only bindings in this function, excluding nested scopes.
            class Bindings(ast.NodeVisitor):
                def visit_Name(s,n):
                    if isinstance(n.ctx,ast.Store):child.names.setdefault(n.id,prefix+n.id)
                def visit_FunctionDef(s,n):child.names.setdefault(n.name,prefix+n.name)
                visit_AsyncFunctionDef=visit_FunctionDef
                def visit_ClassDef(s,n):child.names.setdefault(n.name,prefix+n.name)
                def visit_Import(s,n):
                    for a in n.names:child.names.setdefault(a.asname or a.name.split('.')[0],prefix+(a.asname or a.name.split('.')[0]))
                def visit_ImportFrom(s,n):
                    for a in n.names:child.names.setdefault(a.asname or a.name,prefix+(a.asname or a.name))
            for arg in node.args.posonlyargs+node.args.args+node.args.kwonlyargs:child.names[arg.arg]=prefix+arg.arg
            for stmt in node.body:Bindings().visit(stmt)
            for arg in node.args.posonlyargs+node.args.args+node.args.kwonlyargs:arg.arg=child.find(arg.arg)
            for arg in (node.args.vararg,node.args.kwarg):
                if arg:child.names[arg.arg]=prefix+arg.arg;arg.arg=child.find(arg.arg)
            node.body=[child.visit(stmt) for stmt in node.body]
            functions[node.name]=node
            return node
        visit_AsyncFunctionDef=visit_FunctionDef
        def visit_Import(self,node):
            for alias in node.names:
                key=alias.asname or alias.name.split('.')[0];alias.asname=self.find(key)
            return node
        def visit_ImportFrom(self,node):
            for alias in node.names:alias.asname=self.find(alias.asname or alias.name)
            return node
        def visit_Lambda(self,node):
            # Dynamic closures are handled conservatively below.
            return self.generic_visit(node)
    tree=Scope().visit(tree)
    # Validate the transformed tree while retaining original line locations.
    return _check_tree(tree,filename,functions)

def _check_tree(tree,filename,functions):
    # Python AST inference is the language adapter; membership is shared Rust.
    class Allowed:
        def __init__(self): self.cache = {}
        def __contains__(self, path):
            if path not in self.cache:
                self.cache[path] = request('manifest_accepts', alternatives=[path])
            return self.cache[path]
    allowed = Allowed()
    env={};errors=[];seen=set();returns={}
    roots=('bpy','bmesh','mathutils')
    def error(path,node,dynamic=False):
        key=(node.lineno,path)
        if key in seen:return
        seen.add(key);e=UnsupportedError(path)
        errors.append(dict(code='STATIC_UNRESOLVED' if dynamic else 'UNSUPPORTED_API',message=str(e),location=f'{filename}:{node.lineno}',suggestion=e.suggestion,doc=e.doc))
    def norm(path):
        if path in ('bpy.types.BezierSplinePoint.co','bpy.types.BezierSplinePoint.handle_left','bpy.types.BezierSplinePoint.handle_right'):return 'mathutils.Vector'
        if path in ('bpy.types.Curve.font','bpy.types.TextCurve.font','bpy.types.IDData.font'):return 'bpy.types.VectorFont'
        if path in ('bmesh.types.BMesh.loops.layers.uv','bmesh.types.BMesh.loops.layers.float_color','bmesh.types.BMesh.verts.layers.shape'):return 'bmesh.types.BMLayerCollection'
        if path=='bpy.types.Object.matrix_world':return 'mathutils.Matrix'
        if path=='bpy.context.scene.cursor':return 'bpy.types.View3DCursor'
        if path in ('bpy.types.Mesh.shape_keys','bpy.types.IDData.shape_keys'):return 'bpy.types.Key'
        if path=='bmesh.types.BMLayerCollection.active':return 'bmesh.types.BMLayerItem'
        return {'bpy.context.object':'bpy.types.Object','bpy.context.active_object':'bpy.types.Object','bpy.context.view_layer.objects.active':'bpy.types.Object','bpy.context.collection':'bpy.types.Collection','bpy.context.scene.collection':'bpy.types.Collection','bpy.context.scene.world':'bpy.types.World','bpy.context.scene.camera':'bpy.types.Object','bpy.types.Modifier.mirror_object':'bpy.types.Object','bpy.types.Modifier.offset_object':'bpy.types.Object','bpy.types.Modifier.start_cap':'bpy.types.Object','bpy.types.Modifier.end_cap':'bpy.types.Object','bpy.types.Modifier.object':'bpy.types.Object','bpy.types.Modifier.texture':'bpy.types.CloudsTexture','bpy.types.DisplaceModifier.texture':'bpy.types.CloudsTexture','bpy.types.BooleanModifier.object':'bpy.types.Object','bpy.types.BooleanModifier.collection':'bpy.types.Collection'}.get(path,path)
    def member(base,name):
        # Container methods belong to the Python list, never to its elements.
        if base.startswith('[list]'):return '@listmethod:'+name+':'+base[6:]
        if base.startswith('[dict]'):return '@dictmethod:'+name+':'+base[6:]
        base=norm(base)
        if base=='bpy.types.Object' and name=='data':return 'bpy.types.IDData'
        if base=='bpy.types.Object' and name=='parent':return 'bpy.types.Object'
        if base.endswith('.uv_layers') and name=='active':return 'bpy.types.MeshUVLoopLayer'
        return base+'.'+name
    def item(base):
        base=norm(base)
        if base.startswith('@tuple:'):return base.split(':',3)[3]
        if base.endswith('.splines'):return 'bpy.types.Spline'
        if base=='bpy.types.Spline.points':return 'bpy.types.SplinePoint'
        if base=='bpy.types.Spline.bezier_points':return 'bpy.types.BezierSplinePoint'
        if base.startswith(('[list]','[dict]')):return base[6:]
        if base.startswith('[]'):return base[2:]
        if base in ('bpy.data.objects','bpy.context.scene.objects','bpy.context.selected_objects','bpy.types.Collection.objects','bpy.context.view_layer.objects','bpy.types.Object.children'):return 'bpy.types.Object'
        for kind,cls in [('curves','Curve'),('meshes','Mesh'),('materials','Material'),('cameras','Camera'),('lights','Light'),('collections','Collection'),('images','Image'),('textures','CloudsTexture'),('worlds','World')]:
            if base=='bpy.data.'+kind:return 'bpy.types.'+cls
        if base in ('bpy.types.Mesh.attributes','bpy.types.IDData.attributes'):return 'bpy.types.FloatAttribute'
        if base=='bpy.types.FloatAttribute.data':return 'bpy.types.FloatAttributeValue'
        if base=='bpy.types.IntAttribute.data':return 'bpy.types.IntAttributeValue'
        if base in ('bpy.types.Mesh.color_attributes','bpy.types.IDData.color_attributes'):return 'bpy.types.FloatColorAttribute'
        if base=='bpy.types.FloatColorAttribute.data':return 'bpy.types.FloatColorAttributeValue'
        if base=='bpy.types.Object.vertex_groups':return 'bpy.types.VertexGroup'
        if base=='bpy.types.MeshVertex.groups':return 'bpy.types.VertexGroupElement'
        if base=='bpy.types.Object.modifiers':return 'bpy.types.Modifier'
        if base=='bpy.types.Object.users_collection':return 'bpy.types.Collection'
        if base.endswith('.node_tree.nodes'):return 'bpy.types.ShaderNode'
        if base.endswith('.uv_layers'):return 'bpy.types.MeshUVLoopLayer'
        if base=='bpy.types.MeshUVLoopLayer.data':return 'bpy.types.MeshUVLoop'
        if base in ('bpy.types.ShaderNode.inputs','bpy.types.ShaderNode.outputs'):return 'bpy.types.NodeSocket'
        for field,cls in [('verts','BMVert'),('edges','BMEdge'),('faces','BMFace')]:
            if base=='bmesh.types.BMesh.'+field:return 'bmesh.types.'+cls
        if base=='bmesh.types.BMFace.loops':return 'bmesh.types.BMLoop'
        if base=='bmesh.types.BMLoop':return 'bmesh.types.BMLoopUV'
        if base=='bmesh.types.BMVert':return 'mathutils.Vector'
        if base=='bpy.types.Key.key_blocks':return 'bpy.types.ShapeKey'
        if base=='bpy.types.ShapeKey.data':return 'bpy.types.ShapeKeyPoint'
        if base=='bmesh.types.BMLayerCollection':return 'bmesh.types.BMLayerItem'
        if base in ('bmesh.types.BMFace.verts','bmesh.types.BMEdge.verts'):return 'bmesh.types.BMVert'
        if base=='bmesh.types.BMFace.edges':return 'bmesh.types.BMEdge'
        if base.endswith('.vertices') and base.startswith('bpy.types.'):return 'bpy.types.MeshVertex'
        if base.endswith('.polygons'):return 'bpy.types.MeshPolygon'
        if base.endswith('.edges') and base.startswith('bpy.types.'):return 'bpy.types.MeshEdge'
        if base.endswith('.materials'):return 'bpy.types.Material'
        if base=='mathutils.Matrix':return 'mathutils.Vector'
        if base in ('mathutils.Euler','mathutils.Quaternion','mathutils.Color') or base.endswith('.rotation_quaternion'):return '#number'
        if base.startswith('mathutils.Vector') or base.endswith(('.location','.rotation_euler','.scale','.co','.normal','.dimensions','.uv','.handle_left','.handle_right')):return '#number'
        return base
    def result(base):
        if base.startswith('@dictmethod:'):
            _,method,element=base.split(':',2)
            if method in ('get','pop','setdefault'):return element
            if method=='copy':return '[dict]'+element
            if method=='values':return '[]'+element
            if method=='keys':return '[]#python'
            if method=='items':return '[]@tuple:2:1:'+element
            return None
        if base.startswith('@listmethod:'):
            _,method,element=base.split(':',2)
            if method=='pop':return element
            if method=='copy':return '[list]'+element
            return None
        if base=='bpy.data.fonts.load':return 'bpy.types.VectorFont'
        if base.endswith('.splines.new'):return 'bpy.types.Spline'
        if base=='bpy.types.Object.shape_key_add':return 'bpy.types.ShapeKey'
        if base in ('bmesh.types.BMLayerCollection.new','bmesh.types.BMLayerCollection.get','bmesh.types.BMLayerCollection.verify'):return 'bmesh.types.BMLayerItem'
        if base in ('bpy.types.Mesh.attributes.new','bpy.types.Mesh.attributes.get','bpy.types.IDData.attributes.new','bpy.types.IDData.attributes.get'):return 'bpy.types.FloatAttribute'
        if base in ('bpy.types.Mesh.color_attributes.new','bpy.types.Mesh.color_attributes.get','bpy.types.IDData.color_attributes.new','bpy.types.IDData.color_attributes.get'):return 'bpy.types.FloatColorAttribute'
        if base in ('bpy.types.Object.vertex_groups.new','bpy.types.Object.vertex_groups.get'):return 'bpy.types.VertexGroup'
        if base=='bmesh.ops.inset_region':return '[][]bmesh.types.BMFace'
        if base in ('bmesh.ops.create_cube','bmesh.ops.create_grid','bmesh.ops.create_uvsphere','bmesh.ops.create_cone','bmesh.ops.create_circle'):return '[][]bmesh.types.BMVert'
        if base in ('bmesh.ops.extrude_face_region','bmesh.ops.bevel','bmesh.ops.triangulate','bmesh.ops.solidify','bmesh.ops.bisect_plane','bmesh.ops.subdivide_edges'):return '[][]bmesh.types.BMElement'
        if base=='bpy.types.CloudsTexture.evaluate':return 'mathutils.Vector'
        if base=='bpy.types.Object.modifiers.new':return 'bpy.types.Modifier'
        if base in ('mathutils.Vector','mathutils.Matrix','mathutils.Euler','mathutils.Quaternion','mathutils.Color'):return base
        if base.startswith('mathutils.Color.from_') or base in ('mathutils.Color.copy','mathutils.Color.freeze'):return 'mathutils.Color'
        if base=='bmesh.new':return 'bmesh.types.BMesh'
        if base.endswith('.to_track_quat') or base.endswith('.to_quaternion'):return 'mathutils.Quaternion'
        if base.endswith('.to_euler'):return 'mathutils.Euler'
        if base.endswith('.to_matrix'):return 'mathutils.Matrix'
        if base.startswith('mathutils.Matrix.') and base.rsplit('.',1)[1] in ('Identity','Translation','Rotation','Scale','Diagonal','inverted','transposed','to_3x3','to_4x4'):return 'mathutils.Matrix'
        if base.startswith('mathutils.Quaternion.') and base.rsplit('.',1)[1] in ('normalized','conjugated','inverted','slerp'):return 'mathutils.Quaternion'
        for kind,cls in [('curves','Curve'),('objects','Object'),('meshes','Mesh'),('materials','Material'),('cameras','Camera'),('lights','Light'),('collections','Collection'),('images','Image'),('textures','CloudsTexture'),('worlds','World')]:
            if base in ('bpy.data.'+kind+'.new','bpy.data.'+kind+'.get','bpy.data.'+kind+'.load'):return 'bpy.types.'+cls
        for field,cls in [('verts','BMVert'),('edges','BMEdge'),('faces','BMFace')]:
            if base=='bmesh.types.BMesh.'+field+'.new':return 'bmesh.types.'+cls
        if base.endswith(('.node_tree.nodes.new','.node_tree.nodes.get')):return 'bpy.types.ShaderNode'
        if base.endswith('.uv_layers.new'):return 'bpy.types.MeshUVLoopLayer'
        if base.endswith('.copy'):return base[:-5]
        if base.startswith('mathutils.Vector.'):
            return 'mathutils.Vector' if base.rsplit('.',1)[-1] in ('normalized','lerp','cross','project','reflect','to_2d','to_3d','to_4d') else '#number'
        return None
    def container_path(prefix,element):
        # Recursive pure-Python conversion helpers can return arbitrarily nested
        # lists. Their unknown Python leaves carry no API provenance; keep one
        # container marker rather than growing the fixed point forever. API-bearing
        # element paths remain precise at every depth.
        leaf=element
        while leaf.startswith(('[list]','[dict]','[]')):
            leaf=leaf[2:] if leaf.startswith('[]') else leaf[6:]
        return prefix+('#python' if leaf=='#python' else element)
    def resolve(node):
        if isinstance(node,ast.Name):
            paths=env.get(node.id,set())
            # A binding reused for other modifier types retains the generic
            # union contract instead of inventing Solidify-only restrictions.
            if 'bpy.types.Modifier' in paths:paths=paths-{'bpy.types.SolidifyModifier','bpy.types.WeldModifier','bpy.types.BooleanModifier','bpy.types.DisplaceModifier'}
            return paths
        if isinstance(node,ast.Attribute):return {member(p,node.attr) for p in resolve(node.value)}
        if isinstance(node,ast.Subscript):
            paths=resolve(node.value)
            if isinstance(node.slice,ast.Slice):return paths
            index=node.slice.value if isinstance(node.slice,ast.Constant) and isinstance(node.slice.value,int) else None
            if isinstance(node.slice,ast.UnaryOp) and isinstance(node.slice.op,ast.USub) and isinstance(node.slice.operand,ast.Constant) and isinstance(node.slice.operand.value,int):index=-node.slice.operand.value
            return {item(p) for p in paths if not p.startswith('@tuple:') or index is None or int(p.split(':',3)[2])==(index if index>=0 else int(p.split(':',3)[1])+index)}
        if isinstance(node,ast.Tuple):return {f'@tuple:{len(node.elts)}:{i}:'+p for i,e in enumerate(node.elts) for p in resolve(e)}
        if isinstance(node,ast.List):return {container_path('[list]',p) for e in node.elts for p in resolve(e)} or {'[list]#python'}
        if isinstance(node,ast.Set):return {'[]'+p for e in node.elts for p in resolve(e)}
        if isinstance(node,ast.Dict):return {container_path('[dict]',p) for e in node.values if e for p in resolve(e)} or {'[dict]#python'}
        if isinstance(node,ast.IfExp):return resolve(node.body)|resolve(node.orelse)
        if isinstance(node,ast.BinOp):return resolve(node.left)|resolve(node.right)
        if isinstance(node,ast.UnaryOp):return resolve(node.operand)
        if isinstance(node,ast.Call):
            if isinstance(node.func,ast.Name):
                if node.func.id in functions:return returns.get(node.func.id,set())
                if node.func.id in ('list','sorted'):return {'[list]'+item(p) for p in resolve(node.args[0])} if node.args else {'[list]#python'}
                if node.func.id in ('tuple','set','iter','reversed') and node.args:return resolve(node.args[0])
                if node.func.id=='getattr' and len(node.args)>1 and isinstance(node.args[1],ast.Constant) and isinstance(node.args[1].value,str):return {member(p,node.args[1].value) for p in resolve(node.args[0])}
            paths=resolve(node.func)
            if any(p.endswith('.attributes.new') for p in paths) and any(kw.arg=='type' and isinstance(kw.value,ast.Constant) and kw.value.value=='INT' for kw in node.keywords):return {'bpy.types.IntAttribute'}
            if 'bpy.types.Object.modifiers.new' in paths:
                kind=next((kw.value for kw in node.keywords if kw.arg=='type'),node.args[1] if len(node.args)>1 else None)
                if isinstance(kind,ast.Constant) and kind.value in ('WEIGHTED_NORMAL','SOLIDIFY','WELD','BOOLEAN','DISPLACE'):return {'bpy.types.'+{'WEIGHTED_NORMAL':'WeightedNormalModifier','SOLIDIFY':'SolidifyModifier','WELD':'WeldModifier','BOOLEAN':'BooleanModifier','DISPLACE':'DisplaceModifier'}[kind.value]}
            return {r for p in paths if (r:=result(p))}
        if isinstance(node,ast.ListComp):return {container_path('[list]',p) for p in resolve(node.elt)} or {'[list]#python'}
        if isinstance(node,(ast.SetComp,ast.GeneratorExp)):return {'[]'+p for p in resolve(node.elt)}
        return set()
    def bind(target,paths):
        if isinstance(target,ast.Name):env.setdefault(target.id,set()).update(paths)
        elif isinstance(target,ast.Subscript):
            # Element writes mutate builtin containers. Matrix/vector element
            # writes keep the existing API type instead of wrapping it in a
            # deeper synthetic container on every fixed-point iteration.
            containers=resolve(target.value)
            prefixes={p[:6] if p.startswith(('[list]','[dict]')) else '[]' for p in containers if p.startswith(('[list]','[dict]','[]'))}
            for prefix in prefixes:bind(target.value,{prefix+p for p in paths})
        elif isinstance(target,(ast.Tuple,ast.List)):
            for i,t in enumerate(target.elts):
                bind(t,{item(p) for p in paths if not p.startswith('@tuple:') or (int(p.split(':',3)[1])==len(target.elts) and int(p.split(':',3)[2])==i)})
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            for alias in node.names:
                if alias.name.split('.')[0] in roots:env[alias.asname or alias.name.split('.')[0]]={alias.name}
        elif isinstance(node,ast.ImportFrom) and node.module and node.module.split('.')[0] in roots:
            for alias in node.names:env[alias.asname or alias.name]={node.module+'.'+alias.name}
    def function_returns(fn):
        found=[]
        class Returns(ast.NodeVisitor):
            def visit_Return(self,node):found.append(node)
            def visit_FunctionDef(self,node):pass
            visit_AsyncFunctionDef=visit_FunctionDef
            def visit_Lambda(self,node):pass
        visitor=Returns()
        for stmt in fn.body:visitor.visit(stmt)
        return found
    return_nodes={name:function_returns(fn) for name,fn in functions.items()}
    # Monotone fixed point propagates all observed API types across branches,
    # container aliases, helper arguments and return values. No last-write wins.
    for iteration in range(64):
        before=repr((env,returns))
        for node in ast.walk(tree):
            if isinstance(node,(ast.Assign,ast.AnnAssign)):
                for target in node.targets if isinstance(node,ast.Assign) else [node.target]:bind(target,resolve(node.value))
            elif isinstance(node,(ast.For,ast.comprehension)):bind(node.target,{item(p) for p in resolve(node.iter)})
            elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in functions:
                fn=functions[node.func.id];args=fn.args.posonlyargs+fn.args.args
                for arg,val in zip(args,node.args):env.setdefault(arg.arg,set()).update(resolve(val))
                for kw in node.keywords:
                    for arg in args+fn.args.kwonlyargs:
                        if arg.arg.rsplit('_hb_scope_',1)[-1].split('_',1)[-1]==kw.arg:env.setdefault(arg.arg,set()).update(resolve(kw.value))
            elif isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('append','extend') and isinstance(node.func.value,ast.Name) and node.args:
                paths=resolve(node.args[0]);container=resolve(node.func.value);prefix='[list]' if any(p.startswith('[list]') for p in container) else '[]'
                env.setdefault(node.func.value.id,set()).update({prefix+p for p in paths} if node.func.attr=='append' else {prefix+item(p) for p in paths})
        # Lists alias mutable containers, including helper parameters. Propagate
        # observed element types back to every alias without forgetting old types.
        def alias(a,b):
            if isinstance(a,ast.Name) and isinstance(b,ast.Name):
                paths=env.get(a.id,set())|env.get(b.id,set())
                lists={p for p in paths if p.startswith('[list]')}
                if lists:
                    env.setdefault(a.id,set()).update(lists);env.setdefault(b.id,set()).update(lists)
        for node in ast.walk(tree):
            if isinstance(node,ast.Assign):
                for target in node.targets:alias(target,node.value)
            elif isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in functions:
                fn=functions[node.func.id]
                for arg,value in zip(fn.args.posonlyargs+fn.args.args,node.args):
                    # A helper may be called with both lists and API values.
                    # Only actual list arguments share mutable list storage.
                    if any(p.startswith('[list]') for p in resolve(value)):alias(ast.Name(id=arg.arg),value)
                for kw in node.keywords:
                    for arg in fn.args.posonlyargs+fn.args.args+fn.args.kwonlyargs:
                        if arg.arg.rsplit('_hb_scope_',1)[-1].split('_',1)[-1]==kw.arg and any(p.startswith('[list]') for p in resolve(kw.value)):alias(ast.Name(id=arg.arg),kw.value)
        for name,nodes in return_nodes.items():
            for node in nodes:returns.setdefault(name,set()).update(resolve(node.value))
        if repr((env,returns))==before:break
    else:error('<API inference did not converge>',tree.body[0],True)
    def supported(path):
        if path.startswith('@dictmethod:'):
            return path.split(':',2)[1] in ('get','pop','setdefault','copy','values','keys','items','clear','update','popitem')
        if path.startswith('@listmethod:'):
            return path.split(':',2)[1] in ('append','extend','clear','copy','pop','insert','remove','reverse','sort','count','index')
        if path.startswith('#'):return True
        if path in allowed:return True
        if path.startswith('bmesh.types.BMElement.'):
            return any(supported(path.replace('bmesh.types.BMElement.','bmesh.types.'+c+'.')) for c in ('BMVert','BMEdge','BMFace'))
        if path.startswith('bpy.types.Modifier.'):
            return any(path.replace('bpy.types.Modifier.','bpy.types.'+c+'.') in allowed for c in ('ArrayModifier','MirrorModifier','TriangulateModifier','SolidifyModifier','BevelModifier','WeldModifier','BooleanModifier','SubsurfModifier','DisplaceModifier','WeightedNormalModifier'))
        if path.startswith('bpy.types.Collection.objects') and path.replace('bpy.types.Collection.objects','bpy.context.collection.objects') in allowed:return True
        if path.startswith('[]'):return path.rsplit('.',1)[-1] in ('append','extend','copy')
        if path.startswith('bpy.types.Curve.') and path.replace('bpy.types.Curve.','bpy.types.TextCurve.') in allowed:return True
        if path.startswith('bpy.types.IDData'):return any(path.replace('bpy.types.IDData','bpy.types.'+t) in allowed for t in ('Mesh','Curve','TextCurve','Camera','Light'))
        # Numeric RNA vectors share the tested Vector methods and swizzles.
        if path.startswith('bpy.types.Object.rotation_quaternion.'):
            return supported(path.replace('bpy.types.Object.rotation_quaternion.','mathutils.Quaternion.'))
        for suffix in ('.location','.scale','.co','.normal','.dimensions','.translation','.uv','.handle_left','.handle_right'):
            if suffix+'.' in path:
                base,tail=path.split(suffix+'.',1)
                if supported(base+suffix):return supported('mathutils.Vector.'+tail)
        if path.startswith('mathutils.Vector.'):
            tail=path[len('mathutils.Vector.'):]
            return 1<=len(tail)<=4 and all(c in 'xyzw' for c in tail)
        return False
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom) and node.module and node.module.split('.')[0] in roots:
            for alias in node.names:
                path=node.module+'.'+alias.name
                if path not in allowed or path.startswith('bpy.types'):error(path,node)
        if isinstance(node,ast.Attribute):
            for path in resolve(node):
                if not supported(path):error(path,node)
        if isinstance(node,(ast.Assign,ast.AnnAssign)):
            for target in node.targets if isinstance(node,ast.Assign) else [node.target]:
                for path in resolve(target):
                    if path=='bpy.types.Modifier.fit_type':
                        valid='FIXED_COUNT' if path.endswith('fit_type') else False
                        if not isinstance(node.value,ast.Constant):error(path+'=<dynamic>',node,True)
                        elif node.value.value!=valid:error(path+'='+repr(node.value.value),node)
                    if path in ('bpy.types.Modifier.levels','bpy.types.Modifier.render_levels') and isinstance(node.value,ast.Constant) and isinstance(node.value.value,(int,float)) and node.value.value>6:error(path+'='+repr(node.value.value),node)
                    if path=='bpy.types.Modifier.solver':
                        if not isinstance(node.value,ast.Constant):error(path+'=<dynamic>',node,True)
                        elif node.value.value!='MANIFOLD':error(path+'='+repr(node.value.value),node)
                    if path=='bpy.types.Modifier.double_threshold':
                        if not isinstance(node.value,ast.Constant):error(path+'=<dynamic>',node,True)
                        elif node.value.value not in (1e-6,9.999999974752427e-7):error(path+'='+repr(node.value.value),node)
                    if path in ('bpy.types.WeightedNormalModifier.weight','bpy.types.WeightedNormalModifier.thresh') and isinstance(node.value,ast.Constant) and isinstance(node.value.value,(int,float)):
                        lo,hi=(1,100) if path.endswith('.weight') else (0,10)
                        if not lo<=node.value.value<=hi:error(path+'='+repr(node.value.value),node)
                    texture_enums={'bpy.types.CloudsTexture.noise_basis':('CELL_NOISE','BLENDER_ORIGINAL'),'bpy.types.CloudsTexture.noise_type':('SOFT_NOISE','HARD_NOISE'),'bpy.types.CloudsTexture.cloud_type':('GRAYSCALE',),'bpy.types.Modifier.direction':('NORMAL','X','Y','Z'),'bpy.types.DisplaceModifier.direction':('NORMAL','X','Y','Z')}
                    if path in texture_enums and isinstance(node.value,ast.Constant) and node.value.value not in texture_enums[path]:error(path+'='+repr(node.value.value),node)
                    weld_fixed={'bpy.types.DisplaceModifier.space':'LOCAL','bpy.types.DisplaceModifier.texture_coords':'LOCAL','bpy.types.Modifier.space':'LOCAL','bpy.types.Modifier.texture_coords':'LOCAL','bpy.types.Modifier.quality':3,'bpy.types.Modifier.uv_smooth':'PRESERVE_BOUNDARIES','bpy.types.Modifier.operand_type':'OBJECT','bpy.types.Modifier.material_mode':'INDEX','bpy.types.Modifier.use_self':False,'bpy.types.Modifier.use_hole_tolerant':False,'bpy.types.Modifier.mode':'ALL','bpy.types.Modifier.loose_edges':False,'bpy.types.Modifier.vertex_group':'','bpy.types.Modifier.invert_vertex_group':False}
                    if path in weld_fixed:
                        if not isinstance(node.value,ast.Constant):error(path+'=<dynamic>',node,True)
                        elif node.value.value!=weld_fixed[path]:error(path+'='+repr(node.value.value),node)
        if isinstance(node,ast.Call):
            if isinstance(node.func,ast.Name) and node.func.id in ('exec','eval','__import__'):error('<dynamic Python execution>',node,True)
            if isinstance(node.func,ast.Name) and node.func.id in ('getattr','setattr','hasattr') and node.args:
                for base in resolve(node.args[0]):
                    if len(node.args)>1 and isinstance(node.args[1],ast.Constant) and isinstance(node.args[1].value,str):
                        path=member(base,node.args[1].value)
                        if not supported(path):error(path,node)
                    else:error(base+'.<dynamic>',node,True)
            for path in resolve(node.func):
                if path=='bmesh.ops.recalc_face_normals':
                    if len(node.args)!=1:error(path+'(expected one BMesh positional argument)',node)
                    for kw in node.keywords:
                        if kw.arg!='faces':error(path+'('+str(kw.arg)+'=...)',node,kw.arg is None)
                if path=='bmesh.ops.extrude_face_region':
                    valid={'geom','edges_exclude','use_keep_orig','use_normal_flip','use_normal_from_adjacent','use_dissolve_ortho_edges','use_select_history'}
                    for kw in node.keywords:
                        if kw.arg not in valid:error(path+'('+str(kw.arg)+'=...)',node,kw.arg is None)
                        if kw.arg in ('use_normal_flip','use_normal_from_adjacent','use_dissolve_ortho_edges','use_select_history') and isinstance(kw.value,ast.Constant) and kw.value.value:error(path+'('+kw.arg+'=True)',node)
                if path=='bpy.data.textures.new':
                    value=next((k.value for k in node.keywords if k.arg=='type'),node.args[1] if len(node.args)>1 else None)
                    if not isinstance(value,ast.Constant):error(path+'(type=<dynamic>)',node,True)
                    elif value.value!='CLOUDS':error(path+'(type='+repr(value.value)+')',node)
                if path=='bpy.types.Object.modifiers.new':
                    value=next((k.value for k in node.keywords if k.arg=='type'),node.args[1] if len(node.args)>1 else None)
                    if not isinstance(value,ast.Constant):error(path+'(type=<dynamic>)',node,True)
                    elif value.value not in ('ARRAY','MIRROR','TRIANGULATE','SOLIDIFY','BEVEL','WELD','BOOLEAN','SUBSURF','DISPLACE','WEIGHTED_NORMAL'):error(path+'(type='+repr(value.value)+')',node)
                if path in ('bpy.ops.object.camera_add','bpy.ops.object.light_add','bpy.ops.object.empty_add'):
                    valid={'align','location','rotation','scale'}|({'enter_editmode'} if path.endswith('camera_add') else {'type','radius'})
                    if node.args:error(path+'(keyword arguments required)',node)
                    for kw in node.keywords:
                        if kw.arg not in valid:error(path+'('+str(kw.arg)+'=...)',node,kw.arg is None)
                        if kw.arg in ('align','enter_editmode'):
                            if not isinstance(kw.value,ast.Constant):error(path+'('+kw.arg+'=<dynamic>)',node,True)
                            elif kw.value.value not in ('WORLD',False):error(path+'('+kw.arg+'='+repr(kw.value.value)+')',node)
                        if kw.arg=='type' and isinstance(kw.value,ast.Constant):
                            choices=('POINT','SUN','SPOT','AREA') if path.endswith('light_add') else ('PLAIN_AXES','ARROWS','SINGLE_ARROW','CIRCLE','CUBE','SPHERE','CONE')
                            if kw.value.value not in choices:error(path+'(type='+repr(kw.value.value)+')',node)
                if path.startswith('bpy.ops.mesh.primitive_'):
                    specific={'cube':{'size'},'ico_sphere':{'subdivisions','radius'},'plane':{'size'},'circle':{'vertices','radius','fill_type'},'cylinder':{'vertices','radius','depth','end_fill_type'},'uv_sphere':{'segments','ring_count','radius'},'cone':{'vertices','radius1','radius2','depth','end_fill_type'},'torus':{'major_segments','minor_segments','mode','major_radius','minor_radius','abso_major_rad','abso_minor_rad','generate_uvs'}}
                    kind=path.removeprefix('bpy.ops.mesh.primitive_').removesuffix('_add')
                    valid=specific.get(kind,set())|({'align','location','rotation'} if kind=='torus' else {'calc_uvs','enter_editmode','align','location','rotation','scale'})
                    for kw in node.keywords:
                        if kw.arg not in valid:error(path+'('+str(kw.arg)+'=...)',node,kw.arg is None)
                        if kw.arg=='align' and isinstance(kw.value,ast.Constant) and kw.value.value not in ('WORLD','CURSOR'):error(path+'(align='+repr(kw.value.value)+')',node)
                        if kw.arg=='enter_editmode' and isinstance(kw.value,ast.Constant) and not isinstance(kw.value.value,bool):error(path+'(enter_editmode='+repr(kw.value.value)+')',node)
    return sorted(errors,key=lambda e:(int(e['location'].rsplit(':',1)[1]),e['message']))
