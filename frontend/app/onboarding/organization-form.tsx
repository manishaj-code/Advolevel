"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/button";
import { SelectField, TextField } from "@/components/ui/field";
import { ErrorPanel } from "@/components/ui/states";
import { rememberOrg } from "@/lib/active-org";
import { ApiError } from "@/lib/api/client";
import { useCreateOrganization } from "@/lib/api/hooks";

const SIZE_BANDS = ["1-10", "11-50", "51-200", "201-1000", "1000+"] as const;

function browserTimezone(): string {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
  } catch {
    return "UTC";
  }
}

export function OrganizationForm() {
  const router = useRouter();
  const create = useCreateOrganization();
  const [timezone] = useState(browserTimezone);

  const fieldErrors = Object.fromEntries(
    create.error instanceof ApiError
      ? create.error.fieldErrors.map((e) => [e.field, e.message])
      : [],
  );

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const text = (name: string) => String(form.get(name) ?? "").trim() || undefined;
    const sizeBand = text("size_band") as (typeof SIZE_BANDS)[number] | undefined;
    const org = await create
      .mutateAsync({
        name: String(form.get("name") ?? "").trim(),
        industry: text("industry"),
        size_band: sizeBand,
        website: text("website"),
        timezone: text("timezone") ?? "UTC",
      })
      .catch(() => null);
    if (org) {
      rememberOrg(org.id);
      router.replace(`/o/${org.id}`);
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
      <TextField
        label="Organization name"
        name="name"
        required
        maxLength={120}
        autoComplete="organization"
        error={fieldErrors.name}
      />
      <TextField label="Industry" name="industry" maxLength={120} error={fieldErrors.industry} />
      <SelectField
        label="Size"
        name="size_band"
        defaultValue=""
        error={fieldErrors.size_band}
        options={[
          { value: "", label: "Select…" },
          ...SIZE_BANDS.map((s) => ({ value: s, label: `${s} people` })),
        ]}
      />
      <TextField
        label="Website"
        name="website"
        type="url"
        placeholder="https://"
        error={fieldErrors.website}
      />
      <TextField
        label="Time zone"
        name="timezone"
        defaultValue={timezone}
        hint="IANA name, e.g. Europe/London"
        error={fieldErrors.timezone}
      />
      {create.error && Object.keys(fieldErrors).length === 0 ? (
        <ErrorPanel error={create.error} />
      ) : null}
      <Button type="submit" disabled={create.isPending}>
        {create.isPending ? "Creating…" : "Create organization"}
      </Button>
    </form>
  );
}
