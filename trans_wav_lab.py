import os
import argparse
import librosa
import numpy as np
from multiprocessing import Pool, cpu_count

import soundfile
from tqdm import tqdm
from config import config

global speaker_annos
speaker_annos = []

def process(item):  
    spkdir, wav_name, args = item
    speaker = spkdir.replace("\\", "/").split("/")[-1]
    wav_path = os.path.join(args.in_dir, speaker, wav_name)
    if os.path.exists(wav_path) and '.wav' in wav_path:
        os.makedirs(os.path.join(args.out_dir, speaker), exist_ok=True)
        wav, sr = librosa.load(wav_path, sr=args.sr)
        soundfile.write(
            os.path.join(args.out_dir, speaker, wav_name),
            wav,
            sr
        )

def process_text(item):
    spkdir, wav_name, args,lang = item
    speaker = os.path.split(spkdir)[-1]
    global speaker_annos
    tr_name = wav_name[:-4]
    with open(args.in_dir+'/'+speaker+'/'+tr_name+'.lab', "r", encoding="utf-8") as file:
             text = file.read()
    text = text.replace("{NICKNAME}",'开拓者')
    text = text.replace("{M#他}{F#她}",'他')
    text = text.replace("{F#她}{M#他}","他")
    text = text.replace("{F#她们}{M#他们}","他们")
    text = text.replace("|",'')
    substring = "{M#妹妹}{F#哥哥}" 
    if substring in text:
        if tr_name.endswith("f"):
           text = text.replace("{M#妹妹}{F#哥哥}",'妹妹')
        if tr_name.endswith("m"):
           text = text.replace("{M#妹妹}{F#哥哥}",'哥哥')
    text = text.replace("#",'')   
    text = f'{lang}|{text}\n' #
    speaker_annos.append(args.out_dir+'/'+speaker+'/'+wav_name+ "|" + speaker + "|" + text)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sr", type=int, default=44100, help="sampling rate")
    parser.add_argument("--in_dir", type=str, default=config.resample_config.in_dir, help="path to source dir")
    parser.add_argument("--out_dir", type=str, default=config.resample_config.out_dir, help="path to target dir")
    parent_dir=config.resample_config.in_dir

    print(f"Parent directory: {parent_dir}")

    speaker_names = list(os.walk(parent_dir))[0][1]   
    args = parser.parse_args()
   
    lang='ZH'
    processs = cpu_count()-2 if cpu_count() >4 else 1
    pool = Pool(processes=processs)

    for speaker in os.listdir(args.in_dir):
        spk_dir = os.path.join(args.in_dir, speaker)
        if os.path.isdir(spk_dir):
            print(spk_dir)
            for _ in tqdm(pool.imap_unordered(process, [(spk_dir, i, args) for i in os.listdir(spk_dir) if i.endswith("wav")])):
                pass
            for i in os.listdir(spk_dir):
               if i.endswith("wav"):
                  pro=(spk_dir, i, args, lang)
                  process_text(pro)
    if len(speaker_annos) == 0:
        print("transcribe error. len(speaker_annos) == 0")
    else:
      with open(config.preprocess_text_config.transcription_path, 'w', encoding='utf-8') as f:
        for line in speaker_annos:
            f.write(line)
      print("finished.")
