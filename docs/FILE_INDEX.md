# File Structure and Documentation Index

This document provides a complete index of all files in the RISC-V pipeline simulator project.

---

## 📁 Project Root

### Core Simulator Files

| File | Lines | Purpose | Key Components |
|------|-------|---------|----------------|
| `riscv.py` | ~150 | High-level processor interface | `RISCVProcessor`, `run_program()` |
| `pipeline.py` | ~400 | 5-stage pipeline implementation | All stage classes, hazard detection, flush logic |
| `instruction.py` | ~200 | Instruction parsing and representation | `Instruction` class, parser methods |
| `exe.py` | ~350 | Execution unit (ALU operations) | All execute_* methods for 29 instructions |
| `register_file.py` | ~80 | 32-register file with R0=0 | `RegisterFile` class, PC tracking |
| `memory.py` | ~120 | Byte-addressable memory | Load/store with sign/zero extension |

### Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies (simpy, pyelftools) |
| `.gitignore` | Git ignore rules |
| `.gitmodules` | Git submodules (riscv-tests) |
| `README.md` | Main documentation |

---

## 📁 docs/ - Documentation

### Comprehensive Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `INSTRUCTION_SET.md` | Instruction reference with examples | Developers, users |
| `RV32I_COVERAGE.md` | Complete RV32I implementation analysis | Project managers, developers |
| `PROJECT_OVERVIEW.md` | Architecture and design overview | New developers, contributors |
| `JAL_JALR_IMPLEMENTATION.md` | Jump instruction implementation details | Developers |
| `PIPELINE_FLUSH.md` | Pipeline flush mechanism documentation | Developers |
| `RISCV_TESTS_GUIDE.md` | Guide for official RISC-V test suite | Testers, QA |

**Total:** 6 documentation files covering all aspects of the project

---

## 📁 tests/ - Test Suite (109 Tests)

### Test Organization

| File | Tests | Purpose |
|------|-------|---------|
| `tests/test_all.py` | - | Legacy test runner |
| `tests/run_tests.py` | - | Modern test runner |
| `tests/visualization.py` | - | Pipeline visualization utilities |
| `tests/README.md` | - | Test documentation |
| `tests/README_TESTS.md` | - | Detailed test guide |

### Functional Tests (`tests/functional_tests/`)

| File | Tests | Coverage |
|------|-------|----------|
| `test_instruction_types.py` | 20 | R-type and basic I-type operations |
| `test_immediate.py` | 15 | Immediate operations with edge cases |
| `test_comparison.py` | 10 | SLT/SLTU signed/unsigned comparisons |
| `test_shift.py` | 12 | Shift operations (SLL/SRL/SRA variants) |
| `test_load_store.py` | 18 | Load/store with sign/zero extension |
| `test_upper_immediate.py` | 6 | LUI and AUIPC operations |
| `test_branch.py` | 12 | Branch instructions with pipeline flush |
| `test_jump.py` | 12 | JAL/JALR with return address handling |
| `test_flush.py` | 9 | Pipeline flush mechanism verification |
| `test_pipeline.py` | 8 | Pipeline behavior and hazard detection |
| `test_edge_cases.py` | 5 | Corner cases and boundary conditions |
| `test_complex_programs.py` | 2 | Multi-instruction integration tests |

### Test Support Files

| File | Purpose |
|------|---------|
| `riscv_test_adapter.py` | Adapter for official RISC-V tests |
| `run_riscv_tests.py` | Official test suite runner |
| `__init__.py` | Package initialization |

---

## 📁 utils/ - Utility Modules

| File | Purpose | Key Functions |
|------|---------|---------------|
| `elf_loader.py` | ELF binary loading and decoding | `load_elf()`, `decode_instruction()` |
| `riscv_test_utils.py` | Test pattern extraction | Pattern matching, validation |
| `README.md` | Utils documentation | - |
| `__init__.py` | Package initialization | - |

---

## 📁 scripts/ - Convenience Scripts

| File | Purpose |
|------|---------|
| `run_all_tests.sh` | Run complete test suite |
| `run_functional_tests.sh` | Run functional tests only |
| `run_unit_tests.sh` | Run unit tests only |
| `README.md` | Scripts documentation |

---

## 📁 sandbox/ - Experimental Code

| File | Purpose |
|------|---------|
| `vis_pipeline.py` | Custom visualization examples |

---

## 📁 3rd_party/ - External Dependencies

### riscv-tests (Git Submodule)

Official RISC-V test suite from riscv/riscv-tests repository.

**Purpose:** Validation against official RISC-V test patterns

---

## File Statistics

### Source Code

| Category | Files | Approximate Lines |
|----------|-------|-------------------|
| Core simulator | 6 | ~1,300 |
| Test suite | 13 | ~2,500 |
| Utilities | 2 | ~400 |
| Scripts | 3 | ~100 |
| **Total Code** | **24** | **~4,300** |

### Documentation

| Category | Files | Pages (equiv.) |
|----------|-------|----------------|
| Main docs | 6 | ~40 |
| Test docs | 2 | ~8 |
| Inline docs | - | ~15 (docstrings) |
| **Total Docs** | **8** | **~63 pages** |

---

## Quick File Lookup

### Need to...

**Understand the architecture?**
→ `docs/PROJECT_OVERVIEW.md`

**See what instructions are supported?**
→ `docs/INSTRUCTION_SET.md` or `docs/RV32I_COVERAGE.md`

**Add a new instruction?**
→ Edit `instruction.py`, `exe.py`, `utils/elf_loader.py`

**Add a new test?**
→ Create test in `tests/functional_tests/test_*.py`

**Fix a pipeline bug?**
→ Check `pipeline.py`

**Understand hazard detection?**
→ `pipeline.py` DecodeStage.check_hazard()

**Understand pipeline flush?**
→ `docs/PIPELINE_FLUSH.md` or `pipeline.py` flush logic

**Run all tests?**
→ `./scripts/run_all_tests.sh` or `python -m unittest discover tests/functional_tests`

**See test results?**
→ `python -m unittest discover tests/functional_tests -v`

**Load ELF binaries?**
→ `utils/elf_loader.py`

**Visualize pipeline execution?**
→ `tests/visualization.py`

---

## Documentation Cross-References

### Primary Documentation Flow

1. **Start here:** `README.md` - Project overview and getting started
2. **Architecture:** `docs/PROJECT_OVERVIEW.md` - Deep dive into design
3. **Instructions:** `docs/INSTRUCTION_SET.md` - What you can run
4. **Coverage:** `docs/RV32I_COVERAGE.md` - What's implemented vs. missing
5. **Features:** `docs/PIPELINE_FLUSH.md`, `docs/JAL_JALR_IMPLEMENTATION.md` - Specific features

### By Use Case

**I want to use the simulator:**
1. `README.md` - Setup and basic usage
2. `docs/INSTRUCTION_SET.md` - Available instructions
3. `riscv.py` - API reference

**I want to understand the implementation:**
1. `docs/PROJECT_OVERVIEW.md` - Architecture overview
2. `pipeline.py` - Core pipeline logic
3. `exe.py` - Execution details
4. `docs/PIPELINE_FLUSH.md` - Control flow handling

**I want to contribute:**
1. `docs/PROJECT_OVERVIEW.md` - Architecture
2. `docs/RV32I_COVERAGE.md` - What's missing
3. `tests/functional_tests/` - Test examples
4. `README.md` - Contribution guidelines

**I want to validate correctness:**
1. `tests/README.md` - Test overview
2. `tests/functional_tests/` - All test files
3. `./scripts/run_all_tests.sh` - Run tests

---

## Key Dependencies

### External Packages

| Package | Version | Purpose |
|---------|---------|---------|
| simpy | 4.1.1 | Discrete-event simulation framework |
| pyelftools | 0.32 | ELF binary parsing |

### Python Standard Library

- `unittest` - Test framework
- `struct` - Binary data handling
- `typing` - Type hints
- `dataclasses` - Data structures

---

## Code Metrics

### Test Coverage

**Total Tests:** 109  
**Pass Rate:** 100%  
**Execution Time:** ~0.05 seconds  
**Coverage:** All 29 implemented instructions  

### Instruction Coverage

**Implemented:** 29/40 RV32I instructions (72.5%)  
**Tested:** 29/29 implemented instructions (100%)  
**Documented:** 29/29 implemented instructions (100%)  

---

## Version History

**Current Version:** 1.0  
**Last Updated:** January 28, 2026  
**Status:** Production ready for computational programs

### Major Milestones

- ✅ R-type and I-type ALU operations
- ✅ Load/store variants (LW/LH/LB/LHU/LBU, SW/SH/SB)
- ✅ Branch instructions (BEQ/BNE/BLT/BGE/BLTU/BGEU)
- ✅ Jump instructions (JAL/JALR)
- ✅ Pipeline flush mechanism
- ✅ RAW hazard detection and stalling
- ✅ Comprehensive test suite (109 tests)
- ✅ Complete documentation

---

## Next Steps

### To Complete RV32I (100% coverage)
1. Add ECALL (system call emulation)
2. Add EBREAK (breakpoint support)
3. Add FENCE, FENCE.I (as NOPs)
4. Add CSR operations (7 instructions)

### To Improve Performance
1. Implement data forwarding
2. Add branch prediction
3. Consider out-of-order execution

---

**For detailed information on any file, see the file itself or the corresponding documentation.**
