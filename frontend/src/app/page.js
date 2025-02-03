'use client';

import { useState, useEffect } from 'react';
import { ArrowUpIcon, MicrophoneIcon } from '@heroicons/react/24/solid';

export default function ChatPage() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isThinking, setIsThinking] = useState(false);
  const [inputPosition, setInputPosition] = useState("center");
  const [thinkingText, setThinkingText] = useState("Thinking");
  const [streamingText, setStreamingText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);

  useEffect(() => {
    let interval;
    if (isThinking) {
      let dots = 0;
      interval = setInterval(() => {
        dots = (dots + 1) % 4;
        setThinkingText("Thinking" + ".".repeat(dots));
      }, 500);
    } else {
      setThinkingText("");
    }
    return () => clearInterval(interval);
  }, [isThinking]);

  const simulateStreaming = (text) => {
    setIsStreaming(true);
    let index = 0;
    setStreamingText("");
    
    const streamInterval = setInterval(() => {
      if (index < text.length) {
        setStreamingText((prev) => prev + text.charAt(index));
        index++;
      } else {
        clearInterval(streamInterval);
        setIsStreaming(false);
        setMessages(prev => [...prev, { sender: 'bot', text }]);
        setStreamingText("");
      }
    }, 10); // Adjust speed as needed
  };

  // Updated handleKeyDown function to query API instead of using a hardcoded response
  const handleKeyDown = async (e) => {
    if (e.key === "Enter" && inputValue.trim() !== "") {
      const userMessage = { sender: 'user', text: inputValue.trim() };
      setMessages(prev => [...prev, userMessage]);
      setInputValue("");

      if (inputPosition === 'center') {
        setInputPosition('bottom');
      }

      setIsThinking(true);
      try {
        const response = await fetch('http://127.0.0.1:8000/api/query', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: userMessage.text })
        });
        const data = await response.json();
        setIsThinking(false);
        // Assuming the API returns an object with a 'response' key containing the text
        simulateStreaming(data.response);
      } catch (error) {
        console.error('Error querying API:', error);
        setIsThinking(false);
        simulateStreaming("An error occurred while fetching response.");
      }
    }
  };

  // Updated uploadAudio function to generate an mp3 file
  const uploadAudio = async (chunks) => {
    try {
      // Changed blob type to 'audio/mp3'
      const blob = new Blob(chunks, { type: 'audio/mp3' });
      const formData = new FormData();
      // Changed filename from 'recording.mp4' to 'recording.mp3'
      formData.append('file', blob, 'recording.mp3');
      
      const response = await fetch('http://127.0.0.1:8000/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Convert the audio_content (base64) back to audio and play it
      const audioBlob = new Blob(
        [Uint8Array.from(atob(data.audio_content), c => c.charCodeAt(0))],
        { type: 'audio/mp3' }
      );
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      
      return data;
    } catch (error) {
      console.error('Error uploading file:', error);
      throw error;
    }
  };

  // Updated startRecording function to use uploadAudio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];
      
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = async () => {
        try {
          const data = await uploadAudio(chunks);
          // Move input to bottom after voice input
          if (inputPosition === 'center') setInputPosition('bottom');
          // Add the question from audio input as a user message.
          setMessages(prev => [...prev, { sender: 'user', text: data.question }]);
          // Animate the LLM response as bot message.
          simulateStreaming(data.llm_response);
        } catch (err) {
          console.error('Upload failed:', err);
        }
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (err) {
      console.error('Error recording audio:', err);
    }
  };

  // New function to stop recording
  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div
      className="relative min-h-screen text-gray-200 font-sans"
      style={{
        backgroundImage: 'url(https://pe-images.s3.amazonaws.com/basics/cc/gradients/essentials/radial-gradient-reversed.jpg)',
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Updated chat container to wrap messages in a container matching input box width */}
      <div className="absolute inset-0 flex flex-col justify-center p-4 overflow-y-auto">
        <div className="mx-auto w-11/12 max-w-3xl">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              // Adjusted margin bottom from mb-2 to mb-1 for closer spacing
              className={`mb-1 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                // Reduced max-width to a fixed value for closer alignment
                className={`px-4 py-3 rounded-lg max-w-md 
                  ${msg.sender === 'user' 
                    ? 'bg-blue-700 text-white' 
                    : 'bg-[#1f1f24] text-gray-300'
                  }`}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {isThinking && (
            <div className="mb-4 flex justify-start">
              <div className="max-w-xs md:max-w-md lg:max-w-lg px-4 py-2 rounded-lg bg-gray-800 text-gray-300 italic">
                {thinkingText}
              </div>
            </div>
          )}

          {isStreaming && (
            <div className="mb-4 flex justify-start">
              <div className="max-w-xs md:max-w-md lg:max-w-lg px-4 py-2 rounded-lg bg-gray-800 text-gray-200">
                {streamingText}
                <span className="animate-pulse text-gray-400">▊</span>
              </div>
            </div>
          )}
        </div>
      </div>

      <div
        className={`
          absolute left-1/2 transform -translate-x-1/2 w-11/12 max-w-3xl 
          transition-all duration-500 ease-in-out
          ${inputPosition === 'center'
            ? 'top-1/2 -translate-y-1/2'
            : 'bottom-4'}
        `}
      >
        {/* Conditional header: displayed until a user prompt is sent */}
        {(!messages.some(msg => msg.sender === 'user')) && (
          <div className="flex flex-col items-center justify-center mb-[100px]">
            <h1 className="text-4xl font-bold text-white">Insurance GPT</h1>
            <span className="text-xl text-white opacity-90">Your AI-powered insurance assistant</span>
          </div>
        )}

        <form onSubmit={(e) => {
          e.preventDefault();
          handleKeyDown({ key: 'Enter' });
        }} className="relative flex gap-2">
          <div className="relative w-full">
            <input
              type="text"
              placeholder="Type your prompt..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full p-4 pr-12 rounded-lg bg-[#1f1f24] text-gray-200 focus:outline-none 
                         focus:ring-2 focus:ring-blue-600 shadow-lg placeholder-gray-500"
            />
            {/* Embedded recording button inside input box */}
            <button
              type="button"
              onClick={isRecording ? stopRecording : startRecording}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-full bg-blue-700 hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400 shadow-lg"
            >
              <MicrophoneIcon className="h-5 w-5 text-white" />
            </button>
          </div>
          <button
            type="submit"
            className="p-4 rounded-lg bg-gray-700 hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-600 shadow-lg transition-colors duration-200"
            disabled={!inputValue.trim()}
          >
            <ArrowUpIcon className="h-6 w-6 text-gray-100" />
          </button>
        </form>
      </div>
    </div>
  );
}