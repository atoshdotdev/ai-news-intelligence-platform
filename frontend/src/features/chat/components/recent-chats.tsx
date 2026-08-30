"use client";

import Link from "next/link";
import { MessageSquareIcon } from "lucide-react";

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

type RecentChat = {
  id: string;
  title: string;
};

const recentChats: RecentChat[] = [
  {
    id: "1",
    title: "Latest developments in AI",
  },
  {
    id: "2",
    title: "European tech news",
  },
  {
    id: "3",
    title: "What happened in the markets today?",
  },
];

export function RecentChats() {
  return (
    <SidebarGroup>
      <SidebarGroupLabel>Recent chats</SidebarGroupLabel>

      <SidebarGroupContent>
        <SidebarMenu>
          {recentChats.map((chat) => (
            <SidebarMenuItem key={chat.id}>
              <SidebarMenuButton
                tooltip={chat.title}
                render={<Link href={`/chat/${chat.id}`} />}
              >
                <MessageSquareIcon />
                <span className="truncate">{chat.title}</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          ))}
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
