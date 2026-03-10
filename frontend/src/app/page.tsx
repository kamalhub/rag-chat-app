"use client";

import { useState, useEffect } from "react";
import ChatWindow from "@/components/ChatWindow";
import DocumentList from "@/components/DocumentList";
import Logo from "@/components/Logo";
import FileUpload from "@/components/FileUpload";
import JsonViewer from "@/components/JsonViewer";
import ModelSelector from "@/components/ModelSelector";
import StatusBar from "@/components/StatusBar";
import ThemeToggle from "@/components/ThemeToggle";
import { MODEL_STORAGE_KEY } from "@/components/ModelSelector";
import { getStatus } from "@/lib/api";
import styles from "./page.module.css";

export default function Home() {
  const [docCount, setDocCount] = useState(0);
  const [model, setModel] = useState("gpt-4o-mini");
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem(MODEL_STORAGE_KEY);
    if (stored) setModel(stored);
  }, []);

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
        <div className={styles.header}>
          <div className={styles.brand}>
            <Logo className={styles.logoIcon} />
            <div>
              <h1 className={styles.logo}>SPRKTech</h1>
            <p className={styles.subtitle}>DecisionForge</p>
            <p className={styles.tagline}>Upload your documents to validate with your application</p>
            </div>
          </div>
          <ThemeToggle />
        </div>

        <div className={styles.divider} />

        <ModelSelector value={model} onChange={setModel} />

        <FileUpload onUploaded={refreshStatus} />

        <DocumentList
          selectedFilename={selectedDocument}
          onSelect={setSelectedDocument}
          refreshTrigger={docCount}
        />

        <div className={styles.spacer} />
        <button type="button" className={styles.validateBtn}>
          Validate
        </button>
        <StatusBar docCount={docCount} />
      </aside>

      {/* ---- Main chat area ---- */}
      <main className={styles.main}>
        <ChatWindow model={model} />
      </main>

      {/* ---- JSON viewer ---- */}
      <JsonViewer filename={selectedDocument} />
    </div>
  );
}
