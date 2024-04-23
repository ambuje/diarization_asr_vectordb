from pyannote.audio import Pipeline
import torch
import torchaudio
from pyannote.audio.pipelines.utils.hook import ProgressHook
from utils import group_,combine_timestamp,split_overlap,millisec,break_string_near_k_words
import re
import whisper
from pydub import AudioSegment
import numpy as np
import pandas as pd
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

def final_speaker_end_start(groups):
    asr_info=[]
    for g in groups:
        start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
        start = millisec(start) #- spacermilli
        end = millisec(end)
        speaker = g[0].split()[-1]
        asr_info.append((str(speaker),start,end))
    combine_time_stamp_asr=combine_timestamp(asr_info)
    asr_overlap_list=split_overlap(combine_time_stamp_asr)
    return asr_overlap_list

def diarization_asr_output(audio_path):
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1",use_auth_token="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")
    pipeline.to(torch.device("cuda"))
    waveform, sample_rate = torchaudio.load(audio_path)
    with ProgressHook() as hook:
        diarization = pipeline({"waveform": waveform, "sample_rate": sample_rate},hook=hook)
    with open("diarization.txt", "w") as text_file:
        text_file.write(str(diarization))
    print('Diarization file saved')
    groups=group_()
    asr_overlap_list=final_speaker_end_start(groups)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = whisper.load_model('large', device = device)
    r_t=[]
    audio = AudioSegment.from_wav(audio_path)
    speak=[]
    cnt=1
    for i in asr_overlap_list:
        result = model.transcribe(np.frombuffer(audio[i[1]:i[2]].raw_data, np.int16).flatten().astype(np.float32) / 32768.0, language='en', word_timestamps=True)
        r_t.append(result['text'])
        speak.append(i[0])
        print('Audio file processed ',cnt,'/',len(asr_overlap_list))
        cnt=cnt+1
    text=[]
    f_speaker=[]
    for i in range(0,len(r_t)):
        tmp=break_string_near_k_words(r_t[i],200)
        f_speaker.extend([speak[i]]*len(tmp))
        text.extend(tmp)
    df=pd.DataFrame({'Channel Information':f_speaker,'text':text})
    return df
    