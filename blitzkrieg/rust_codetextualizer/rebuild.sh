pip uninstall rust_codetextualizer
cargo build --release
maturin develop --release
pip install -e .
