(() => {
  const copyButtons = document.querySelectorAll("[data-copy-target]");

  copyButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const selector = button.getAttribute("data-copy-target");
      const target = selector ? document.querySelector(selector) : null;
      const snippet = target?.getAttribute("data-embed-snippet") || target?.textContent || "";
      if (!snippet.trim() || !navigator.clipboard) {
        return;
      }

      await navigator.clipboard.writeText(snippet.trim());
      const original = button.textContent;
      button.textContent = "Copied";
      window.setTimeout(() => {
        button.textContent = original;
      }, 1800);
    });
  });
})();
