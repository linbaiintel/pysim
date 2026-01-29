"""Core Local Interruptor (CLINT) for RISC-V

Implements the RISC-V CLINT peripheral providing:
- Timer interrupts (mtime/mtimecmp) for OS scheduling
- Software interrupts (msip) for inter-processor interrupts

Memory Map (standard RISC-V CLINT):
- 0x02000000: msip (Machine Software Interrupt Pending) - 4 bytes
- 0x02004000: mtimecmp (Machine Timer Compare) - 8 bytes  
- 0x0200bff8: mtime (Machine Time) - 8 bytes

This is essential for FreeRTOS and other RTOS implementations that rely
on periodic timer interrupts for task scheduling.
"""


class CLINT:
    """Core Local Interruptor peripheral
    
    Provides timer and software interrupt functionality for RISC-V systems.
    """
    
    # Memory-mapped register addresses (standard RISC-V CLINT)
    MSIP_BASE = 0x02000000      # Software interrupt pending
    MTIMECMP_BASE = 0x02004000  # Timer compare register
    MTIME_BASE = 0x0200bff8     # Timer register
    
    def __init__(self, interrupt_controller, time_scale=1):
        """Initialize CLINT peripheral
        
        Args:
            interrupt_controller: InterruptController instance for triggering interrupts
            time_scale: Time scaling factor (cycles per time unit)
                       1 = increment every cycle
                       1000 = increment every 1000 cycles (for ms timing)
        """
        self.interrupt_controller = interrupt_controller
        self.time_scale = time_scale
        
        # Timer registers (64-bit)
        self.mtime = 0          # Current time counter
        self.mtimecmp = 0xFFFFFFFFFFFFFFFF  # Timer compare (default: max value, no interrupt)
        
        # Software interrupt register (32-bit)
        self.msip = 0           # Software interrupt pending
        
        # Internal state
        self.cycle_count = 0    # Cycle counter for time scaling
        self.timer_enabled = True
        
    def tick(self, cycles=1):
        """Advance the timer by specified cycles
        
        Should be called each simulation cycle to update mtime and check
        for timer interrupt conditions.
        
        Args:
            cycles: Number of cycles to advance (default: 1)
        """
        if not self.timer_enabled:
            return
            
        self.cycle_count += cycles
        
        # Update mtime based on time scale
        if self.cycle_count >= self.time_scale:
            mtime_increment = self.cycle_count // self.time_scale
            self.mtime = (self.mtime + mtime_increment) & 0xFFFFFFFFFFFFFFFF
            self.cycle_count = self.cycle_count % self.time_scale
            
            # Check for timer interrupt
            self._check_timer_interrupt()
    
    def _check_timer_interrupt(self):
        """Check if timer interrupt should be triggered"""
        if self.mtime >= self.mtimecmp:
            # Trigger timer interrupt
            self.interrupt_controller.set_pending(self.interrupt_controller.INT_TIMER)
    
    def read_register(self, address):
        """Read from CLINT memory-mapped register
        
        Args:
            address: Register address
            
        Returns:
            Register value (32-bit or 64-bit depending on register)
        """
        if address == self.MSIP_BASE:
            # Read msip (32-bit)
            return self.msip & 0xFFFFFFFF
            
        elif address == self.MTIMECMP_BASE:
            # Read lower 32 bits of mtimecmp
            return self.mtimecmp & 0xFFFFFFFF
            
        elif address == self.MTIMECMP_BASE + 4:
            # Read upper 32 bits of mtimecmp
            return (self.mtimecmp >> 32) & 0xFFFFFFFF
            
        elif address == self.MTIME_BASE:
            # Read lower 32 bits of mtime
            return self.mtime & 0xFFFFFFFF
            
        elif address == self.MTIME_BASE + 4:
            # Read upper 32 bits of mtime
            return (self.mtime >> 32) & 0xFFFFFFFF
            
        else:
            # Invalid address
            return 0
    
    def write_register(self, address, value):
        """Write to CLINT memory-mapped register
        
        Args:
            address: Register address
            value: Value to write (32-bit)
        """
        value = value & 0xFFFFFFFF  # Ensure 32-bit
        
        if address == self.MSIP_BASE:
            # Write msip (only bit 0 is significant)
            old_msip = self.msip
            self.msip = value & 0x1
            
            # Trigger/clear software interrupt
            if self.msip and not old_msip:
                self.interrupt_controller.set_pending(self.interrupt_controller.INT_SOFTWARE)
            elif not self.msip and old_msip:
                self.interrupt_controller.clear_pending(self.interrupt_controller.INT_SOFTWARE)
                
        elif address == self.MTIMECMP_BASE:
            # Write lower 32 bits of mtimecmp
            self.mtimecmp = (self.mtimecmp & 0xFFFFFFFF00000000) | value
            # Clear timer interrupt when mtimecmp is written
            self.interrupt_controller.clear_pending(self.interrupt_controller.INT_TIMER)
            
        elif address == self.MTIMECMP_BASE + 4:
            # Write upper 32 bits of mtimecmp
            self.mtimecmp = (self.mtimecmp & 0xFFFFFFFF) | (value << 32)
            # Clear timer interrupt when mtimecmp is written
            self.interrupt_controller.clear_pending(self.interrupt_controller.INT_TIMER)
            
        elif address == self.MTIME_BASE:
            # Write lower 32 bits of mtime
            self.mtime = (self.mtime & 0xFFFFFFFF00000000) | value
            
        elif address == self.MTIME_BASE + 4:
            # Write upper 32 bits of mtime
            self.mtime = (self.mtime & 0xFFFFFFFF) | (value << 32)
    
    def read_mtime_64(self):
        """Read full 64-bit mtime value
        
        Returns:
            64-bit mtime value
        """
        return self.mtime
    
    def write_mtime_64(self, value):
        """Write full 64-bit mtime value
        
        Args:
            value: 64-bit value to write
        """
        self.mtime = value & 0xFFFFFFFFFFFFFFFF
    
    def read_mtimecmp_64(self):
        """Read full 64-bit mtimecmp value
        
        Returns:
            64-bit mtimecmp value
        """
        return self.mtimecmp
    
    def write_mtimecmp_64(self, value):
        """Write full 64-bit mtimecmp value
        
        Args:
            value: 64-bit value to write
        """
        self.mtimecmp = value & 0xFFFFFFFFFFFFFFFF
        # Clear timer interrupt when mtimecmp is written
        self.interrupt_controller.clear_pending(self.interrupt_controller.INT_TIMER)
    
    def set_timer_interrupt(self, interval):
        """Configure timer interrupt at specified interval
        
        Args:
            interval: Number of time units until next interrupt
        """
        self.mtimecmp = self.mtime + interval
    
    def clear_timer_interrupt(self):
        """Clear pending timer interrupt by setting mtimecmp to max"""
        self.mtimecmp = 0xFFFFFFFFFFFFFFFF
        self.interrupt_controller.clear_pending(self.interrupt_controller.INT_TIMER)
    
    def trigger_software_interrupt(self):
        """Trigger software interrupt (set msip)"""
        self.msip = 1
        self.interrupt_controller.set_pending(self.interrupt_controller.INT_SOFTWARE)
    
    def clear_software_interrupt(self):
        """Clear software interrupt (clear msip)"""
        self.msip = 0
        self.interrupt_controller.clear_pending(self.interrupt_controller.INT_SOFTWARE)
    
    def reset(self):
        """Reset CLINT to initial state"""
        self.mtime = 0
        self.mtimecmp = 0xFFFFFFFFFFFFFFFF
        self.msip = 0
        self.cycle_count = 0
        self.interrupt_controller.clear_pending(self.interrupt_controller.INT_TIMER)
        self.interrupt_controller.clear_pending(self.interrupt_controller.INT_SOFTWARE)
    
    def get_status(self):
        """Get current CLINT status
        
        Returns:
            Dictionary with current state
        """
        return {
            'mtime': self.mtime,
            'mtimecmp': self.mtimecmp,
            'msip': self.msip,
            'timer_pending': self.mtime >= self.mtimecmp,
            'cycles_until_interrupt': max(0, self.mtimecmp - self.mtime) if self.mtime < self.mtimecmp else 0
        }
