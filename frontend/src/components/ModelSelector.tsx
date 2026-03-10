"use client";

import { useState, useEffect } from "react";
import { ChevronDown } from "lucide-react";
import { getModels, ModelOption } from "@/lib/api";
import styles from "./ModelSelector.module.css";

const MODEL_STORAGE_KEY = "rag-selected-model";

const FALLBACK_MODELS: ModelOption[] = [
  { id: "gpt-4o-mini", name: "GPT-4o Mini", description: "Fast, cost-effective" },
  { id: "gpt-4o", name: "GPT-4o", description: "Balanced performance" },
  { id: "claude-3-5-sonnet-20241022", name: "Claude 3.5 Sonnet", description: "Strong reasoning, coding" },
  { id: "claude-3-5-haiku-20241022", name: "Claude 3.5 Haiku", description: "Fast, efficient" },
];

interface Props {
  value: string;
  onChange: (modelId: string) => void;
}

export default function ModelSelector({ value, onChange }: Props) {
  const [models, setModels] = useState<ModelOption[]>(FALLBACK_MODELS);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    getModels()
      .then((res) => setModels(res.models))
      .catch(() => { /* keep fallback */ });
  }, []);

  const handleSelect = (id: string) => {
    onChange(id);
    setOpen(false);
    localStorage.setItem(MODEL_STORAGE_KEY, id);
  };

  const selected = models.find((m) => m.id === value) ?? models[0];

  return (
    <div className={styles.wrapper}>
      <label className={styles.label}>Model</label>
      <div className={styles.selectWrapper}>
        <button
          type="button"
          className={styles.trigger}
          onClick={() => setOpen(!open)}
          aria-haspopup="listbox"
          aria-expanded={open}
          aria-label="Select model"
        >
          <span className={styles.triggerText}>
            {selected?.name ?? "Select model"}
          </span>
          <ChevronDown size={16} className={styles.chevron} />
        </button>
        {open && (
          <ul
            className={styles.dropdown}
            role="listbox"
            onMouseLeave={() => setOpen(false)}
          >
            {models.map((m) => (
              <li key={m.id} role="option">
                <button
                  type="button"
                  className={`${styles.option} ${m.id === value ? styles.selected : ""}`}
                  onClick={() => handleSelect(m.id)}
                >
                  <span className={styles.optionName}>{m.name}</span>
                  <span className={styles.optionDesc}>{m.description}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export { MODEL_STORAGE_KEY };
