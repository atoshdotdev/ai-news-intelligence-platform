"use client";

import Link from "next/link";
import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { PlusIcon } from "lucide-react";
import { Separator } from "@/components/ui/separator";

export function ChatActions() {
  return (
    <SidebarGroup>
      <Separator
        orientation="horizontal"
        className="h-4 mb-4 data-horizontal:self-auto"
      />

      <SidebarGroupContent>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="New chat"
              render={<Link href="/chat" />}
            >
              <PlusIcon />
              <span>New chat</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  );
}
