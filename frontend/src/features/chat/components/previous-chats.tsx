"use client";

import { MessageSquareIcon } from "lucide-react";

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
} from "@/components/ui/sidebar";
import { usePreviousChats } from "@/features/chat/hooks/use-chat";
import { ChatItem } from "@/features/chat/components/chat-item";

export function PreviousChats() {
  const { data: chats = [], isLoading } = usePreviousChats();

  if (isLoading || chats.length === 0) {
    return null;
  }

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Previous chats</SidebarGroupLabel>

      <SidebarGroupContent>
        <SidebarMenu>
          {chats.map((chat) => (
            <ChatItem key={chat.id} chat={chat} icon={<MessageSquareIcon />} />
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
