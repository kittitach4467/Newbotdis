import requests
import discord
import asyncio
from datetime import datetime, timezone, timedelta


# ตั้งค่าท็อกเคนและ Channel ID ของ Discord
DISCORD_TOKEN = ""
CHANNEL_ID =   # ใส่ Channel ID ที่ต้องการส่งข้อความ

# ฟังก์ชันดึงอัตราแลกเปลี่ยนจาก API
def get_exchange_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()
    return data["rates"].get("THB", "ไม่พบข้อมูล")

# ฟังก์ชันส่งข้อความไปยัง Discord
async def send_message():
    client = discord.Client(intents=discord.Intents.default())
    
    @client.event
    async def on_ready():
        channel = client.get_channel(CHANNEL_ID)
        if channel:
            rate = get_exchange_rate()
            thai_time = datetime.now(timezone.utc) + timedelta(hours=7)
            weekdays = ["จันทร์", "อังคาร", "พุธ", "พฤหัสบดี", "ศุกร์", "เสาร์", "อาทิตย์"]
            weekday_thai = weekdays[thai_time.weekday()]
            message = (
                "```diff\n"
                "*------------------------------------*\n"
                "ค่าเงิน Bath/USD\n"
                "*------------------------------------*\n"
                "เวลา\n"
                f"{weekday_thai} \n"
                f"{thai_time.strftime('%H:%M:%S')}\n"
                "อัตรา\n"
                f"{rate}\n"
                "บาท/USD\n"
                "*------------------------------------*"
                "```"
            )
            await channel.send(message)
        await client.close()
    
    await client.start(DISCORD_TOKEN)

# รันฟังก์ชัน
asyncio.run(send_message())
