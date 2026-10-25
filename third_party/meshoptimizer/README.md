# meshoptimizer decoder source

Unmodified files from [meshoptimizer v0.25](https://github.com/zeux/meshoptimizer/tree/6daea4695c48338363b08022d2fb15deaef6ac09), commit `6daea4695c48338363b08022d2fb15deaef6ac09`. MIT license: [LICENSE.md](LICENSE.md).

hb links the three EXT_meshopt_compression decoders and standard post-filters. SIMD is disabled for a portable scalar implementation across the two release targets. Encoder/experimental filter code is present in upstream source but unused and removed by linker section collection. No compression or repacking export path is exposed.

Reference regeneration: fetch the pinned `js/meshopt_encoder.js` and `js/meshopt_decoder.js` into `.build/compatibility/meshopt/upstream/`, then run `node products/hb/compat/meshopt_reference.cjs` from the repository root. The first 57 cases are the preserved codec oracle; generated asset twins are copied from `.build/compatibility/meshopt/assets` to `products/hb/compat/fixtures/meshopt`.
