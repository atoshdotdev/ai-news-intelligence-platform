import Link from "next/link";
import {
  ArrowRightIcon,
  BookOpenIcon,
  BotMessageSquare,
  NewspaperIcon,
  WaypointsIcon,
} from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { buttonVariants } from "@/components/ui/button";

const quickActions = [
  {
    title: "News Feed",
    description:
      "Browse the latest news articles and discover what is happening across your sources.",
    href: "/feed",
    icon: NewspaperIcon,
  },
  {
    title: "AI Chat",
    description:
      "Ask questions about the collected news and get answers grounded in the available articles.",
    href: "/chat",
    icon: BotMessageSquare,
  },
  {
    title: "Sources",
    description:
      "View and manage the news sources used by the platform for content collection.",
    href: "/sources",
    icon: WaypointsIcon,
  },
];

export default function Page() {
  return (
    <div className="@container/main flex min-h-0 flex-1 flex-col">
      <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-4 py-6 md:px-6 md:py-8">
        <section className="flex flex-col items-start gap-5 rounded-xl border bg-card p-6 md:p-8">
          <div className="max-w-2xl space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight md:text-3xl">
              Welcome to NeuralPress
            </h1>
            <p className="text-sm leading-6 text-muted-foreground md:text-base">
              Explore collected news, follow important events, and use AI to
              find answers across the available articles.
            </p>
          </div>

          <Link
            className={buttonVariants({ variant: "default", size: "default" })}
            href="/feed"
          >
            Explore the news
            <ArrowRightIcon />
          </Link>
        </section>

        <section className="mt-8 space-y-4">
          <div>
            <h2 className="text-lg font-semibold tracking-tight">
              Quick access
            </h2>
            <p className="text-sm text-muted-foreground">
              Jump directly to the part of the platform you want to use.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {quickActions.map((action) => {
              const Icon = action.icon;

              return (
                <Card
                  key={action.href}
                  className="transition-colors hover:bg-muted/40"
                >
                  <CardHeader>
                    <div className="mb-1 flex size-9 items-center justify-center rounded-md border bg-background">
                      <Icon className="size-4 text-muted-foreground" />
                    </div>

                    <CardTitle className="text-base">{action.title}</CardTitle>
                    <CardDescription className="leading-5">
                      {action.description}
                    </CardDescription>
                  </CardHeader>

                  <CardContent>
                    <Link
                      className={buttonVariants({
                        variant: "ghost",
                        size: "default",
                      })}
                      href={action.href}
                    >
                      Open {action.title}
                      <ArrowRightIcon />
                    </Link>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
}
