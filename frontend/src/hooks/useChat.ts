import { useState, useEffect } from "react";
import useWebSocket from "react-use-websocket";

const useChat = () => {
  const socketUrl = `ws://localhost:8000/api/v1/chat/ws?token=${localStorage.getItem("access_token")}`;
  const { sendMessage, lastMessage, readyState } = useWebSocket(socketUrl, {
    shouldReconnect: () => true,
  });

  const [messages, setMessages] = useState<string[]>([]);
  console.log(lastMessage);

  useEffect(() => {
    setMessages((state) => [...state, lastMessage?.data]);
  }, [lastMessage]);

  useEffect(() => {
    setMessages(JSON.parse(localStorage.getItem("savedMessages") || "[]"));
    return () => {
      localStorage.setItem("savedMessages", JSON.stringify(messages));
    };
  }, []);

  return {
    messages,
    sendMessage,
    lastMessage,
    readyState,
  };
};

export default useChat;
