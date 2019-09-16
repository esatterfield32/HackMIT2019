from ibm_watson import TextToSpeechV1

text_to_speech = TextToSpeechV1(
    iam_apikey='ymx55yTkswRY-eHpv1xAl_eainG1sTaj7P2N0f9Y_eqI',
    url='https://stream.watsonplatform.net/text-to-speech/api'
    
)
text_to_speech.disable_SSL_verification()
def getAudio(word):
    with open('newpronunciation.wav', 'wb') as audio_file:
        audio_file.write(
            text_to_speech.synthesize(
                word,
                voice='en-US_AllisonVoice',
                accept='audio/wav'        
            ).get_result().content)
