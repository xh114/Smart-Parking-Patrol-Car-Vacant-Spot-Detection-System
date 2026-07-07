#include "parements.h"

#include "control.h"

#include "pns.h"

extern Robot_Parament_InitTypeDef Robot_Parament; // 机器人硬件参数结构体

extern Moter_Parameter_InitTypeDef MOTOR_A, MOTOR_B; // 电机速度控制相关参数结构体

//  机器人参数初始化
void Robot_Parament_Init()
{
	/*机器人参数*/
	Robot_Parament.GearRatio = 53; // 电机减速比	N

	//  Robot_Parament.Wheel_R = 0.088; // 轮子半径	R

	Robot_Parament.Wheel_R = 0.085; // 轮子半径	R   SHD 修改

	Robot_Parament.EncoderLine = 2048; // 编码器线数量 P   --本身编码器是512线的

	//  Robot_Parament.Wheel_spacing = 0.36; // 轮轴距		D

	Robot_Parament.Wheel_spacing = 0.50; // 轴距		D   SHD 修改
}

void Pid_Parament_Init(void)
{
	/*----------低速控制PID-----------------*/

	//  MOTOR_A.Velocity_KP = 1.5;

	//  MOTOR_A.Velocity_KI = 210;

	//  MOTOR_A.Velocity_KD = 155;

	MOTOR_A.Velocity_KP = 3.5; // 2.05 --3.5  --3.6 后期偏右  --4  稍早偏右  --3 稍早偏右

	MOTOR_A.Velocity_KI = 15; // 5--4.75偏右--4.65后期偏左 --4.70  5m后偏左  --4.72 5.5m后偏左 --4.73 稍早偏右 --4.725稍早缓慢偏右

	MOTOR_A.Velocity_KD = 1.5;
	/*----------低速控制PID-----------------*/

	/*----------高速控制PID-----------------*/
	MOTOR_B.Velocity_KP = 0.6;

	MOTOR_B.Velocity_KI = 20;

	MOTOR_B.Velocity_KD = 10;
	/*----------高速控制PID-----------------*/
}
