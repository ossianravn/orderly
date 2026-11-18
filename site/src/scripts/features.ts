// Feature switches: each turns its feature on or off in its own example.
export function initFeatures(): void {
  for (const input of document.querySelectorAll<HTMLInputElement>("[data-feature] input[data-tag]")) {
    const sample = input.closest("[data-feature]")?.querySelector<HTMLElement>(".sample");
    if (!sample) continue;
    input.addEventListener("change", () => {
      sample.style.fontFeatureSettings = `"${input.dataset.tag}" ${input.checked ? 1 : 0}`;
    });
  }
}
