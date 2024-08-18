pip uninstall rust_function_extractor
cargo build --release
maturin develop --release
pip install -e .
