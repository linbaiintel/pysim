/*
 * Minimal C library implementations for bare-metal FreeRTOS
 * Only includes what's actually needed by FreeRTOS
 */

#include <stddef.h>

/* memset - fill memory with a constant byte */
void *memset(void *s, int c, size_t n) {
    unsigned char *p = (unsigned char *)s;
    while (n--) {
        *p++ = (unsigned char)c;
    }
    return s;
}

/* memcpy - copy memory area */
void *memcpy(void *dest, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dest;
    const unsigned char *s = (const unsigned char *)src;
    while (n--) {
        *d++ = *s++;
    }
    return dest;
}

/* abort - called on assertion failures */
void abort(void) {
    /* Infinite loop - hang the system */
    while (1) {
        __asm__ volatile ("nop");
    }
}
