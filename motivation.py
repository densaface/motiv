import inspect
import os
import random
import time

from gtts import gTTS
from pydub import AudioSegment

# проще скопировать исполняемые файлы ffmpeg в папку Windows
# from pydub.utils import which
# ffmpeg_dir = "c:\\Users\\DEN\\Downloads\\ffmpeg-2022-01-13-git-c936c319bd-essentials_build\\bin"
# AudioSegment.converter = which("ffmpeg")
# AudioSegment.ffmpeg = ffmpeg_dir + "\\ffmpeg.exe"
# AudioSegment.ffprobe = ffmpeg_dir + "\\ffprobe.exe"
script_path = os.path.realpath(os.path.abspath(os.path.join(os.path.split(
    inspect.getfile(inspect.currentframe()))[0])))
script_path = script_path.replace("\\", "/")

file_name_motivation = "M:/Мой диск/Андркомп/my_motiv.txt"
file_name_export = "M:/Мой диск/Андркомп/my_motivation.mp3"
random_shift = True  # для рандомного помещения верхней части текста вниз, чтобы больше шансов
# равномерно слушать входящий текст
infinite_loop = False  # если требуется, то можно в бесконечном цикле каждые 4 часа получать новый мотивирующий файл

while True:
    with open(file_name_motivation) as f:  # , encoding='utf-8'
        motiv_text = f.read().splitlines()

    if random_shift:
        random_index = random.randint(0, len(motiv_text) - 1)
        motiv_text = motiv_text[random_index:] + motiv_text[:random_index]

    out_text = ''
    for ii in range(len(motiv_text)):
        motiv_text[ii] = motiv_text[ii].replace("==========", "")
        if motiv_text[ii][0: 3] == '[a=':
            probability = float(motiv_text[ii][3: motiv_text[ii].find(']')])
            if random.uniform(0.0, 1.0) > probability:
                motiv_text[ii] = ''
            else:
                motiv_text[ii] = motiv_text[ii][motiv_text[ii].find(']')+1:]
        out_text += motiv_text[ii] + ' '

    summ_mp3 = None
    while True:
        patt = '<silence msec="'
        fi1 = out_text.find(patt)
        if fi1 == -1:
            if out_text.strip():
                for _ in range(1000):
                    try:
                        myobj = gTTS(text=out_text, lang='ru', slow=False)
                        myobj.save('motiv_tmp.mp3')
                        sound1 = AudioSegment.from_file(script_path + '/motiv_tmp.mp3', format='mp3')
                        if summ_mp3:
                            summ_mp3 += sound1
                        else:
                            summ_mp3 = sound1
                        break
                    except Exception as e:
                        # обычно гугл говорит Too Many Requests (сработали временные лимиты), делаем паузу и повторяем
                        print("error for text", out_text, e)
                        time.sleep(10)
            break
        fi2 = out_text.find('"', fi1 + len(patt) + 1)
        duration_pause = int(out_text[fi1 + len(patt): fi2])
        txt_portion = out_text[0: fi1]
        out_text = out_text[out_text.find('>', fi1) + 1:]
        if txt_portion.strip():
            for _ in range(1000):
                try:
                    myobj = gTTS(text=txt_portion, lang='ru', slow=False)
                    myobj.save('motiv_tmp.mp3')
                    break
                except Exception as e:
                    # обычно гугл говорит Too Many Requests (сработали частотные лимиты), делаем паузу и повторяем
                    print("error for text", out_text, e)
                    time.sleep(10)
                    continue
        sound1 = AudioSegment.from_file(script_path + '/motiv_tmp.mp3', format='mp3')
        if summ_mp3:
            summ_mp3 += sound1
        else:
            summ_mp3 = sound1
        summ_mp3 += AudioSegment.silent(duration=duration_pause)
    summ_mp3.export(file_name_export, format="mp3")
    print(time.asctime(time.localtime()) + ": сохранен текст в mp3")
    if not infinite_loop:
        exit(0)
    time.sleep(3600 * 4)
