import type { QueryKey } from "@tanstack/svelte-query";

export async function apiRequest<ResponseModel>({ queryKey }: any) {
  const response = await window.fetch("/api" + queryKey.join(""));
  if (response.ok) {
    return (await response.json()) as ResponseModel;
  } else {
    throw new Error("Could not fetch data");
  }
}
