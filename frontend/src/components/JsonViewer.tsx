"use client";

import { useState, useEffect, useMemo, useRef } from "react";
import {
  getMortgageApplications,
  getMortgageApplication,
  MortgageApplicationSummary,
} from "@/lib/api";
import styles from "./JsonViewer.module.css";

const DEBOUNCE_MS = 200;

interface Props {
  filename?: string | null;
}

function formatJson(obj: unknown): string {
  return JSON.stringify(obj, null, 2);
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlightMatches(text: string, search: string): React.ReactNode {
  if (!search.trim()) return text;
  const escaped = escapeRegex(search.trim());
  const regex = new RegExp(`(${escaped})`, "gi");
  const parts = text.split(regex);
  return parts.map((part, i) =>
    i % 2 === 1 ? (
      <mark key={i} className={styles.highlight}>
        {part}
      </mark>
    ) : (
      part
    )
  );
}

export default function JsonViewer({ filename: _filename }: Props) {
  const [applications, setApplications] = useState<MortgageApplicationSummary[]>(
    []
  );
  const [selectedId, setSelectedId] = useState<string>("");
  const [search, setSearch] = useState<string>("");
  const [searchFilter, setSearchFilter] = useState<string>("");
  const [json, setJson] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSearchFilter(search);
      debounceRef.current = null;
    }, DEBOUNCE_MS);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [search]);

  const filteredApplications = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return applications;
    const filtered = applications.filter(
      (app) =>
        app.documentID.toLowerCase().includes(q) ||
        app.label.toLowerCase().includes(q)
    );
    if (selectedId && !filtered.some((a) => a.documentID === selectedId)) {
      const sel = applications.find((a) => a.documentID === selectedId);
      if (sel) filtered.push(sel);
    }
    return filtered;
  }, [applications, search, selectedId]);

  useEffect(() => {
    getMortgageApplications()
      .then((res) => setApplications(res.applications))
      .catch(() => setApplications([]));
  }, []);

  useEffect(() => {
    if (!selectedId) {
      setJson("");
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    getMortgageApplication(selectedId)
      .then((data) => setJson(formatJson(data)))
      .catch((e) => {
        setError(e instanceof Error ? e.message : "Failed to load");
        setJson("");
      })
      .finally(() => setLoading(false));
  }, [selectedId]);

  return (
    <aside className={styles.panel}>
      <div className={styles.header}>
        <h3 className={styles.title}>Mortgage Application</h3>
        <input
          type="search"
          placeholder="Search by document ID or value…"
          className={styles.search}
          aria-label="Search by document ID or value"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select
          className={styles.select}
          value={selectedId}
          onChange={(e) => setSelectedId(e.target.value)}
          aria-label="Select document"
        >
          <option value="">
            {filteredApplications.length === 0 && search.trim()
              ? "No documents match search"
              : "Select a document…"}
          </option>
          {filteredApplications.map((app) => (
            <option key={app.documentID} value={app.documentID}>
              {app.label}
            </option>
          ))}
        </select>
        {selectedId && (
          <span className={styles.filename} title={selectedId}>
            {selectedId}
          </span>
        )}
      </div>
      <div className={styles.content}>
        {!selectedId && (
          <p className={styles.placeholder}>
            Select a mortgage application to perform checks.
          </p>
        )}
        {selectedId && loading && (
          <p className={styles.loading}>Loading…</p>
        )}
        {selectedId && error && (
          <p className={styles.error}>{error}</p>
        )}
        {selectedId && !loading && !error && (
          <pre className={styles.pre}>
            {searchFilter.trim()
              ? json.split("\n").map((line, i) => (
                  <span key={i}>
                    {highlightMatches(line, searchFilter)}
                    {"\n"}
                  </span>
                ))
              : json}
          </pre>
        )}
      </div>
    </aside>
  );
}
