import {
  Avatar,
  Box,
  Button,
  Container,
  Flex,
  Heading,
  Input,
  Text,
} from "@chakra-ui/react";
import { createFileRoute } from "@tanstack/react-router";
import { FormEvent, useState } from "react";
import useChat from "../../hooks/useChat";
import useAuth from "../../hooks/useAuth";

export const Route = createFileRoute("/_layout/chat")({
  component: Chat,
});

function Chat() {
  const { messages, sendMessage } = useChat();

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Chat
      </Heading>
      <ChatMessages messages={messages} />
      <ChatInput sendMessage={sendMessage} />
    </Container>
  );
}

function ChatMessages({ messages }: { messages: string[] }) {
  const { user } = useAuth();
  const name = user?.full_name ?? "Anonymous";
  return (
    <Box>
      {messages.map((message, index) => (
        <Flex key={index} gap={2}>
          <Avatar name={name} />
          <Box>
            <Text fontWeight="bold">{name}</Text>
            <Text>{message}</Text>
          </Box>
        </Flex>
      ))}
    </Box>
  );
}

function ChatInput({ sendMessage }: { sendMessage: any }) {
  const [message, setMessage] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    sendMessage(message);
    setMessage("");
  };

  return (
    <Box>
      <form onSubmit={handleSubmit}>
        <Input
          placeholder="Type your message..."
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <Button type="submit">Send</Button>
      </form>
    </Box>
  );
}
