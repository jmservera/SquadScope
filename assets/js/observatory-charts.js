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

      try {
        await navigator.clipboard.writeText(snippet.trim());
        const original = button.textContent;
        button.textContent = "Copied";
        window.setTimeout(() => {
          button.textContent = original;
        }, 1800);
      } catch {
        button.textContent = "Copy failed";
        window.setTimeout(() => {
          button.textContent = "Copy embed snippet";
        }, 1800);
      }
    });
  });

  const tooltipWrappers = document.querySelectorAll("[data-observatory-tooltip]");
  let openTooltip = null;

  function closeTooltip() {
    if (!openTooltip) {
      return;
    }
    openTooltip.classList.remove("is-open");
    openTooltip.querySelector("a")?.setAttribute("aria-expanded", "false");
    openTooltip = null;
  }

  tooltipWrappers.forEach((wrapper) => {
    const link = wrapper.querySelector("a");
    if (!link) {
      return;
    }
    const open = () => {
      if (openTooltip && openTooltip !== wrapper) {
        closeTooltip();
      }
      wrapper.classList.add("is-open");
      link.setAttribute("aria-expanded", "true");
      openTooltip = wrapper;
    };

    link.addEventListener("focus", open);
    link.addEventListener("mouseenter", open);
    link.addEventListener("blur", () => {
      if (openTooltip === wrapper) {
        closeTooltip();
      }
    });
    link.addEventListener("mouseleave", () => {
      if (openTooltip === wrapper) {
        closeTooltip();
      }
    });
    link.addEventListener("touchstart", (event) => {
      if (openTooltip !== wrapper) {
        event.preventDefault();
        open();
      }
    });
    link.addEventListener("click", (event) => {
      if (window.matchMedia("(hover: none)").matches && openTooltip !== wrapper) {
        event.preventDefault();
        open();
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeTooltip();
    }
  });

  document.addEventListener("click", (event) => {
    if (openTooltip && !openTooltip.contains(event.target)) {
      closeTooltip();
    }
  });
})();
