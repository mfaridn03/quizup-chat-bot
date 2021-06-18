import aiohttp
import asyncio

from modules import Message

BOT_ID = "2157631894639466452"

with open('web_session') as op:
    web_session = op.read()

headers = {  # Stolen from somewhere idk
    "Host": "www.quizup.com",
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Cookie": f"web_session={web_session}",
    "User-Agent": "UnityPlayer/2018.2.16f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
    "X-Unity-Version": "2018.2.16f1"
}


async def check_chat():
    url = "https://www.quizup.com/api/chat"

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()

    if not data or not data['conversations']:
        return None

    for conv in data['conversations']:
        _msg = Message(conv)
        if _msg.content.startswith('a!') and _msg.sender != BOT_ID and not _msg.read:
            return _msg
        else:
            return None


async def main_loop():
    while True:
        msg = await check_chat()

        if msg:
            # print(f"Message received from {msg.sender}")
            await msg.process_command()
            await msg.close()

        else:
            print(f"No messages yet")

        await asyncio.sleep(1)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_loop())
