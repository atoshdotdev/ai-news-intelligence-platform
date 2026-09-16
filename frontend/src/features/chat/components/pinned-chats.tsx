"use client";

import { PinIcon } from "lucide-react";

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
} from "@/components/ui/sidebar";
import { usePinnedChats } from "@/features/chat/hooks/use-chat";
import { ChatItem } from "@/features/chat/components/chat-item";

export function PinnedChats() {
  const { data: chats = [], isLoading } = usePinnedChats();

  if (isLoading || chats.length === 0) {
    return null;
  }

  return (
    <SidebarGroup>
      <SidebarGroupLabel>Pinned</SidebarGroupLabel>

      <SidebarGroupContent>
        <SidebarMenu>
          {chats.map((chat) => (
            <ChatItem key={chat.id} chat={chat} icon={<PinIcon />} />
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
