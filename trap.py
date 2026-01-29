"""Trap and Interrupt Mechanism for RISC-V simulator"""

from interrupt import InterruptController


class TrapController:
    """Handles trap entry and interrupt delivery for RISC-V
    
    Implements the machine-mode trap handling mechanism including:
    - Exception handling (ECALL, EBREAK, illegal instruction, etc.)
    - Interrupt delivery (timer, software, external)
    - CSR state management during trap entry/exit
    - Trap vectoring (direct and vectored modes)
    """
    
    # Exception Codes (mcause values for synchronous exceptions)
    EXCEPTION_INSTRUCTION_MISALIGNED = 0
    EXCEPTION_INSTRUCTION_ACCESS_FAULT = 1
    EXCEPTION_ILLEGAL_INSTRUCTION = 2
    EXCEPTION_BREAKPOINT = 3
    EXCEPTION_LOAD_MISALIGNED = 4
    EXCEPTION_LOAD_ACCESS_FAULT = 5
    EXCEPTION_STORE_MISALIGNED = 6
    EXCEPTION_STORE_ACCESS_FAULT = 7
    EXCEPTION_ECALL_FROM_U = 8
    EXCEPTION_ECALL_FROM_S = 9
    EXCEPTION_ECALL_FROM_M = 11
    EXCEPTION_INSTRUCTION_PAGE_FAULT = 12
    EXCEPTION_LOAD_PAGE_FAULT = 13
    EXCEPTION_STORE_PAGE_FAULT = 15
    
    # Interrupt Codes (mcause values with MSB set for asynchronous interrupts)
    INTERRUPT_SOFTWARE = 0x80000003
    INTERRUPT_TIMER = 0x80000007
    INTERRUPT_EXTERNAL = 0x8000000B
    
    def __init__(self, csr_bank):
        """Initialize trap controller
        
        Args:
            csr_bank: CSRBank instance for accessing/modifying CSRs
        """
        self.csr_bank = csr_bank
        self.pending_interrupts = set()  # Set of pending interrupt codes (legacy)
        self.interrupt_controller = InterruptController(csr_bank)  # New interrupt logic
    
    def trigger_exception(self, exception_code, pc, trap_value=0):
        """Trigger a synchronous exception
        
        Enters machine-mode trap handler by:
        1. Saving current PC to mepc
        2. Saving current privilege mode to mstatus.MPP
        3. Saving current interrupt enable to mstatus.MPIE
        4. Clearing mstatus.MIE (disable interrupts)
        5. Setting mcause to exception code
        6. Setting mtval to trap value (bad address, illegal instruction, etc.)
        7. Jumping to trap handler at mtvec
        
        Args:
            exception_code: Exception code (0-15 for synchronous exceptions)
            pc: Current program counter (address of faulting instruction)
            trap_value: Additional trap information (default 0)
            
        Returns:
            Dictionary with trap information:
            {
                'type': 'exception',
                'handler_pc': <mtvec_address>,
                'cause': <exception_code>,
                'epc': <saved_pc>,
                'tval': <trap_value>
            }
        """
        if self.csr_bank is None:
            return None
        
        # 1. Save PC to mepc (address of faulting instruction)
        self.csr_bank.write(0x341, pc)
        
        # 2. Save current mstatus and modify it
        mstatus = self.csr_bank.read(0x300)
        
        # Extract current MIE (bit 3) and MPP (bits 11-12)
        current_mie = (mstatus >> 3) & 0x1
        current_mpp = (mstatus >> 11) & 0x3
        
        # Modify mstatus:
        # - MPIE (bit 7) = current MIE
        # - MIE (bit 3) = 0 (disable interrupts)
        # - MPP (bits 11-12) = current privilege (assume Machine=3 for now)
        
        # Clear MIE, MPIE, MPP fields
        mstatus &= ~((1 << 3) | (1 << 7) | (0x3 << 11))
        
        # Set MPIE = current MIE
        mstatus |= (current_mie << 7)
        
        # Set MPP = 3 (Machine mode - simplified, always Machine for now)
        mstatus |= (0x3 << 11)
        
        # MIE = 0 (already cleared above)
        
        self.csr_bank.write(0x300, mstatus)
        
        # 3. Set mcause (exception code, MSB=0 for exceptions)
        self.csr_bank.write(0x342, exception_code & 0x7FFFFFFF)
        
        # 4. Set mtval (trap value)
        self.csr_bank.write(0x343, trap_value)
        
        # 5. Get trap handler address from mtvec
        mtvec = self.csr_bank.read(0x305)
        mode = mtvec & 0x3  # Bottom 2 bits are mode
        base = mtvec & ~0x3  # Top bits are base address
        
        # For exceptions, always use base address (vectoring only for interrupts)
        handler_pc = base
        
        return {
            'type': 'exception',
            'handler_pc': handler_pc,
            'cause': exception_code,
            'epc': pc,
            'tval': trap_value
        }
    
    def trigger_interrupt(self, interrupt_code):
        """Trigger an asynchronous interrupt
        
        Similar to exception handling but:
        1. mepc saves the PC of the *next* instruction (not current)
        2. mcause has MSB=1 to indicate interrupt
        3. May use vectored mode if mtvec mode=1
        
        Args:
            interrupt_code: Interrupt code (with MSB set)
            
        Returns:
            Dictionary with interrupt information or None if not deliverable
        """
        if self.csr_bank is None:
            return None
        
        # Check if interrupts are globally enabled (mstatus.MIE)
        mstatus = self.csr_bank.read(0x300)
        mie_enabled = (mstatus >> 3) & 0x1
        
        if not mie_enabled:
            # Interrupts disabled, add to pending
            self.pending_interrupts.add(interrupt_code)
            return None
        
        # Check if this specific interrupt is enabled in mie CSR
        mie = self.csr_bank.read(0x304)
        interrupt_bit = interrupt_code & 0x7FFFFFFF  # Remove MSB
        
        if interrupt_bit == 3:  # Software interrupt
            if not (mie & (1 << 3)):
                self.pending_interrupts.add(interrupt_code)
                return None
        elif interrupt_bit == 7:  # Timer interrupt
            if not (mie & (1 << 7)):
                self.pending_interrupts.add(interrupt_code)
                return None
        elif interrupt_bit == 11:  # External interrupt
            if not (mie & (1 << 11)):
                self.pending_interrupts.add(interrupt_code)
                return None
        
        # Interrupt is deliverable - proceed with trap entry
        # Note: For interrupts, we assume PC is the next instruction to execute
        # This should be called with the next PC, not current PC
        
        return interrupt_code
    
    def check_pending_interrupts(self, next_pc):
        """Check for pending interrupts and deliver if possible
        
        Should be called at the beginning of each instruction fetch to check
        if any interrupts can be delivered.
        
        Args:
            next_pc: The PC of the next instruction to execute
            
        Returns:
            Trap info dictionary if interrupt delivered, None otherwise
        """
        # Use the InterruptController to get the highest priority interrupt
        interrupt_code = self.interrupt_controller.get_highest_priority_interrupt()
        
        if interrupt_code is None:
            # Also check legacy pending_interrupts for compatibility
            if not self.pending_interrupts:
                return None
            
            # Check if interrupts are globally enabled
            mstatus = self.csr_bank.read(0x300)
            mie_enabled = (mstatus >> 3) & 0x1
            
            if not mie_enabled:
                return None
            
            # Try to deliver highest priority pending interrupt (legacy)
            priority_order = [
                self.INTERRUPT_EXTERNAL,
                self.INTERRUPT_SOFTWARE,
                self.INTERRUPT_TIMER
            ]
            
            for interrupt_code in priority_order:
                if interrupt_code in self.pending_interrupts:
                    # Try to deliver this interrupt
                    mie = self.csr_bank.read(0x304)
                    interrupt_bit = interrupt_code & 0x7FFFFFFF
                    
                    enabled = False
                    if interrupt_bit == 3:  # Software
                        enabled = (mie & (1 << 3)) != 0
                    elif interrupt_bit == 7:  # Timer
                        enabled = (mie & (1 << 7)) != 0
                    elif interrupt_bit == 11:  # External
                        enabled = (mie & (1 << 11)) != 0
                    
                    if enabled:
                        # Deliver this interrupt
                        self.pending_interrupts.remove(interrupt_code)
                        return self._deliver_interrupt(interrupt_code, next_pc)
            
            return None
        else:
            # New path: InterruptController has a pending, enabled interrupt
            # interrupt_code here is just the bit position (3, 7, or 11)
            # Convert to full interrupt code with MSB set
            interrupt_bit = interrupt_code
            full_interrupt_code = 0x80000000 | interrupt_bit
            
            # Clear it from the controller and deliver
            self.interrupt_controller.clear_pending(interrupt_bit)
            
            # Also clear from legacy pending_interrupts for compatibility
            self.pending_interrupts.discard(full_interrupt_code)
            
            return self._deliver_interrupt(full_interrupt_code, next_pc)
    
    def _deliver_interrupt(self, interrupt_code, next_pc):
        """Internal method to deliver an interrupt
        
        Args:
            interrupt_code: Interrupt code with MSB set
            next_pc: PC of next instruction (saved to mepc)
            
        Returns:
            Dictionary with trap information
        """
        # 1. Save next PC to mepc
        self.csr_bank.write(0x341, next_pc)
        
        # 2. Save current mstatus and modify it (same as exception)
        mstatus = self.csr_bank.read(0x300)
        current_mie = (mstatus >> 3) & 0x1
        
        # Clear MIE, MPIE, MPP fields
        mstatus &= ~((1 << 3) | (1 << 7) | (0x3 << 11))
        
        # Set MPIE = current MIE
        mstatus |= (current_mie << 7)
        
        # Set MPP = 3 (Machine mode)
        mstatus |= (0x3 << 11)
        
        self.csr_bank.write(0x300, mstatus)
        
        # 3. Set mcause (with MSB=1 for interrupt)
        self.csr_bank.write(0x342, interrupt_code)
        
        # 4. Clear mtval (not used for interrupts)
        self.csr_bank.write(0x343, 0)
        
        # 5. Calculate handler address from mtvec
        mtvec = self.csr_bank.read(0x305)
        mode = mtvec & 0x3
        base = mtvec & ~0x3
        
        if mode == 0:  # Direct mode
            handler_pc = base
        elif mode == 1:  # Vectored mode
            # Each interrupt gets its own vector
            interrupt_number = interrupt_code & 0x7FFFFFFF
            handler_pc = base + (interrupt_number * 4)
        else:  # Reserved modes - treat as direct
            handler_pc = base
        
        return {
            'type': 'interrupt',
            'handler_pc': handler_pc,
            'cause': interrupt_code,
            'epc': next_pc,
            'tval': 0
        }
    
    def set_interrupt_pending(self, interrupt_type):
        """Mark an interrupt as pending
        
        Args:
            interrupt_type: One of 'software', 'timer', 'external'
        """
        if interrupt_type == 'software':
            self.pending_interrupts.add(self.INTERRUPT_SOFTWARE)
            # Also set mip bit
            mip = self.csr_bank.read(0x344)
            mip |= (1 << 3)
            self.csr_bank.write(0x344, mip)
        elif interrupt_type == 'timer':
            self.pending_interrupts.add(self.INTERRUPT_TIMER)
            mip = self.csr_bank.read(0x344)
            mip |= (1 << 7)
            self.csr_bank.write(0x344, mip)
        elif interrupt_type == 'external':
            self.pending_interrupts.add(self.INTERRUPT_EXTERNAL)
            mip = self.csr_bank.read(0x344)
            mip |= (1 << 11)
            self.csr_bank.write(0x344, mip)
    
    def clear_interrupt_pending(self, interrupt_type):
        """Clear a pending interrupt
        
        Args:
            interrupt_type: One of 'software', 'timer', 'external'
        """
        if interrupt_type == 'software':
            self.pending_interrupts.discard(self.INTERRUPT_SOFTWARE)
            mip = self.csr_bank.read(0x344)
            mip &= ~(1 << 3)
            self.csr_bank.write(0x344, mip)
        elif interrupt_type == 'timer':
            self.pending_interrupts.discard(self.INTERRUPT_TIMER)
            mip = self.csr_bank.read(0x344)
            mip &= ~(1 << 7)
            self.csr_bank.write(0x344, mip)
        elif interrupt_type == 'external':
            self.pending_interrupts.discard(self.INTERRUPT_EXTERNAL)
            mip = self.csr_bank.read(0x344)
            mip &= ~(1 << 11)
            self.csr_bank.write(0x344, mip)
    
    def ecall(self, pc):
        """Handle ECALL instruction
        
        Treats ECALL as an environment call exception from Machine mode.
        
        Args:
            pc: Current PC (address of ECALL instruction)
            
        Returns:
            Trap info dictionary
        """
        return self.trigger_exception(self.EXCEPTION_ECALL_FROM_M, pc)
    
    def ebreak(self, pc):
        """Handle EBREAK instruction
        
        Treats EBREAK as a breakpoint exception.
        
        Args:
            pc: Current PC (address of EBREAK instruction)
            
        Returns:
            Trap info dictionary
        """
        return self.trigger_exception(self.EXCEPTION_BREAKPOINT, pc)
    
    def illegal_instruction(self, pc, instruction_bits=0):
        """Handle illegal instruction exception
        
        Args:
            pc: Current PC (address of illegal instruction)
            instruction_bits: The illegal instruction encoding
            
        Returns:
            Trap info dictionary
        """
        return self.trigger_exception(self.EXCEPTION_ILLEGAL_INSTRUCTION, 
                                     pc, instruction_bits)
