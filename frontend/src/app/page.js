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

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && inputValue.trim() !== "") {
      const userMessage = { sender: 'user', text: inputValue.trim() };
      setMessages(prev => [...prev, userMessage]);
      setInputValue("");

      if (inputPosition === 'center') {
        setInputPosition('bottom');
      }

      setIsThinking(true);
      setTimeout(() => {
        setIsThinking(false);
        simulateStreaming("This is a hardcoded response that will be streamed character by character, similar to ChatGPT's behavior.");
      }, 5000);
    }
  };

  // Updated startRecording function to download as .mp4 to laptop
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];
      
      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'video/mp4' });
        // Create a temporary URL for the blob and trigger a download
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = 'recording.mp4';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
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
    <div className="relative min-h-screen bg-gray-900 text-gray-100">
      <div className="absolute inset-0 overflow-y-auto p-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`mb-4 flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs md:max-w-md lg:max-w-lg px-4 py-2 rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-gray-700 text-gray-100'
                  : 'bg-gray-800 text-gray-200'
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

      <div
        className={`
          absolute left-1/2 transform -translate-x-1/2 w-11/12 max-w-3xl transition-all duration-500 ease-in-out
          ${inputPosition === 'center'
            ? 'top-1/2 -translate-y-1/2'
            : 'bottom-4'}
        `}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          handleKeyDown({ key: 'Enter' });
        }} className="relative flex gap-2">
          <div className="relative w-full">
            <input
              type="text"
              placeholder="Ask anything..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full p-4 pr-12 rounded-lg bg-gray-800 text-gray-100 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-600 shadow-lg placeholder-gray-500"
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
