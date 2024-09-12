import os
import discord
import asyncio
import yfinance as yf

from datetime import datetime, time, timedelta

from myserver import server_on

# ตั้งค่า token ของบอทที่นี่
CHANNEL_ID = '1281951649845477418'  # ID ของ channel ที่จะให้บอทส่งข้อความ

client = discord.Client()

# ฟังก์ชันคำนวณเวลาที่เหลือก่อนถึงช่วงเวลาที่ต้องการส่งข้อมูล
def time_until_next_target(target_time):
    now = datetime.now()
    target = now.replace(hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0)
    
    if now > target:
        target = target.replace(day=now.day + 1)  # ถ้าเวลาปัจจุบันเกินเป้าหมาย ให้เลื่อนไปส่งวันถัดไป
    return (target - now).total_seconds()

async def send_exchange_rate():
    await client.wait_until_ready()
    channel = client.get_channel(int(CHANNEL_ID))
    times_to_send = [time(hour=h, minute=m) for h in range(0, 24) for m in range(0, 60, 1)]  # กำหนดเวลาที่จะส่ง

    while not client.is_closed():
        now = datetime.now().time()

        # ตรวจสอบว่าเวลาปัจจุบันตรงกับหนึ่งในเวลาที่ต้องการส่งหรือไม่
        for target_time in times_to_send:
            if now >= target_time and now < (datetime.combine(datetime.today(), target_time) + timedelta(minutes=1)).time():
                try:
                    # ดึงข้อมูลจาก yfinance สำหรับค่าเงิน USD/THB
                    data = yf.download('USDTHB=X', period='1d', interval='1m')
                    last_rate = data['Close'][-1]  # ดึงค่าล่าสุด
                    
                    # ดึงวันที่และเวลาปัจจุบัน
                    days_of_week = {
                    'Monday': 'วันจันทร์',
                    'Tuesday': 'วันอังคาร',
                    'Wednesday': 'วันพุธ',
                    'Thursday': 'วันพฤหัสบดี',
                    'Friday': 'วันศุกร์',
                    'Saturday': 'วันเสาร์',
                    'Sunday': 'วันอาทิตย์'
                    }
                    now = datetime.now()
                    day_of_week_eng = now.strftime('%A')
                    day_of_week_th = days_of_week.get(day_of_week_eng, day_of_week_eng)

                    now_str = datetime.now().strftime('%d:%m:%y')
                    now_ste = datetime.now().strftime('%H:%M:%S')
                    last_m = f"{last_rate:.4f}"
                    # ส่งข้อความพร้อมการตกแต่ง
                    message = (
                                f">>> ```css"
                                f"\n*{'-'*33}*"
                                f"\n{'★    ค่าเงิน Bath/USD    ★'.center(33)}"
                                f"\n*{'-'*33}*"
                                f"\n{'⏰เวลา'.center(32)}"
                                f"\n{day_of_week_th.center(37)}"
                                f"\n{now_str.center(33)}"
                                f"\n{now_ste.center(33)}"
                                f"\n{'💵 อัตรา'.center(33)}"
                                f"\n{last_m.center(33)}"
                                f"\n{'บาท/USD'.center(33)}"
                                f"\n*{'-'*33}*"
                                f"\n```"
                            )

                    await channel.send(message)
                except Exception as e:
                    await channel.send(f"เกิดข้อผิดพลาดในการดึงข้อมูลค่าเงิน: {str(e)}")

        # รอจนถึงเวลาถัดไปที่กำหนด
        next_target_time = min(times_to_send, key=lambda t: time_until_next_target(t))
        sleep_duration = time_until_next_target(next_target_time)
        await asyncio.sleep(sleep_duration)

@client.event
async def on_ready():
    print(f'บอท {client.user} เข้าสู่ระบบแล้ว!')

    client.loop.create_task(send_exchange_rate())

    server_on()

client.run(os.getenv('TOKEN'))