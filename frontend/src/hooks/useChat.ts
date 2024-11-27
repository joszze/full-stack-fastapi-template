import { useState, useEffect } from "react";
import useWebSocket from "react-use-websocket";
import { ChatMessagePublic, ChatService } from "../client";
import { useQuery } from "@tanstack/react-query";

function getMessagesQueryOptions() {
  return {
    queryFn: () => ChatService.getMessages(),
    queryKey: ["messages"],
  };
}

const useChat = () => {
  const socketUrl = `ws://localhost:8000/api/v1/chat/ws?token=${localStorage.getItem("access_token")}`;
  const { lastJsonMessage, readyState, sendJsonMessage } = useWebSocket<string>(
    socketUrl,
    {
      shouldReconnect: () => true,
    }
  );

  const { data: initialMessages, isPending } = useQuery({
    ...getMessagesQueryOptions(),
  });

  const [messages, setMessages] = useState<ChatMessagePublic[]>([]);

  function sendMessage(message: string) {
    sendJsonMessage({ message });
  }

  useEffect(() => {
    console.log(typeof lastJsonMessage);
    lastJsonMessage &&
      setMessages((state) => [
        ...state,
        JSON.parse(lastJsonMessage) as ChatMessagePublic,
      ]);
  }, [lastJsonMessage]);

  useEffect(() => {
    console.log(initialMessages);
    initialMessages && setMessages(initialMessages.data);
  }, [initialMessages]);

  return {
    loadingMessages: isPending,
    messages,
    sendMessage,
    lastJsonMessage,
    readyState,
  };
};

export default useChat;
