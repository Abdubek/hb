use super::*;
use math::*;
fn triangle_scene() -> Scene {
    let mut s = Scene::default();
    let mesh = s.create("meshes", "Triangle", json!({})).unwrap();
    s.mesh_from(
        mesh,
        json!([[-2., -2., -3.], [2., -2., -3.], [0., 2., -3.]]),
        json!([]),
        json!([[0, 1, 2]]),
        false,
    )
    .unwrap();
    let m = s
        .create("materials", "Red", json!({"diffuse_color":[1.,0.,0.,1.]}))
        .unwrap();
    s.get_mut("meshes", mesh).unwrap()["materials"] = json!([m]);
    let object = s
        .create(
            "objects",
            "Triangle",
            json!({"data":{"kind":"meshes","id":mesh}}),
        )
        .unwrap();
    s.link(1, object, false, false).unwrap();
    let camera = s.create("cameras", "Lens", json!({})).unwrap();
    let object = s
        .create(
            "objects",
            "Camera",
            json!({"data":{"kind":"cameras","id":camera}}),
        )
        .unwrap();
    s.link(1, object, false, false).unwrap();
    s.camera = Some(object);
    s
}
#[test]
fn revision_survives_float_roundtrip() {
    let mut s = Scene::default();
    s.create(
        "objects",
        "Float",
        json!({"location":[0.017453292519943295,0.8660254037844386,0.3333333333333333]}),
    )
    .unwrap();
    let bytes = serde_json::to_vec(&s).unwrap();
    let copy: Scene = serde_json::from_slice(&bytes).unwrap();
    assert_eq!(bytes, serde_json::to_vec(&copy).unwrap());
    assert_eq!(
        s.revision("script", None, 42),
        copy.revision("script", None, 42)
    );
}
#[test]
fn matrix_parent_inverse() {
    let m = matmul(
        trs([1., 2., 3.], [0.3, -0.2, 0.7], [2., 3., 4.]),
        trs([4., 5., 6.], [0.1, 0.2, 0.3], [1.; 3]),
    );
    let identity = matmul(inverse(m).unwrap(), m);
    for i in 0..4 {
        for j in 0..4 {
            assert!((identity[i][j] - IDENTITY[i][j]).abs() < 1e-12);
        }
    }
    let p = [1., 2., 3.];
    assert_eq!(point(Y_TO_Z, point(Z_TO_Y, p)), p);
}
#[test]
fn concave_polygon_area() {
    let p = vec![
        [0., 0., 0.],
        [2., 0., 0.],
        [2., 1., 0.],
        [1., 1., 0.],
        [1., 2., 0.],
        [0., 2., 0.],
    ];
    let triangles = geometry::triangulate(&p).unwrap();
    let area: f64 = triangles
        .iter()
        .map(|t| length(cross(sub(p[t[1]], p[t[0]]), sub(p[t[2]], p[t[0]]))) * 0.5)
        .sum();
    assert_eq!(triangles.len(), 4);
    assert!((area - 3.).abs() < 1e-12);
}
#[test]
fn raster_depth_and_frustum_clipping() {
    let s = triangle_scene();
    let renderer = render::Renderer::new(&s).unwrap();
    let camera = render::Camera::scene(&s, None, 1.).unwrap();
    assert!(camera.intersects(&renderer.geometry.triangles[0]));
    let image = renderer.frame(&camera, 64, 64, false);
    let center = image.get_pixel(32, 32);
    assert!(center[0] > center[1] * 2);
    let mut clipped = camera.clone();
    clipped.near = 4.;
    assert!(!clipped.intersects(&renderer.geometry.triangles[0]));
    assert_ne!(
        renderer.frame(&clipped, 64, 64, false).get_pixel(32, 32),
        center
    );
}
#[test]
fn image_orientation_and_linear_filter() {
    let v = json!({"width":2,"height":2,"pixels":[1.,0.,0.,1.,0.,1.,0.,1.,0.,0.,1.,1.,1.,1.,1.,1.],"colorspace":"Non-Color"});
    let texture = images::Texture::new(&v).unwrap();
    assert_eq!(texture.sample([0.25, 0.25], false), [1., 0., 0., 1.]);
    assert_eq!(texture.sample([0.25, 0.75], false), [0., 0., 1., 1.]);
    assert_eq!(texture.sample([1.25, 0.25], false), [1., 0., 0., 1.]);
}
#[test]
fn camera_and_area_light_gltf_roundtrip() {
    let mut s = triangle_scene();
    let key = id(&s.cameras[0]);
    s.get_mut("cameras", key).unwrap()["shift_x"] = json!(0.125);
    let light = s
        .create(
            "lights",
            "Area",
            json!({"type":"AREA","energy":50.,"size":2.}),
        )
        .unwrap();
    let o = s
        .create(
            "objects",
            "Area",
            json!({"data":{"kind":"lights","id":light},"location":[1.,2.,3.]}),
        )
        .unwrap();
    s.link(1, o, false, false).unwrap();
    let (bytes, _) = io::glb(&s).unwrap();
    let path = std::env::temp_dir().join(format!("hb-roundtrip-{}.glb", std::process::id()));
    std::fs::write(&path, bytes).unwrap();
    let mut restored = Scene::default();
    io::import(&mut restored, &path).unwrap();
    std::fs::remove_file(path).unwrap();
    assert_eq!(restored.cameras[0]["shift_x"], 0.125);
    assert_eq!(restored.lights[0]["type"], "AREA");
    assert_eq!(restored.lights[0]["energy"], 50.);
}

#[test]
fn floating_image_color_export_and_linear_sampling() {
    let v =
        json!({"width":1,"height":1,"pixels":[0.25,0.5,0.75,1.0],"colorspace":"Linear Rec.709"});
    let color = image::load_from_memory(&images::png(&v, true).unwrap())
        .unwrap()
        .to_rgba8();
    let data = image::load_from_memory(&images::png(&v, false).unwrap())
        .unwrap()
        .to_rgba8();
    assert_eq!(color.get_pixel(0, 0).0, [137, 188, 225, 255]);
    assert_eq!(data.get_pixel(0, 0).0, [64, 128, 191, 255]);
    assert_eq!(images::pixels(&v).unwrap(), vec![0.25, 0.5, 0.75, 1.0]);
    let sample = images::Texture::new(&v).unwrap().sample([0.5, 0.5], true);
    assert!((sample[0] - 0.25).abs() < 0.002);
}
