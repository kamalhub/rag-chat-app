"use client";

import { useState, useEffect } from "react";
import { FileText } from "lucide-react";
import { getDocuments, DocumentSummary } from "@/lib/api";
import styles from "./DocumentList.module.css";

interface Props {
  selectedFilename: string | null;
  onSelect: (filename: string | null) => void;
  refreshTrigger?: number; // increment to refetch
}

export default function DocumentList({
  selectedFilename,
  onSelect,
  refreshTrigger = 0,
}: Props) {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getDocuments()
      .then((res) => setDocs(res.documents))
      .catch(() => setDocs([]))
      .finally(() => setLoading(false));
  }, [refreshTrigger]);

  if (loading && docs.length === 0) return null;

  return (
    <div className={styles.wrapper}>
      <label className={styles.label}>Documents</label>
      <div className={styles.list}>
        {docs.length === 0 ? (
          <p className={styles.empty}>No documents stored. Enable MongoDB to persist uploads.</p>
        ) : (
          docs.map((d) => (
            <button
              key={`${d.filename}-${d.ingested_at}`}
              type="button"
              className={`${styles.item} ${selectedFilename === d.filename ? styles.selected : ""}`}
              onClick={() => onSelect(selectedFilename === d.filename ? null : d.filename)}
            >
              <FileText size={14} />
              <span className={styles.filename}>{d.filename}</span>
              <span className={styles.chunks}>{d.num_chunks}</span>
            </button>
          ))
        )}
      </div>
    </div>
  );
}
