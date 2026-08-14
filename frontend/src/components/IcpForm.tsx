import { useState } from "react";
import type { FormEvent } from "react";
import type { IcpInput } from "../types";
import { TagInput } from "./TagInput";

interface IcpFormProps {
  initial?: IcpInput;
  submitLabel: string;
  onSubmit: (input: IcpInput) => Promise<void>;
}

const EMPTY: IcpInput = {
  name: "",
  industries: [],
  company_size_min: null,
  company_size_max: null,
  locations: [],
  technologies: [],
  target_titles: [],
};

export function IcpForm({ initial, submitLabel, onSubmit }: IcpFormProps) {
  const [form, setForm] = useState<IcpInput>(initial ?? EMPTY);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!form.name.trim()) {
      setError("Name is required.");
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await onSubmit(form);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save ICP.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="icp-form" onSubmit={handleSubmit}>
      <label className="field">
        Name
        <input
          type="text"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          placeholder="e.g. Mid-market DevTools buyers"
        />
      </label>

      <TagInput
        label="Industries"
        values={form.industries}
        onChange={(industries) => setForm({ ...form, industries })}
        placeholder="Type an industry, press Enter"
      />

      <div className="field-row">
        <label className="field">
          Company size min
          <input
            type="number"
            value={form.company_size_min ?? ""}
            onChange={(e) =>
              setForm({
                ...form,
                company_size_min: e.target.value === "" ? null : Number(e.target.value),
              })
            }
          />
        </label>
        <label className="field">
          Company size max
          <input
            type="number"
            value={form.company_size_max ?? ""}
            onChange={(e) =>
              setForm({
                ...form,
                company_size_max: e.target.value === "" ? null : Number(e.target.value),
              })
            }
          />
        </label>
      </div>

      <TagInput
        label="Locations"
        values={form.locations}
        onChange={(locations) => setForm({ ...form, locations })}
        placeholder="e.g. USA, Remote"
      />

      <TagInput
        label="Technologies"
        values={form.technologies}
        onChange={(technologies) => setForm({ ...form, technologies })}
        placeholder="e.g. Kubernetes, React"
      />

      <TagInput
        label="Target job titles"
        values={form.target_titles}
        onChange={(target_titles) => setForm({ ...form, target_titles })}
        placeholder="e.g. VP Engineering"
      />

      {error && <p className="form-error">{error}</p>}

      <button type="submit" disabled={saving}>
        {saving ? "Saving..." : submitLabel}
      </button>
    </form>
  );
}
