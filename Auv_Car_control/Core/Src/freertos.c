/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * File Name          : freertos.c
 * Description        : Code for freertos applications
 ******************************************************************************
 * @attention
 *
 * Copyright (c) 2024 STMicroelectronics.
 * All rights reserved.
 *
 * This software is licensed under terms that can be found in the LICENSE file
 * in the root directory of this software component.
 * If no LICENSE file comes with this software, it is provided AS-IS.
 *
 ******************************************************************************
 */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <string.h>
#include "control.h"
#include "usart.h"
#include "MBcrc.h"
#include "pns.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

int16_t Speed_left = 0; // 接收的左电机速度

int16_t Speed_Right = 0; // 接收的右电机速度

int16_t read = 1; // 读数据标志

int16_t send = 0; // 写数据标志

int16_t read_finish = 0; // 读取完成标志

extern int Car_Left_Speed; // 向驱动器发送速度--左电机

extern int Car_Right_Speed; // 向驱动器发送速度--右电机

extern int Car_Baibi_Speed; // 向驱动器发送速度--摆臂电机

extern uint8_t receive_485_Left[MAX_RXD_LEN]; // 左电机接收485消息包

extern uint8_t receive_485_Right[MAX_RXD_LEN]; // 右电机接收485消息包

extern uint8_t send_bit; // 发送标志

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */

/* USER CODE END Variables */
osThreadId defaultTaskHandle;
osThreadId Led_Bug_taskHandle;
osThreadId Usart4_Bug_taskHandle;
osThreadId Usart6_Bug_taskHandle;

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */

/* USER CODE END FunctionPrototypes */

void StartDefaultTask(void const * argument);
void Led_Bug_task_function(void const * argument);
void Usart4_Bug_task_function(void const * argument);
void Usart6_Bug_task_function(void const * argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/* GetIdleTaskMemory prototype (linked to static allocation support) */
void vApplicationGetIdleTaskMemory( StaticTask_t **ppxIdleTaskTCBBuffer, StackType_t **ppxIdleTaskStackBuffer, uint32_t *pulIdleTaskStackSize );

/* USER CODE BEGIN GET_IDLE_TASK_MEMORY */
static StaticTask_t xIdleTaskTCBBuffer;
static StackType_t xIdleStack[configMINIMAL_STACK_SIZE];

void vApplicationGetIdleTaskMemory(StaticTask_t **ppxIdleTaskTCBBuffer, StackType_t **ppxIdleTaskStackBuffer, uint32_t *pulIdleTaskStackSize)
{
  *ppxIdleTaskTCBBuffer = &xIdleTaskTCBBuffer;
  *ppxIdleTaskStackBuffer = &xIdleStack[0];
  *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
  /* place for user code */
}
/* USER CODE END GET_IDLE_TASK_MEMORY */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* definition and creation of defaultTask */
  osThreadDef(defaultTask, StartDefaultTask, osPriorityLow, 0, 128);
  defaultTaskHandle = osThreadCreate(osThread(defaultTask), NULL);

  /* definition and creation of Led_Bug_task */
  osThreadDef(Led_Bug_task, Led_Bug_task_function, osPriorityLow, 0, 128);
  Led_Bug_taskHandle = osThreadCreate(osThread(Led_Bug_task), NULL);

  /* definition and creation of Usart4_Bug_task */
  osThreadDef(Usart4_Bug_task, Usart4_Bug_task_function, osPriorityHigh, 0, 256);
  Usart4_Bug_taskHandle = osThreadCreate(osThread(Usart4_Bug_task), NULL);

  /* definition and creation of Usart6_Bug_task */
  osThreadDef(Usart6_Bug_task, Usart6_Bug_task_function, osPriorityLow, 0, 256);
  Usart6_Bug_taskHandle = osThreadCreate(osThread(Usart6_Bug_task), NULL);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

}

/* USER CODE BEGIN Header_StartDefaultTask */
/**
 * @brief  Function implementing the defaultTask thread.
 * @param  argument: Not used
 * @retval None
 */
/* USER CODE END Header_StartDefaultTask */
void StartDefaultTask(void const * argument)
{
  /* USER CODE BEGIN StartDefaultTask */
  /* Infinite loop */
  for (;;)
  {
    Hand_model_explain(); // 遥控器接收解析
//		Run_square();
    osDelay(1);
  }
  /* USER CODE END StartDefaultTask */
}

/* USER CODE BEGIN Header_Led_Bug_task_function */
/**
 * @brief Function implementing the Led_Bug_task thread.
 * @param argument: Not used
 * @retval None
 */
/* USER CODE END Header_Led_Bug_task_function */
void Led_Bug_task_function(void const * argument)
{
  /* USER CODE BEGIN Led_Bug_task_function */
  /* Infinite loop */
  for (;;)
  {

      if (read_finish == 1) // 当485控制器接收速度信息完成后，开始上传给PNS
      {

        Mcu_To_Pns(); // 给PNS回传信息

        read_finish = 0; // 标志位清零
      }

    osDelay(1);
  }
  /* USER CODE END Led_Bug_task_function */
}

/* USER CODE BEGIN Header_Usart4_Bug_task_function */
/**
 * @brief Function implementing the Usart4_Bug_task thread.
 * @param argument: Not used
 * @retval None
 */
/* USER CODE END Header_Usart4_Bug_task_function */
void Usart4_Bug_task_function(void const * argument)
{
  /* USER CODE BEGIN Usart4_Bug_task_function */
  //		int left;
  /* Infinite loop */
  for (;;)
  {
    if (send == 0)
    {
      Send_four_and_six(Car_Right_Speed, Car_Left_Speed, Car_Baibi_Speed); // 给驱动器发送速度指令
      send = 1;
      read = 0;
    }
    osDelay(1);
  }
  /* USER CODE END Usart4_Bug_task_function */
}

/* USER CODE BEGIN Header_Usart6_Bug_task_function */
/**
 * @brief Function implementing the Usart6_Bug_task thread.
 * @param argument: Not used
 * @retval None
 */
/* USER CODE END Header_Usart6_Bug_task_function */
void Usart6_Bug_task_function(void const * argument)
{
  /* USER CODE BEGIN Usart6_Bug_task_function */
  /* Infinite loop */
  //	int left;
  for (;;)
  {
    if (read == 0)
    {
      Read_left_and_right();

      Speed_Right = modbus_handle(receive_485_Right, 9); // 处理右驱动器收到的数据

      Speed_left = modbus_handle(receive_485_Left, 9); // 处理左驱动器接收到的数据

      if (((Speed_left >> 8) && 0x01) == 1) // 反向--因为两个电机的安装方向不一样，必然有一个是反的
      {
        Speed_left = 65535 - Speed_left;
      }

      else
        Speed_left = -Speed_left;

      read = 1;

      send = 0;

      read_finish = 1;
    }
    osDelay(1); // 任务延时、给时间让其他任务执行
  }
  /* USER CODE END Usart6_Bug_task_function */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */

/* USER CODE END Application */
