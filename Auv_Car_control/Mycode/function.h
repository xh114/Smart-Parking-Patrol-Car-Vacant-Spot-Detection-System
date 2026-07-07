#ifndef __FUNCTION_H__
#define __FUNCTION_H__

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "function.h"
#include "main.h"
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include <string.h>
/* USER CODE END Includes */

/* USER CODE BEGIN Private defines */

	
	
/* USER CODE END Private defines */



/* USER CODE BEGIN Prototypes */
extern uint8_t SUM_Cal(uint8_t *pBuf, uint16_t nLen);
extern float target_limit_float(float insert, float low, float high);
extern int target_limit_int(int insert, int low, int high);
extern float float_abs(float insert);	
extern uint32_t myabs(long int a);
extern int Incremental_PI_A(float Encoder, float Target);
extern int Incremental_PI_B(float Encoder, float Target);
/* USER CODE END Prototypes */

#ifdef __cplusplus
}
#endif
#endif /*__ __FUNCTION_H__ */
