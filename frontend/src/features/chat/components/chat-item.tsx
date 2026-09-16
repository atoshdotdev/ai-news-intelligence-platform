"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MoreHorizontalIcon,
  PinIcon,
  PinOffIcon,
  Trash2Icon,
} from "lucide-react";

import {
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import {
  useDeleteChat,
  useToggleChatPin,
} from "@/features/chat/hooks/use-chat";

import type { Chat } from "@/features/chat/types";

type ChatItemProps = {
  chat: Chat;
  icon: React.ReactNode;
};

export function ChatItem({ chat, icon }: ChatItemProps) {
  const pathname = usePathname();
  const togglePin = useToggleChatPin();
  const deleteChat = useDeleteChat();

  const isActive = pathname === `/chat/${chat.id}`;
  const isPending = togglePin.isPending || deleteChat.isPending;

  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        render={
          <Link href={`/chat/${chat.id}`}>
            {icon}
            <span className="truncate">{chat.title}</span>
          </Link>
        }
        isActive={isActive}
        tooltip={chat.title}
      ></SidebarMenuButton>

      <DropdownMenu>
        <DropdownMenuTrigger
          render={
            <SidebarMenuAction showOnHover>
              <MoreHorizontalIcon />
              <span className="sr-only">Chat options</span>
            </SidebarMenuAction>
          }
        />

        <DropdownMenuContent align="start" side="right">
          <DropdownMenuItem
            disabled={isPending}
            onClick={() => togglePin.mutate(chat.id)}
          >
            {chat.pinned ? <PinOffIcon /> : <PinIcon />}
            {chat.pinned ? "Unpin" : "Pin"}
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem
            variant="destructive"
            disabled={isPending}
            onClick={() => deleteChat.mutate(chat.id)}
          >
            <Trash2Icon />
            Delete
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </SidebarMenuItem>
  );
}
