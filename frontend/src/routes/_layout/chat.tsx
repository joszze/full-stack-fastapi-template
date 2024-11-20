import {
  Container,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { z } from "zod";

import Navbar from "../../components/Common/Navbar";
import AddItem from "../../components/Items/AddItem";
import React from "react";

export const Route = createFileRoute("/_layout/chat")({
  component: Chat,
});

function Chat() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Chat
      </Heading>
    </Container>
  );
}
