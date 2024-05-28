# 1. 구글 stt가 5초 이하의 음성 파일은 인식하지 못함.
#    -> 인코딩 형식을 mp3로 바꾸니 짧은 파일도 잘 인식함
# 2. 숫자 세는 건 잘 인식되는데 '119'는 인식못함

from google.cloud import speech
from google.cloud import texttospeech
import openai
import os


class VoiceChat:
    def __init__(self, stt_key_path, tts_key_path, openai_api_key):
        self.stt_client = speech.SpeechClient.from_service_account_file(stt_key_path)
        self.tts_client = texttospeech.TextToSpeechClient.from_service_account_file(tts_key_path)
        self.api_key = openai_api_key
        openai.api_key = self.api_key

    def speechToText(self, file_name):
        with open(file_name, 'rb') as f:
            voice_data = f.read()

        audio_file = speech.RecognitionAudio(content=voice_data)
        config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.MP3,  #speech.RecognitionConfig.AudioEncoding.LINEAR16(PCM 형식)
                sample_rate_hertz=16000,
                language_code="ko-KR"
        )

        response = self.stt_client.recognize(config=config, audio=audio_file)
        return response.results[0].alternatives[0].transcript

    def getGptResponse(self, user_input):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            prompt=user_input,
            max_tokens=150
        )

        return response.choices[0].text.strip()

    def textToSpeech(self, text):
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name='ko-KR-Standard-B'
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            #effects_profile_id=['phone-class-device'],  # 오디오 프로파일
            speaking_rate=1.3,  # 발화속도
            pitch=1
        )
        response = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        with open("output.mp3", "wb") as output:
            output.write(response.audio_content)
            print("Audio content written to file")

        return "output.mp3"



if __name__ == "__main__":
    stt_key_path = 'stt_key.json'
    tts_key_path = 'tts_key.json'
    openai_api_key = os.getenv("OPENAI_API_KEY")

    voicechat = VoiceChat(stt_key_path, tts_key_path, openai_api_key)

    text = '괜찮으세요? 119를 부를까요?'
    text2 = '알겠습니다. 119를 부르지 않고 엄마한테 전화합니다.'
    voicechat.textToSpeech(text2)
    # file_name = "voicetestData/stttest1.mp3"
    # result = voicechat.speechToText(file_name)
    # print(result)

