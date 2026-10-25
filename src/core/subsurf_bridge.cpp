// Narrow C ABI for OpenSubdiv's CPU topology and primitive-variable refinement.
#include "opensubdiv/far/topologyDescriptor.h"
#include "opensubdiv/far/topologyRefinerFactory.h"
#include "opensubdiv/far/primvarRefiner.h"
#include "opensubdiv/far/error.h"
#include "opensubdiv/far/patchTableFactory.h"
#include "opensubdiv/far/patchMap.h"
#include "opensubdiv/far/ptexIndices.h"
#include <array>
#include <memory>
#include <vector>
#include <string>
#include <mutex>
#include <stdexcept>
#include <cstdio>
#include <cstdint>
#include <cstddef>
namespace Far=OpenSubdiv::Far;namespace Sdc=OpenSubdiv::Sdc;
extern "C" {
struct HbSubdivInput {
 const float* positions;const int32_t* face_counts;const int32_t* face_indices;
 const float* uv_values;const int32_t* uv_indices;const int32_t* uv_counts;
 const int32_t* crease_edges;const float* crease_weights;const float* vertex_creases;
 const float* colors;const float* normals;size_t crease_count;int use_creases;
 size_t vertex_count,face_count,corner_count,uv_layer_count;
};
struct HbSubdivView {
 const float* positions;const int32_t* faces;const int32_t* source_faces;const float* uv;
 const float* colors;const float* normals;const float* vertex_creases;const int32_t* crease_edges;const float* crease_weights;const int32_t* original_vertices;size_t crease_count;
 size_t vertex_count,face_count,uv_layer_count;
};
}
namespace {
static_assert(sizeof(Far::Index)==sizeof(int32_t));
template <int N> struct Primvar {
 float values[N]={};
 void Clear(){for(auto& v:values)v=0;}
 void AddWithWeight(const Primvar& source,float weight){for(int i=0;i<N;i++)values[i]+=source.values[i]*weight;}
};
struct Result { std::vector<Primvar<3>> positions;std::vector<int32_t> faces,source_faces;std::vector<float> uv,colors,normals,vertex_creases,crease_weights;std::vector<int32_t> crease_edges,original_vertices;size_t uv_layer_count; };
thread_local std::string last_error;
void error_callback(Far::ErrorType,const char* message){if(last_error.empty())last_error=message;}
void warning_callback(const char* message){if(last_error.empty())last_error=message;}
void check_error(){if(!last_error.empty())throw std::runtime_error("SUBSURF: "+last_error);}
struct SampleFace { int ptex=0;std::array<std::array<float,2>,4> coordinates; };
std::array<float,2> midpoint(std::array<float,2> a,std::array<float,2> b){return {(a[0]+b[0])*.5f,(a[1]+b[1])*.5f};}
std::vector<SampleFace> samples(const Far::TopologyRefiner& refiner,int level){
 const std::array<std::array<float,2>,4> square={{{0,0},{1,0},{1,1},{0,1}}};
 Far::PtexIndices ptex(refiner);std::vector<SampleFace> faces(refiner.GetLevel(0).GetNumFaces());
 for(size_t i=0;i<faces.size();i++)faces[i]={ptex.GetFaceId(i),square};
 for(int depth=1;depth<=level;depth++){
  const auto& parent=refiner.GetLevel(depth-1);const auto& child=refiner.GetLevel(depth);std::vector<SampleFace> next(child.GetNumFaces());
  for(int f=0;f<parent.GetNumFaces();f++){
   auto vertices=parent.GetFaceVertices(f);auto edges=parent.GetFaceEdges(f);auto children=parent.GetFaceChildFaces(f);
   for(int k=0;k<children.size();k++){
    SampleFace sample;std::array<std::array<float,2>,4> coords;
    if(depth==1 && vertices.size()!=4){sample.ptex=faces[f].ptex+k;coords=square;}
    else {sample.ptex=faces[f].ptex;const auto& p=faces[f].coordinates;coords={p[k],midpoint(p[k],p[(k+1)%4]),midpoint(midpoint(p[0],p[1]),midpoint(p[2],p[3])),midpoint(p[k],p[(k+3)%4])};}
    std::array<int,4> ids={parent.GetVertexChildVertex(vertices[k]),parent.GetEdgeChildVertex(edges[k]),parent.GetFaceChildVertex(f),parent.GetEdgeChildVertex(edges[(k+vertices.size()-1)%vertices.size()])};
    auto actual=child.GetFaceVertices(children[k]);
    for(int corner=0;corner<4;corner++){int j=0;while(j<4 && ids[j]!=actual[corner])j++;if(j==4)throw std::runtime_error("SUBSURF child patch parameter mapping failed");sample.coordinates[corner]=coords[j];}
    next[children[k]]=sample;
   }
  }
  faces.swap(next);
 }
 return faces;
}
void evaluate_limit(const HbSubdivInput* in,const Far::TopologyDescriptor& descriptor,const Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Options& options,const Far::TopologyRefiner& uniform,int level,Result& result){
 std::unique_ptr<Far::TopologyRefiner> refiner(Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Create(descriptor,options));check_error();
 if(!refiner)throw std::runtime_error("SUBSURF invalid limit topology");
 Far::PatchTableFactory::Options patch_options(3);patch_options.generateVaryingTables=false;patch_options.generateFVarTables=in->uv_layer_count>0;patch_options.generateFVarLegacyLinearPatches=false;patch_options.useInfSharpPatch=true;
 refiner->RefineAdaptive(patch_options.GetRefineAdaptiveOptions());check_error();
 std::unique_ptr<const Far::PatchTable> patches(Far::PatchTableFactory::Create(*refiner,patch_options));check_error();
 if(!patches)throw std::runtime_error("SUBSURF limit patch construction failed");
 int count=refiner->GetNumVerticesTotal();int local=patches->GetNumLocalPoints();
 if(count+local>8000000)throw std::runtime_error("SUBSURF limit refinement exceeds eight million control points");
 std::vector<Primvar<3>> positions(count+local);for(size_t i=0;i<in->vertex_count;i++)for(int k=0;k<3;k++)positions[i].values[k]=in->positions[i*3+k];
 Far::PrimvarRefiner primvars(*refiner);auto* source=positions.data();
 for(int i=1;i<refiner->GetNumLevels();i++){auto* target=source+refiner->GetLevel(i-1).GetNumVertices();primvars.Interpolate(i,source,target);source=target;}
 if(local)patches->GetLocalPointStencilTable()->UpdateValues(positions.data(),positions.data()+count);
 std::vector<std::vector<Primvar<2>>> uv(in->uv_layer_count);size_t at=0;
 for(size_t channel=0;channel<uv.size();channel++){
  int refined=refiner->GetNumFVarValuesTotal(channel);int local_values=patches->GetNumLocalPointsFaceVarying(channel);
  uv[channel].resize(refined+local_values);for(int i=0;i<in->uv_counts[channel];i++)for(int k=0;k<2;k++)uv[channel][i].values[k]=in->uv_values[at++];
  auto* source=uv[channel].data();for(int i=1;i<refiner->GetNumLevels();i++){auto* target=source+refiner->GetLevel(i-1).GetNumFVarValues(channel);primvars.InterpolateFaceVarying(i,source,target,channel);source=target;}
  if(local_values)patches->GetLocalPointFaceVaryingStencilTable(channel)->UpdateValues(uv[channel].data(),uv[channel].data()+refined);
 }
 check_error();
 // Store one limit value per refined face-varying vertex. Sampling the same
 // UV point separately from adjacent patches introduces float roundoff seams.
 std::vector<std::vector<Primvar<2>>> final_uv(uv.size());std::vector<std::vector<bool>> uv_written(uv.size());
 for(size_t channel=0;channel<uv.size();channel++){int count=uniform.GetLevel(level).GetNumFVarValues(channel);final_uv[channel].resize(count);uv_written[channel].resize(count,false);}
 Far::PatchMap map(*patches);auto sample_faces=samples(uniform,level);std::vector<bool> written(result.positions.size(),false);
 for(size_t face=0;face<sample_faces.size();face++)for(int corner=0;corner<4;corner++){
  auto param=sample_faces[face].coordinates[corner];const auto* patch=map.FindPatch(sample_faces[face].ptex,param[0],param[1]);if(!patch)throw std::runtime_error("SUBSURF could not locate limit patch");
  float weights[32];int vertex=result.faces[4*face+corner];
  if(!written[vertex]){patches->EvaluateBasis(*patch,param[0],param[1],weights);auto cvs=patches->GetPatchVertices(*patch);result.positions[vertex].Clear();for(int k=0;k<cvs.size();k++)result.positions[vertex].AddWithWeight(positions[cvs[k]],weights[k]);written[vertex]=true;}
  for(size_t channel=0;channel<uv.size();channel++){
   int uv_index=uniform.GetLevel(level).GetFaceFVarValues(face,channel)[corner];
   auto& value=final_uv[channel][uv_index];
   if(!uv_written[channel][uv_index]){
    patches->EvaluateBasisFaceVarying(*patch,param[0],param[1],weights,nullptr,nullptr,nullptr,nullptr,nullptr,channel);auto cvs=patches->GetPatchFVarValues(*patch,channel);
    for(int k=0;k<cvs.size();k++)value.AddWithWeight(uv[channel][cvs[k]],weights[k]);
    uv_written[channel][uv_index]=true;
   }
   size_t index=(channel*result.faces.size()+4*face+corner)*2;result.uv[index]=value.values[0];result.uv[index+1]=value.values[1];
  }
 }
 check_error();
}

// Corner colors and preserved normals are bilinear data on the original ptex
// face, independent of geometric smoothing and face-varying UV seam rules.
template<int N> void interpolate_corners(const HbSubdivInput* in,const Far::TopologyRefiner& refiner,int level,const float* source,std::vector<float>& target){
 if(!source)return;
 std::vector<int> starts(in->face_count+1);for(size_t f=0;f<in->face_count;f++)starts[f+1]=starts[f]+in->face_counts[f];
 std::vector<std::array<Primvar<N>,4>> patches;
 for(size_t f=0;f<in->face_count;f++){
  int count=in->face_counts[f];std::vector<Primvar<N>> corners(count);Primvar<N> center;
  for(int i=0;i<count;i++){for(int k=0;k<N;k++)corners[i].values[k]=source[(starts[f]+i)*N+k];center.AddWithWeight(corners[i],1.f/count);}
  if(count==4){patches.push_back({corners[0],corners[1],corners[2],corners[3]});continue;}
  for(int i=0;i<count;i++){Primvar<N> after,before;after.AddWithWeight(corners[i],.5f);after.AddWithWeight(corners[(i+1)%count],.5f);before.AddWithWeight(corners[i],.5f);before.AddWithWeight(corners[(i+count-1)%count],.5f);patches.push_back({corners[i],after,center,before});}
 }
 auto sample_faces=samples(refiner,level);target.reserve(sample_faces.size()*4*N);
 for(const auto& face:sample_faces)for(auto uv:face.coordinates){
  float u=uv[0],v=uv[1];std::array<float,4> w={(1-u)*(1-v),u*(1-v),u*v,(1-u)*v};Primvar<N> value;
  for(int i=0;i<4;i++)value.AddWithWeight(patches[face.ptex][i],w[i]);
  for(float x:value.values)target.push_back(x);
 }
}

}
extern "C" void* hb_subdivide(const HbSubdivInput* in,int level,int simple,int limit,int corners,char* error,size_t error_size) noexcept {
 try {
  static std::once_flag callbacks;
  std::call_once(callbacks,[]{Far::SetErrorCallback(error_callback);Far::SetWarningCallback(warning_callback);});last_error.clear();
  if(level<1 || level>6 || !in->face_count || in->vertex_count>2000000 || in->face_count>2000000 || in->uv_layer_count>8)throw std::runtime_error("SUBSURF invalid input bounds");
  Far::TopologyDescriptor descriptor;descriptor.numVertices=in->vertex_count;descriptor.numFaces=in->face_count;descriptor.numVertsPerFace=in->face_counts;descriptor.vertIndicesPerFace=in->face_indices;
  std::vector<float> sharpness(in->crease_count);std::vector<int> corner_indices;std::vector<float> corner_sharpness;
  if(in->use_creases){
   for(size_t i=0;i<in->crease_count;i++)sharpness[i]=in->crease_weights[i]*in->crease_weights[i]*10.f;
   for(size_t i=0;i<in->vertex_count;i++)if(in->vertex_creases[i]>0){corner_indices.push_back(i);corner_sharpness.push_back(in->vertex_creases[i]*in->vertex_creases[i]*10.f);}
   descriptor.numCreases=in->crease_count;descriptor.creaseVertexIndexPairs=in->crease_edges;descriptor.creaseWeights=sharpness.data();
   descriptor.numCorners=corner_indices.size();descriptor.cornerVertexIndices=corner_indices.data();descriptor.cornerWeights=corner_sharpness.data();
  }
  std::vector<Far::TopologyDescriptor::FVarChannel> channels(in->uv_layer_count);
  for(size_t i=0;i<channels.size();i++){channels[i].numValues=in->uv_counts[i];channels[i].valueIndices=in->uv_indices+i*in->corner_count;}
  descriptor.numFVarChannels=channels.size();descriptor.fvarChannels=channels.data();
  Sdc::Options settings;settings.SetVtxBoundaryInterpolation(corners?Sdc::Options::VTX_BOUNDARY_EDGE_AND_CORNER:Sdc::Options::VTX_BOUNDARY_EDGE_ONLY);settings.SetFVarLinearInterpolation(Sdc::Options::FVAR_LINEAR_BOUNDARIES);
  Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Options options(simple?Sdc::SCHEME_BILINEAR:Sdc::SCHEME_CATMARK,settings);options.validateFullTopology=true;
  std::unique_ptr<Far::TopologyRefiner> refiner(Far::TopologyRefinerFactory<Far::TopologyDescriptor>::Create(descriptor,options));check_error();
  if(!refiner)throw std::runtime_error("SUBSURF invalid topology");
  Far::TopologyRefiner::UniformOptions uniform(level);uniform.fullTopologyInLastLevel=true;refiner->RefineUniform(uniform);check_error();
  const auto& final_level=refiner->GetLevel(level);
  if(final_level.GetNumVertices()>2000000 || final_level.GetNumFaces()>2000000)throw std::runtime_error("SUBSURF output exceeds two million vertices/faces");
  auto result=std::make_unique<Result>();result->uv_layer_count=in->uv_layer_count;
  result->positions.resize(in->vertex_count);for(size_t i=0;i<in->vertex_count;i++)for(int j=0;j<3;j++)result->positions[i].values[j]=in->positions[3*i+j];
  result->source_faces.resize(in->face_count);for(size_t i=0;i<in->face_count;i++)result->source_faces[i]=i;
  std::vector<std::vector<Primvar<2>>> uv(in->uv_layer_count);size_t offset=0;
  for(size_t i=0;i<uv.size();i++){uv[i].resize(in->uv_counts[i]);for(auto& v:uv[i]){v.values[0]=in->uv_values[offset++];v.values[1]=in->uv_values[offset++];}}
  std::vector<Primvar<1>> vertex_creases(in->vertex_count);for(size_t i=0;i<in->vertex_count;i++)vertex_creases[i].values[0]=in->vertex_creases[i];
  Far::PrimvarRefiner primvars(*refiner);
  for(int i=1;i<=level;i++){
   const auto& topology=refiner->GetLevel(i);
   std::vector<Primvar<1>> next_creases(topology.GetNumVertices());primvars.InterpolateVarying(i,vertex_creases,next_creases);vertex_creases.swap(next_creases);
   std::vector<Primvar<3>> vertices(topology.GetNumVertices());primvars.Interpolate(i,result->positions,vertices);result->positions.swap(vertices);
   std::vector<int32_t> faces(topology.GetNumFaces());primvars.InterpolateFaceUniform(i,result->source_faces,faces);result->source_faces.swap(faces);
   for(size_t channel=0;channel<uv.size();channel++){std::vector<Primvar<2>> values(topology.GetNumFVarValues(channel));primvars.InterpolateFaceVarying(i,uv[channel],values,channel);uv[channel].swap(values);}
   check_error();
  }
  result->faces.reserve(final_level.GetNumFaces()*4);
  for(int i=0;i<final_level.GetNumFaces();i++){auto face=final_level.GetFaceVertices(i);if(face.size()!=4)throw std::runtime_error("SUBSURF expected refined quad topology");for(auto v:face)result->faces.push_back(v);}
  result->uv.reserve(in->uv_layer_count*result->faces.size()*2);
  for(size_t channel=0;channel<uv.size();channel++)for(int i=0;i<final_level.GetNumFaces();i++){auto values=final_level.GetFaceFVarValues(i,channel);for(auto v:values)for(float x:uv[channel][v].values)result->uv.push_back(x);}
  if(limit && !simple)evaluate_limit(in,descriptor,options,*refiner,level,*result);
  interpolate_corners<4>(in,*refiner,level,in->colors,result->colors);
  interpolate_corners<3>(in,*refiner,level,in->normals,result->normals);
  result->original_vertices.resize(in->vertex_count);
  result->vertex_creases.reserve(vertex_creases.size());for(auto v:vertex_creases)result->vertex_creases.push_back(v.values[0]);
  for(size_t i=0;i<in->vertex_count;i++){int v=i;for(int depth=0;depth<level;depth++)v=refiner->GetLevel(depth).GetVertexChildVertex(v);result->original_vertices[i]=v;result->vertex_creases[v]=in->vertex_creases[i];}
  for(size_t i=0;i<in->crease_count;i++){
   auto base_edges=refiner->GetLevel(0).GetVertexEdges(in->crease_edges[2*i]);int found=-1;
   for(auto e:base_edges){auto vs=refiner->GetLevel(0).GetEdgeVertices(e);if(vs[0]==in->crease_edges[2*i+1] || vs[1]==in->crease_edges[2*i+1]){found=e;break;}}
   if(found<0)throw std::runtime_error("SUBSURF crease edge is absent from surface");
   std::vector<int> edges={found};for(int depth=0;depth<level;depth++){std::vector<int> next;for(int e:edges)for(auto child:refiner->GetLevel(depth).GetEdgeChildEdges(e))next.push_back(child);edges.swap(next);}
   for(int e:edges){auto vs=final_level.GetEdgeVertices(e);result->crease_edges.push_back(vs[0]);result->crease_edges.push_back(vs[1]);result->crease_weights.push_back(in->crease_weights[i]);}
  }

  return result.release();
 } catch(const std::exception& exception){if(error_size)std::snprintf(error,error_size,"%s",exception.what());}
 catch(...){if(error_size)std::snprintf(error,error_size,"Unknown OpenSubdiv failure");}
 return nullptr;
}
extern "C" void hb_subdivide_view(const void* raw,HbSubdivView* view) noexcept {
 const auto& result=*static_cast<const Result*>(raw);
 *view={result.positions.empty()?nullptr:result.positions[0].values,result.faces.data(),result.source_faces.data(),result.uv.data(),result.colors.data(),result.normals.data(),result.vertex_creases.data(),result.crease_edges.data(),result.crease_weights.data(),result.original_vertices.data(),result.crease_weights.size(),result.positions.size(),result.source_faces.size(),result.uv_layer_count};
}
extern "C" void hb_subdivide_free(void* raw) noexcept {delete static_cast<Result*>(raw);}
