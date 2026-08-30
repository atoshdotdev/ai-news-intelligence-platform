"use client";

import { usePathname } from "next/navigation";

import { Separator } from "@/components/ui/separator";
import { SidebarTrigger } from "@/components/ui/sidebar";

const titles: Record<string, string> = {
  "/": "Dashboard",
  "/sources": "Sources",
  "/feed": "Feed",
  "/chat": "Chat",
};

export function SiteHeader() {
  const pathname = usePathname();

  const title =
    titles[pathname] ??
    titles[`/${pathname.split("/")[1]}/${pathname.split("/")[2]}`] ??
    "Dashboard";

  return (
    <header className="flex h-(--header-height) shrink-0 items-center gap-2">
      <div className="flex w-full items-center gap-1 px-4 lg:px-6">
        <SidebarTrigger className="-ml-1" />

        <Separator
          orientation="vertical"
          className="mx-2 h-4 data-vertical:self-auto"
        />

        <h1 className="text-base font-medium">{title}</h1>
      </div>
    </header>
  );
}
