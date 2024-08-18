use pyo3::prelude::*;
use rayon::prelude::*;
use std::fs;
use std::path::{Path, PathBuf};
use syn::{parse_file, visit::Visit, Item, ImplItem, TraitItem};
use walkdir::{WalkDir, DirEntry};
use indicatif::{ProgressBar, ProgressStyle};
use console::{style, Emoji};
use std::time::Instant;

static LOOKING_GLASS: Emoji<'_, '_> = Emoji("🔍  ", "");
static SPARKLES: Emoji<'_, '_> = Emoji("✨ ", ":-)");

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
        match i {
            Item::Fn(f) => {
                if f.sig.ident == self.target_name {
                    self.function_def = Some(quote::quote!(#f).to_string());
                }
            },
            Item::Impl(impl_item) => {
                for item in &impl_item.items {
                    if let ImplItem::Method(method) = item {
                        if method.sig.ident == self.target_name {
                            self.function_def = Some(quote::quote!(#method).to_string());
                        }
                    }
                }
            },
            _ => {}
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

fn is_hidden(entry: &DirEntry) -> bool {
    entry.file_name()
         .to_str()
         .map(|s| s.starts_with("."))
         .unwrap_or(false)
}

fn should_ignore(entry: &DirEntry) -> bool {
    let ignore_dirs = ["venv", "env", ".git", "__pycache__", "node_modules", "target"];
    entry.file_type().is_dir() && (is_hidden(entry) || ignore_dirs.iter().any(|dir| entry.path().ends_with(dir)))
}

fn get_python_files(dir: &Path) -> Vec<PathBuf> {
    WalkDir::new(dir)
        .into_iter()
        .filter_entry(|e| !should_ignore(e))
        .filter_map(|e| e.ok())
        .filter(|e| !e.file_type().is_dir() && e.path().extension().map_or(false, |ext| ext == "py"))
        .map(|e| e.path().to_path_buf())
        .collect()
}

fn process_file(path: &Path, function_name: &str) -> (Option<String>, Vec<String>) {
    match fs::read_to_string(path) {
        Ok(content) => {
            match syn::parse_file(&content) {
                Ok(syntax) => {
                    let mut visitor = FunctionVisitor {
                        target_name: function_name.to_string(),
                        function_def: None,
                        references: Vec::new(),
                    };
                    visitor.visit_file(&syntax);
                    (visitor.function_def, visitor.references)
                },
                Err(_) => (None, Vec::new()),
            }
        },
        Err(_) => (None, Vec::new()),
    }
}

#[pyfunction]
fn extract_function_and_references(function_name: String) -> PyResult<(Option<String>, Vec<String>)> {
    let start = Instant::now();
    println!("{} {} Initiating search for function '{}'", style("[1/4]").bold().dim(), LOOKING_GLASS, style(&function_name).cyan());

    let current_dir = std::env::current_dir()?;
    println!("{} {} Scanning directory: {}", style("[2/4]").bold().dim(), LOOKING_GLASS, style(current_dir.display()).green());

    let python_files = get_python_files(&current_dir);
    println!("{} {} Found {} Python files to analyze", style("[3/4]").bold().dim(), LOOKING_GLASS, style(python_files.len()).yellow());

     // Replace this section
    let progress_bar = ProgressBar::new(python_files.len() as u64);
    let progress_style = ProgressStyle::default_bar()
        .template("{spinner:.green} [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})")
        .unwrap()
        .progress_chars("#>-");
    progress_bar.set_style(progress_style);

    println!("{} {} Analyzing files...", style("[4/4]").bold().dim(), LOOKING_GLASS);
    let (function_def, all_references) = python_files.par_iter()
        .map(|path| {
            let result = process_file(path, &function_name);
            progress_bar.inc(1);
            result
        })
        .reduce(|| (None, Vec::new()), |acc, (def, refs)| {
            (acc.0.or(def), [acc.1, refs].concat())
        });

    progress_bar.finish_with_message("Analysis complete");

    let duration = start.elapsed();
    println!("\n{} Analysis completed in {:.2?}", SPARKLES, duration);

    if let Some(def) = &function_def {
        println!("\n{}", style("Function Definition:").green().bold());
        println!("{}", style(def).dim());
    } else {
        println!("\n{}", style("Function Definition: Not found").red());
    }

    println!("\n{}", style("References:").green().bold());
    if all_references.is_empty() {
        println!("{}", style("No references found").yellow());
    } else {
        for (i, reference) in all_references.iter().enumerate() {
            println!("{}. {}", style(i + 1).dim(), reference);
        }
    }

    Ok((function_def, all_references))
}

#[pymodule]
fn rust_function_extractor(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_function_and_references, m)?)?;
    Ok(())
}
