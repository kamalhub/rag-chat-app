"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import { Send, Download } from "lucide-react";
import { sendMessage, exportChat, ChatResponse } from "@/lib/api";
import SourceCard from "./SourceCard";
import styles from "./ChatWindow.module.css";

interface Message {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: ChatResponse["sources"];
}

interface Props {
  model?: string;
}

export default function ChatWindow({ model }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const userMsg: Message = { id: crypto.randomUUID(), role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendMessage(text, model);
      const assistantMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: res.answer,
        sources: res.sources,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Something went wrong";
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        text: `Error: ${errorMessage}`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* ---- Messages ---- */}
      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.empty}>
            <p className={styles.emptyTitle}>No messages yet</p>
            <p className={styles.emptyHint}>
              Upload a document in the sidebar, then ask a question.
            </p>
          </div>
        )}

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`${styles.row} ${
              msg.role === "user" ? styles.userRow : styles.assistantRow
            }`}
          >
            <div
              className={`${styles.bubble} ${
                msg.role === "user" ? styles.userBubble : styles.assistantBubble
              }`}
            >
              {msg.text}
            </div>

            {msg.sources && msg.sources.length > 0 && (
              <div className={styles.sources}>
                <p className={styles.sourcesLabel}>Sources</p>
                {msg.sources.map((s, i) => (
                  <SourceCard key={i} content={s.content} source={s.source} />
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className={`${styles.row} ${styles.assistantRow}`}>
            <div className={`${styles.bubble} ${styles.assistantBubble}`}>
              <span className={styles.dots}>
                <span />
                <span />
                <span />
              </span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ---- Input ---- */}
      <form onSubmit={handleSubmit} className={styles.inputBar}>
        <input
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about your documents..."
          disabled={loading}
        />
        <button
          type="button"
          className={styles.exportBtn}
          disabled={messages.length === 0 || exporting}
          title="Export chat as PDF"
          onClick={async () => {
            setExporting(true);
            try {
              await exportChat(
                messages.map((m) => ({
                  role: m.role,
                  text: m.text,
                  sources: m.sources ?? [],
                }))
              );
            } catch {
              /* silently fail — could add toast here */
            } finally {
              setExporting(false);
            }
          }}
        >
          <Download size={18} />
        </button>
        <button
          type="submit"
          className={styles.sendBtn}
          disabled={loading || !input.trim()}
        >
          <Send size={18} />
        </button>
      </form>
    </>
  );
}
