"use client";

import { useState, useEffect } from "react";
import ChatWindow from "@/components/ChatWindow";
import FileUpload from "@/components/FileUpload";
import StatusBar from "@/components/StatusBar";
import { getStatus } from "@/lib/api";
import styles from "./page.module.css";

export default function Home() {
  const [docCount, setDocCount] = useState(0);

  const refreshStatus = async () => {
    try {
      const s = await getStatus();
      setDocCount(s.num_documents);
    } catch {
      /* backend not up yet */
    }
  };

  useEffect(() => {
    refreshStatus();
  }, []);

  return (
    <div className={styles.container}>
      {/* ---- Sidebar ---- */}
      <aside className={styles.sidebar}>
        <h1 className={styles.logo}>SPRKTech magic</h1>
        <p className={styles.subtitle}>DecisionForge</p>
        <p className={styles.tagline}>Chat with your documents</p>

        <div className={styles.divider} />

        <FileUpload onUploaded={refreshStatus} />

        <div className={styles.spacer} />
        <StatusBar docCount={docCount} />
      </aside>

      {/* ---- Main chat area ---- */}
      <main className={styles.main}>
        <ChatWindow />
      </main>
    </div>
  );
}
