# Third-party material

HB's original code is licensed under [MIT](LICENSE). Imported code and test
fixtures retain their own licenses and attribution.

| Material | License and provenance |
| --- | --- |
| Embedded CPython | [PSF license](docs/CPYTHON-LICENSE.txt), pinned build in `scripts/build_python.sh` |
| Manifold, OpenSubdiv, meshoptimizer | Licenses and source inventories in [third_party](third_party) |
| MT19937 random-number implementation | [BSD notice](docs/LICENSE-MT19937) |
| Compatibility fonts | [Font provenance](compat/fixtures/fonts/README.md) |
| Public compatibility snippets | [Corpus provenance](compat/corpus/README.md) and per-sample licenses in `compat/corpus/index.json` |
| GitHub compatibility samples | [Source records](compat/github/README.md) |

The executable includes dependency notices through `hb licenses`. Full notices
are also in [docs/THIRD-PARTY-NOTICES.txt](docs/THIRD-PARTY-NOTICES.txt).
Blender is an external compatibility reference and is not bundled with HB.
