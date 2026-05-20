"use client";

import * as React from "react";
import Link from "next/link";

import { NavMain } from "@/components/nav-main";

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
  ChartBarStackedIcon,
  BotMessageSquare,
} from "lucide-react";

const navMain = [
  {
    title: "Feed",
    url: "/dashboard/feed",
    icon: <NewspaperIcon />,
  },
  {
    title: "Chat",
    url: "/dashboard/chat",
    icon: <BotMessageSquare />,
  },
  {
    title: "Sources",
    url: "/dashboard/sources",
    icon: <WaypointsIcon />,
  },
  {
    title: "Categories",
    url: "/dashboard/categories",
    icon: <ChartBarStackedIcon />,
  },
];

export function AppSidebar(props: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="offcanvas" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton render={<Link href="/dashboard" />}>
              <CommandIcon className="size-6" />
              <span className="text-base font-semibold">NeuralPress</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <NavMain items={navMain} />
      </SidebarContent>
    </Sidebar>
  );
}
