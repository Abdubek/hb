// hb's narrow C ABI around the Apache-2.0 Manifold kernel.
// No C++ object or exception crosses the Rust boundary.
#include <algorithm>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <exception>
#include <memory>
#include <stdexcept>
#include <vector>
#include "manifold/manifold.h"

extern "C" {
struct HbManifoldInput {
  const double* properties;
  const uint64_t* triangles;
  const uint64_t* merge_from;
  const uint64_t* merge_to;
  const uint64_t* face_ids;
  size_t vertex_count;
  size_t triangle_count;
  size_t merge_count;
  size_t property_count;
};
struct HbManifoldView {
  const double* properties;
  const uint64_t* triangles;
  const uint64_t* merge_from;
  const uint64_t* merge_to;
  const uint64_t* face_ids;
  size_t vertex_count;
  size_t triangle_count;
  size_t merge_count;
  size_t property_count;
};
}

namespace {
struct Result { manifold::MeshGL64 mesh; };
manifold::Manifold input_mesh(const HbManifoldInput& in, uint32_t original) {
  manifold::MeshGL mesh;
  mesh.numProp=in.property_count;
  if (in.vertex_count) mesh.vertProperties.assign(in.properties,in.properties+in.vertex_count*in.property_count);
  if (in.triangle_count) {
    mesh.triVerts.assign(in.triangles,in.triangles+in.triangle_count*3);
    mesh.faceID.assign(in.face_ids,in.face_ids+in.triangle_count);
    mesh.runIndex={0,static_cast<uint32_t>(in.triangle_count*3)};
    mesh.runOriginalID={original};
  }
  if (in.merge_count) {
    mesh.mergeFromVert.assign(in.merge_from,in.merge_from+in.merge_count);
    mesh.mergeToVert.assign(in.merge_to,in.merge_to+in.merge_count);
  }
  manifold::Manifold solid(mesh);
  if (solid.Status()!=manifold::Manifold::Error::NoError)
    throw std::runtime_error("BOOLEAN requires closed, consistently oriented manifold operands (Manifold status "+std::to_string(static_cast<int>(solid.Status()))+")");
  return solid;
}
}

extern "C" void* hb_manifold_boolean(const HbManifoldInput* a,const HbManifoldInput* b,int operation,char* error,size_t error_size) noexcept {
  try {
    const auto first=manifold::Manifold::ReserveIDs(2);
    const auto left=input_mesh(*a,first),right=input_mesh(*b,first+1);
    const auto op=operation==0?manifold::OpType::Add:operation==1?manifold::OpType::Subtract:manifold::OpType::Intersect;
    auto solid=left.Boolean(right,op);
    if (solid.Status()!=manifold::Manifold::Error::NoError)
      throw std::runtime_error("Manifold boolean evaluation failed with status "+std::to_string(static_cast<int>(solid.Status())));
    auto result=std::make_unique<Result>();result->mesh=solid.GetMeshGL64();
    if (result->mesh.faceID.size()!=result->mesh.NumTri() || result->mesh.numProp!=3 || result->mesh.mergeFromVert.size()!=result->mesh.mergeToVert.size())
      throw std::runtime_error("BOOLEAN returned an invalid mesh layout");
    if (result->mesh.NumVert()>2000000 || result->mesh.NumTri()>2000000)
      throw std::runtime_error("BOOLEAN result exceeds 2,000,000 vertices/triangles");
    return result.release();
  } catch (const std::exception& exception) {
    if (error_size) std::snprintf(error,error_size,"%s",exception.what());
  } catch (...) {
    if (error_size) std::snprintf(error,error_size,"Unknown Manifold exception");
  }
  return nullptr;
}
extern "C" void hb_manifold_view(const void* opaque,HbManifoldView* view) noexcept {
  const auto& mesh=static_cast<const Result*>(opaque)->mesh;
  *view={mesh.vertProperties.data(),mesh.triVerts.data(),mesh.mergeFromVert.data(),mesh.mergeToVert.data(),mesh.faceID.data(),mesh.NumVert(),mesh.NumTri(),mesh.mergeFromVert.size(),mesh.numProp};
}
extern "C" void hb_manifold_free(void* opaque) noexcept { delete static_cast<Result*>(opaque); }

#include "manifold/polygon.h"
extern "C" size_t hb_text_triangulate(const double* xy, const uint32_t* lengths,
    size_t contour_count, uint32_t* triangles, size_t triangle_capacity,
    char* error, size_t error_size) noexcept {
  try {
    manifold::Polygons polygons;
    size_t offset=0;
    for (size_t i=0;i<contour_count;++i) {
      manifold::SimplePolygon polygon;
      for (size_t j=0;j<lengths[i];++j,++offset) polygon.push_back({xy[2*offset],xy[2*offset+1]});
      polygons.push_back(std::move(polygon));
    }
    auto result=manifold::Triangulate(polygons);
    if (result.size()>triangle_capacity) throw std::runtime_error("Text triangle limit exceeded");
    for (size_t i=0;i<result.size();++i) for (size_t j=0;j<3;++j) triangles[3*i+j]=result[i][j];
    return result.size();
  } catch (const std::exception& exception) {
    if (error_size) std::snprintf(error,error_size,"%s",exception.what());
  } catch (...) {
    if (error_size) std::snprintf(error,error_size,"Text triangulation failed");
  }
  return SIZE_MAX;
}
