(() => {
  "use strict";

  const eventFields = {
    dataset_download: ["dataset_id", "path"],
    chart_embed_view: ["chart_id", "path", "referrer_host"],
    tool_interaction: ["tool_id", "action", "path"],
  };
  const toolActions = new Set([
    "load",
    "search",
    "language_filter",
    "topic_filter",
    "repository_open",
  ]);
  const viewedCharts = new WeakSet();
  let analyticsConsent = false;

  function normalizeId(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[^a-z0-9-]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 64);
  }

  function normalizePath(value) {
    try {
      const url = new URL(String(value || ""), window.location.origin);
      if (url.origin !== window.location.origin) {
        return "";
      }
      return url.pathname.replace(/\/{2,}/g, "/").slice(0, 200);
    } catch {
      return "";
    }
  }

  function normalizeHost(value) {
    const host = String(value || "").toLowerCase();
    return /^[a-z0-9.-]{1,253}$/.test(host) ? host : "";
  }

  function sanitizePayload(eventName, values) {
    const allowedFields = eventFields[eventName];
    if (!allowedFields) {
      return null;
    }

    const payload = {};
    allowedFields.forEach((field) => {
      let value = values[field];
      if (field.endsWith("_id")) {
        value = normalizeId(value);
      } else if (field === "path") {
        value = normalizePath(value);
      } else if (field === "referrer_host") {
        value = normalizeHost(value);
      } else if (field === "action") {
        value = toolActions.has(value) ? value : "";
      }

      if (value) {
        payload[field] = value;
      }
    });
    return payload;
  }

  function track(eventName, values = {}) {
    if (!analyticsConsent || typeof window.gtag !== "function") {
      return false;
    }

    const payload = sanitizePayload(eventName, values);
    if (!payload) {
      return false;
    }

    window.gtag("event", eventName, payload);
    return true;
  }

  function referrerHost() {
    try {
      return new URL(document.referrer).hostname;
    } catch {
      return "";
    }
  }

  function trackChartViews(root = document) {
    root
      .querySelectorAll('[data-observatory-embed="true"][data-observatory-chart-id]')
      .forEach((chart) => {
        if (viewedCharts.has(chart)) {
          return;
        }
        const dispatched = track("chart_embed_view", {
          chart_id: chart.getAttribute("data-observatory-chart-id"),
          path: window.location.pathname,
          referrer_host: referrerHost(),
        });
        if (dispatched) {
          viewedCharts.add(chart);
        }
      });
  }

  function setConsent(enabled) {
    analyticsConsent = enabled === true;
    if (analyticsConsent) {
      trackChartViews();
    }
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest("a[href]");
    if (!link) {
      return;
    }

    let url;
    try {
      url = new URL(link.href, window.location.origin);
    } catch {
      return;
    }
    if (url.origin !== window.location.origin || !url.pathname.startsWith("/datasets/")) {
      return;
    }

    const datasetId = url.pathname.split("/").filter(Boolean)[1];
    track("dataset_download", {
      dataset_id: datasetId,
      path: url.pathname,
    });
  });

  window.ObservatoryAnalytics = Object.freeze({
    setConsent,
    track,
    trackChartViews,
  });
})();
