import { IcpForm } from "../components/IcpForm";
import { api } from "../api/client";
import type { Icp, IcpInput } from "../types";

interface IcpFormPageProps {
  editing: Icp | null;
  onDone: () => void;
}

export function IcpFormPage({ editing, onDone }: IcpFormPageProps) {
  async function handleSubmit(input: IcpInput) {
    if (editing) {
      await api.put(`/api/icps/${editing.id}`, input);
    } else {
      await api.post("/api/icps", input);
    }
    onDone();
  }

  return (
    <div className="icp-form-page">
      <h2>{editing ? "Edit ICP" : "New ICP"}</h2>
      <IcpForm
        initial={editing ?? undefined}
        submitLabel={editing ? "Save changes" : "Create ICP"}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
