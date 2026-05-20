export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <FeedSidebar />

      <main className="flex-1 overflow-auto">
        <Topbar />
        {children}
      </main>

      <AiAssistantPanel />
    </div>
  );
}
