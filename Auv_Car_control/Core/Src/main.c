/* USER CODE BEGIN Header */
/**
 ******************************************************************************
 * @file           : main.c
 * @brief          : Main program body
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
#include "main.h"
#include "cmsis_os.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <string.h>
#include "pns.h"
#include "parements.h"

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

uint16_t Tim_count = 0; // 定时器计数值---Bug灯

uint16_t Tim2_count = 0; // 转圈

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

extern int16_t Speed_left; // 左轮速度

extern int16_t Speed_Right; // 右轮速度

extern uint8_t receivedDate; // 串口三PNS----单字符接收


extern uint8_t start_bit;

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
void MX_FREERTOS_Init(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM4_Init();
  MX_TIM1_Init();
  MX_USART3_UART_Init();
  MX_USART6_UART_Init();
  MX_USART2_UART_Init();
  MX_UART7_Init();
  MX_TIM2_Init();
  /* USER CODE BEGIN 2 */

  HAL_TIM_Base_Start_IT(&htim4); // 启动定时器四  Bug 灯
	
	

  //  printf("--Hello--\r\n");                          // 开机测试

  __HAL_UART_ENABLE_IT(&huart2, UART_IT_RXNE); // 串口二使能    右电机485控制

  __HAL_UART_ENABLE_IT(&huart6, UART_IT_RXNE); // 串口六使能    左电机485控制

  __HAL_UART_ENABLE_IT(&huart7, UART_IT_RXNE); // 串口七使能     摆臂电机485控制

  HAL_TIM_Base_Start(&htim1); // 启动定时器八 遥控器读取

  HAL_UART_Receive_IT(&huart3, &receivedDate, 1); // 开启串口一接收中断,接受到1个字节后，就会进入到中断回调中  PNS 接收
	

	
  //	HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_3);         // 开启定时器3，PWM通道3---电机速度控制-----摆臂电机

  /* USER CODE END 2 */

  /* Call init function for freertos objects (in freertos.c) */
  MX_FREERTOS_Init();

  /* Start scheduler */
  osKernelStart();

  /* We should never get here as control is now taken by the scheduler */
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  Robot_Parament_Init(); // 机器人参数初始化
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 180;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Activate the Over-Drive mode
  */
  if (HAL_PWREx_EnableOverDrive() != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

/*************************Printf函数重写**********************************************/

// #if 1
// #pragma import(__use_no_semihosting) // 确保没有从 C 库链接使用半主机的函数

// int fputc(int c, FILE *p) // 函数默认的，在使用printf函数时自动调用
//{
//   uint8_t ch[1] = {c};
//   HAL_UART_Transmit(&huart1, ch, 1, 0xFFFF);
//   return c;
// }

// FILE __stdout;

// struct __FILE
//{
//   int handle;
// };

//// 定义_sys_exit()以避免使用半主机模式
// void _sys_exit(int x)
//{
//   x = x;
// }
// #endif

/*************************Printf函数重写**********************************************/

/******************************遥控器接收*********************************************/
extern uint16_t CountSensor_Count;

extern uint16_t PPM_Sample_Cnt; // 通道

extern uint8_t PPM_Chn_Max; // 最大通道数

extern uint32_t PPM_Time; // 获取通道时间

extern uint16_t PPM_Okay; // 下一次解析状态

extern uint16_t PPM_Databuf[13]; // 所有通道的数组

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  //		/*如果出现数据乱跳的现象，可再次判断引脚电平，以避免抖动*/

  if (GPIO_Pin == GPIO_PIN_10)
  {
    PPM_Time = TIM1->CNT; // 将定时数转存
    TIM1->CNT = 0;        // 计数器归零
    if (PPM_Okay == 1)    // 判断是否是新的一轮解析
    {
      PPM_Sample_Cnt++;                           // 通道数+1
      PPM_Databuf[PPM_Sample_Cnt - 1] = PPM_Time; // 把每一个通道的数值存入数组
      if (PPM_Sample_Cnt >= PPM_Chn_Max)          // 判断是否超过额定通道数
        PPM_Okay = 0;
    }
    if (PPM_Time >= 2050) // 长时间无下降沿即无通道数据，进入下一轮解析
    {
      PPM_Okay = 1;
      PPM_Sample_Cnt = 0;
    }
  }
}
/******************************遥控器接收*********************************************/

/* USER CODE END 4 */

/**
  * @brief  Period elapsed callback in non blocking mode
  * @note   This function is called  when TIM14 interrupt took place, inside
  * HAL_TIM_IRQHandler(). It makes a direct call to HAL_IncTick() to increment
  * a global variable "uwTick" used as application time base.
  * @param  htim : TIM handle
  * @retval None
  */
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
  /* USER CODE BEGIN Callback 0 */
  /******************************心跳灯*********************************************/
  if (htim == &htim4)
  {
    Tim_count++;          // 心跳
    if (Tim_count == 500) //----心跳中断---- 200ms
    {

      HAL_GPIO_TogglePin(GPIOC, LED_BUG_Pin); // 电平反转
      Tim_count = 0;
    }
  }
  /******************************心跳灯*********************************************/

	
	if(htim == &htim2)
	{
		Tim2_count++;
	  if (Tim2_count == 5000) //----心跳中断---- 200ms
    {
			HAL_TIM_Base_Stop_IT(&htim2);  //停止定时器的时候调用这个函数关闭
			start_bit=1;
      Tim2_count = 0;
    }
	}
	
	
  /* USER CODE END Callback 0 */
  if (htim->Instance == TIM14) {
    HAL_IncTick();
  }
  /* USER CODE BEGIN Callback 1 */

  /* USER CODE END Callback 1 */
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
