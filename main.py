import telebot
import yt_dlp
import os

TOKEN = '7657271837:AAH0LnnjBED28pf_kILtguVDKShIN38m930'
bot = telebot.TeleBot(TOKEN)

MAX_SIZE = 50 * 1024 * 1024  # 50 MB

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "OK.ru video linkini yuboring (https://ok.ru/video/...).")

@bot.message_handler(func=lambda m: 'ok.ru/video/' in m.text)
def download_and_send(message):
    url = message.text
    bot.reply_to(message, "Video yuklanmoqda. Iltimos, kuting...")

    try:
        # Video yuklash
        ydl_opts = {
            'outtmpl': 'video.%(ext)s',
            'format': 'best[ext=mp4]/best'
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        file_size = os.path.getsize(filename)

        if file_size <= MAX_SIZE:
            # Fayl kichik bo‘lsa, to‘g‘ridan-to‘g‘ri yuboriladi
            with open(filename, 'rb') as f:
                bot.send_video(message.chat.id, f, caption="Mana video!")
        else:
            bot.send_message(message.chat.id, "Video 50MB dan katta. Kichik qismlarga bo‘linmoqda...")

            part_number = 1
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(MAX_SIZE)
                    if not chunk:
                        break
                    part_name = f'video_part_{part_number}.mp4'
                    with open(part_name, 'wb') as part_file:
                        part_file.write(chunk)

                    with open(part_name, 'rb') as video_part:
                        bot.send_video(message.chat.id, video_part, caption=f"Qism {part_number}")

                    os.remove(part_name)
                    part_number += 1

        os.remove(filename)

    except Exception as e:
        bot.reply_to(message, f"Xatolik yuz berdi: {str(e)}")

# Botni ishga tushirish
try:
    bot.infinity_polling()
except Exception as err:
    print('Botda xatolik:', err)