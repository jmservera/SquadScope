(function () {
  "use strict";

  const numberFormatter = new Intl.NumberFormat("en-US");

  function setStatus(root, message) {
    const status = root.querySelector("[data-trend-status]");
    if (status) {
      status.textContent = message;
    }
  }

  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function isValidPayload(payload) {
    return payload && Array.isArray(payload.repositories);
  }

  function renderFilters(root, payload) {
    const languageSelect = root.querySelector("[data-trend-language]");
    const topicSelect = root.querySelector("[data-trend-topic]");
    if (!languageSelect || !topicSelect) {
      return;
    }

    asArray(payload.language_filters).forEach((language) => {
      const option = document.createElement("option");
      option.value = String(language);
      option.textContent = String(language);
      languageSelect.appendChild(option);
    });

    asArray(payload.topic_filters).forEach((topic) => {
      const option = document.createElement("option");
      option.value = String(topic);
      option.textContent = String(topic);
      topicSelect.appendChild(option);
    });
  }

  function metric(value) {
    return numberFormatter.format(Number.isFinite(value) ? value : 0);
  }

  function safeGitHubUrl(value) {
    try {
      const parsed = new URL(String(value || ""), window.location.origin);
      if (parsed.protocol === "https:" && parsed.hostname === "github.com") {
        return parsed.href;
      }
    } catch (error) {
      return "#";
    }
    return "#";
  }

  function renderRows(root, repositories) {
    const list = root.querySelector("[data-trend-results]");
    if (!list) {
      return;
    }
    list.textContent = "";

    repositories.slice(0, 25).forEach((repo, index) => {
      const item = document.createElement("li");
      item.className = "trend-explorer__result";

      const title = document.createElement("a");
      title.href = safeGitHubUrl(repo.url);
      title.textContent = `${index + 1}. ${repo.repository || "Unknown repository"}`;
      title.rel = "noopener";

      const meta = document.createElement("p");
      meta.textContent = `${repo.primary_language || "Unknown"} · +${metric(
        Number(repo.observed_star_change),
      )} stars observed · ${metric(Number(repo.latest_stars))} latest stars`;

      const sparkline = document.createElement("div");
      sparkline.className = "trend-explorer__sparkline";
      sparkline.setAttribute("aria-label", "Observed star history");
      asArray(repo.series).forEach((point) => {
        const bar = document.createElement("span");
        bar.title = `${point.week}: ${metric(Number(point.stars))} stars`;
        bar.style.height = `${Math.max(6, Math.min(100, Number(point.stars) / 2500))}%`;
        sparkline.appendChild(bar);
      });

      item.append(title, meta, sparkline);
      list.appendChild(item);
    });
  }

  function applyFilters(root, payload) {
    const search = root.querySelector("[data-trend-search]");
    const language = root.querySelector("[data-trend-language]");
    const topic = root.querySelector("[data-trend-topic]");
    const query = String(search && search.value ? search.value : "").trim().toLowerCase();
    const selectedLanguage = String(language && language.value ? language.value : "");
    const selectedTopic = String(topic && topic.value ? topic.value : "");

    const repositories = asArray(payload.repositories).filter((repo) => {
      const topics = asArray(repo.top_topics).map((item) => String(item));
      const matchesQuery =
        !query ||
        String(repo.repository || "").toLowerCase().includes(query) ||
        String(repo.description || "").toLowerCase().includes(query);
      const matchesLanguage = !selectedLanguage || repo.primary_language === selectedLanguage;
      const matchesTopic = !selectedTopic || topics.includes(selectedTopic);
      return matchesQuery && matchesLanguage && matchesTopic;
    });

    renderRows(root, repositories);
    setStatus(
      root,
      repositories.length
        ? `Showing ${Math.min(25, repositories.length)} of ${repositories.length} matching repositories.`
        : "No repositories match those filters.",
    );
  }

  async function initTrendExplorer(root) {
    const dataUrl = root.getAttribute("data-source");
    if (!dataUrl) {
      setStatus(root, "Trend data source is missing.");
      return;
    }

    try {
      const response = await fetch(dataUrl, { credentials: "same-origin" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const payload = await response.json();
      if (!isValidPayload(payload)) {
        setStatus(root, "Trend data is malformed, so the explorer is unavailable.");
        return;
      }
      if (payload.repositories.length === 0) {
        setStatus(root, "No trend data is available yet.");
        return;
      }

      renderFilters(root, payload);
      ["input", "change"].forEach((eventName) => {
        root.addEventListener(eventName, () => applyFilters(root, payload));
      });
      applyFilters(root, payload);
    } catch (error) {
      setStatus(root, "Trend data could not be loaded. Try again later.");
    }
  }

  window.initTrendExplorer = initTrendExplorer;

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-trend-explorer]").forEach((root) => {
      initTrendExplorer(root);
    });
  });
})();
