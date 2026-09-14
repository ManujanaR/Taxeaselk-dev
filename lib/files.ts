// Client-side pre-validation of picked files. The backend enforces the same rules.
export const ACCEPTED_EXTENSIONS = [".pdf", ".xlsx", ".xls", ".csv", ".png", ".jpg", ".jpeg"];
export const ACCEPT_ATTR = ACCEPTED_EXTENSIONS.join(",");
export const MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024;

export function validateFiles(files: FileList | File[]): { valid: File[]; rejected: { fileName: string; reason: string }[] } {
  const valid: File[] = [];
  const rejected: { fileName: string; reason: string }[] = [];
  Array.from(files).forEach((file) => {
    const ext = "." + (file.name.split(".").pop()?.toLowerCase() ?? "");
    if (!ACCEPTED_EXTENSIONS.includes(ext)) rejected.push({ fileName: file.name, reason: `Unsupported type (${ext}). Use PDF, XLSX, XLS, CSV, PNG or JPG.` });
    else if (file.size === 0) rejected.push({ fileName: file.name, reason: "File is empty (0 bytes)." });
    else if (file.size > MAX_FILE_SIZE_BYTES) rejected.push({ fileName: file.name, reason: `Too large (${(file.size / 1024 / 1024).toFixed(1)} MB). Max 10 MB.` });
    else valid.push(file);
  });
  return { valid, rejected };
}
