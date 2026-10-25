# Test-only image: Blender is never included in the hb runtime image.
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl xz-utils python3 libx11-6 libxxf86vm1 libxfixes3 libxi6 libxkbcommon0 libsm6 libgl1 libegl1 libxrender1 libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /opt
COPY scripts/verify_blender_download.py /opt/verify_blender_download.py
RUN mkdir .build && curl --retry 3 -fL https://download.blender.org/release/Blender4.5/blender-4.5.9-linux-x64.tar.xz -o .build/blender.tar.xz && curl --retry 3 -fL https://download.blender.org/release/Blender4.5/blender-4.5.9.sha256 -o .build/blender.sha256 && python3 verify_blender_download.py && tar -xf .build/blender.tar.xz && mv blender-4.5.9-linux-x64 blender && rm -r .build
# Original OBJ operators were removed in Blender 4; keep their actual 3.6 oracle.
RUN mkdir .build && curl --retry 3 -fL https://download.blender.org/release/Blender3.6/blender-3.6.23-linux-x64.tar.xz -o .build/blender.tar.xz && curl --retry 3 -fL https://download.blender.org/release/Blender3.6/blender-3.6.23.sha256 -o .build/blender.sha256 && python3 verify_blender_download.py blender-3.6.23-linux-x64.tar.xz && tar -xf .build/blender.tar.xz && mv blender-3.6.23-linux-x64 blender-legacy && rm -r .build
WORKDIR /workspace
