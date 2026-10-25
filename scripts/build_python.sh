#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
version=3.13.7
src="$PWD/.build/Python-$version"
if [ ! -f "$src/configure" ]; then
    mkdir -p .build
    if [ ! -f ".build/Python-$version.tar.xz" ]; then
        curl --retry 3 -fL "https://www.python.org/ftp/python/$version/Python-$version.tar.xz" -o ".build/Python-$version.tar.xz.part"
        mv ".build/Python-$version.tar.xz.part" ".build/Python-$version.tar.xz"
    fi
    expected=5462f9099dfd30e238def83c71d91897d8caa5ff6ebc7a50f14d4802cdaaa79a
    if command -v sha256sum >/dev/null; then
        actual=$(sha256sum ".build/Python-$version.tar.xz" | cut -d ' ' -f 1)
    else
        actual=$(shasum -a 256 ".build/Python-$version.tar.xz" | cut -d ' ' -f 1)
    fi
    test "$actual" = "$expected" || { echo 'CPython archive checksum mismatch' >&2; exit 1; }
    tar -xf ".build/Python-$version.tar.xz" -C .build
fi
cd "$src"
# Static built-ins avoid runtime extension libraries. Disable all nonessential modules.
cat > Modules/Setup.local <<'SETUP'
*static*
math mathmodule.c
_struct _struct.c
_json _json.c
_random _randommodule.c
*disabled*
_asyncio _bisect _blake2 _bz2 _codecs_cn _codecs_hk _codecs_iso2022 _codecs_jp _codecs_kr _codecs_tw _contextvars _crypt _csv _ctypes _curses _curses_panel _dbm _decimal _elementtree _gdbm _hashlib _heapq _interpreters _interpchannels _interpqueues _lsprof _lzma _md5 _multibytecodec _multiprocessing _opcode _pickle _posixshmem _posixsubprocess _queue _scproxy _sha1 _sha2 _sha3 _socket _sqlite3 _ssl _statistics _testbuffer _testcapi _testclinic _testclinic_limited _testimportmultiple _testinternalcapi _testlimitedcapi _testmultiphase _testsinglephase _tkinter _uuid _xxsubinterpreters _xxtestfuzz array audioop binascii fcntl grp mmap nis ossaudiodev pyexpat readline resource select spwd syslog termios unicodedata xxlimited xxlimited_35 zlib
SETUP
if [ ! -f Makefile ]; then
    ./configure --disable-shared --without-ensurepip --without-doc-strings --disable-test-modules CFLAGS="-Os -fPIC" > ../python-configure.log 2>&1
fi
python_target=python
if [ "$(uname -s)" = Darwin ]; then python_target=python.exe; fi
make -j "${HB_BUILD_JOBS:-8}" "$python_target" libpython3.13.a > ../python-build.log 2>&1
