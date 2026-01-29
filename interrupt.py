"""Interrupt Enable and Pending Logic for RISC-V simulator

This module provides fine-grained control over interrupt enable/pending state,
masking, priority resolution, and edge/level triggering.
"""


class InterruptController:
    """Interrupt Controller with enable/pending logic
    
    Manages interrupt enable masks, pending bits, priority resolution,
    and edge/level triggering for RISC-V interrupts.
    """
    
    # Interrupt bit positions in mie/mip
    INT_SOFTWARE = 3
    INT_TIMER = 7
    INT_EXTERNAL = 11
    
    # Interrupt codes (with MSB set)
    INTERRUPT_SOFTWARE = 0x80000003
    INTERRUPT_TIMER = 0x80000007
    INTERRUPT_EXTERNAL = 0x8000000B
    
    # Priority order (higher number = higher priority)
    PRIORITY = {
        INT_EXTERNAL: 3,   # Highest
        INT_SOFTWARE: 2,
        INT_TIMER: 1       # Lowest
    }
    
    def __init__(self, csr_bank):
        """Initialize interrupt controller
        
        Args:
            csr_bank: CSRBank instance for mie/mip access
        """
        self.csr_bank = csr_bank
        self.edge_triggered = set()  # Edge-triggered interrupts
        self.level_triggered = {self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL}
        self.latched_edges = set()  # Latched edge interrupts
    
    def set_pending(self, interrupt_bit, edge=False):
        """Set an interrupt as pending
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
            edge: If True, treat as edge-triggered (latch and clear source)
        """
        if interrupt_bit not in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            return
        
        # Update mip CSR
        mip = self.csr_bank.read(0x344)
        mip |= (1 << interrupt_bit)
        self.csr_bank.write(0x344, mip)
        
        # Track edge-triggered interrupts
        if edge:
            self.latched_edges.add(interrupt_bit)
    
    def clear_pending(self, interrupt_bit):
        """Clear an interrupt pending bit
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
        """
        if interrupt_bit not in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            return
        
        # Update mip CSR
        mip = self.csr_bank.read(0x344)
        mip &= ~(1 << interrupt_bit)
        self.csr_bank.write(0x344, mip)
        
        # Clear edge latch if applicable
        self.latched_edges.discard(interrupt_bit)
    
    def is_pending(self, interrupt_bit):
        """Check if interrupt is pending
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
            
        Returns:
            True if interrupt is pending
        """
        mip = self.csr_bank.read(0x344)
        return (mip & (1 << interrupt_bit)) != 0
    
    def is_enabled(self, interrupt_bit):
        """Check if interrupt is enabled
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
            
        Returns:
            True if interrupt is enabled in mie
        """
        mie = self.csr_bank.read(0x304)
        return (mie & (1 << interrupt_bit)) != 0
    
    def is_globally_enabled(self):
        """Check if interrupts are globally enabled
        
        Returns:
            True if mstatus.MIE is set
        """
        mstatus = self.csr_bank.read(0x300)
        return (mstatus & (1 << 3)) != 0
    
    def get_pending_interrupts(self):
        """Get list of all pending interrupts
        
        Returns:
            List of interrupt bit positions that are pending
        """
        mip = self.csr_bank.read(0x344)
        pending = []
        
        for bit in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            if mip & (1 << bit):
                pending.append(bit)
        
        return pending
    
    def get_enabled_interrupts(self):
        """Get list of all enabled interrupts
        
        Returns:
            List of interrupt bit positions that are enabled
        """
        mie = self.csr_bank.read(0x304)
        enabled = []
        
        for bit in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            if mie & (1 << bit):
                enabled.append(bit)
        
        return enabled
    
    def get_deliverable_interrupts(self):
        """Get list of interrupts ready for delivery
        
        Returns pending interrupts that are both:
        - Individually enabled (mie bit set)
        - Globally enabled (mstatus.MIE set)
        
        Returns:
            List of interrupt bit positions ready for delivery
        """
        if not self.is_globally_enabled():
            return []
        
        mip = self.csr_bank.read(0x344)
        mie = self.csr_bank.read(0x304)
        
        # Mask pending with enabled
        deliverable_mask = mip & mie
        
        deliverable = []
        for bit in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            if deliverable_mask & (1 << bit):
                deliverable.append(bit)
        
        return deliverable
    
    def get_highest_priority_interrupt(self):
        """Get highest priority deliverable interrupt
        
        Uses priority: External > Software > Timer
        
        Returns:
            Interrupt bit position of highest priority interrupt,
            or None if no interrupts are deliverable
        """
        deliverable = self.get_deliverable_interrupts()
        
        if not deliverable:
            return None
        
        # Sort by priority (highest first)
        deliverable.sort(key=lambda bit: self.PRIORITY.get(bit, 0), reverse=True)
        
        return deliverable[0]
    
    def acknowledge_interrupt(self, interrupt_bit):
        """Acknowledge (clear) an interrupt after delivery
        
        For edge-triggered interrupts, clears the pending bit.
        For level-triggered interrupts, software must clear the source.
        
        Args:
            interrupt_bit: Interrupt bit position to acknowledge
        """
        # Edge-triggered: automatically clear pending
        if interrupt_bit in self.latched_edges:
            self.clear_pending(interrupt_bit)
        
        # Level-triggered: software must clear the interrupt source
        # The pending bit remains set until source is cleared
    
    def set_edge_triggered(self, interrupt_bit):
        """Configure interrupt as edge-triggered
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
        """
        if interrupt_bit in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            self.edge_triggered.add(interrupt_bit)
            self.level_triggered.discard(interrupt_bit)
    
    def set_level_triggered(self, interrupt_bit):
        """Configure interrupt as level-triggered
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
        """
        if interrupt_bit in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            self.level_triggered.add(interrupt_bit)
            self.edge_triggered.discard(interrupt_bit)
    
    def is_edge_triggered(self, interrupt_bit):
        """Check if interrupt is edge-triggered
        
        Args:
            interrupt_bit: Interrupt bit position
            
        Returns:
            True if edge-triggered
        """
        return interrupt_bit in self.edge_triggered
    
    def is_level_triggered(self, interrupt_bit):
        """Check if interrupt is level-triggered
        
        Args:
            interrupt_bit: Interrupt bit position
            
        Returns:
            True if level-triggered
        """
        return interrupt_bit in self.level_triggered
    
    def enable_interrupt(self, interrupt_bit):
        """Enable a specific interrupt
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
        """
        if interrupt_bit not in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            return
        
        mie = self.csr_bank.read(0x304)
        mie |= (1 << interrupt_bit)
        self.csr_bank.write(0x304, mie)
    
    def disable_interrupt(self, interrupt_bit):
        """Disable a specific interrupt
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
        """
        if interrupt_bit not in [self.INT_SOFTWARE, self.INT_TIMER, self.INT_EXTERNAL]:
            return
        
        mie = self.csr_bank.read(0x304)
        mie &= ~(1 << interrupt_bit)
        self.csr_bank.write(0x304, mie)
    
    def enable_global_interrupts(self):
        """Enable interrupts globally (set mstatus.MIE)"""
        mstatus = self.csr_bank.read(0x300)
        mstatus |= (1 << 3)
        self.csr_bank.write(0x300, mstatus)
    
    def disable_global_interrupts(self):
        """Disable interrupts globally (clear mstatus.MIE)"""
        mstatus = self.csr_bank.read(0x300)
        mstatus &= ~(1 << 3)
        self.csr_bank.write(0x300, mstatus)
    
    def mask_interrupts(self, mask):
        """Set interrupt enable mask
        
        Args:
            mask: Bitmask with bits 3, 7, 11 for software/timer/external
        """
        # Only allow setting valid interrupt bits
        valid_mask = (1 << 3) | (1 << 7) | (1 << 11)
        mask &= valid_mask
        
        # Read current mie, clear interrupt bits, set new mask
        mie = self.csr_bank.read(0x304)
        mie &= ~valid_mask
        mie |= mask
        self.csr_bank.write(0x304, mie)
    
    def get_interrupt_mask(self):
        """Get current interrupt enable mask
        
        Returns:
            Bitmask of enabled interrupts from mie
        """
        mie = self.csr_bank.read(0x304)
        valid_mask = (1 << 3) | (1 << 7) | (1 << 11)
        return mie & valid_mask
    
    def get_pending_mask(self):
        """Get current interrupt pending mask
        
        Returns:
            Bitmask of pending interrupts from mip
        """
        mip = self.csr_bank.read(0x344)
        valid_mask = (1 << 3) | (1 << 7) | (1 << 11)
        return mip & valid_mask
    
    def get_interrupt_code(self, interrupt_bit):
        """Convert interrupt bit position to interrupt code
        
        Args:
            interrupt_bit: Interrupt bit position (3, 7, or 11)
            
        Returns:
            Interrupt code with MSB set (0x80000003, 0x80000007, 0x8000000B)
        """
        if interrupt_bit == self.INT_SOFTWARE:
            return self.INTERRUPT_SOFTWARE
        elif interrupt_bit == self.INT_TIMER:
            return self.INTERRUPT_TIMER
        elif interrupt_bit == self.INT_EXTERNAL:
            return self.INTERRUPT_EXTERNAL
        return None
    
    def reset(self):
        """Reset interrupt controller state"""
        # Clear all pending interrupts
        self.csr_bank.write(0x344, 0)
        
        # Disable all interrupts
        mie = self.csr_bank.read(0x304)
        valid_mask = (1 << 3) | (1 << 7) | (1 << 11)
        mie &= ~valid_mask
        self.csr_bank.write(0x304, mie)
        
        # Disable global interrupts
        self.disable_global_interrupts()
        
        # Clear edge latches
        self.latched_edges.clear()
    
    def get_status_string(self):
        """Get human-readable status string
        
        Returns:
            String describing interrupt controller state
        """
        status = []
        status.append(f"Global Enable: {self.is_globally_enabled()}")
        status.append(f"Pending: SW={self.is_pending(3)} T={self.is_pending(7)} E={self.is_pending(11)}")
        status.append(f"Enabled: SW={self.is_enabled(3)} T={self.is_enabled(7)} E={self.is_enabled(11)}")
        
        deliverable = self.get_deliverable_interrupts()
        if deliverable:
            status.append(f"Deliverable: {deliverable}")
            highest = self.get_highest_priority_interrupt()
            status.append(f"Highest Priority: {highest}")
        else:
            status.append("No deliverable interrupts")
        
        return "\n".join(status)


class InterruptSource:
    """Represents an external interrupt source
    
    Can be connected to InterruptController to simulate
    real hardware interrupt sources (timers, peripherals, etc.)
    """
    
    def __init__(self, name, interrupt_bit):
        """Initialize interrupt source
        
        Args:
            name: Human-readable name
            interrupt_bit: Target interrupt bit (3, 7, or 11)
        """
        self.name = name
        self.interrupt_bit = interrupt_bit
        self.active = False
        self.controller = None
    
    def connect(self, controller):
        """Connect to an interrupt controller
        
        Args:
            controller: InterruptController instance
        """
        self.controller = controller
    
    def assert_interrupt(self):
        """Assert (raise) the interrupt signal"""
        self.active = True
        if self.controller:
            if self.controller.is_edge_triggered(self.interrupt_bit):
                # Edge-triggered: set pending on rising edge
                self.controller.set_pending(self.interrupt_bit, edge=True)
            else:
                # Level-triggered: set pending while active
                self.controller.set_pending(self.interrupt_bit)
    
    def deassert_interrupt(self):
        """Deassert (lower) the interrupt signal"""
        self.active = False
        if self.controller:
            if self.controller.is_level_triggered(self.interrupt_bit):
                # Level-triggered: clear pending when signal drops
                self.controller.clear_pending(self.interrupt_bit)
    
    def pulse(self):
        """Generate interrupt pulse (assert then deassert)"""
        self.assert_interrupt()
        self.deassert_interrupt()
    
    def is_active(self):
        """Check if interrupt signal is active
        
        Returns:
            True if interrupt is asserted
        """
        return self.active
