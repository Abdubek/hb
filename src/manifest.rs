// SPDX-License-Identifier: MIT
//! Supported bpy symbols and prefix lookup.
use serde_json::{Value, json};
use std::collections::{BTreeMap, BTreeSet};

pub struct Manifest {
    pub document: Value,
    allowed: BTreeSet<String>,
}
impl Manifest {
    pub fn new(document: Value) -> Result<Self, String> {
        let symbols = document["symbols"]
            .as_object()
            .ok_or("Manifest needs a symbols object")?;
        let mut allowed = BTreeSet::new();
        for symbol in symbols.keys() {
            allowed.insert(symbol.clone());
            for (index, _) in symbol.match_indices('.') {
                allowed.insert(symbol[..index].into());
            }
        }
        Ok(Self { document, allowed })
    }
    pub fn accepts(&self, alternatives: &[String]) -> bool {
        alternatives
            .iter()
            .any(|symbol| self.allowed.contains(symbol))
    }
    pub fn filter(&self, prefix: &str) -> Value {
        let entries: BTreeMap<_, _> = self.document["symbols"]
            .as_object()
            .unwrap()
            .iter()
            .filter(|(k, _)| *k == prefix || k.starts_with(&(prefix.to_owned() + ".")))
            .collect();
        json!({"symbols":entries,"milestone":self.document["milestone"]})
    }
}
