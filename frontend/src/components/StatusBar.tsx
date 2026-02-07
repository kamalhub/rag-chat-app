"use client";

import { Database } from "lucide-react";
import styles from "./StatusBar.module.css";

interface Props {
  docCount: number;
}

export default function StatusBar({ docCount }: Props) {
  return (
    <div className={styles.bar}>
      <Database size={14} />
      <span>
        {docCount === 0
          ? "No documents loaded"
          : `${docCount} chunk${docCount !== 1 ? "s" : ""} indexed`}
      </span>
    </div>
  );
}
