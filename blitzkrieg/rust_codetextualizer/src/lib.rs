use colored::*;
use pyo3::prelude::*;
use rayon::prelude::*;
use regex::Regex;
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::time::Instant;
use walkdir::{DirEntry, WalkDir};

#[pyclass]
#[derive(Debug, Clone)]
struct CodeElement {
    #[pyo3(get)]
    name: String,
    #[pyo3(get)]
    element_type: String,
    #[pyo3(get)]
    content: String,
    #[pyo3(get)]
    file_path: String,
    #[pyo3(get)]
    language: String,
    #[pyo3(get)]
    start_line: usize,
    #[pyo3(get)]
    end_line: usize,
    #[pyo3(get)]
    imports: Vec<String>,
    #[pyo3(get)]
    nested_elements: Vec<CodeElement>,
}

#[derive(Debug, Clone)]
enum Language {
    Python,
    Rust,
    JavaScript,
}

trait LanguageParser: Send + Sync {
    fn parse_file(&self, content: &str, file_path: &str) -> Vec<CodeElement>;
    fn find_references(&self, content: &str) -> HashSet<String>;
}

struct PythonParser;
struct RustParser;
struct JavaScriptParser;

impl LanguageParser for PythonParser {
    fn parse_file(&self, content: &str, file_path: &str) -> Vec<CodeElement> {
        let mut elements = Vec::new();
        let func_regex = Regex::new(r"(?m)^def\s+(\w+)\s*\([^)]*\):").unwrap();
        let class_regex = Regex::new(r"(?m)^class\s+(\w+)(?:\([^)]*\))?:").unwrap();
        let import_regex = Regex::new(r"(?m)^(?:from\s+\S+\s+)?import\s+(.+)").unwrap();

        let mut imports = Vec::new();
        for import_match in import_regex.captures_iter(content) {
            imports.push(import_match[1].trim().to_string());
        }

        for cap in func_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "function".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "Python".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        for cap in class_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "class".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "Python".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        elements
    }

    fn find_references(&self, content: &str) -> HashSet<String> {
        let call_regex = Regex::new(r"\b(\w+)\s*\(").unwrap();
        call_regex
            .captures_iter(content)
            .filter_map(|cap| cap.get(1).map(|m| m.as_str().to_string()))
            .collect()
    }
}

impl PythonParser {
    fn extract_block(&self, content: &str, start: usize) -> (usize, String) {
        let mut depth = 0;
        let mut end = start;
        for (idx, line) in content[start..].lines().enumerate() {
            let stripped_line = line.trim();
            if idx == 0 || depth > 0 {
                if stripped_line.ends_with(':') {
                    depth += 1;
                } else if stripped_line == "" {
                    // Skip empty lines
                } else if depth > 0 && !line.starts_with(' ') && !line.starts_with('\t') {
                    depth -= 1;
                    if depth == 0 {
                        break;
                    }
                }
            }
            end = start + line.len() + 1 + content[start..].find(line).unwrap_or(0);
        }
        (end, content[start..end].to_string())
    }
}

impl LanguageParser for RustParser {
    fn parse_file(&self, content: &str, file_path: &str) -> Vec<CodeElement> {
        let mut elements = Vec::new();
        let func_regex = Regex::new(r"(?m)^(?:pub\s+)?fn\s+(\w+)\s*\([^)]*\)").unwrap();
        let struct_regex = Regex::new(r"(?m)^(?:pub\s+)?struct\s+(\w+)").unwrap();
        let impl_regex = Regex::new(r"(?m)^impl(?:<[^>]+>)?\s+(\w+)").unwrap();
        let use_regex = Regex::new(r"(?m)^use\s+(.+);").unwrap();

        let mut imports = Vec::new();
        for import_match in use_regex.captures_iter(content) {
            imports.push(import_match[1].trim().to_string());
        }

        for cap in func_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "function".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "Rust".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        for cap in struct_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "struct".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "Rust".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        for cap in impl_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "impl".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "Rust".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        elements
    }

    fn find_references(&self, content: &str) -> HashSet<String> {
        let call_regex = Regex::new(r"\b(\w+)\s*\(").unwrap();
        let struct_regex = Regex::new(r"\b(\w+)\s*\{").unwrap();
        let mut references = HashSet::new();
        for cap in call_regex.captures_iter(content) {
            references.insert(cap[1].to_string());
        }
        for cap in struct_regex.captures_iter(content) {
            references.insert(cap[1].to_string());
        }
        references
    }
}

impl RustParser {
    fn extract_block(&self, content: &str, start: usize) -> (usize, String) {
        let mut depth = 0;
        let mut end = start;
        for (idx, line) in content[start..].lines().enumerate() {
            let stripped_line = line.trim();
            if idx == 0 || depth > 0 {
                if stripped_line.ends_with('{') {
                    depth += 1;
                } else if stripped_line == "}" {
                    depth -= 1;
                    if depth == 0 {
                        end = start + line.len() + 1 + content[start..].find(line).unwrap_or(0);
                        break;
                    }
                }
            }
            end = start + line.len() + 1 + content[start..].find(line).unwrap_or(0);
        }
        (end, content[start..end].to_string())
    }
}

impl LanguageParser for JavaScriptParser {
    fn parse_file(&self, content: &str, file_path: &str) -> Vec<CodeElement> {
        let mut elements = Vec::new();
        let func_regex =
            Regex::new(r"(?m)^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\([^)]*\)").unwrap();
        let class_regex = Regex::new(r"(?m)^(?:export\s+)?class\s+(\w+)").unwrap();
        let arrow_func_regex =
            Regex::new(r"(?m)^(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\([^)]*\)\s*=>")
                .unwrap();
        let import_regex = Regex::new(r#"(?m)^import\s+.*\s+from\s+['"]\S+['"];"#).unwrap();

        let mut imports = Vec::new();
        for import_match in import_regex.find_iter(content) {
            imports.push(import_match.as_str().to_string());
        }

        for cap in func_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "function".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "JavaScript".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        for cap in class_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "class".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "JavaScript".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        for cap in arrow_func_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            elements.push(CodeElement {
                name,
                element_type: "arrow_function".to_string(),
                content: element_content,
                file_path: file_path.to_string(),
                language: "JavaScript".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            });
        }

        elements
    }

    fn find_references(&self, content: &str) -> HashSet<String> {
        let call_regex = Regex::new(r"\b(\w+)\s*\(").unwrap();
        let new_regex = Regex::new(r"new\s+(\w+)").unwrap();
        let mut references = HashSet::new();
        for cap in call_regex.captures_iter(content) {
            references.insert(cap[1].to_string());
        }
        for cap in new_regex.captures_iter(content) {
            references.insert(cap[1].to_string());
        }
        references
    }
}

impl JavaScriptParser {
    fn extract_block(&self, content: &str, start: usize) -> (usize, String) {
        let mut depth = 0;
        let mut end = start;
        let mut in_string = false;
        let mut string_char = ' ';
        for (idx, ch) in content[start..].char_indices() {
            if !in_string {
                match ch {
                    '{' => depth += 1,
                    '}' => {
                        depth -= 1;
                        if depth == 0 {
                            end = start + idx + 1;
                            break;
                        }
                    }
                    '\'' | '"' | '`' => {
                        in_string = true;
                        string_char = ch;
                    }
                    _ => {}
                }
            } else if ch == string_char && content[start + idx - 1..].starts_with('\\') {
                in_string = false;
            }
            end = start + idx + 1;
        }
        (end, content[start..end].to_string())
    }
}

fn get_parser_for_language(language: &Language) -> Box<dyn LanguageParser> {
    match language {
        Language::Python => Box::new(PythonParser),
        Language::Rust => Box::new(RustParser),
        Language::JavaScript => Box::new(JavaScriptParser),
    }
}

fn detect_language(file_path: &Path) -> Language {
    match file_path.extension().and_then(|s| s.to_str()) {
        Some("py") => Language::Python,
        Some("rs") => Language::Rust,
        Some("js") | Some("jsx") | Some("ts") | Some("tsx") | Some("mjs") => Language::JavaScript,

        _ => Language::Python, // Default to Python for unknown extensions
    }
}

fn is_hidden(entry: &DirEntry) -> bool {
    entry
        .file_name()
        .to_str()
        .map(|s| s.starts_with("."))
        .unwrap_or(false)
}

fn should_ignore(entry: &DirEntry) -> bool {
    let ignore_dirs = [".git", "__pycache__", "node_modules", "target"];
    entry.file_type().is_dir() && ignore_dirs.iter().any(|dir| entry.path().ends_with(dir))
}

fn get_project_files(dir: &Path) -> Vec<PathBuf> {
    WalkDir::new(dir)
        .into_iter()
        .filter_entry(|e| !should_ignore(e) && !is_hidden(e))
        .filter_map(|e| e.ok())
        .filter(|e| !e.file_type().is_dir())
        .map(|e| e.path().to_path_buf())
        .collect()
}

fn process_file(
    path: &Path,
    all_elements: &mut HashMap<String, CodeElement>,
    keyword: &str,
    files_processed: &AtomicUsize,
    total_files: usize,
) -> Result<Vec<CodeElement>, std::io::Error> {
    // Check if the file extension is one we want to process
    if let Some(extension) = path.extension().and_then(|s| s.to_str()) {
        if !["py", "rs", "js", "jsx", "ts", "tsx"].contains(&extension) {
            return Ok(Vec::new());
        }
    } else {
        return Ok(Vec::new());
    }

    // Read the file content
    let content = fs::read_to_string(path)?;

    // Parse the file
    let language = detect_language(path);
    let parser = get_parser_for_language(&language);
    let file_elements = parser.parse_file(&content, path.to_str().unwrap_or_default());

    // Add all elements to the HashMap
    for element in &file_elements {
        all_elements.insert(element.name.clone(), element.clone());
    }

    // Filter elements that match the keyword
    let matched_elements: Vec<CodeElement> = file_elements
        .into_iter()
        .filter(|element| element.name == keyword)
        .collect();

    // Process matched elements
    for element in &matched_elements {
        all_elements.insert(element.name.clone(), element.clone());
        let references = parser.find_references(&element.content);
        for reference in references {
            if let Some(referenced_element) = all_elements.get(&reference) {
                let mut new_element = element.clone();
                new_element.nested_elements.push(referenced_element.clone());
                all_elements.insert(element.name.clone(), new_element);
            }
        }
    }

    // Update progress
    let processed = files_processed.fetch_add(1, Ordering::SeqCst) + 1;
    if processed % 10 == 0 || processed == total_files {
        println!("Processed {}/{} files", processed, total_files);
    }

    Ok(matched_elements)
}

fn trace_logic_chains(
    keyword: &str,
    all_elements: &HashMap<String, CodeElement>,
) -> Option<CodeElement> {
    fn trace_recursive(
        element: &CodeElement,
        all_elements: &HashMap<String, CodeElement>,
        traced: &mut HashSet<String>,
        depth: usize,
    ) -> CodeElement {
        if depth > 10 {
            println!(
                "{}: {} (depth limit reached)",
                "Stopping trace".bright_yellow(),
                element.name
            );
            return element.clone();
        }

        println!(
            "{} {}: {}",
            "Tracing".bright_blue(),
            "element".bright_cyan(),
            element.name.bright_yellow()
        );
        let mut traced_element = element.clone();
        traced_element.nested_elements.clear();

        let references = element
            .content
            .split_whitespace()
            .filter(|&word| all_elements.contains_key(word))
            .collect::<HashSet<_>>();

        println!(
            "  Found {} potential references",
            references.len().to_string().bright_cyan()
        );

        for reference in references {
            if !traced.contains(reference) {
                traced.insert(reference.to_string());
                if let Some(referenced_element) = all_elements.get(reference) {
                    println!(
                        "    {}: {}",
                        "Following reference".bright_green(),
                        reference.bright_yellow()
                    );
                    traced_element.nested_elements.push(trace_recursive(
                        referenced_element,
                        all_elements,
                        traced,
                        depth + 1,
                    ));
                } else {
                    println!("    {}: {}", "Reference not found".bright_red(), reference);
                }
            } else {
                println!(
                    "    {}: {}",
                    "Circular reference detected".bright_yellow(),
                    reference
                );
            }
        }

        traced_element
    }

    println!(
        "{} {}",
        "Starting trace for".bright_blue(),
        keyword.bright_yellow()
    );
    all_elements.get(keyword).map(|element| {
        let mut traced = HashSet::new();
        traced.insert(keyword.to_string());
        trace_recursive(element, all_elements, &mut traced, 0)
    })
}
fn format_output(element: &CodeElement, depth: usize) -> String {
    let indent = "  ".repeat(depth);
    let mut output = format!(
        "{}{}: {}\n",
        indent,
        "Element".bright_cyan(),
        element.name.bright_yellow()
    );
    output += &format!(
        "{}  {}: {}\n",
        indent,
        "Type".bright_blue(),
        element.element_type.bright_green()
    );
    output += &format!(
        "{}  {}: {}\n",
        indent,
        "File".bright_blue(),
        element.file_path.bright_green()
    );
    output += &format!(
        "{}  {}: {}\n",
        indent,
        "Language".bright_blue(),
        element.language.bright_green()
    );
    output += &format!(
        "{}  {}: {}-{}\n",
        indent,
        "Lines".bright_blue(),
        element.start_line.to_string().bright_green(),
        element.end_line.to_string().bright_green()
    );
    if !element.imports.is_empty() {
        output += &format!("{}  {}: \n", indent, "Imports".bright_blue());
        for import in &element.imports {
            output += &format!("{}    {}\n", indent, import.bright_green());
        }
    }
    output += &format!("{}  {}: \n", indent, "Content".bright_blue());
    for line in element.content.lines() {
        output += &format!("{}    {}\n", indent, line);
    }
    if !element.nested_elements.is_empty() {
        output += &format!("{}  {}: \n", indent, "Nested Elements".bright_blue());
        for nested in &element.nested_elements {
            if depth < 2 {
                output += &format_output(nested, depth + 1);
            } else {
                output += &format!(
                    "{}    {} (nested, content omitted)\n",
                    indent,
                    nested.name.bright_yellow()
                );
            }
        }
    }
    output
}

#[pyfunction]
fn extract_code_context(keyword: String) -> PyResult<String> {
    let start = Instant::now();
    let current_dir = std::env::current_dir()?;

    let output = Arc::new(Mutex::new(String::new()));

    println!("{}", "Starting code context extraction...".bright_green());
    println!(
        "Searching for '{}' in directory: {:?}\n",
        keyword.bright_yellow(),
        current_dir.to_string_lossy().bright_blue()
    );
    {
        let mut output = output.lock().unwrap();
        output.push_str(&format!(
            "Searching for '{}' in directory: {:?}\n\n",
            keyword, current_dir
        ));
    }

    let project_files = get_project_files(&current_dir);
    let total_files = project_files.len();
    println!(
        "Found {} potentially relevant files\n",
        total_files.to_string().bright_cyan()
    );
    {
        let mut output = output.lock().unwrap();
        output.push_str(&format!(
            "Found {} potentially relevant files\n\n",
            total_files
        ));
    }

    let all_elements = Arc::new(Mutex::new(HashMap::new()));
    let files_processed = Arc::new(AtomicUsize::new(0));

    project_files.par_iter().for_each(|path| {
        let mut elements = all_elements.lock().unwrap();
        match process_file(path, &mut elements, &keyword, &files_processed, total_files) {
            Ok(file_elements) => {
                if !file_elements.is_empty() {
                    println!(
                        "{}: {:?}",
                        "Found relevant elements in file".bright_green(),
                        path
                    );
                    let mut output = output.lock().unwrap();
                    output.push_str(&format!("Found relevant elements in file: {:?}\n", path));
                }
            }
            Err(e) => {
                eprintln!(
                    "{}: {:?} - {}",
                    "Error processing file".bright_red(),
                    path,
                    e
                );
            }
        }
    });

    println!("\n{}", "Starting logic chain tracing...".bright_green());
    let traced_element = {
        let elements = all_elements.lock().unwrap();
        trace_logic_chains(&keyword, &elements)
    };

    let duration = start.elapsed();
    {
        let mut output = output.lock().unwrap();
        output.push_str(&format!("Analysis completed in {:?}\n\n", duration));
        output.push_str(&format!("Files processed: {}\n\n", total_files));
    }

    if let Some(element) = traced_element {
        println!(
            "{}: {}",
            "Found and traced element".bright_green(),
            keyword.bright_yellow()
        );
        let formatted_output = format_output(&element, 0);
        println!(
            "{}\n{}",
            "Formatted output:".bright_cyan(),
            formatted_output
        );
        let mut output = output.lock().unwrap();
        output.push_str(&format!("Found and traced element: {}\n\n", keyword));
        output.push_str(&formatted_output);
    } else {
        println!(
            "{}: {}",
            "Element not found".bright_red(),
            keyword.bright_yellow()
        );
        let mut output = output.lock().unwrap();
        output.push_str(&format!(
            "Element '{}' not found in the codebase.\n",
            keyword
        ));
    }

    let final_output = output.lock().unwrap().clone();
    println!(
        "{}: {} characters",
        "Final output length".bright_cyan(),
        final_output.len().to_string().bright_yellow()
    );
    Ok(final_output)
}

#[pymodule]
fn rust_codetextualizer(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_code_context, m)?)?;
    m.add_class::<CodeElement>()?;
    Ok(())
}
