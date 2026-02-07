"use client";

import { useState, useRef, ChangeEvent } from "react";
import { Upload, CheckCircle, AlertCircle } from "lucide-react";
import { uploadFile } from "@/lib/api";
import styles from "./FileUpload.module.css";

interface Props {
  onUploaded: () => void;
}

export default function FileUpload({ onUploaded }: Props) {
  const [status, setStatus] = useState<
    "idle" | "uploading" | "success" | "error"
  >("idle");
  const [info, setInfo] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setStatus("uploading");
    setInfo(`Uploading ${file.name}...`);

    try {
      const res = await uploadFile(file);
      setStatus("success");
      setInfo(`${res.message} (${res.num_chunks} chunks)`);
      onUploaded();
    } catch (err: unknown) {
      setStatus("error");
      setInfo(err instanceof Error ? err.message : "Upload failed");
    }

    // reset input so the same file can be re-uploaded
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <div className={styles.wrapper}>
      <label className={styles.dropzone}>
        <Upload size={20} />
        <span>Upload .txt or .md</span>
        <input
          ref={inputRef}
          type="file"
          accept=".txt,.md"
          onChange={handleFile}
          className={styles.hidden}
        />
      </label>

      {info && (
        <div
          className={`${styles.toast} ${
            status === "success"
              ? styles.success
              : status === "error"
              ? styles.error
              : ""
          }`}
        >
          {status === "success" && <CheckCircle size={14} />}
          {status === "error" && <AlertCircle size={14} />}
          <span>{info}</span>
        </div>
      )}
    </div>
  );
}
