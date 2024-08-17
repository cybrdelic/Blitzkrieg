use pyo3::prelude::*;
use rayon::prelude::*;
use std::fs;
use std::path::Path;
use syn::{parse_file, Item, ImplItem, TraitItem, visit::Visit};

struct FunctionVisitor {
    target_name: String,
    function_def: Option<String>,
    references: Vec<String>,
}

impl<'ast> Visit<'ast> for FunctionVisitor {
    fn visit_item_fn(&mut self, i: &'ast syn::ItemFn) {
        if i.sig.ident == self.target_name {
            self.function_def = Some(quote::quote!(#i).to_string());
        }
    }

    fn visit_expr_path(&mut self, i: &'ast syn::ExprPath) {
        if i.path.segments.last().map_or(false, |s| s.ident == self.target_name) {
            self.references.push(quote::quote!(#i).to_string());
        }
    }

    fn visit_item(&mut self, i: &'ast Item) {
        if let Item::Fn(f) = i {
            if f.sig.ident == self.target_name {
                self.function_def = Some(quote::quote!(#f).to_string());
            }
        }
        syn::visit::visit_item(self, i);
    }

    fn visit_impl_item(&mut self, i: &'ast ImplItem) {
        if let ImplItem::Method(m) = i {
            if m.sig.ident == self.target_name {
                self.function_def = Some(quote::quote!(#m).to_string());
            }
        }
        syn::visit::visit_impl_item(self, i);
    }

    fn visit_trait_item(&mut self, i: &'ast TraitItem) {
        if let TraitItem::Method(m) = i {
            if m.sig.ident == self.target_name {
                self.function_def = Some(quote::quote!(#m).to_string());
            }
        }
        syn::visit::visit_trait_item(self, i);
    }
}

#[pyfunction]
fn extract_function_and_references(function_name: String) -> PyResult<(Option<String>, Vec<String>)> {
    let current_dir = std::env::current_dir()?;
    let python_files: Vec<_> = fs::read_dir(current_dir)?
        .filter_map(Result::ok)
        .filter(|entry| entry.path().extension().map_or(false, |ext| ext == "py"))
        .collect();

    let (function_def, all_references) = python_files.par_iter()
        .map(|entry| {
            let path = entry.path();
            let content = fs::read_to_string(&path).unwrap_or_default();
            let syntax = syn::parse_file(&content).unwrap_or_else(|_| syn::File { shebang: None, attrs: vec![], items: vec![] });

            let mut visitor = FunctionVisitor {
                target_name: function_name.clone(),
                function_def: None,
                references: Vec::new(),
            };
            visitor.visit_file(&syntax);
            (visitor.function_def, visitor.references)
        })
        .reduce(|| (None, Vec::new()), |acc, (def, refs)| {
            (acc.0.or(def), [acc.1, refs].concat())
        });

    Ok((function_def, all_references))
}

#[pymodule]
fn rust_function_extractor(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_function_and_references, m)?)?;
    Ok(())
}
