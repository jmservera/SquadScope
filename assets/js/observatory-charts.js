(() => {
  const copyButtons = document.querySelectorAll("[data-copy-target]");

  copyButtons.forEach((button) => {
    button.addEventListener("click", async () => {
      const selector = button.getAttribute("data-copy-target");
      const target = selector ? document.querySelector(selector) : null;
      const snippet = target?.getAttribute("data-embed-snippet") || target?.textContent || "";
      const status = button.parentElement?.querySelector("[data-copy-status]");
      const updateStatus = (message, label) => {
        button.textContent = label;
        if (status) {
          status.textContent = message;
        }
      };
      if (!snippet.trim() || !navigator.clipboard) {
        updateStatus(
          "Copy failed. Select and copy the embed snippet manually.",
          "Copy failed",
        );
        return;
      }

      const original = button.textContent;
      try {
        await navigator.clipboard.writeText(snippet.trim());
        updateStatus("Embed snippet copied to the clipboard.", "Copied");
        window.setTimeout(() => {
          button.textContent = original;
        }, 1800);
      } catch {
        updateStatus(
          "Copy failed. Select and copy the embed snippet manually.",
          "Copy failed",
        );
        window.setTimeout(() => {
          button.textContent = original;
        }, 1800);
      }
    });
  });

  const tooltipWrappers = document.querySelectorAll("[data-observatory-tooltip]");
  let openTooltip = null;

  function closeTooltip(dismissed = false) {
    if (!openTooltip) {
      return;
    }
    const wrapper = openTooltip;
    openTooltip = null;
    const link = wrapper.querySelector("a");
    wrapper.classList.remove("is-open");
    wrapper.classList.toggle("is-dismissed", dismissed);
    link?.setAttribute("aria-expanded", "false");
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
      wrapper.classList.remove("is-dismissed");
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
      if (openTooltip === wrapper && link !== document.activeElement) {
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
      closeTooltip(true);
    }
  });

  document.addEventListener("click", (event) => {
    if (openTooltip && !openTooltip.contains(event.target)) {
      closeTooltip();
    }
  });
})();
