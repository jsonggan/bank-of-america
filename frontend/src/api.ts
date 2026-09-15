export async function api<T>(path: string, body?: string): Promise<T> {
  let response: Response;
  try { response = await fetch(`/api${path}`, body === undefined ? undefined : { method: "POST", headers: { "Content-Type": "application/json" }, body }); }
  catch { throw new Error("Cannot reach the API. Start the backend and try again."); }
  let data; try { data = await response.json(); } catch { throw new Error(`API returned HTTP ${response.status}. Check that the backend is running.`); }
  if (!response.ok) throw new Error(data.errors?.map((error: { path: string; reason: string }) => `${error.path}: ${error.reason}`).join(" ? ") || `Request failed (HTTP ${response.status}).`);
  return data as T;
}
