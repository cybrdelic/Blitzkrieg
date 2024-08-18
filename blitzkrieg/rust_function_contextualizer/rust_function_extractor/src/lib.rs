use console::{style, Emoji};
use indicatif::{ProgressBar, ProgressStyle};
use pyo3::prelude::*;
use rayon::prelude::*;
use std::collections::HashSet;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Instant;
use walkdir::{DirEntry, WalkDir};

static LOOKING_GLASS: Emoji<'_, '_> = Emoji("🔍  ", "");
static SPARKLES: Emoji<'_, '_> = Emoji("✨ ", ":-)");
static WARNING: Emoji<'_, '_> = Emoji("⚠️  ", "");

#[pyclass]
#[derive(Debug, Clone)]
struct CodeContext {
    #[pyo3(get)]
    file_path: String,
    #[pyo3(get)]
    content: String,
    #[pyo3(get)]
    imports: Vec<String>,
    #[pyo3(get)]
    start_line: usize,
    #[pyo3(get)]
    end_line: usize,
    #[pyo3(get)]
    nested_functions: Vec<CodeContext>,
}

#[pyclass]
#[derive(Debug, Clone)]
struct Reference {
    #[pyo3(get)]
    file_path: String,
    #[pyo3(get)]
    line_number: usize,
    #[pyo3(get)]
    line_content: String,
}

fn is_hidden(entry: &DirEntry) -> bool {
    entry
        .file_name()
        .to_str()
        .map(|s| s.starts_with("."))
        .unwrap_or(false)
}

fn should_ignore(entry: &DirEntry) -> bool {
    let ignore_dirs = [
        "venv",
        "env",
        ".git",
        "__pycache__",
        "node_modules",
        "target",
    ];
    entry.file_type().is_dir()
        && (is_hidden(entry) || ignore_dirs.iter().any(|dir| entry.path().ends_with(dir)))
}

fn get_python_files(dir: &Path) -> Vec<PathBuf> {
    WalkDir::new(dir)
        .into_iter()
        .filter_entry(|e| !should_ignore(e))
        .filter_map(|e| e.ok())
        .filter(|e| {
            !e.file_type().is_dir() && e.path().extension().map_or(false, |ext| ext == "py")
        })
        .map(|e| e.path().to_path_buf())
        .collect()
}

fn extract_imports(content: &str) -> Vec<String> {
    content
        .lines()
        .filter(|line| line.trim().starts_with("import ") || line.trim().starts_with("from "))
        .map(String::from)
        .collect()
}

fn extract_function_calls(content: &str) -> HashSet<String> {
    let function_call_regex = regex::Regex::new(r"\b(\w+)\s*\(").unwrap();
    function_call_regex
        .captures_iter(content)
        .filter_map(|cap| cap.get(1).map(|m| m.as_str().to_string()))
        .collect()
}

fn extract_function(
    content: &str,
    function_name: &str,
    all_functions: &[CodeContext],
) -> Option<CodeContext> {
    let lines: Vec<_> = content.lines().collect();
    let mut in_function = false;
    let mut start_line = 0;
    let mut end_line = 0;
    let mut bracket_count = 0;
    let mut function_content = String::new();

    for (i, line) in lines.iter().enumerate() {
        if line.trim().starts_with(&format!("def {}(", function_name)) {
            in_function = true;
            start_line = i;
            bracket_count = line.matches('(').count() - line.matches(')').count();
        }

        if in_function {
            function_content.push_str(line);
            function_content.push('\n');
            bracket_count += line.matches('(').count() - line.matches(')').count();

            if bracket_count == 0 && (line.trim().ends_with(":") || line.trim() == "pass") {
                end_line = i;
                break;
            }
        }
    }

    if in_function {
        let mut indentation = lines[start_line]
            .chars()
            .take_while(|&c| c.is_whitespace())
            .count();
        for (i, line) in lines.iter().enumerate().skip(end_line + 1) {
            let line_indent = line.chars().take_while(|&c| c.is_whitespace()).count();
            if line_indent > indentation || line.trim().is_empty() {
                function_content.push_str(line);
                function_content.push('\n');
                end_line = i;
            } else {
                break;
            }
        }

        let nested_function_calls = extract_function_calls(&function_content);
        let nested_functions: Vec<CodeContext> = nested_function_calls
            .iter()
            .filter_map(|func_name| {
                all_functions
                    .iter()
                    .find(|f| f.content.starts_with(&format!("def {}(", func_name)))
                    .cloned()
            })
            .collect();

        Some(CodeContext {
            file_path: String::new(), // This will be set later
            content: function_content,
            imports: Vec::new(), // This will be set later
            start_line,
            end_line,
            nested_functions,
        })
    } else {
        None
    }
}

fn find_references(content: &str, function_name: &str) -> Vec<(usize, String)> {
    content
        .lines()
        .enumerate()
        .filter(|(_, line)| line.contains(function_name))
        .map(|(i, line)| (i, line.to_string()))
        .collect()
}

fn process_file(
    path: &Path,
    function_name: &str,
    all_functions: &[CodeContext],
) -> Result<(Option<CodeContext>, Vec<Reference>), String> {
    let content =
        fs::read_to_string(path).map_err(|e| format!("Error reading file {:?}: {:?}", path, e))?;
    let imports = extract_imports(&content);
    let file_path = path.to_str().unwrap_or_default().to_string();

    let mut function_def = extract_function(&content, function_name, all_functions);
    if let Some(def) = &mut function_def {
        def.file_path = file_path.clone();
        def.imports = imports;
    }

    let references = find_references(&content, function_name)
        .into_iter()
        .map(|(line_number, line_content)| Reference {
            file_path: file_path.clone(),
            line_number,
            line_content,
        })
        .collect();

    Ok((function_def, references))
}

#[pyfunction]
fn extract_function_and_references(
    function_name: String,
) -> PyResult<(Option<CodeContext>, Vec<Reference>)> {
    let start = Instant::now();
    println!(
        "{} {} Initiating search for function '{}'",
        style("[1/5]").bold().dim(),
        LOOKING_GLASS,
        style(&function_name).cyan()
    );

    let current_dir = std::env::current_dir()?;
    println!(
        "{} {} Scanning directory: {}",
        style("[2/5]").bold().dim(),
        LOOKING_GLASS,
        style(current_dir.display()).green()
    );

    let python_files = get_python_files(&current_dir);
    println!(
        "{} {} Found {} Python files to analyze",
        style("[3/5]").bold().dim(),
        LOOKING_GLASS,
        style(python_files.len()).yellow()
    );

    println!(
        "{} {} Extracting all functions...",
        style("[4/5]").bold().dim(),
        LOOKING_GLASS
    );

    let all_functions: Vec<CodeContext> = python_files
        .par_iter()
        .flat_map(|path| {
            let content = fs::read_to_string(path).unwrap_or_default();
            content
                .lines()
                .enumerate()
                .filter(|(_, line)| line.trim().starts_with("def "))
                .filter_map(|(i, line)| {
                    let func_name = line.trim()[4..].split('(').next()?;
                    extract_function(&content, func_name, &[])
                })
                .collect::<Vec<_>>()
        })
        .collect();

    println!(
        "{} {} Analyzing files for target function...",
        style("[5/5]").bold().dim(),
        LOOKING_GLASS
    );

    let progress_bar = ProgressBar::new(python_files.len() as u64);
    let progress_style = ProgressStyle::default_bar()
        .template(
            "{spinner:.green} [{elapsed_precise}] [{wide_bar:.cyan/blue}] {pos}/{len} ({eta})",
        )
        .unwrap()
        .progress_chars("#>-");
    progress_bar.set_style(progress_style);

    let results: Vec<_> = python_files
        .par_iter()
        .map(|path| {
            let result = process_file(path, &function_name, &all_functions);
            progress_bar.inc(1);
            result
        })
        .collect();

    progress_bar.finish_with_message("Analysis complete");

    let mut function_def = None;
    let mut all_references = Vec::new();
    let mut errors = Vec::new();

    for result in results {
        match result {
            Ok((def, refs)) => {
                if function_def.is_none() {
                    function_def = def;
                }
                all_references.extend(refs);
            }
            Err(e) => errors.push(e),
        }
    }

    let duration = start.elapsed();
    println!("\n{} Analysis completed in {:.2?}", SPARKLES, duration);

    if let Some(context) = &function_def {
        println!("\n{}", style("Function Definition:").green().bold());
        println!("File: {}", context.file_path);
        println!("\nImports:");
        for import in &context.imports {
            println!("{}", import);
        }
        println!("\nFunction content:");
        println!("{}", context.content);

        if !context.nested_functions.is_empty() {
            println!("\n{}", style("Nested Functions:").blue().bold());
            for nested_func in &context.nested_functions {
                println!(
                    "\nNested Function: {}",
                    nested_func.content.lines().next().unwrap_or("")
                );
                println!("{}", nested_func.content);
            }
        }
    } else {
        println!("\n{}", style("Function Definition: Not found").red());
    }

    println!("\n{}", style("References:").green().bold());
    if all_references.is_empty() {
        println!("{}", style("No references found").yellow());
    } else {
        for (i, reference) in all_references.iter().enumerate() {
            println!(
                "{}. File: {}, Line: {}",
                i + 1,
                reference.file_path,
                reference.line_number + 1
            );
            println!("   {}", reference.line_content);
        }
    }

    if !errors.is_empty() {
        println!(
            "\n{} {}",
            WARNING,
            style("Errors encountered:").red().bold()
        );
        for error in errors {
            println!("  {}", error);
        }
    }

    Ok((function_def, all_references))
}

#[pymodule]
fn rust_function_extractor(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_function_and_references, m)?)?;
    m.add_class::<CodeContext>()?;
    m.add_class::<Reference>()?;
    Ok(())
}
