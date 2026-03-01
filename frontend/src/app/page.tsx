"use client";

import { Header } from "@/components/layout/Header";
import { ConversationPanel } from "@/components/layout/ConversationPanel";
import { ChatContainer } from "@/components/chat/ChatContainer";
import { SettingsDialog } from "@/components/common/SettingsDialog";
import { Toaster } from "sonner";

export default function Home() {
  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <ConversationPanel />
        <main className="flex-1 overflow-hidden">
          <ChatContainer />
        </main>
      </div>
      <SettingsDialog />
      <Toaster position="bottom-right" />
    </div>
  );
}
