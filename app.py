from flask import Flask, escape, request, render_template
import string
import json
import pictureFinder
import bingImageSearch


class WrongWord(Exception):
    pass
class DoneStreaming(Exception):
    pass
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':  #this block is only entered when the form is submitted
        originalInput = request.form['userInput']
        userInput = originalInput.translate(str.maketrans("","", string.punctuation)).lower()
        userInput = userInput.split(' ')
        # Sampling rate of your microphone and desired chunk size
        rate = 44100
        chunk = int(rate/10)

        # Insert your access token here
        access_token = "02RwwjqE2Tvzhs6EzGJlGqrpj71gT6SfeEKLGYi-LuZ1inGQsTOAOob1OYjly5ShYrunkVAfk3EHKMI3gFtFt1WvlrH1k"

        # Creates a media config with the settings set for a raw microphone input
        example_mc = MediaConfig('audio/x-raw', 'interleaved', 44100, 'S16LE', 1)

        streamclient = RevAiStreamingClient(access_token, example_mc)

        # Opens microphone input. The input will stop after a keyboard interrupt.
        with MicrophoneStream(rate, chunk) as stream:
            # Uses try method to allow users to manually close the stream
            try:
                # Starts the server connection and thread sending microphone audio
                response_gen = streamclient.start(stream.generator())

                curr_response = None
                # Iterates through responses and prints them
                textFromSpeech = []
                for response in response_gen:
                    response = json.loads(response)
                    if response["type"] == "final":
                        for elt in response["elements"]:
                            val = elt["value"].lower()
                            if (val != ' ' and val != '.' and val != ',' and val != '?' and val!='!'):
                                textFromSpeech.append(val)
                                if val != userInput[len(textFromSpeech)-1]:
                                    print("lol2")
                                    raise WrongWord 
                            print(textFromSpeech)
                            print(userInput)
                    if len(textFromSpeech) >= len(userInput):
                        print("lol")
                        raise DoneStreaming    
            except DoneStreaming:
                return render_template('correct.html')
                # Ends the websocket connection.
                streamclient.client.send("EOS")
                pass
            except WrongWord:
                wrongText = textFromSpeech
                wrongWord = wrongText[-1]
                rightText = userInput
                wordImage = bingImageSearch.findImage(wrongWord)
                return render_template('wrong.html', wrongText = wrongText, rightText = rightText, wrongWord = wrongWord, wordImage = wordImage)
                # Ends the websocket connection.
                streamclient.client.send("EOS")
                pass
    #if startMicrophone == True:

    return render_template('index.html', hasInput = False)



"""Copyright 2019 Google, Modified by REV 2019

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pyaudio
import json
from rev_ai.models import MediaConfig
from rev_ai.streamingclient import RevAiStreamingClient
from six.moves import queue


class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


if __name__ == '__main__':
    app.run(debug=True)