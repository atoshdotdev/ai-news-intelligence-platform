"use client";

import * as React from "react";
import Link from "next/link";

import { NavMain } from "@/components/nav-main";
import { PreviousChats } from "@/features/chat/components/previous-chats";
import { PinnedChats } from "@/features/chat/components/pinned-chats";
import { ChatActions } from "@/features/chat/components/chat-actions";
import { UserMenu } from "@/components/user-menu";

import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

import {
  WaypointsIcon,
  CommandIcon,
  NewspaperIcon,
  BotMessageSquare,
} from "lucide-react";
import { Separator } from "@/components/ui/separator";

const navMain = [
  {
    title: "Feed",
    url: "/feed",
    icon: <NewspaperIcon />,
  },
  {
    title: "Chat",
    url: "/chat",
    icon: <BotMessageSquare />,
  },
  {
    title: "Sources",
    url: "/sources",
    icon: <WaypointsIcon />,
  },
];

export function AppSidebar(props: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton render={<Link href="/" />}>
              <CommandIcon className="size-6" />
              <span className="text-base font-semibold">NeuralPress</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>

        <NavMain items={navMain} />

        <Separator
          orientation="horizontal"
          className="h-4 data-horizontal:self-auto"
        />

        <ChatActions />
      </SidebarHeader>

      <SidebarContent className="gap-0">
        <PinnedChats />

        <PreviousChats />

        <UserMenu />
      </SidebarContent>
    </Sidebar>
  );
}
