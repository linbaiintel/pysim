#include "FreeRTOS.h"
#include "task.h"

/* UART addresses */
#define UART_BASE 0x10000000
#define UART_TX_DATA (*(volatile unsigned int *)UART_BASE)

/* Simple UART output functions */
void uart_putc(char c)
{
    UART_TX_DATA = (unsigned int)c;
}

void uart_puts(const char *str)
{
    while (*str) {
        uart_putc(*str++);
    }
}

void uart_putnum(int num)
{
    char buffer[12];
    int i = 0;
    int is_negative = 0;
    
    if (num < 0) {
        is_negative = 1;
        num = -num;
    }
    
    if (num == 0) {
        uart_putc('0');
        return;
    }
    
    while (num > 0) {
        buffer[i++] = '0' + (num % 10);
        num /= 10;
    }
    
    if (is_negative) {
        uart_putc('-');
    }
    
    while (i > 0) {
        uart_putc(buffer[--i]);
    }
}

/* Task 1: Print message */
void vTask1(void *pvParameters)
{
    int counter = 0;
    (void)pvParameters;
    
    uart_puts("Task1: Starting\n");
    
    for (;;)
    {
        uart_puts("Task1: Running (counter=");
        uart_putnum(counter++);
        uart_puts(")\n");
        vTaskDelay(pdMS_TO_TICKS(500));  /* Delay 500ms */
    }
}

/* Task 2: Print message */
void vTask2(void *pvParameters)
{
    int counter = 0;
    (void)pvParameters;
    
    uart_puts("Task2: Starting\n");
    
    for (;;)
    {
        uart_puts("Task2: Hello from FreeRTOS! (counter=");
        uart_putnum(counter++);
        uart_puts(")\n");
        vTaskDelay(pdMS_TO_TICKS(1000));  /* Delay 1000ms */
    }
}

/* Main function */
int main(void)
{
    uart_puts("\n");
    uart_puts("===========================================\n");
    uart_puts("FreeRTOS Demo on RISC-V RV32I Simulator\n");
    uart_puts("===========================================\n");
    uart_puts("Creating tasks...\n\n");
    
    /* Create Task 1 */
    xTaskCreate(
        vTask1,                 /* Task function */
        "Task1",                /* Task name */
        configMINIMAL_STACK_SIZE, /* Stack size */
        NULL,                   /* Parameters */
        1,                      /* Priority */
        NULL                    /* Task handle */
    );
    
    /* Create Task 2 */
    xTaskCreate(
        vTask2,
        "Task2",
        configMINIMAL_STACK_SIZE,
        NULL,
        2,                      /* Higher priority */
        NULL
    );
    
    uart_puts("Starting scheduler...\n\n");
    
    /* Start the scheduler */
    vTaskStartScheduler();
    
    /* Should never reach here */
    uart_puts("ERROR: Scheduler failed to start!\n");
    for (;;);
}

/* FreeRTOS Hook Functions */
void vApplicationMallocFailedHook(void)
{
    uart_puts("ERROR: Malloc failed!\n");
    taskDISABLE_INTERRUPTS();
    for (;;);
}

void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName)
{
    (void) xTask;
    uart_puts("ERROR: Stack overflow in task: ");
    uart_puts(pcTaskName);
    uart_puts("\n");
    taskDISABLE_INTERRUPTS();
    for (;;);
}

void vApplicationIdleHook(void)
{
    /* Called when idle - can be used for low power mode */
}

void vApplicationTickHook(void)
{
    /* Called on each tick - keep it short! */
}
