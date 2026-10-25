# Intentional deviations from Blender

1. **Numeric wrapper types and tolerance.** Vector-valued object location/scale,
   mesh vertex coordinates and UV pairs now support the tested float32 Vector
   subset. RNA Vector views are Python subclasses, so strict type identity and
   type representations are not Blender parity. Euler rotations, colors and socket arrays remain restricted numeric
   views, without arithmetic. The independent Vector implementation is MIT;
   no Blender source is embedded. Tests: `compat/golden/m2_vectors.py`,
   `compat/vector_fuzz.py`, `tests/test_m2.py`. Vector normalization/interpolation
   can differ by a few float32 rounding steps; the 100,000-operation comparison
   uses absolute 1e-5 or relative 1e-6. Full method/operator/type/error parity is won't do (unbounded).
   Extra-family scope follows the 2% preserved-corpus rule in the backlog.
2. **Non-finite values.** hb rejects NaN/infinite coordinates before persistence;
   Blender can retain them. Reason: valid glTF and deterministic scene records
   require finite coordinates. Test: `tests/test_cli.py::CLI.test_nonfinite_transform`.


3. **UV-sphere index ordering and floating-point construction.**
   `bpy.ops.mesh.primitive_uv_sphere_add` and `bmesh.ops.create_uvsphere` use
   stable north-pole, longitude-major interior rings, south-pole indexing.
   Blender's spin-and-merge construction changes vertex and face order during
   pole merging and accumulates float32 rotation error. hb constructs coordinates
   directly, avoiding dependence on that merge ordering. Counts, positions,
   oriented connectivity and corner UVs match the tested Blender fixtures within
   1e-5; scripts relying on Blender's raw sphere indices are not compatible.
   This is an intentional, bounded deviation, not bit-exact topology-array parity.
   Tests: `compat/golden/m2_round_primitives.py`, `compat/golden/m2_bmesh_round.py`,
   `tests/test_round_primitives.py::RoundPrimitives.test_sphere_index_contract_and_render`.
   Only fixtures declaring `HB_EQUIVALENT_MESH_PREFIXES` use index-independent
   comparison; every other mesh retains the exact indexed comparison. The
   comparator validates a vertex bijection, face counts, winding and UV corners;
   `tests/test_equivalent.py` proves it rejects changed positions, reversed
   winding, missing/duplicate geometry and leaves attribute mismatches visible.

4. **Face-region extrusion ordering.**
   `bmesh.ops.extrude_face_region` uses stable original-edge order for generated
   side walls, instead of reproducing Blender's varying side-wall order. Repeated
   extrusion can also place new caps at different face indices when Blender
   reuses removed face storage. Vertex indices, topology, winding, material indices
   and smooth flags retain the tested Blender behavior; face traversal indices
   are not interchangeable. Use the operator's returned cap handles.
   Tests: `compat/golden/m2_extrude.py`,
   `tests/test_extrude.py::Extrusion.test_returned_geometry_cap_winding_and_roundtrip`.
   Only fixtures declaring `HB_FACE_ORDER_MESH_PREFIXES` allow face permutations
   and cyclic corner starts. This comparison leaves vertex coordinates/indices
   untouched and still compares oriented connectivity and all face/corner data.
   `tests/test_equivalent.py::FaceOrder` proves that changed winding, counts,
   duplicate faces, positions and attributes cannot pass unnoticed.

Mixed vertex/edge/face extrusion additionally uses stable duplication traversal
rather than Blender allocation order. The `m3_extrude_mixed.py` golden opts its
explicit mesh names into vertex bijection and oriented face equivalence; original
face-only goldens retain their existing comparison. The 102-case fixture also
checks edge multiplicity and returned geometry counts at the unchanged 1e-5 bound.

5. **Boolean mesh index ordering.**
   Manifold booleans preserve tested positions, oriented polygon connectivity,
   material indices, smooth flags and UV corners, but not Blender's raw vertex,
   polygon or edge traversal indices. Original face regions are reconstructed
   from kernel provenance; holes are decomposed into simple polygons. Only the
   Boolean fixtures declaring `HB_EQUIVALENT_MESH_PREFIXES` use the existing
   bijection comparator. Its tolerances and topology checks are unchanged.
   Tests: `compat/golden/m2_boolean.py`, `m2_boolean_shapes.py`,
   `m2_boolean_holes.py`, and `tests/test_boolean.py`.
   Relative transforms that reverse orientation are explicitly unsupported:
   Blender's MANIFOLD result in that case differs from an outward-oriented
   solid operation, and its corner transfer has not been reproduced.

Only the declared assembly/modeling subset is supported. Unsupported values (panoramic
cameras, unsupported node graphs, other rotation modes, etc.) fail explicitly.
Native hb previews, spatial queries, import metadata and revision tools are hb
extensions and do not claim to be Blender operations. Their scope and methods
are documented in `docs/compatibility.md` and `hb capabilities`.

## SUBSURF topology ordering

CPU OpenSubdiv returns a deterministic refinement order different from Blender's
mesh allocation order. `compat/golden/m2_subsurf.py` explicitly opts its named
subdivision meshes into the existing vertex-bijection comparison. Geometry,
vertex counts, oriented face connectivity, UV values, material indices and smooth
flags are still compared; GLB counts remain exact. This avoids coupling the
engine to Blender's internal index allocation. It does not permit missing faces,
reversed winding, texture seams or a tolerance increase. Supported subdivision
levels, quality and interpolation modes are stated in `docs/compatibility.md`.

## Rotation representations

Tracking quaternions use a deterministic matrix-to-quaternion conversion. A
quaternion and its negation encode the same rotation; hb may choose the opposite
sign from Blender's shortest-arc/roll construction. Tracking comparisons therefore
check the full 3x3 rotation, including roll, rather than require a particular sign.
Euler angles can also differ by equivalent full turns at branch boundaries. These
are representation differences, not permission to relax the 1e-5 transform check.
The randomized matrix/Euler/quaternion workload and axial tracking probes retain
these numerical checks. Matrix storage currently supports square sizes 2–4.

Object dimensions are evaluated on demand. Blender can expose stale dependency-
graph values until `view_layer.update()`; hb immediately reflects current geometry
and transforms. Assignment follows Blender's local-scale behavior, including its
surprising interaction with parent scale, and preserves existing scale signs.

## Weighted corner normals

WEIGHTED_NORMAL uses the measured float32 area/angle weighting and a compact
polar normal representation. It currently supports weight 50, threshold 0.01,
three weighting modes and `keep_sharp`; face-strength/vertex-group influence and
existing custom corner normals are rejected. Nonfinite or near-zero weighted
sums (length below 1e-6) are rejected explicitly, rather than approximating
Blender's degenerate-geometry fallback. The workload limit is one million
vertices and two million corners. Loose vertices are retained.

The differential test captures Blender's exact input geometry separately from
the BEVEL → WEIGHTED_NORMAL composition. Exact-input normals retain the 1e-5
component tolerance. Composed normals use 1e-4: existing float32 bevel coordinate
approximation can move a packed-normal quantization boundary. The golden scene
and GLB tests retain their existing geometry tolerances and exact exported
vertex/index counts. This is not a general tolerance increase for geometry or
transforms. Export deduplication treats positive and negative zero as equal.

## Editable transforms and standalone Color

Editable mesh transform operators accept 3x3/4x4 matrices and nonsingular
transform space. Duplicate vertex inputs are rejected before editing, matching
Blender. Shape-key editing remains excluded. Primitive matrices transform only
the newly created vertices; editable UV layers remain unsupported. The existing
UV-sphere index equivalence also applies to transformed editable spheres, while
positions, winding, connectivity, and exported counts are still checked.

Standalone Color supports RGB/HSV arithmetic, freezing and the eight factory
color-space conversions. RGB RNA properties remain restricted numeric views;
convert to an explicit Color for standalone arithmetic. Color-space matrices
are measured numerical data from Blender's factory configuration; custom OCIO
working spaces are unsupported. The scene-linear to sRGB path uses a quantized
fractional-power estimate to match Blender's fast transfer curve, with positive
linear inputs limited to 1e10. Its reciprocal-root rounding and sRGB decoding's
standard power evaluation may differ numerically; the 34,000-operation differential
workload retains the existing 1e-5 absolute / 1e-6 relative math tolerance.

## Ico-sphere construction indices

`primitive_ico_sphere_add` uses a canonical barycentric triangle grid. Vertex and
face indices may differ from Blender's BMesh insertion order. The compatibility
check requires a position bijection, identical oriented connectivity and matching
corner UVs; it does not discard topology, seams or winding. Subdivisions 1..7,
nonnegative radii, WORLD/CURSOR alignment, single-mesh EDIT construction, explicit
scale and optional UVs are the manifest contract. The original icosahedron and its unfolded UV coefficients were
measured in Blender 4.5.9 before implementation. Higher subdivisions exceed the
100,000-vertex construction limit. Zero-radius ico spheres retain their indexed
connectivity and UVs; a unit-radius reference supplies the otherwise ambiguous
vertex bijection when every coordinate coincides.

## Parent compensation and glTF shear

`bpy.ops.object.parent_set(type='OBJECT')` retains inverse-parent compensation in
scene evaluation and subsequent transform edits. Blender's glTF exporter
converts a compensated local matrix to translation/rotation/scale, removing
shear that these components cannot represent. hb follows that export behavior
and emits a warning when it removes shear. The stored scene and CPU preview keep
the full affine transform. `keep_transform` supports both values; nonsingular
parents are required. Bone/vertex/rig parenting and other unnamed modes are
outside the operator's manifest contract.

## Mesh origin relocation

`origin_set` exposes `ORIGIN_GEOMETRY` and `GEOMETRY_ORIGIN`, with `MEDIAN` or
`BOUNDS` centers. Shared mesh coordinates shift once; unselected users retain
their object transforms, following Blender. Relocating an origin recomputes child
compensation, including when its center is already zero. Compensating parents
must be nonsingular. Other origin modes and non-mesh geometry types are outside
this operator's current manifest contract; no complete operator-parameter parity
is implied.

## Inset region indexing

`bmesh.ops.inset_region` preserves the original face handles but creates boundary
vertices and rim faces in deterministic traversal order. Blender's new element
indices differ. The golden comparison requires a bijection of vertex positions,
identical oriented face connectivity, material indices, smoothing and corner
attributes; it does not relax geometry or topology.

## BMesh bevel indexing

The complete-cuboid bmesh bevel reuses the native bevel kernel. Original handles
are invalidated as in Blender; all new edges/vertices and the beveled faces are
returned. New indices follow the kernel's deterministic order. The reference
comparison checks bijective geometry and oriented topology, including attributes.

## BMesh subdivision indexing

Linear subdivision retains original handles and matches Blender return categories.
New vertex/face allocation order differs; goldens require a position bijection
and identical oriented topology and attributes. Partial selections use explicit
face edges so the test does not depend on global edge allocation order.

## BMesh plane cuts and shells

Plane cuts and solidification retain surviving original handles. New indices use
deterministic local traversal rather than Blender allocation order. Reference
checks require bijective positions, oriented topology and face attributes.
Solidify supports oriented manifold shells; nonmanifold and singular offset
corners fail before editable topology changes.

## Editable triangulation face ordering

All five quad methods and both n-gon methods are tested. N-gon face allocation and
cyclic corner starts can differ; vertex indices, oriented connectivity and corner
attributes must match. All 400 preserved differential polygons match Blender
connectivity exactly. Original face handles survive and return maps refer to them.

## USDZ packaging and orthographic camera consumers

USDZ uses a USDA default layer, while Blender's exporter uses USDC. Both are
allowed by the [USDZ specification](https://openusd.org/release/spec_usdz.html).
The package preserves oriented polygons, UV/normal corners and face materials;
Blender imports of the two encodings are compared in the compatibility gate.
World environments are omitted with an explicit warning. USD identifiers are
sanitized; original object names remain in `displayName` and `hb:originalName`.

USD camera apertures use tenths of a scene unit, as specified by
[UsdGeomCamera](https://openusd.org/dev/api/class_usd_geom_camera.html).
For a six-meter orthographic view, hb writes aperture 60. Blender 4.5 imports
`ortho_scale=60` instead of 6 and does not export this orthographic camera in the
reference workload. hb keeps standard units and warns about the consumer defect;
the import test records it rather than claiming an exact orthographic round trip.
Perspective camera and light values match Blender's exported reference.

Floating image PNGs retain 16-bit channels; byte images use 8-bit channels. USD's
[`sourceColorSpace=auto`](https://openusd.org/dev/spec_usdpreviewsurface.html)
interprets untagged 8-bit RGB/RGBA as sRGB and untagged 16-bit images as raw.
The fixture compares actual Blender-imported color and alpha pixels; the native
preview and arbitrary consumers are not claimed to be pixel-identical renderers.

### PLY import normal storage and attributes

PLY custom normals are stored as normalized float32 corners. Blender 4.5 encodes
and decodes them in its split-normal representation; the measured non-coplanar
fixture differs by at most 3.92e-5 per component. The PLY oracle comparison alone
uses 5e-5 for these normals; positions, topology and UVs retain their existing
strict checks. Vertex RGB is decoded from sRGB (1e-6 comparison tolerance).
PLY colors are retained on face corners; loose-vertex colors warn that they
cannot be retained in this mesh contract. Unknown scalar/list attributes and
face texcoord lists are skipped with their property names in the warning.

## SOLIDIFY radial fan ordering

NON_MANIFOLD allocates vertices by connected radial face-side fans rather than
Blender's edge-reference traversal. The new fixtures opt into a position bijection
with exact oriented indexed face connectivity, UV-corner and deform-weight
comparisons. The 42-probe oracle also resolves coincident clamped vertices through
incidence and adjacency; it does not reduce comparison to counts or bounds.
Original EXTRUDE fixtures retain their exact indexed comparison.

The bounded constraint solver requires consistent face planes. General degenerate
repair and conflicting thickness constraints are rejected explicitly. Zero offsets
retain Blender's 1e-5 shell minimum; zero total thickness retains its reversed
winding. These are observed Blender semantics, not corrective changes to goldens.

- Legacy Curves are a POLY/round-bevel subset. `CURVE` identity and controls persist
  alongside an internal evaluated surface; open 3D and XY-planar cyclic geometry,
  radius/tilt, UVs and materials have 134 differential checks. Bezier/NURBS, 2D
  fill, caps, profiles, taper and full lifecycle parity are explicitly excluded.

- Text is an explicit static TrueType/ASCII subset. Assign a loaded font before
  evaluating nonempty text; default Bfont geometry is not bundled or substituted.
  Flat fill, line spacing, horizontal alignment and generated UVs are supported.
  Internal triangulation diagonals may differ while boundaries, winding, filled
  area, triangle counts and vertex/corner data remain equivalent.

- Text GLB comparison welds identical position/UV records and excludes normals
  only on zero-area triangles. Blender emits reversed normals and three extra
  vertex records on such triangles in two checked labels. Nondegenerate normals,
  filled topology, UVs, transforms and export bounds remain checked.

- EXT_meshopt_compression import decodes standard modes/filters within explicit
  32 MiB per-view / 64 MiB total bounds. Encoding/repacking and experimental COLOR
  filters are excluded; decompression does not expand the static glTF schema.

## Cuboid bevel precision rejection

The canonical bevel stencil and overlap clamp remain unchanged. HB now refuses
evaluated float32 triangles below the same relative area threshold used by review,
before applying or persisting the modifier. Blender 4.5.9 accepts a 2×1×0.002 m
solid with width 0.08 m and two segments, but its result also contains 16 triangles
below this threshold. Width 0.0008 m produces none. HB's early rejection is an
intentional validity boundary, not a new Blender-equivalent clamp or a promise
that every large bevel is invalid. Existing valid stencil reference comparisons
retain their topology, coordinate and UV tolerances.

Tests: `tests/test_engine_improvements.py`, `tests/test_bevel.py`. Measured oracle:
`outputs/subway-rush/engine-evidence/blender-bevel-reference.json`.
