//! EXT_meshopt_compression decoding with bounded, aligned output buffers.
use super::{Value, text};
use std::{collections::BTreeMap, ffi::c_void};
unsafe extern "C" {
    fn meshopt_decodeVertexBuffer(
        destination: *mut c_void,
        count: usize,
        stride: usize,
        source: *const u8,
        length: usize,
    ) -> i32;
    fn meshopt_decodeIndexBuffer(
        destination: *mut c_void,
        count: usize,
        stride: usize,
        source: *const u8,
        length: usize,
    ) -> i32;
    fn meshopt_decodeIndexSequence(
        destination: *mut c_void,
        count: usize,
        stride: usize,
        source: *const u8,
        length: usize,
    ) -> i32;
    fn meshopt_decodeFilterOct(destination: *mut c_void, count: usize, stride: usize);
    fn meshopt_decodeFilterQuat(destination: *mut c_void, count: usize, stride: usize);
    fn meshopt_decodeFilterExp(destination: *mut c_void, count: usize, stride: usize);
}
const VIEW_LIMIT: usize = 32 * 1024 * 1024;
const TOTAL_LIMIT: usize = 64 * 1024 * 1024;
fn index(value: &Value) -> Result<usize, String> {
    value
        .as_u64()
        .and_then(|n| usize::try_from(n).ok())
        .ok_or("Meshopt requires nonnegative integer fields".into())
}
fn offset(value: &Value) -> Result<usize, String> {
    if value.is_null() { Ok(0) } else { index(value) }
}
fn decode(
    stream: &[u8],
    count: usize,
    stride: usize,
    mode: &str,
    filter: &str,
) -> Result<Vec<u8>, String> {
    let length = count
        .checked_mul(stride)
        .filter(|&n| n > 0 && n <= VIEW_LIMIT)
        .ok_or("Meshopt decoded view must be 1 byte..32 MiB")?;
    if stream.is_empty() || stream.len() > VIEW_LIMIT {
        return Err("Meshopt compressed view must be 1 byte..32 MiB".into());
    }
    match mode {
        "ATTRIBUTES" if (4..=256).contains(&stride) && stride.is_multiple_of(4) => {}
        "TRIANGLES" if count.is_multiple_of(3) && [2, 4].contains(&stride) && filter == "NONE" => {}
        "INDICES" if [2, 4].contains(&stride) && filter == "NONE" => {}
        _ => return Err("Invalid Meshopt mode, stride, count or index filter".into()),
    }
    match filter {
        "NONE" => {}
        "OCTAHEDRAL" if [4, 8].contains(&stride) => {}
        "QUATERNION" if stride == 8 => {}
        "EXPONENTIAL" if stride.is_multiple_of(4) => {}
        _ => return Err("Unsupported or invalid Meshopt filter".into()),
    }
    let header = match mode {
        "ATTRIBUTES" => 0xa0,
        "TRIANGLES" => 0xe1,
        _ => 0xd1,
    };
    if stream[0] != header {
        return Err("Unsupported EXT_meshopt_compression bitstream version".into());
    }
    // Filter implementations access 32-bit words. A Vec<u8> alone would not
    // guarantee their alignment, so retain a word allocation through decoding.
    let mut output = vec![0u32; length.div_ceil(4)];
    let destination = output.as_mut_ptr().cast::<c_void>();
    // Dimensions above satisfy every upstream precondition. Decoders validate
    // stream contents and return errors rather than reading beyond source.
    let result = unsafe {
        match mode {
            "ATTRIBUTES" => meshopt_decodeVertexBuffer(
                destination,
                count,
                stride,
                stream.as_ptr(),
                stream.len(),
            ),
            "TRIANGLES" => {
                meshopt_decodeIndexBuffer(destination, count, stride, stream.as_ptr(), stream.len())
            }
            _ => meshopt_decodeIndexSequence(
                destination,
                count,
                stride,
                stream.as_ptr(),
                stream.len(),
            ),
        }
    };
    if result != 0 {
        return Err(format!(
            "Malformed Meshopt {mode} stream (decoder {result})"
        ));
    }
    unsafe {
        match filter {
            "OCTAHEDRAL" => meshopt_decodeFilterOct(destination, count, stride),
            "QUATERNION" => meshopt_decodeFilterQuat(destination, count, stride),
            "EXPONENTIAL" => meshopt_decodeFilterExp(destination, count, stride),
            _ => {}
        }
    }
    // Both supported release targets are little-endian; preserve the decoded
    // byte representation, including halfword index buffers and packed filters.
    Ok(unsafe { std::slice::from_raw_parts(output.as_ptr().cast::<u8>(), length) }.to_vec())
}
pub fn views(doc: &Value, buffers: &[Vec<u8>]) -> Result<BTreeMap<usize, Vec<u8>>, String> {
    let mut decoded = BTreeMap::new();
    let mut total = 0usize;
    for (i, view) in doc["bufferViews"]
        .as_array()
        .into_iter()
        .flatten()
        .enumerate()
    {
        let extension = &view["extensions"]["EXT_meshopt_compression"];
        if extension.is_null() {
            continue;
        }
        if !extension.is_object() {
            return Err("Meshopt extension must be an object".into());
        }
        let count = index(&extension["count"])?;
        let stride = index(&extension["byteStride"])?;
        let length = count.checked_mul(stride).ok_or("Meshopt size overflow")?;
        if length != index(&view["byteLength"])?
            || view
                .get("byteStride")
                .is_some_and(|v| v.as_u64() != Some(stride as u64))
        {
            return Err("Meshopt decoded layout differs from parent bufferView".into());
        }
        let parent = doc["buffers"]
            .get(index(&view["buffer"])?)
            .ok_or("Invalid Meshopt parent buffer")?;
        if offset(&view["byteOffset"])?
            .checked_add(length)
            .is_none_or(|end| end > index(&parent["byteLength"]).unwrap_or(0))
        {
            return Err("Meshopt parent view exceeds declared buffer".into());
        }
        total = total
            .checked_add(length)
            .filter(|&n| n <= TOTAL_LIMIT)
            .ok_or("Meshopt total decoded data exceeds 64 MiB")?;
        let buffer = buffers
            .get(index(&extension["buffer"])?)
            .ok_or("Invalid Meshopt source buffer")?;
        let start = offset(&extension["byteOffset"])?;
        let compressed = index(&extension["byteLength"])?;
        let stream = buffer
            .get(
                start
                    ..start
                        .checked_add(compressed)
                        .ok_or("Meshopt source size overflow")?,
            )
            .ok_or("Meshopt source view exceeds buffer")?;
        let filter = extension.get("filter").map(text).unwrap_or("NONE");
        decoded.insert(
            i,
            decode(stream, count, stride, text(&extension["mode"]), filter)?,
        );
    }
    Ok(decoded)
}

#[cfg(test)]
mod tests {
    use super::*;
    use base64::{Engine, engine::general_purpose::STANDARD};
    #[test]
    fn wasm_reference_streams() {
        let cases: Value = serde_json::from_str(include_str!(
            "../../compat/fixtures/meshopt-codec-reference.json"
        ))
        .unwrap();
        assert_eq!(cases.as_array().unwrap().len(), 57);
        for case in cases.as_array().unwrap() {
            let source = STANDARD.decode(text(&case["compressed"])).unwrap();
            let expected = STANDARD.decode(text(&case["decoded"])).unwrap();
            assert_eq!(
                decode(
                    &source,
                    index(&case["count"]).unwrap(),
                    index(&case["stride"]).unwrap(),
                    text(&case["mode"]),
                    text(&case["filter"])
                )
                .unwrap(),
                expected,
                "{}",
                case["id"]
            );
            for cut in [0, 1, source.len() / 2, source.len() - 1] {
                assert!(
                    decode(
                        &source[..cut],
                        index(&case["count"]).unwrap(),
                        index(&case["stride"]).unwrap(),
                        text(&case["mode"]),
                        text(&case["filter"])
                    )
                    .is_err(),
                    "{} truncated at {cut}",
                    case["id"]
                );
            }
        }
    }
}
