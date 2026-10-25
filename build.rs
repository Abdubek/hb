use std::{env, io::Write, path::PathBuf, process::Command};
fn main() {
    let root = PathBuf::from(env::var("CARGO_MANIFEST_DIR").unwrap());
    let py = env::var_os("HB_PYTHON_SOURCE")
        .map(PathBuf::from)
        .unwrap_or(root.join(".build/Python-3.13.7"));
    let out = PathBuf::from(env::var("OUT_DIR").unwrap());
    // Keep canonical coefficient JSON reviewable while embedding compact data.
    for name in [
        "bevel_stencils",
        "bevel_uv_stencils",
        "bevel_vertex_stencils",
        "bevel_vertex_uv_stencils",
    ] {
        let source = root.join(format!("src/core/{name}.json"));
        let mut encoder = flate2::write::ZlibEncoder::new(Vec::new(), flate2::Compression::best());
        encoder.write_all(&std::fs::read(&source).unwrap()).unwrap();
        std::fs::write(
            out.join(format!("{name}.json.zlib")),
            encoder.finish().unwrap(),
        )
        .unwrap();
        println!("cargo:rerun-if-changed={}", source.display());
    }
    let mut meshopt = cc::Build::new();
    meshopt
        .cpp(true)
        .std("c++11")
        .define("MESHOPTIMIZER_NO_SIMD", None)
        .flag_if_supported("-Os")
        .warnings(false)
        .cpp_link_stdlib(None);
    for file in ["vertexcodec.cpp", "indexcodec.cpp", "vertexfilter.cpp"] {
        let path = root.join("third_party/meshoptimizer").join(file);
        meshopt.file(&path);
        println!("cargo:rerun-if-changed={}", path.display());
    }
    println!("cargo:rerun-if-changed=third_party/meshoptimizer/meshoptimizer.h");
    meshopt.compile("hb_meshopt");
    let mut manifold = cc::Build::new();
    manifold
        .cpp(true)
        .std("c++17")
        .include("third_party/manifold/include")
        .define("MANIFOLD_PAR", "-1")
        .define("MANIFOLD_NO_IOSTREAM", None)
        .define("MANIFOLD_NO_FILESYSTEM", None)
        .flag_if_supported("-ffp-contract=off")
        .flag_if_supported("-Os")
        .warnings(false)
        .cpp_link_stdlib(None)
        .file("src/core/manifold_bridge.cpp");
    for source in [
        "boolean3",
        "boolean_result",
        "constructors",
        "csg_tree",
        "edge_op",
        "execution_impl",
        "face_op",
        "impl",
        "manifold",
        "minkowski",
        "polygon",
        "properties",
        "quickhull",
        "sdf",
        "smoothing",
        "sort",
        "subdivision",
        "tree2d",
    ] {
        manifold.file(format!("third_party/manifold/src/{source}.cpp"));
    }
    manifold.compile("hb_manifold");
    let mut subdivision = cc::Build::new();
    subdivision
        .cpp(true)
        .std("c++17")
        .include("third_party/opensubdiv")
        .flag_if_supported("-ffp-contract=off")
        .flag_if_supported("-Os")
        .warnings(false)
        .cpp_link_stdlib(None)
        .file("src/core/subsurf_bridge.cpp");
    for part in ["far", "vtr", "sdc"] {
        let mut files: Vec<_> =
            std::fs::read_dir(root.join("third_party/opensubdiv/opensubdiv").join(part))
                .unwrap()
                .map(|entry| entry.unwrap().path())
                .filter(|path| path.extension().is_some_and(|ext| ext == "cpp"))
                .collect();
        files.sort();
        for file in files {
            subdivision.file(file);
        }
    }
    subdivision.compile("hb_subdivision");
    println!("cargo:rerun-if-changed=third_party/opensubdiv");
    println!("cargo:rerun-if-changed=src/core/subsurf_bridge.cpp");
    if env::var("CARGO_CFG_TARGET_OS").unwrap() == "linux" {
        let compiler = manifold.get_compiler();
        let location = Command::new(compiler.path())
            .arg("-print-file-name=libstdc++.a")
            .output()
            .unwrap();
        let archive = PathBuf::from(String::from_utf8(location.stdout).unwrap().trim());
        assert!(
            archive.is_file(),
            "Static libstdc++ is required for the Linux binary"
        );
        println!(
            "cargo:rustc-link-search=native={}",
            archive.parent().unwrap().display()
        );
        println!("cargo:rustc-link-lib=static=stdc++");
    } else {
        println!("cargo:rustc-link-lib=c++");
    }
    println!("cargo:rerun-if-changed=third_party/manifold");
    println!("cargo:rerun-if-changed=src/core/manifold_bridge.cpp");
    let exe = if py.join("python.exe").exists() {
        py.join("python.exe")
    } else {
        py.join("python")
    };
    assert!(exe.exists(), "Run ./scripts/build_python.sh first");
    assert!(
        Command::new(exe)
            .arg(root.join("scripts/freeze_stdlib.py"))
            .arg(py.join("Lib"))
            .arg(out.join("frozen.c"))
            .status()
            .unwrap()
            .success()
    );
    cc::Build::new()
        .include(&py)
        .include(py.join("Include"))
        .file("pyshim/embed.c")
        .file(out.join("frozen.c"))
        .flag_if_supported("-Os")
        .compile("hb_embed");
    println!("cargo:rustc-link-search=native={}", py.display());
    println!("cargo:rustc-link-lib=static=python3.13");
    for lib in ["m", "dl", "pthread"] {
        println!("cargo:rustc-link-lib={lib}");
    }
    #[cfg(target_os = "macos")]
    println!("cargo:rustc-link-lib=framework=CoreFoundation");
    println!("cargo:rerun-if-env-changed=HB_PYTHON_SOURCE");
    for p in [
        "pyshim",
        "compat/manifest.json",
        "scripts/freeze_stdlib.py",
        "scripts/frozen_codec_maps.py",
    ] {
        println!("cargo:rerun-if-changed={p}");
    }
}
