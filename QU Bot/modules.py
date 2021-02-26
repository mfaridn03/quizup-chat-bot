import aiohttp
import datetime
import uuid

from commands import commands

with open('web_session') as op:  # Can be implemented in a different way so i wont have to do this every for file
    web_session = op.read()  # I'm just lazy ugh

headers = {  # Stolen from somewhere idk
    "Host": "www.quizup.com",
    "Accept": "*/*",
    "Accept-Encoding": "identity",
    "Cookie": f"web_session={web_session}",
    "User-Agent": "UnityPlayer/2018.2.16f1 (UnityWebRequest/1.0, libcurl/7.52.0-DEV)",
    "X-Unity-Version": "2018.2.16f1"
}

send_headers = {  # Random android phone thing
    "Accept": "application/vnd.plainvanilla.quizup-v2.0.0+json",
    "Accept-Language": "en",
    "User-Agent": "SM-A908N QuizUp Android-7.1.2/4.1.4",
    "QuizUp-Client-Platform": "android",
    "QuizUp-Client-OS-Version": "7.1.2",
    "QuizUp-Client-Version": "4.1.4",
    "QuizUp-Client-App-ID": "com.quizup.core",
    "Quizup-Client-Device": "samsung SM-A908N",
    "Content-Type": "application/json; charset=UTF-8",
    "Host": "api-android20.quizup.com",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip",
    "Cookie": f"session={web_session}"
}


class Message(dict):
    def __init__(self, message):
        super().__init__()
        self.content: str = message['last_message']['text']
        self.sender: str = message['player']['id']
        self.read: bool = message['last_message']['read']

    def __repr__(self):
        return self

    def __bool__(self):
        return True

    async def process_command(self):
        command = self.content.split('a!')[1:]
        cmd_name = command[0].split(' ')[0].lower()  # Lmao
        sender = Sender(self.sender)
        print(self.sender, "triggered", cmd_name)

        if cmd_name == 'ping':
            await commands.command_ping(sender)

        elif cmd_name == 'mystats':
            await commands.my_stats(sender)

        elif cmd_name == 'topicstats':
            topic_slug = command[0].split(' ')[1].lower()
            await commands.my_topic_stats(sender, topic_slug)

    async def close(self):
        url = "https://www.quizup.com/api/chat/" + self.sender

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, headers=headers) as resp:
                return resp.status


class Sender(str):
    def __init__(self, user_id):
        self.uid = user_id
        super().__init__()

    async def send(self, msg: str):
        now = str(datetime.datetime.now()).replace(' ', 'T')
        url = "https://api-android20.quizup.com/chat/store"
        content = {
            "messages": [
                {
                    "event_name": "CHAT_MESSAGE",
                    "created": now,
                    "text": msg,
                    "type": "message",
                    "from_player": "2157631894639466452",
                    "to_player": self.uid,
                    "message_id": str(uuid.uuid4())
                }
            ],
            "is_live_chat": False
        }

        async with aiohttp.ClientSession() as ses:
            async with ses.post(
                url,
                json=content,
                headers=send_headers
            ) as resp:
                return await resp.text()  # doesn't need to return anything, this is only for debug
