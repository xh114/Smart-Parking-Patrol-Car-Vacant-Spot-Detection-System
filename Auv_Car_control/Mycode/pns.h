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
#ifndef __PNS_H__
#define __PNS_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "main.h"
	
#include "tim.h"
#include <stdio.h>
#include <string.h>
/* USER CODE BEGIN Includes */

/* USER CODE END Includes */

/* USER CODE BEGIN Private defines */
#define PI 3.14
	
#define SEND_DATA_SIZE		24								//发送数据位数
	
#define RECEIVE_DATA_SIZE 11								//接收数据位数

/***************** 命令处理 ************************/
typedef struct
{
	uint8_t Mode;		   // 模式
	uint8_t Brake;		   // 刹车
	int Velocity;	   // 线速度
	int Angular;	   // 角速度
	uint8_t NavigationMode; // 导航方式
	uint16_t Abnormal;	   // 异常
	uint32_t ControlEnable; // 控制使能
	uint32_t ControlSet;	   // 控制控制位
	uint32_t DeviceControl; // 设备控制
	uint32_t CanData[8];	   // 对于can数据
	uint16_t UpCommand;	   // 升级命令
} COMMAND_DATA_TypeDef;


// 电机速度控制相关参数结构体
typedef struct
{
	float Encoder;	   // 编码器值：实际读到的速度值

	int Encoder_Rpm;   // 编码器值：定时器读到的编码器值

	int Motor_Pwm;	   // 电机的PWM

	float Target;	   // 电机目标速度
	
	int Speed;

	float Velocity_KP; // 速度控制：PID参数

	float Velocity_KI; // 速度控制：PID参数

	float Velocity_KD; // 速度控制：PID参数

} Moter_Parameter_InitTypeDef;


// 机器人硬件参数结构体
typedef struct
{
	float Wheel_R;	 // 轮子半径				 单位: m

	int GearRatio;	 // 电机减速比

	int EncoderLine; // 编码器线数量

	float Encoder_precision;	// 编码器精度，若用AB相采集应*2

	float Wheel_perimeter;		// 轮子周长 				 单位: m

	float Wheel_spacing;		// 主动轮距 				 单位: m

	float Wheelbase_separation; // 小车前后轴的距离  单位: m

	float Ture_radius;			// 转弯半径 				 单位: m
	
} Robot_Parament_InitTypeDef;



/********** 串口发送数据结构体 **************/
typedef struct _SEND_DATA_
{
	unsigned char buffer[SEND_DATA_SIZE];
	struct _Sensor_Str_
	{
	  unsigned char Frame_Header;							//帧头
		short X_speed;													//x轴熟读   	2位
		short Y_speed;													//y轴熟读   	2位
		short Z_speed;													//z轴熟读   	2位
		short Power_Voltage;										//电池电压  	2位
		unsigned char Frame_Tail;								//帧尾
	}Sensor_Str;
}SEND_DATA;
	
/* USER CODE END Private defines */



/* USER CODE BEGIN Prototypes */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin);
void Hand_model_explain(void);
void Mcu_To_Pns(void);
void Run_square(void);
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif
#endif /*__PNS_H__ */

