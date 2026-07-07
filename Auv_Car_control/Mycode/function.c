#include "function.h"

#include "pns.h"

extern Robot_Parament_InitTypeDef Robot_Parament; // 机器人硬件参数结构体

extern Moter_Parameter_InitTypeDef MOTOR_A, MOTOR_B; // 电机速度控制相关参数结构体

extern uint8_t Robot_mode; // 机器人模式  0 遥控  1 手动

/**************************---校验和值计算---********************************/
// 函数功能：---校验和值计算 -----
// 功能描述：PNS下发协议校验
// PNS
uint8_t SUM_Cal(uint8_t *pBuf, uint16_t nLen)
{
  uint8_t nSUM = 0;
  for (int i = 0; i < nLen; ++i)
  {
    nSUM += pBuf[i];
  }
  return nSUM;
}
/**************************---校验和值计算---********************************/

/**************************-----限幅函数-----********************************/
// 函数功能： ----- 限幅函数 -----
// 功能描述：电机限幅
// 电机
float target_limit_float(float insert, float low, float high)
{
  if (insert < low)
    return low;
  else if (insert > high)
    return high;
  else
    return insert;
}

int target_limit_int(int insert, int low, int high)
{
  if (insert < low)
    return low;
  else if (insert > high)
    return high;
  else
    return insert;
}
/**************************-----限幅函数-----********************************/

/**************************-----求绝对值-----********************************/
// 函数功能：浮点型数据计算绝对值
// 功能描述：电机限幅
// 电机
float float_abs(float insert)
{
  if (insert >= 0)
    return insert;
  else
    return -insert;
}
/**************************-----求绝对值-----********************************/

/**************************-----求绝对值-----********************************/
// 函数功能：求绝对值
// 入口参数：long int
// 返回  值：unsigned int
uint32_t myabs(long int a)
{
  uint32_t temp;
  if (a < 0)
    temp = -a;
  else
    temp = a;
  return temp;
}
/**************************-----求绝对值-----**************************/

/**************************-A-PID控制器-********************************/

// 函数功能：增量式PI控制器--A电机
// 入口参数：编码器测量值(实际速度)，目标速度
// 返回  值：电机PWM

int Incremental_PI_A(float Encoder, float Target)
{
  /*************************** 增量式PI ****************************************/
  static float Bias_A = 0, PwmA_A = 0, Last_bias_A = 0, PrevError_A = 0;

  if (Robot_mode == 0)
  {
    Bias_A = 0, PwmA_A = 0, Last_bias_A = 0, PrevError_A = 0;
  } // 在遥控模式下，对static变量进行清除

  Target = float_abs(Target);

  Encoder = float_abs(Encoder);

  Bias_A = Target - Encoder;

  PwmA_A += MOTOR_A.Velocity_KP * (Bias_A - Last_bias_A) + MOTOR_A.Velocity_KI * Bias_A + MOTOR_A.Velocity_KD * (Bias_A - 2 * Last_bias_A + PrevError_A);

  if (PwmA_A > 1000)
  {
    PwmA_A = 1000;
  } // 有没有必要限制

  if (PwmA_A < -1000)
  {
    PwmA_A = -1000;
  }

  PrevError_A = Last_bias_A;

  Last_bias_A = Bias_A;

  return PwmA_A;
}
/**************************-A-PID控制器-********************************/

/**************************-B-PID控制器-********************************/

// 函数功能：增量式PI控制器--B电机
// 入口参数：编码器测量值(实际速度)，目标速度
// 返回  值：电机PWM
int Incremental_PI_B(float Encoder, float Target)
{
  static float Bias_B = 0, PwmB_B = 0, Last_bias_B = 0, PrevError_B = 0;

  if (Robot_mode == 0)
  {
    Bias_B = 0;
    PwmB_B = 0;
    Last_bias_B = 0, PrevError_B = 0;
  } // 在遥控模式下，对static变量进行清除

  Target = float_abs(Target);

  Encoder = float_abs(Encoder);

  Bias_B = Target - Encoder;

  PwmB_B += MOTOR_B.Velocity_KP * (Bias_B - Last_bias_B) + MOTOR_B.Velocity_KI * Bias_B + MOTOR_B.Velocity_KD * (Bias_B - 2 * Last_bias_B + PrevError_B);

  if (PwmB_B > 1000)
  {
    PwmB_B = 1000;
  }

  if (PwmB_B < -1000)
  {
    PwmB_B = -1000;
  }

  PrevError_B = Last_bias_B;

  Last_bias_B = Bias_B;

  return PwmB_B;
}
/**************************-B-PID控制器-********************************/
