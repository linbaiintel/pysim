# Makefile for FreeRTOS Demo on RISC-V RV32I Simulator
# Minimal configuration for RV32I ISA with CLINT support

# Toolchain - use riscv64 toolchain with rv32i flags
PREFIX = riscv64-unknown-elf-
CC = $(PREFIX)gcc
AS = $(PREFIX)as
LD = $(PREFIX)ld
OBJCOPY = $(PREFIX)objcopy
OBJDUMP = $(PREFIX)objdump
SIZE = $(PREFIX)size

# Project name
PROJECT = freertos_demo

# Directories
FREERTOS_ROOT = ../3rd_party/FreeRTOS-Kernel
FREERTOS_PORT = $(FREERTOS_ROOT)/portable/GCC/RISC-V
FREERTOS_CHIP = $(FREERTOS_PORT)/chip_specific_extensions/RV32I_CLINT_no_extensions
FREERTOS_MEMMANG = $(FREERTOS_ROOT)/portable/MemMang

# Source files
FREERTOS_SOURCES = \
	$(FREERTOS_ROOT)/tasks.c \
	$(FREERTOS_ROOT)/queue.c \
	$(FREERTOS_ROOT)/list.c \
	$(FREERTOS_ROOT)/timers.c \
	$(FREERTOS_ROOT)/event_groups.c \
	$(FREERTOS_ROOT)/stream_buffer.c \
	$(FREERTOS_PORT)/port.c \
	$(FREERTOS_MEMMANG)/heap_4.c

FREERTOS_ASM = \
	$(FREERTOS_PORT)/portASM.S

APP_SOURCES = \
	main.c \
	minilibc.c

APP_ASM = \
	startup.S

# All sources
C_SOURCES = $(FREERTOS_SOURCES) $(APP_SOURCES)
ASM_SOURCES = $(FREERTOS_ASM) $(APP_ASM)

# Include paths
INCLUDES = \
	-I. \
	-I$(FREERTOS_ROOT)/include \
	-I$(FREERTOS_PORT) \
	-I$(FREERTOS_CHIP)

# Compiler flags for RV32I with Zicsr (CSR instructions)
ARCH_FLAGS = -march=rv32i_zicsr -mabi=ilp32
CFLAGS = $(ARCH_FLAGS) -O2 -g -Wall -Wextra
CFLAGS += -ffunction-sections -fdata-sections
CFLAGS += $(INCLUDES)

# Assembler flags
ASFLAGS = $(ARCH_FLAGS) -g
ASFLAGS += $(INCLUDES)

# Linker flags
LDFLAGS = $(ARCH_FLAGS)
LDFLAGS += -nostdlib -nostartfiles
LDFLAGS += -Wl,--gc-sections
LDFLAGS += -T linker.ld

# Libraries (minimal - just libgcc for compiler builtins, no libc)
LIBS = -lgcc

# Object files
C_OBJECTS = $(C_SOURCES:.c=.o)
ASM_OBJECTS = $(ASM_SOURCES:.S=.o)
OBJECTS = $(C_OBJECTS) $(ASM_OBJECTS)

# Targets
.PHONY: all clean size

all: $(PROJECT).elf $(PROJECT).bin $(PROJECT).hex $(PROJECT).lst

$(PROJECT).elf: $(OBJECTS)
	@echo "Linking..."
	$(CC) $(LDFLAGS) -o $@ $(OBJECTS) $(LIBS)
	@echo "Build complete: $@"

$(PROJECT).bin: $(PROJECT).elf
	@echo "Creating binary..."
	$(OBJCOPY) -O binary $< $@

$(PROJECT).hex: $(PROJECT).elf
	@echo "Creating hex..."
	$(OBJCOPY) -O ihex $< $@

$(PROJECT).lst: $(PROJECT).elf
	@echo "Creating listing..."
	$(OBJDUMP) -d -S $< > $@

%.o: %.c
	@echo "Compiling $<..."
	$(CC) $(CFLAGS) -c -o $@ $<

%.o: %.S
	@echo "Assembling $<..."
	$(CC) $(ASFLAGS) -c -o $@ $<

size: $(PROJECT).elf
	$(SIZE) $<

clean:
	@echo "Cleaning..."
	rm -f $(OBJECTS)
	rm -f $(PROJECT).elf $(PROJECT).bin $(PROJECT).hex $(PROJECT).lst
	rm -f $(PROJECT).map

help:
	@echo "FreeRTOS Demo Build System"
	@echo ""
	@echo "Targets:"
	@echo "  all     - Build the project (default)"
	@echo "  clean   - Remove build artifacts"
	@echo "  size    - Show memory usage"
	@echo "  help    - Show this help"
	@echo ""
	@echo "Requirements:"
	@echo "  - riscv32-unknown-elf toolchain"
	@echo "  - FreeRTOS-Kernel in ../3rd_party/"
	@echo ""
	@echo "Configuration:"
	@echo "  - RV32I ISA (no extensions)"
	@echo "  - CLINT for timer interrupts"
	@echo "  - UART at 0x10000000 for printf"
