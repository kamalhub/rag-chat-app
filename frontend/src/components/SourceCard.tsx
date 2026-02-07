"use client";

import { useState } from "react";
import { FileText, ChevronDown, ChevronUp } from "lucide-react";
import styles from "./SourceCard.module.css";

interface Props {
  content: string;
  source: string;
}

export default function SourceCard({ content, source }: Props) {
  const [open, setOpen] = useState(false);
  const filename = source.split("/").pop() ?? source;

  return (
    <div className={styles.card}>
      <button className={styles.header} onClick={() => setOpen(!open)}>
        <FileText size={14} />
        <span className={styles.filename}>{filename}</span>
        {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      {open && <p className={styles.body}>{content}</p>}
    </div>
  );
}
