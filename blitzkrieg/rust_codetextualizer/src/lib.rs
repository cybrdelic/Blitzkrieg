use colored::*;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use rayon::prelude::*;
use regex::Regex;
use std::collections::{HashMap, HashSet};
use std::fs;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
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
        println!("Parsing Python file: {}", file_path);
        let mut elements = Vec::new();
        let func_regex = Regex::new(r"(?m)^(?:async\s+)?def\s+(\w+)\s*\([^)]*\):").unwrap();
        let class_regex = Regex::new(r"(?m)^class\s+(\w+)(?:\([^)]*\))?:").unwrap();
        let method_regex = Regex::new(r"(?m)^\s+(?:async\s+)?def\s+(\w+)\s*\([^)]*\):").unwrap();
        let import_regex = Regex::new(r"(?m)^(?:from\s+\S+\s+)?import\s+(.+)").unwrap();

        let mut imports = Vec::new();
        for import_match in import_regex.captures_iter(content) {
            imports.push(import_match[1].trim().to_string());
        }

        for cap in class_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, class_content) = self.extract_block(content, start);
            println!("Found class: {}", name);
            let mut class_element = CodeElement {
                name: name.clone(),
                element_type: "class".to_string(),
                content: class_content.clone(),
                file_path: file_path.to_string(),
                language: "Python".to_string(),
                start_line: content[..start].lines().count() + 1,
                end_line: content[..end].lines().count(),
                imports: imports.clone(),
                nested_elements: Vec::new(),
            };

            for method_cap in method_regex.captures_iter(&class_content) {
                let method_start = method_cap.get(0).unwrap().start();
                let method_name = method_cap[1].to_string();
                let (method_end, method_content) = self.extract_block(&class_content, method_start);
                println!("  Found method: {}.{}", name, method_name);
                let method_element = CodeElement {
                    name: format!("{}.{}", name, method_name),
                    element_type: "method".to_string(),
                    content: method_content,
                    file_path: file_path.to_string(),
                    language: "Python".to_string(),
                    start_line: class_element.start_line
                        + class_content[..method_start].lines().count(),
                    end_line: class_element.start_line
                        + class_content[..method_end].lines().count(),
                    imports: Vec::new(),
                    nested_elements: Vec::new(),
                };
                class_element.nested_elements.push(method_element.clone());
                elements.push(method_element);
            }

            elements.push(class_element);
        }

        for cap in func_regex.captures_iter(content) {
            let start = cap.get(0).unwrap().start();
            let name = cap[1].to_string();
            let (end, element_content) = self.extract_block(content, start);
            println!("Found top-level function: {}", name);
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

        println!(
            "Finished parsing file: {}. Found {} elements.",
            file_path,
            elements.len()
        );
        elements
    }

    fn find_references(&self, content: &str) -> HashSet<String> {
        let mut references = HashSet::new();

        let call_regex = Regex::new(r"\b(\w+(?:\.\w+)*)\s*\(").unwrap();
        let attr_regex = Regex::new(r"\b(\w+)\.(\w+)").unwrap();

        for cap in call_regex.captures_iter(content) {
            references.insert(cap[1].to_string());
        }

        for cap in attr_regex.captures_iter(content) {
            references.insert(format!("{}.{}", cap[1].to_string(), cap[2].to_string()));
        }

        println!("Found {} references", references.len());
        references
    }
}

impl PythonParser {
    fn extract_block(&self, content: &str, start: usize) -> (usize, String) {
        let mut depth = 0;
        let mut end = start;
        let max_depth = 1000; // Prevent infinite loops
        for (idx, line) in content[start..].lines().enumerate() {
            if idx > max_depth {
                break; // Break loop if depth is too high
            }
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
    let ignore_dirs = [
        ".git",
        "__pycache__",
        "node_modules",
        "target",
        ".venv",
        "venv",
        "env",
    ];
    entry.file_type().is_dir()
        && ignore_dirs
            .iter()
            .any(|dir| entry.path().to_string_lossy().contains(dir))
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
    cancel_flag: &AtomicBool,
) -> Result<Vec<CodeElement>, std::io::Error> {
    if cancel_flag.load(Ordering::Relaxed) {
        return Ok(Vec::new());
    }

    println!("Processing file: {:?}", path);

    if let Some(extension) = path.extension().and_then(|s| s.to_str()) {
        if !["py", "rs", "js", "jsx", "ts", "tsx"].contains(&extension) {
            println!("Skipping file with unsupported extension: {:?}", path);
            return Ok(Vec::new());
        }
    } else {
        println!("Skipping file without extension: {:?}", path);
        return Ok(Vec::new());
    }

    let content = fs::read_to_string(path)?;
    let language = detect_language(path);
    let parser = get_parser_for_language(&language);
    let file_elements = parser.parse_file(&content, path.to_str().unwrap_or_default());

    for element in &file_elements {
        all_elements.insert(element.name.clone(), element.clone());
        if element.element_type == "class" {
            for method in &element.nested_elements {
                all_elements.insert(method.name.clone(), method.clone());
            }
        }
    }

    let matched_elements: Vec<CodeElement> = file_elements
        .into_iter()
        .filter(|element| element.name.contains(keyword))
        .collect();

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

    let processed = files_processed.fetch_add(1, Ordering::SeqCst) + 1;
    if processed % 5 == 0 || processed == total_files {
        println!("Processed {}/{} files", processed, total_files);
    }

    Ok(matched_elements)
}

fn trace_logic_chains(
    keyword: &str,
    all_elements: &HashMap<String, CodeElement>,
    start: Instant,
    timeout: Duration,
    max_depth: usize,
    cancel_flag: &AtomicBool,
) -> Option<CodeElement> {
    println!("Starting trace_logic_chains for keyword: {}", keyword);

    fn trace_recursive(
        element: &CodeElement,
        all_elements: &HashMap<String, CodeElement>,
        traced: &mut HashSet<String>,
        depth: usize,
        start: &Instant,
        timeout: &Duration,
        max_depth: usize,
        cancel_flag: &AtomicBool,
    ) -> Option<CodeElement> {
        if cancel_flag.load(Ordering::Relaxed) {
            println!("Tracing cancelled by user");
            return None;
        }

        if start.elapsed() > *timeout {
            println!("Tracing timed out");
            return None;
        }

        if depth > max_depth {
            println!(
                "{}: {} (max depth reached)",
                "Stopping trace".bright_yellow(),
                element.name
            );
            return Some(element.clone());
        }

        if depth % 5 == 0 {
            println!("Tracing at depth: {}", depth);
        }

        println!(
            "{} {}: {}",
            "Tracing".bright_blue(),
            "element".bright_cyan(),
            element.name.bright_yellow()
        );
        let mut traced_element = element.clone();
        traced_element.nested_elements.clear();

        let call_regex = Regex::new(r"((?:\w+\.)*\w+)\s*\(").unwrap();
        let attr_regex = Regex::new(r"(\w+)\.(\w+)").unwrap();
        let mut references = HashSet::new();

        for cap in call_regex.captures_iter(&element.content) {
            references.insert(cap[1].to_string());
        }
        for cap in attr_regex.captures_iter(&element.content) {
            references.insert(cap[2].to_string());
        }

        println!(
            "  Found {} potential references",
            references.len().to_string().bright_cyan()
        );

        for reference in references {
            if !traced.contains(&reference) {
                traced.insert(reference.clone());
                if let Some(referenced_element) = all_elements.get(&reference) {
                    println!(
                        "    {}: {}",
                        "Following reference".bright_green(),
                        reference.bright_yellow()
                    );
                    if let Some(nested) = trace_recursive(
                        referenced_element,
                        all_elements,
                        traced,
                        depth + 1,
                        start,
                        timeout,
                        max_depth,
                        cancel_flag,
                    ) {
                        traced_element.nested_elements.push(nested);
                    }
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

        Some(traced_element)
    }

    // First, look for an exact match
    if let Some(start_element) = all_elements.get(keyword) {
        println!("Found exact match for keyword: {}", keyword);
        let mut traced = HashSet::new();
        return trace_recursive(
            start_element,
            all_elements,
            &mut traced,
            0,
            &start,
            &timeout,
            max_depth,
            cancel_flag,
        );
    }

    // If no exact match, look for methods ending with the keyword
    println!("No exact match found, searching for methods");
    let method_matches: Vec<_> = all_elements
        .values()
        .filter(|e| e.name.ends_with(&format!(".{}", keyword)))
        .collect();

    if !method_matches.is_empty() {
        println!("Found matching methods:");
        for element in &method_matches {
            println!("  {}", element.name);
        }
        if let Some(matched_element) = method_matches.first() {
            println!("Tracing first matching method: {}", matched_element.name);
            let mut traced = HashSet::new();
            return trace_recursive(
                matched_element,
                all_elements,
                &mut traced,
                0,
                &start,
                &timeout,
                max_depth,
                cancel_flag,
            );
        }
    }

    // If still no match, look for partial matches
    println!("No exact or method match found, searching for partial matches");
    let partial_matches: Vec<_> = all_elements
        .values()
        .filter(|e| e.name.contains(keyword))
        .collect();

    if !partial_matches.is_empty() {
        println!("Found partial matches:");
        for element in &partial_matches {
            println!("  {}", element.name);
        }
        if let Some(matched_element) = partial_matches.first() {
            println!("Tracing first partial match: {}", matched_element.name);
            let mut traced = HashSet::new();
            return trace_recursive(
                matched_element,
                all_elements,
                &mut traced,
                0,
                &start,
                &timeout,
                max_depth,
                cancel_flag,
            );
        }
    }

    println!("No matching element found for keyword: {}", keyword);
    None
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
fn extract_code_context(
    keyword: String,
    timeout_seconds: Option<u64>,
    max_depth: Option<usize>,
) -> PyResult<String> {
    let start = Instant::now();
    let timeout = Duration::from_secs(timeout_seconds.unwrap_or(300)); // Default to 5 minutes if not specified
    let max_depth = max_depth.unwrap_or(20); // Default max depth
    let current_dir = std::env::current_dir()?;

    let cancel_flag = Arc::new(AtomicBool::new(false));
    let cancel_flag_clone = cancel_flag.clone();

    // Spawn a thread to listen for user input to cancel
    std::thread::spawn(move || {
        println!("Press 'q' and Enter to cancel the operation.");
        let mut input = String::new();
        std::io::stdin().read_line(&mut input).unwrap();
        if input.trim() == "q" {
            cancel_flag_clone.store(true, Ordering::Relaxed);
        }
    });

    let output = Arc::new(Mutex::new(String::new()));

    println!("{}", "Starting code context extraction...".bright_green());
    println!(
        "Searching for '{}' in directory: {:?}\n",
        keyword.bright_yellow(),
        current_dir.to_string_lossy().bright_blue()
    );
    {
        let mut output = output
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Failed to lock output"))?;
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
        let mut output = output
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Failed to lock output"))?;
        output.push_str(&format!(
            "Found {} potentially relevant files\n\n",
            total_files
        ));
    }

    let all_elements = Arc::new(Mutex::new(HashMap::new()));
    let files_processed = Arc::new(AtomicUsize::new(0));

    project_files.par_iter().for_each(|path| {
        if cancel_flag.load(Ordering::Relaxed) {
            return;
        }
        let mut elements = match all_elements.lock() {
            Ok(guard) => guard,
            Err(_) => {
                eprintln!("Failed to lock all_elements");
                return;
            }
        };
        match process_file(
            path,
            &mut elements,
            &keyword,
            &files_processed,
            total_files,
            &cancel_flag,
        ) {
            Ok(file_elements) => {
                if !file_elements.is_empty() {
                    println!(
                        "{}: {:?}",
                        "Found relevant elements in file".bright_green(),
                        path
                    );
                    if let Ok(mut output) = output.lock() {
                        output.push_str(&format!("Found relevant elements in file: {:?}\n", path));
                    }
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

    if cancel_flag.load(Ordering::Relaxed) {
        return Err(PyRuntimeError::new_err("Operation cancelled by user"));
    }

    if start.elapsed() > timeout {
        return Err(PyRuntimeError::new_err("Operation timed out"));
    }

    println!("\n{}", "Starting logic chain tracing...".bright_green());
    let traced_element = {
        let elements = all_elements
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Failed to lock all_elements"))?;
        println!("Number of elements in HashMap: {}", elements.len());
        for (key, value) in elements.iter() {
            println!("Element in HashMap: {} ({})", key, value.element_type);
        }
        trace_logic_chains(&keyword, &elements, start, timeout, max_depth, &cancel_flag)
    };

    let duration = start.elapsed();
    {
        let mut output = output
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Failed to lock output"))?;
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
        let mut output = output
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Failed to lock output"))?;
        output.push_str(&format!("Found and traced element: {}\n\n", keyword));
        output.push_str(&formatted_output);
    } else {
        println!(
            "{}: {}",
            "Element not found".bright_red(),
            keyword.bright_yellow()
        );
        let mut output = output
            .lock()
            .map_err(|_| PyRuntimeError::new_err("Failed to lock output"))?;
        output.push_str(&format!(
            "Element '{}' not found in the codebase.\n",
            keyword
        ));
    }

    let final_output = output
        .lock()
        .map_err(|_| PyRuntimeError::new_err("Failed to lock output"))?
        .clone();
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
