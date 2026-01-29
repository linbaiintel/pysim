#!/bin/bash
# Quick setup script for FreeRTOS demo

set -e

echo "==========================================="
echo "FreeRTOS Demo Setup"
echo "==========================================="
echo ""

# Check if we're in the right directory
if [ ! -d "../3rd_party/FreeRTOS-Kernel" ]; then
    echo "ERROR: FreeRTOS-Kernel not found!"
    echo "Please run: git submodule update --init --recursive"
    exit 1
fi

# Check for RISC-V toolchain
if ! command -v riscv32-unknown-elf-gcc &> /dev/null; then
    echo "WARNING: RISC-V toolchain not found!"
    echo ""
    echo "Please install riscv32-unknown-elf toolchain:"
    echo "  Ubuntu/Debian: sudo apt-get install gcc-riscv64-unknown-elf"
    echo "  Or build from source: https://github.com/riscv/riscv-gnu-toolchain"
    echo ""
    exit 1
fi

# Show toolchain info
echo "Toolchain found:"
riscv32-unknown-elf-gcc --version | head -1
echo ""

# Build
echo "Building FreeRTOS demo..."
make clean
make

if [ $? -eq 0 ]; then
    echo ""
    echo "==========================================="
    echo "Build successful!"
    echo "==========================================="
    echo ""
    make size
    echo ""
    echo "Output files:"
    ls -lh freertos_demo.elf freertos_demo.bin freertos_demo.lst 2>/dev/null || true
    echo ""
    echo "Next steps:"
    echo "  1. Review disassembly: less freertos_demo.lst"
    echo "  2. Check symbols: riscv32-unknown-elf-nm -n freertos_demo.elf"
    echo "  3. Load into simulator (when ELF loader is ready)"
    echo ""
else
    echo ""
    echo "Build failed! Check errors above."
    exit 1
fi
