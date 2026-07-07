#include "control.h"
#include "tim.h"
#include "usart.h"
#include "MBcrc.h"

// 左电机参数
uint8_t send_485_Left[10] = {0x01, 0x06, 0x00, 0x40, 0x02, 0x12, 0x09, 0x73};     // 发送485消息包-----速度控制   地址  +   功能码   +寄存器   +   速度   + CRC 校验   530转
unsigned short send_485_1_Left[9];											      //  校验转换数组

// 右电机参数
uint8_t send_485_2_Right[10] = {0x01, 0x06, 0x00, 0x40, 0x02, 0x12, 0x09, 0x73};  // 发送485消息包-----速度控制   地址  +   功能码   +寄存器   +   速度   + CRC 校验   530转
unsigned short send_485_1_2_Right[9];											  //  校验转换数组

// 摆臂电机参数
uint8_t send_485_7_Baibi[10] = {0x01, 0x06, 0x00, 0x40, 0x02, 0x12, 0x09, 0x73};  // 发送485消息包-----速度控制   地址  +   功能码   +寄存器   +   速度   + CRC 校验   530转
unsigned short send_485_1_7_Baibi[9];											  //  校验转换数组

uint8_t SHifang[] = {0x01, 0x06, 0x00, 0x44, 0x00, 0x01, 0x08, 0x1F};             //  急停释放

uint8_t Zisuo[] = {0x01,0x06, 0x00, 0x42, 0x03, 0xE7, 0x69, 0x64};                //  自锁

uint8_t read_485_Left_and_right[8] = {0x01, 0x03, 0x00, 0x1e, 0x00, 0x02, 0xA4, 0x0D}; //  发送485消息包----只读取转速

uint8_t receive_485_Left[MAX_RXD_LEN];  // 左电机接收485消息包--速度消息包

uint8_t receive_485_Right[MAX_RXD_LEN]; // 右电机接收485消息包--速度消息包

uint8_t key; // 串口接收标志

/***********************************************串口六+左电机*********************************************/

void PNS_to6_mcu_Left(int Send_speed_Left)
{
	unsigned char crch = 0;

	unsigned char crcl = 0;

	int SEND_SAVE = Send_speed_Left;

	//-------------------------------------校验数组------------------------------------//

	send_485_1_Left[0] = 0x01; // 获取高位

	send_485_1_Left[1] = 0x06; // 获取低位

	send_485_1_Left[2] = 0x00; // 获取高位

	send_485_1_Left[3] = 0x40; // 获取低位

	send_485_1_Left[4] = (Send_speed_Left >> 8) & 0xFF; // 获取高位

	send_485_1_Left[5] = Send_speed_Left & 0xFF; // 获取低位

	unsigned short crc = CRC16(send_485_1_Left, 6);

	crch = crc >> 8;

	crcl = crc & 0xff;

	if (Send_speed_Left != 0) // 速度不为0时 正常控制速度
	{
		//-------------------------------------发送数组------------------------------------//
		send_485_1_Left[6] = crcl;

		send_485_1_Left[7] = crch;

		send_485_Left[0] = 0x01; // 获取高位

		send_485_Left[1] = 0x06; // 获取低位

		send_485_Left[2] = 0x00; // 获取高位

		send_485_Left[3] = 0x40; // 获取低位

		send_485_Left[4] = (SEND_SAVE >> 8) & 0xFF; // 获取高位

		send_485_Left[5] = SEND_SAVE & 0xFF; // 获取低位

		send_485_Left[6] = crcl;

		send_485_Left[7] = crch;
	}
	else // 速度为0时 自锁
	{

//释放
		send_485_Left[0] = 0x01; // 获取高位

		send_485_Left[1] = 0x06; // 获取低位

		send_485_Left[2] = 0x00; // 获取高位

		send_485_Left[3] = 0x44; // 获取低位

		send_485_Left[4] = 0x00; // 获取高位

		send_485_Left[5] = 0x01; // 获取低位

		send_485_Left[6] = 0x08;

		send_485_Left[7] = 0x1F;
		
		
//    自锁
//		send_485_Left[0] = 0x01; // 获取高位

//		send_485_Left[1] = 0x06; // 获取低位

//		send_485_Left[2] = 0x00; // 获取高位

//		send_485_Left[3] = 0x42; // 获取低位

//		send_485_Left[4] = 0x03; // 获取高位

//		send_485_Left[5] = 0xE7; // 获取低位

//		send_485_Left[6] = 0x69;

//		send_485_Left[7] = 0x64;
	}
}


/***********************************************串口二+右电机*********************************************/
void PNS_to2_mcu_Right(int Send_speed_2_Right)
{
	unsigned char crch = 0;

	unsigned char crcl = 0;

	int SEND_SAVE_4 = Send_speed_2_Right;

	//-------------------------------------校验数组------------------------------------//

	send_485_1_2_Right[0] = 0x01; // 获取高位

	send_485_1_2_Right[1] = 0x06; // 获取低位

	send_485_1_2_Right[2] = 0x00; // 获取高位

	send_485_1_2_Right[3] = 0x40; // 获取低位

	send_485_1_2_Right[4] = (Send_speed_2_Right >> 8) & 0xFF; // 获取高位

	send_485_1_2_Right[5] = Send_speed_2_Right & 0xFF; // 获取低位

	unsigned short crc = CRC16(send_485_1_2_Right, 6);

	crch = crc >> 8;

	crcl = crc & 0xff;
	//-------------------------------------发送数组------------------------------------//
	if (Send_speed_2_Right != 0)
	{
		send_485_1_2_Right[6] = crcl;

		send_485_1_2_Right[7] = crch;

		send_485_2_Right[0] = 0x01; // 获取高位

		send_485_2_Right[1] = 0x06; // 获取低位

		send_485_2_Right[2] = 0x00; // 获取高位

		send_485_2_Right[3] = 0x40; // 获取低位

		send_485_2_Right[4] = (SEND_SAVE_4 >> 8) & 0xFF; // 获取高位

		send_485_2_Right[5] = SEND_SAVE_4 & 0xFF; // 获取低位

		send_485_2_Right[6] = crcl;

		send_485_2_Right[7] = crch;
	}

	else
	{
		
//  释放
		
		send_485_2_Right[0] = 0x01; // 获取高位

		send_485_2_Right[1] = 0x06; // 获取低位

		send_485_2_Right[2] = 0x00; // 获取高位

		send_485_2_Right[3] = 0x44; // 获取低位

		send_485_2_Right[4] = 0x00; // 获取高位

		send_485_2_Right[5] = 0x01; // 获取低位

		send_485_2_Right[6] = 0x08;

		send_485_2_Right[7] = 0x1F;

		
		
//    自锁

//		send_485_2_Right[0] = 0x01; // 获取高位

//		send_485_2_Right[1] = 0x06; // 获取低位

//		send_485_2_Right[2] = 0x00; // 获取高位

//		send_485_2_Right[3] = 0x42; // 获取低位

//		send_485_2_Right[4] = 0x03; // 获取高位

//		send_485_2_Right[5] = 0xE7; // 获取低位

//		send_485_2_Right[6] = 0x69;

//		send_485_2_Right[7] = 0x64;
	}
}



/***********************************************串口七+摆臂电机*********************************************/
void PNS_to7_mcu_Baibi(int Send_speed_7_Baibi)
{
	unsigned char crch = 0;

	unsigned char crcl = 0;

	int SEND_SAVE = Send_speed_7_Baibi;

	//-------------------------------------校验数组------------------------------------//

	send_485_1_7_Baibi[0] = 0x01; // 获取高位

	send_485_1_7_Baibi[1] = 0x06; // 获取低位

	send_485_1_7_Baibi[2] = 0x00; // 获取高位

	send_485_1_7_Baibi[3] = 0x40; // 获取低位

	send_485_1_7_Baibi[4] = (Send_speed_7_Baibi >> 8) & 0xFF; // 获取高位

	send_485_1_7_Baibi[5] = Send_speed_7_Baibi & 0xFF; // 获取低位

	unsigned short crc = CRC16(send_485_1_7_Baibi, 6);

	crch = crc >> 8;

	crcl = crc & 0xff;

	if (Send_speed_7_Baibi != 0)
	{
		//-------------------------------------发送数组------------------------------------//
		send_485_1_7_Baibi[6] = crcl;

		send_485_1_7_Baibi[7] = crch;

		send_485_7_Baibi[0] = 0x01; // 获取高位

		send_485_7_Baibi[1] = 0x06; // 获取低位

		send_485_7_Baibi[2] = 0x00; // 获取高位

		send_485_7_Baibi[3] = 0x40; // 获取低位

		send_485_7_Baibi[4] = (SEND_SAVE >> 8) & 0xFF; // 获取高位

		send_485_7_Baibi[5] = SEND_SAVE & 0xFF; // 获取低位

		send_485_7_Baibi[6] = crcl;

		send_485_7_Baibi[7] = crch;
	}
	else
	{
		// 自锁---摆臂电机必须自锁才能够实现不被主动轮带动
		send_485_7_Baibi[0] = 0x01; // 获取高位

		send_485_7_Baibi[1] = 0x06; // 获取低位

		send_485_7_Baibi[2] = 0x00; // 获取高位

		send_485_7_Baibi[3] = 0x42; // 获取低位

		send_485_7_Baibi[4] = 0x03; // 获取高位

		send_485_7_Baibi[5] = 0xE7; // 获取低位

		send_485_7_Baibi[6] = 0x69;

		send_485_7_Baibi[7] = 0x64;
	}
}

void read6_left_Speed(void)
{
	RS485_Send_Data_6(read_485_Left_and_right, 8); // 发送8个字节

	HAL_Delay(20); // 等待中断接受完成

	RS485_Receive_Data_6(receive_485_Left, &key);

	HAL_Delay(20); // 等待中断接受完成
}

void USART6_read_Date(void) // 读取速度控制
{
	RS485_Send_Data_6(send_485_Left, 8); // 发送8个字节
}

void USART4_read_Date(void) // 读取速度控制
{
	RS485_Send_Data(send_485_2_Right, 8); // 发送8个字节
}

void USART7_read_Date(void) // 读取速度控制
{
	RS485_Send_Data_7(send_485_7_Baibi, 8); // 发送8个字节
}

void read4_right_Speed(void)
{
	RS485_Send_Data(read_485_Left_and_right, 8); // 发送8个字节

	HAL_Delay(20); // 等待中断接受完成

	RS485_Receive_Data(receive_485_Right, &key);

	HAL_Delay(20); // 等待中断接受完成
}

void Send_four_and_six(int Car_Right_Speed, int Car_Left_Speed, int Car_Baibi_Speed)
{
	PNS_to2_mcu_Right(Car_Right_Speed); // 给右电机发送速度指令

	PNS_to6_mcu_Left(Car_Left_Speed); // 给左电机发送速度指令

	PNS_to7_mcu_Baibi(Car_Baibi_Speed); // 给摆臂电机发送速度指令

	USART4_read_Date(); // 速度指令应答

	USART6_read_Date(); // 速度指令应答

	USART7_read_Date(); // 速度指令应答

	HAL_Delay(15); // 等待中断接受完成
}

void Read_left_and_right()
{
	RS485_Send_Data(read_485_Left_and_right, 8); // 发送8个字节

	RS485_Send_Data_6(read_485_Left_and_right, 8); // 发送8个字节

	HAL_Delay(5); // 等待中断接受完成

	RS485_Receive_Data(receive_485_Right, &key);

	HAL_Delay(9); // 等待中断接受完成

	RS485_Receive_Data_6(receive_485_Left, &key);

	HAL_Delay(9); // 等待中断接受完成
}

/***********************************************MODBUS--CRC校验*********************************************/
int modbus_handle(uint8_t *buf, unsigned char len)
{
	int Speed;

	unsigned short crc;

	unsigned char crch, crcl;

	if (buf[0] != 0x01) // 校验位置
	{
		return 0;
	}

	if (buf[1] != 0x03) // 校验功能码
	{
		return 0;
	}

	else if (buf[0] == 0x01 && buf[1] == 0x03)
	{
		crc = CRC16((unsigned short *)buf, len);

		crch = crc >> 8;

		crcl = crc & 0xff;

		if (buf[len - 2] == crcl || buf[len - 1] == crch) // 校验CRC
		{
			return 0;
		}
		else
		{
			Speed = (int)(buf[5] << 8) + buf[6];
		}
	}
	return Speed;
}































