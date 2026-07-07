#include "pns.h"
#include "control.h"
#include "main.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"
#include "function.h"

uint8_t start_bit=0;

uint8_t suqare_mode =0;

uint8_t suqare_bit1 =0;

uint8_t suqare_bit2 =0;

uint8_t suqare_bit3 =0;

uint8_t suqare_bit4 =0;

int bit_water = 0; // 前进 后退 参数

int bit_ziwaideng = 0; // 前进 后退 参数

int PW1_up_down = 0; // 前进 后退 参数

int PW2_left_right = 0; // 左转右转参数

int PW3_baibi = 0; // 摆臂参数

int PW4_Vx_multiple = 0; // 线速度放大控制

int PW5_Wx_multiple = 0; // 角速度放大控制

int Vx_multiple = 50; // 线速度放大比例

int Wx_multiple = 50; // 角速度放大比例

int Mode_change = 0; // 机器人运动模式

uint8_t Robot_mode = 0; // 机器人模式  0 遥控  1 手动

uint8_t Auto_to_Hand; // 自动模式到手动模式

uint8_t Receive_Finish; // 接收完一帧数据包

int Car_Left_Speed = 0; // 左电机速度

int Car_Right_Speed = 0; // 右电机速度

int Car_Baibi_Speed = 0; // 摆臂电机速度

uint8_t RxState; // 接收状态标志

uint8_t RxState_ok; // 接收状态标志打印

uint8_t receivedDate; // 单字符接收

uint8_t receivedLength; // PNS接收长度

uint8_t receivedPns[16]; // 接收PNS消息包

uint8_t Receive_Finish; // 接收完一帧数据包

uint8_t receivedCount; // 接收PNS消息个数

uint8_t sendPns[22]; // 发送给PNS消息包

float amplitude_x = 1.3; // 目标速度限幅

float amplitude_w = 4; // 目标速度限幅

uint8_t Hand_to_Auto; // 手动模式到自动模式

float target_Vx = 0, target_Wz = 0; // 机器人速度

short SVL = 0, SVR = 0; // 左右电机速度

Moter_Parameter_InitTypeDef MOTOR_A, MOTOR_B; // 电机速度控制相关参数结构体

Robot_Parament_InitTypeDef Robot_Parament; // 机器人硬件参数结构体

SEND_DATA Send_Data; // 给PNS发送消息结构体

COMMAND_DATA_TypeDef Command_Data; // 机器人状态结构体

uint16_t PPM_Sample_Cnt = 0; // 通道

uint8_t PPM_Chn_Max = 8; // 最大通道数

uint32_t PPM_Time = 0; // 获取通道时间

uint16_t PPM_Okay = 0; // 下一次解析状态

uint16_t PPM_Databuf[13] = {0}; // 所有通道的数组

extern volatile uint8_t receptionComplete; // 接收完成标志

uint8_t send_bit; // 发送标志

uint8_t Receive_Finish; // 接收完一帧数据包

Moter_Parameter_InitTypeDef MOTOR_A, MOTOR_B; // 电机速度控制相关参数结构体

Robot_Parament_InitTypeDef Robot_Parament; // 机器人硬件参数结构体

SEND_DATA Send_Data; // 给PNS发送消息结构体

COMMAND_DATA_TypeDef Command_Data; // 机器人状态结构体

extern volatile uint8_t receptionComplete; // 接收完成标志

extern int16_t Speed_left;

extern int16_t Speed_Right;

// 摆臂电机----MORTOR3---方向控制
void Motor3_Set(int8_t Model)
{
	if (Model >= 0)
	{
		HAL_GPIO_WritePin(GPIOD, MORTOR3_1_Pin, GPIO_PIN_SET);
		HAL_GPIO_WritePin(GPIOD, MORTOR3_2_Pin, GPIO_PIN_RESET);
	}
	else
	{
		HAL_GPIO_WritePin(GPIOD, MORTOR3_1_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(GPIOD, MORTOR3_2_Pin, GPIO_PIN_SET);
	}
}


/**************************飞机遥控器处理********************************/
// 函数功能：---飞机遥控器外部中断 -----
// 功能描述：
// 心跳指示灯--PD10
/**************************-遥控器解析-*******************************/
void Hand_model_explain()
{
	int save_speed_4, save_speed_6;
  
  

	PW1_up_down = PPM_Databuf[1] - 1500; // PWM1的值 --上下

	PW2_left_right = PPM_Databuf[3] - 1500; // PWM2的值 --左右

	PW3_baibi = PPM_Databuf[2] - 1500; // PWM3的值 --摆臂
	
	PW4_Vx_multiple = PPM_Databuf[6]; // PWM4的值 --线速度放大比例控制

	PW5_Wx_multiple = PPM_Databuf[5] ; // PWM5的值 --角速度放大比例控制
	

  
  
  
// 紫外线灯-20251111-调节速度
/************************************1-线速度控制比例****************************/
	
	
	if (PW4_Vx_multiple > 1900) // 全部熄灭--->功能调整：速度等级划分
	{
//	  HAL_GPIO_WritePin(Led_red_GPIO_Port,   Led_red_Pin,   GPIO_PIN_RESET); 
//		HAL_GPIO_WritePin(Led_green_GPIO_Port, Led_green_Pin, GPIO_PIN_RESET); 
    Vx_multiple = 5;
    Wx_multiple = 5;
	}
	

	if ((PW4_Vx_multiple < 1900)&&(PW4_Vx_multiple>1400)) // 绿灯亮--->功能调整：速度等级划分
	{
//	  HAL_GPIO_WritePin(Led_red_GPIO_Port,   Led_red_Pin,   GPIO_PIN_SET); 
//		HAL_GPIO_WritePin(Led_green_GPIO_Port, Led_green_Pin, GPIO_PIN_RESET); 
     Vx_multiple = 10;
    Wx_multiple = 5;
	}
	
	
	
	if (PW4_Vx_multiple < 1200) // 红灯亮--->功能调整：速度等级划分
	{
//	  HAL_GPIO_WritePin(Led_red_GPIO_Port,   Led_red_Pin,   GPIO_PIN_RESET); 
//		HAL_GPIO_WritePin(Led_green_GPIO_Port, Led_green_Pin, GPIO_PIN_SET); 
    Vx_multiple = 20;
    Wx_multiple = 5;
	}
	
/************************************1-线速度控制比例****************************/

	
	
	
	
// 喷水电机
/************************************2-角速度控制比例****************************/

	if (PW5_Wx_multiple > 1900) // 喷水关闭---紫外线关闭
	{
	  HAL_GPIO_WritePin(water_control_GPIO_Port, water_control_Pin, GPIO_PIN_RESET); 
		HAL_GPIO_WritePin(Ziled_control_GPIO_Port, Ziled_control_Pin, GPIO_PIN_RESET); 
	}
	

	if ((PW5_Wx_multiple < 1900)&&(PW5_Wx_multiple>1400)) // 紫外线打开
	{
	  HAL_GPIO_WritePin(water_control_GPIO_Port, water_control_Pin, GPIO_PIN_RESET); 
		HAL_GPIO_WritePin(Ziled_control_GPIO_Port, Ziled_control_Pin, GPIO_PIN_SET); 
	}
	
	
	
	if (PW5_Wx_multiple < 1200) // 喷水打开
	{
		HAL_GPIO_WritePin(water_control_GPIO_Port, water_control_Pin, GPIO_PIN_SET);   
		HAL_GPIO_WritePin(Ziled_control_GPIO_Port, Ziled_control_Pin, GPIO_PIN_SET); 
	}
	
	
/************************************2-角速度控制比例****************************/

	
	
	
	
 /************************************3-控制模式选择******************************/
	Mode_change = PPM_Databuf[7];
	if (Mode_change > 1550)
	{

		HAL_GPIO_WritePin(GPIOC, LED4_Pin, GPIO_PIN_RESET); // 遥控----LED4亮


		Robot_mode = 0; // 遥控

		Hand_to_Auto = 0;

		Receive_Finish = 0;
	}

	else
	{
		HAL_GPIO_WritePin(GPIOC, LED4_Pin, GPIO_PIN_SET); // 导航-----LED4熄灭

		Robot_mode = 1; // 导航

		Auto_to_Hand = 0;
	}
  /************************************3-控制模式选择******************************/

	
	
	//  遥控模式
	if (Robot_mode == 0)
	{
		if (Auto_to_Hand == 0)
		{
			Command_Data.Velocity = 0; // PNS --解析的线速度清除

			Command_Data.Angular = 0; // PNS --解析的角速度清除

			target_Vx = 0, target_Wz = 0; // 目标速度清零

			MOTOR_A.Speed = 0;

			MOTOR_B.Speed = 0;

			Send_Data.Sensor_Str.X_speed = 0; // 通过编码器返回左电机实际的速度

			Send_Data.Sensor_Str.Z_speed = 0; // 通过编码器返回右电机实际的速度

			SVR = 0; // motorA 右电机

			SVL = 0; // motorB 左电机

			Auto_to_Hand = 1;
		}
    
    

		if (PW1_up_down > 100) // 前进
		{
			save_speed_4 =  PW1_up_down * Vx_multiple;  // 右电机
			save_speed_6 = -PW1_up_down * Vx_multiple; // 左电机
			
		}

		if (PW1_up_down < 100) // 后退
		{
			save_speed_4 = PW1_up_down * Vx_multiple;
			save_speed_6 = -PW1_up_down * Vx_multiple;
		}

		if ((PW1_up_down >= -100 && PW1_up_down <= 100)) //----停止----
		{
			save_speed_4 = 0;
			save_speed_6 = 0;
		}

		
		
		//  赋值操作
		Car_Right_Speed = save_speed_4;
		Car_Left_Speed = save_speed_6;

		if (PW2_left_right > 100) //----左转----
		{
			Car_Right_Speed = -100 * Wx_multiple+save_speed_4;
			Car_Left_Speed = -100 * Wx_multiple+save_speed_6;
		}

		if (PW2_left_right < -100) //----右转----
		{
			Car_Right_Speed = 100 * Wx_multiple+save_speed_4;
			Car_Left_Speed = 100 * Wx_multiple+save_speed_6;
		}

		if (PW3_baibi > 450)
		{
			// Motor3_Set(1); //----上摆臂----
			//__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, 400);
			Car_Baibi_Speed = 300;
		}

		if (PW3_baibi < -450)
		{
			// Motor3_Set(-1); // 下摆臂
			//__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, 400);
			Car_Baibi_Speed = -300;
		}

		if (PW3_baibi > -100 && PW3_baibi < 100)
		{
			//__HAL_TIM_SET_COMPARE(&htim3, TIM_CHANNEL_3, 0);
			Car_Baibi_Speed = 0;
		}
	}
}




/**************************-行走正方行控制-********************************/

void Run_square()
{
   if(suqare_mode==0)
	 {
	    HAL_TIM_Base_Start_IT(&htim2); // 启动定时器二 
		 
		  if((suqare_bit1==0)&&(start_bit==0))
				{
						MOTOR_A.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
          	MOTOR_B.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
				}
				
			if((suqare_bit1==1)&&(start_bit==0))
				{
						MOTOR_A.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
          	MOTOR_B.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
				}
				
					
			if((suqare_bit1==2)&&(start_bit==0))
				{
						MOTOR_A.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
          	MOTOR_B.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
				}	
				
				
				if((suqare_bit1==3)&&(start_bit==0))
				{
						MOTOR_A.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
          	MOTOR_B.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
				}	
						if((suqare_bit1==4)&&(start_bit==0))
				{
						MOTOR_A.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
          	MOTOR_B.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
				}	
						if((suqare_bit1==5)&&(start_bit==0))
				{
						MOTOR_A.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
          	MOTOR_B.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
				}	
						if((suqare_bit1==6)&&(start_bit==0))
				{
						MOTOR_A.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
          	MOTOR_B.Speed = (int)(((0.1f / 0.5f) * 53.0f) * 60.0f); //----------- 将 m/s转化为 r/min
				}	
				
			if(start_bit==1)
				{
						MOTOR_A.Speed =0;
					  MOTOR_B.Speed =0;
					  suqare_bit1=suqare_bit1+1;
					  start_bit=0;
					  HAL_TIM_Base_Start_IT(&htim2); // 启动定时器二 
				}	
				
				if(suqare_bit1==0) //直
				{
          Car_Right_Speed = MOTOR_A.Speed;
          Car_Left_Speed =  -MOTOR_B.Speed;
				}
				
				if(suqare_bit1==1) //左
				{
				  Car_Right_Speed = MOTOR_A.Speed;
		      Car_Left_Speed =  MOTOR_B.Speed;
				}
				
				if(suqare_bit1==2)//直
				{
          Car_Right_Speed = MOTOR_A.Speed;
          Car_Left_Speed =  -MOTOR_B.Speed;
				}
				
				if(suqare_bit1==3)//左
				{
          Car_Right_Speed = MOTOR_A.Speed;
          Car_Left_Speed =  MOTOR_B.Speed;
				}
				
				if(suqare_bit1==4)//直
				{
          Car_Right_Speed = MOTOR_A.Speed;
          Car_Left_Speed =  -MOTOR_B.Speed;
				}
				
				
				if(suqare_bit1==5) //左
				{
          Car_Right_Speed = MOTOR_A.Speed;
          Car_Left_Speed =  MOTOR_B.Speed;
				}
				
				if(suqare_bit1==6) //直
				{
				 Car_Right_Speed = MOTOR_A.Speed;
		    Car_Left_Speed =  -MOTOR_B.Speed;
				}
	 }		 

}
/**************************-行走正方行控制-********************************/








/**************************-左右电机速度解析-********************************/

// 函数功能：---机器人电机目标速度解析 -----
// 功能描述：解析PNS下发下来的速度，得到A，B电机速度
// 电机
void Drive_Motor(float Vx, float Wz) //   左转  右转更改此处
{
	//  MOTOR_A.Target = Vx + (Wz * Robot_Parament.Wheel_spacing / 2); // PNS下发解析到右电机的速度

	//  MOTOR_B.Target = Vx - (Wz * Robot_Parament.Wheel_spacing / 2); // PNS下发解析到左电机的速度

	//	MOTOR_A.Target = Vx + (Wz * 0.25); // PNS下发解析到右电机的速度

	//  MOTOR_B.Target = Vx - (Wz * 0.25); // PNS下发解析到左电机的速度

	MOTOR_A.Target = Vx + (Wz * 0.21f); // 轮距为0.42

	MOTOR_B.Target = Vx - (Wz * 0.21f); // 轮距为0.42

	/************ 目标速度限幅  ***********/
	MOTOR_A.Target = target_limit_float(MOTOR_A.Target, -amplitude_x, amplitude_x); // 右电机的速度

	MOTOR_B.Target = target_limit_float(MOTOR_B.Target, -amplitude_w, amplitude_w); // 左电机的速度

	MOTOR_A.Speed = (int)(((MOTOR_A.Target / 0.5f) * 53) * 60); //----------- 将 m/s转化为 r/min

	MOTOR_B.Speed = (int)(((MOTOR_B.Target / 0.5f) * 53) * 60); //----------- 将 m/s转化为 r/min
}
/**************************-左右电机速度解析-********************************/



/**************************-串口接收回调-******************************/

// 函数功能：---串口三接收回调函数 -----
// 功能描述：用于处理串口接收完成时的中断事件，当接收到指定长度的数据后，该回调函数将被触发
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	if (huart == &huart3) // 串口三回调
	{

		if (RxState == 0) // 验证
		{
			if (receivedDate == 0xAA) // 帧头一
			{
				RxState = 1;
			}
		}
		else if (RxState == 1)
		{
			if (receivedDate == 0xBB) // 帧头二
			{
				RxState = 2;
			}
		}
		else if (RxState == 2)
		{
			if (receivedDate == 0xCC) // 帧头三
			{
				RxState = 3;
			}
		}
		else if (RxState == 3) // 长度
		{
			receivedLength = receivedDate;

			RxState = 4;

			receivedCount = 4;
		}

		else if (RxState == 4) // 校验
		{
			receivedPns[receivedCount++] = receivedDate;
			if (receivedCount == receivedLength + 3)
			{
				RxState = 5;

				receivedPns[0] = 0xAA;

				receivedPns[1] = 0xBB;

				receivedPns[2] = 0xCC;

				receivedPns[3] = receivedLength;

				if (receivedPns[receivedCount - 1] == SUM_Cal(receivedPns, receivedLength + 2)) // 注意校验长度
				{

					RxState_ok = 1;

					if (receivedPns[4] == 0x01)
					{

						HAL_GPIO_TogglePin(GPIOC, LED_BUG_Pin); // 电平反转

						Command_Data.Mode = receivedPns[5]; // 模式

						Command_Data.Brake = receivedPns[6]; // 刹车

						if (receivedPns[8] >> 3 & 0x01)
						{

							Command_Data.Velocity = (int)(receivedPns[8] << 8) | receivedPns[7] - 65536;
						}

						else
						{
							Command_Data.Velocity = (int)(receivedPns[8] << 8) | receivedPns[7];
						}

						if (receivedPns[10] >> 3 & 0x01)
						{

							Command_Data.Angular = (int)(receivedPns[10] << 8) | receivedPns[9] - 65536;
						}

						else
						{
							Command_Data.Angular = (int)(receivedPns[10] << 8) | receivedPns[9];
						}

						Command_Data.NavigationMode = receivedPns[11]; // PNS 下发的导航方式

						Command_Data.Abnormal = (receivedPns[13] << 8) | receivedPns[12]; // PNS异常

						target_Vx = (float)Command_Data.Velocity / 100; // 解析PNS--得到线速度

						target_Wz = (float)Command_Data.Angular / 100; // 解析PNS--得到角速度

						/*--实现小车巡线，但问题是小车并没有在线上,解决办法：转向解算加快点 只加快角速度，或者把角速度乘一个系数，杨文涛老师--*/

						//					Drive_Motor(target_Vx, target_Wz * 1.13); // 逆运动解析--通过线速度和角速度得到两个轮子分别的速度

						//					Drive_Motor(target_Vx, target_Wz*2.5 );

						Drive_Motor(target_Vx, target_Wz * 1.5); //***********************************************************************************

						if (Robot_mode == 1) // 导航模式
						{
							if (Hand_to_Auto == 0)
							{

								PW1_up_down = 0; // PWM1的值清除

								PW2_left_right = 0; // PWM2的值清除

								PW3_baibi = 0; // PWM3的值清除

								Hand_to_Auto = 1;
							}

							//---将解析到的速度传给驱动器

							Car_Right_Speed = MOTOR_A.Speed; // 右电机

							Car_Left_Speed = -MOTOR_B.Speed; // 左电机
						}
					}

					RxState = 0; // 转换状态清空

					receivedCount = 0; // 接收大小清零

					receivedLength = 0; // 接收长度清零

					Receive_Finish = 1; // 接收完成标志

					send_bit = 1; // 发送标志

					memset(receivedPns, 0, sizeof(receivedPns)); // pns接收数据清理
				}
			}
		}
		HAL_UART_Receive_IT(&huart3, &receivedDate, 1);
	}
}


/**************************-MCU反馈消息-*******************************/

// 函数功能：---MCU反馈给PNS消息 -----
// 功能描述：给PNS反馈信息
// PNS
void Mcu_To_Pns()
{
	MOTOR_A.Encoder = Speed_Right / 6360.0; // 读取驱动器的转速r/min----转换为m/s

	MOTOR_B.Encoder = Speed_left / 6360.0; // 读取驱动器的转速r/min----转换为m/s

	float rounded_number_A = ((int)(MOTOR_A.Encoder * 100 + 0.5)) / 100.0; //-----将浮点数四舍五入，比如0.009，并且想将其舍入为0.01

	float rounded_number_B = ((int)(MOTOR_B.Encoder * 100 + 0.5)) / 100.0; //-----将浮点数四舍五入，比如0.009，并且想将其舍入为0.01

	Send_Data.Sensor_Str.X_speed = (((MOTOR_A.Encoder + MOTOR_B.Encoder) / 2) * 100); // 返回电机线速度

	Send_Data.Sensor_Str.Z_speed = (((MOTOR_A.Encoder - MOTOR_B.Encoder) / 0.42) * 100); // 返回电机角速度

	//	Send_Data.Sensor_Str.X_speed = (((rounded_number_A + rounded_number_B) / 2) * 100); // 返回电机线速度

	//  Send_Data.Sensor_Str.Z_speed = (((rounded_number_A - rounded_number_B ) / 0.42) * 100); // 返回电机角速度

	//  SVR = MOTOR_A.Encoder * 1000;   // motorA 右电机
	//
	//	SVR = SVR / 10;                 // motorA

	//  SVL = MOTOR_B.Encoder * 1000;   // motorB 左电机
	//
	//	SVL = SVL / 10;                 // motorB

	SVR = rounded_number_A * 100; // motorA 右电机

	SVL = rounded_number_B * 100; // motorB 左电机

	// 消除--在有角速度时，负数一边总是差-0.1
	if (target_Wz != 0)
	{
		if (SVR < 0)
		{
			SVR = SVR - 1;
		}

		else if (SVL < 0)
		{
			SVL = SVL - 1;
		}
	}

	sendPns[0] = 0xAA;

	sendPns[1] = 0xBB;

	sendPns[2] = 0xCC;

	sendPns[3] = 0x12;

	sendPns[4] = 0x11;

	sendPns[5] = 0x00;

	sendPns[6] = 0x00;

	sendPns[7] = 0x00;

	sendPns[8] = Send_Data.Sensor_Str.X_speed;

	sendPns[9] = Send_Data.Sensor_Str.X_speed >> 8; // 车速

	sendPns[10] = Send_Data.Sensor_Str.Z_speed;

	sendPns[11] = Send_Data.Sensor_Str.Z_speed >> 8; // 角速

	sendPns[12] = SVL;

	sendPns[13] = SVL >> 8; // 左轮线速度

	sendPns[14] = SVR;

	sendPns[15] = SVR >> 8; // 右轮线速度

	sendPns[16] = 0x00;

	sendPns[17] = 0x00;

	sendPns[18] = 0x00;

	sendPns[19] = 0x0A;

	sendPns[20] = SUM_Cal((unsigned char *)sendPns, 20);

	HAL_UART_Transmit_IT(&huart3, sendPns, 21); // 中断发送
}
