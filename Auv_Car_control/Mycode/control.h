/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file    gpio.h
  * @brief   This file contains all the function prototypes for
  *          the gpio.c file
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
/* Define to prevent recursive inclusion -------------------------------------*/
#ifndef __CONTROL_H__
#define __CONTROL_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include <stdio.h>
#include <string.h>
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* USER CODE BEGIN Private defines */
#define MAX_REV_TIME 6
#define 	MAX_RXD_LEN  10
/* USER CODE END Private defines */



/* USER CODE BEGIN Prototypes */
void USART6_send6_Date(void); // 发送速度控制
void USART6_read6_Date(void) ;// 读取速度控制
void  PNS_to6_mcu_Left(int Send_speed);
void USART4_send_Date(void); // 发送速度控制
void USART4_read_Date(void) ;// 读取速度控制
void  PNS_to2_mcu_Right(int Send_speed_4);

void USART6_read_Date(void); // 读取速度控制


void read6_left_Speed(void);

void read4_right_Speed(void);

void  Send_four_and_six(int Car_Right_Speed,int Car_Left_Speed,int Car_Baibi_Speed);

void  Read_left_and_right(void);
	
int  modbus_handle(uint8_t *buf,unsigned char len);
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif
#endif /*__CONTROL_H__ */

