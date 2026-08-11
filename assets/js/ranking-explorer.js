(function () {
  "use strict";

  const SCHEMA_VERSION = "1.0.0";
  const VALID_SORTS = new Set(["rank", "metric", "name"]);

  function normalized(value) {
    return String(value || "").trim().toLowerCase();
  }

  function qs(root, selector) {
    return root.querySelector(selector);
  }

  function setHidden(element, hidden) {
    if (element) {
      element.hidden = hidden;
    }
  }

  function hideMessages(root) {
    [
      "[data-ranking-error]",
      "[data-ranking-unavailable]",
      "[data-ranking-future-version]",
      "[data-ranking-empty]",
    ].forEach((selector) => setHidden(qs(root, selector), true));
  }

  function validGithubUrl(value) {
    const parsed = new URL(value);
    const segments = parsed.pathname.split("/").filter(Boolean);
    if (
      parsed.protocol !== "https:" ||
      parsed.host !== "github.com" ||
      parsed.username ||
      parsed.password ||
      parsed.search ||
      parsed.hash ||
      segments.length !== 2
    ) {
      throw new Error(`Repository URL is outside GitHub: ${value}`);
    }
    return `https://github.com/${segments[0]}/${segments[1]}`;
  }

  function readState(root) {
    const params = new URLSearchParams(window.location.search);
    const search = qs(root, "[data-ranking-search]");
    const language = qs(root, "[data-ranking-language]");
    const sort = qs(root, "[data-ranking-sort]");
    const next = {
      q: params.get("q") || "",
      lang: params.get("lang") || "",
      sort: params.get("sort") || "rank",
    };
    if (!VALID_SORTS.has(next.sort)) {
      next.sort = "rank";
    }
    search.value = next.q;
    language.value = next.lang;
    next.lang = language.value;
    sort.value = next.sort;
    return next;
  }

  function writeState(state) {
    const params = new URLSearchParams();
    if (state.lang) {
      params.set("lang", state.lang);
    }
    if (state.sort && state.sort !== "rank") {
      params.set("sort", state.sort);
    }
    if (state.q) {
      params.set("q", state.q);
    }
    const query = params.toString();
    const target = `${window.location.pathname}${query ? `?${query}` : ""}`;
    window.history.replaceState({}, "", target);
  }

  function populateLanguages(select, records) {
    const values = Array.from(new Set(records.map((record) => record.language).filter(Boolean))).sort();
    select.querySelectorAll("option:not([value=''])").forEach((option) => option.remove());
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    });
  }

  function normalizeRecord(record) {
    return {
      rank: Number(record.rank) || 0,
      full_name: String(record.full_name || ""),
      github_url: validGithubUrl(record.github_url),
      metric_value: Number(record.metric_value) || 0,
      metric_label: String(record.metric_label || ""),
      comparison_label: String(record.comparison_label || ""),
      language: String(record.language || "Unknown"),
      context_summary: String(record.context_summary || "No summary available."),
      context_accessible_text: String(
        record.context_accessible_text || record.context_summary || "No summary available.",
      ),
    };
  }

  function comparator(sort) {
    if (sort === "name") {
      return (left, right) => left.full_name.localeCompare(right.full_name);
    }
    if (sort === "metric") {
      return (left, right) => right.metric_value - left.metric_value || left.full_name.localeCompare(right.full_name);
    }
    return (left, right) => left.rank - right.rank || left.full_name.localeCompare(right.full_name);
  }

  function tooltipId(root, record) {
    const base = root.getAttribute("data-ranking-id") || "ranking";
    return `ctx-${base}-${record.rank}-${record.full_name.replace(/[^a-z0-9]+/gi, "-").toLowerCase()}`;
  }

  function createTooltipWrapper(root, record) {
    const wrapper = document.createElement("span");
    wrapper.className = "ranking-table__repo-trigger";
    wrapper.setAttribute("data-ranking-tooltip", "");

    const link = document.createElement("a");
    const id = tooltipId(root, record);
    link.href = record.github_url;
    link.rel = "noopener";
    link.className = "ranking-table__repo-link";
    link.textContent = record.full_name;
    link.setAttribute("data-repo-name", record.full_name);
    link.setAttribute("data-context-summary", record.context_summary);
    link.setAttribute("aria-describedby", id);

    const tooltip = document.createElement("span");
    tooltip.id = id;
    tooltip.className = "ranking-table__context-tooltip";
    tooltip.setAttribute("role", "tooltip");
    const visibleSummary = document.createElement("span");
    visibleSummary.setAttribute("aria-hidden", "true");
    visibleSummary.textContent = record.context_summary;
    const accessibleSummary = document.createElement("span");
    accessibleSummary.className = "visually-hidden";
    accessibleSummary.textContent = record.context_accessible_text;
    tooltip.appendChild(visibleSummary);
    tooltip.appendChild(accessibleSummary);

    wrapper.appendChild(link);
    wrapper.appendChild(tooltip);
    return wrapper;
  }

  function renderCards(root, records) {
    const container = document.createElement("ol");
    container.className = "ranking-results";
    records.forEach((record) => {
      const item = document.createElement("li");
      item.className = "ranking-results__item";

      const head = document.createElement("div");
      head.className = "ranking-results__head";
      const badge = document.createElement("span");
      badge.className = "ranking-results__rank";
      badge.textContent = `#${record.rank}`;
      head.appendChild(badge);

      const repo = document.createElement("div");
      repo.className = "ranking-results__repo";
      const heading = document.createElement("h3");
      heading.className = "ranking-results__title";
      heading.appendChild(createTooltipWrapper(root, record));
      repo.appendChild(heading);

      const meta = document.createElement("div");
      meta.className = "ranking-results__meta";
      const metric = document.createElement("span");
      metric.className = "ranking-results__metric";
      metric.textContent = record.metric_label;
      meta.appendChild(metric);
      const language = document.createElement("span");
      language.className = "ranking-results__language";
      language.textContent = record.language;
      meta.appendChild(language);
      if (record.comparison_label) {
        const comparison = document.createElement("span");
        comparison.className = "ranking-results__comparison";
        comparison.textContent = record.comparison_label;
        meta.appendChild(comparison);
      }
      repo.appendChild(meta);

      const context = document.createElement("p");
      context.className = "ranking-results__context";
      context.textContent = record.context_summary;
      repo.appendChild(context);

      head.appendChild(repo);
      item.appendChild(head);
      container.appendChild(item);
    });
    return container;
  }

  function positionTooltip(wrapper) {
    const tooltip = wrapper.querySelector("[role='tooltip']");
    if (!tooltip) {
      return;
    }
    tooltip.dataset.align = "end";
    tooltip.dataset.placement = window.innerWidth < 600 ? "below" : "side";
    const rect = tooltip.getBoundingClientRect();
    if (window.innerWidth >= 600 && rect.right > window.innerWidth - 16) {
      tooltip.dataset.align = "start";
    }
    if (rect.bottom > window.innerHeight - 16) {
      tooltip.dataset.placement = "above";
    }
    if (rect.top < 16) {
      tooltip.dataset.placement = "below";
    }
  }

  function initTooltips(root) {
    function closeOpenTooltip() {
      if (root.__rankingOpenWrapper) {
        root.__rankingOpenWrapper.classList.remove("is-open");
        const link = root.__rankingOpenWrapper.querySelector("a");
        if (link) {
          link.removeAttribute("aria-expanded");
        }
      }
      root.__rankingOpenWrapper = null;
    }

    root.querySelectorAll("[data-ranking-tooltip]").forEach((wrapper) => {
      if (wrapper.dataset.rankingTooltipBound === "true") {
        return;
      }
      wrapper.dataset.rankingTooltipBound = "true";
      const link = wrapper.querySelector("a");
      if (!link) {
        return;
      }

      const show = (persist) => {
        if (
          persist &&
          root.__rankingOpenWrapper &&
          root.__rankingOpenWrapper !== wrapper
        ) {
          closeOpenTooltip();
        }
        if (persist) {
          wrapper.classList.add("is-open");
          link.setAttribute("aria-expanded", "true");
          root.__rankingOpenWrapper = wrapper;
        }
        window.requestAnimationFrame(() => positionTooltip(wrapper));
      };

      wrapper.addEventListener("mouseenter", () => show(false));
      wrapper.addEventListener("focusin", () => show(false));
      wrapper.addEventListener("touchstart", (event) => {
        if (!wrapper.classList.contains("is-open")) {
          event.preventDefault();
          show(true);
        }
      }, { passive: false });

      link.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          closeOpenTooltip();
          link.blur();
        }
      });
    });

    if (root.__rankingTooltipDocumentBound) {
      return;
    }
    root.__rankingTooltipDocumentBound = true;
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        closeOpenTooltip();
      }
    });

    document.addEventListener("click", (event) => {
      if (
        root.__rankingOpenWrapper &&
        !root.__rankingOpenWrapper.contains(event.target)
      ) {
        closeOpenTooltip();
      }
    });
  }

  function apply(root, payload, state) {
    const list = qs(root, "[data-ranking-list]");
    const empty = qs(root, "[data-ranking-empty]");
    const status = qs(root, "[data-ranking-status]");
    const query = normalized(state.q);
    const language = normalized(state.lang);

    hideMessages(root);
    const visible = payload.records
      .filter((record) => {
        const haystack = normalized(`${record.full_name} ${record.context_summary} ${record.language}`);
        return (!language || normalized(record.language) === language) && (!query || haystack.includes(query));
      })
      .sort(comparator(state.sort));

    list.replaceChildren(renderCards(root, visible));
    setHidden(empty, visible.length !== 0);
    status.textContent = visible.length
      ? `Showing ${visible.length} of ${payload.records.length} repositories.`
      : "No repositories match the current filters.";
    initTooltips(list);
    writeState(state);
  }

  async function loadRankingExplorer(root) {
    const rankingId = root.getAttribute("data-ranking-id");
    const loading = qs(root, "[data-ranking-loading]");
    const error = qs(root, "[data-ranking-error]");
    const unavailable = qs(root, "[data-ranking-unavailable]");
    const future = qs(root, "[data-ranking-future-version]");
    const language = qs(root, "[data-ranking-language]");
    const search = qs(root, "[data-ranking-search]");
    const sort = qs(root, "[data-ranking-sort]");
    const reset = qs(root, "[data-ranking-reset]");
    const status = qs(root, "[data-ranking-status]");

    hideMessages(root);
    setHidden(loading, false);
    root.setAttribute("aria-busy", "true");

    try {
      const response = await fetch(`/data/rankings/${rankingId}.json`, { credentials: "same-origin" });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      let payload;
      try {
        payload = await response.json();
      } catch (jsonError) {
        setHidden(error, false);
        status.textContent = "Unable to parse ranking data.";
        return;
      }
      if (!payload || payload.schema_version !== SCHEMA_VERSION) {
        setHidden(future, false);
        status.textContent = "This viewer does not support the available ranking dataset version.";
        return;
      }
      if (!Array.isArray(payload.records)) {
        setHidden(error, false);
        status.textContent = "Ranking data is malformed.";
        return;
      }

      try {
        payload.records = payload.records.map(normalizeRecord);
      } catch (normalizationError) {
        console.error(normalizationError);
        setHidden(error, false);
        status.textContent = "Ranking data is malformed.";
        return;
      }
      populateLanguages(language, payload.records);
      const state = readState(root);
      apply(root, payload, state);

      search.addEventListener("input", () => {
        state.q = search.value.trim();
        apply(root, payload, state);
      });
      language.addEventListener("change", () => {
        state.lang = language.value;
        apply(root, payload, state);
      });
      sort.addEventListener("change", () => {
        state.sort = VALID_SORTS.has(sort.value) ? sort.value : "rank";
        apply(root, payload, state);
      });
      reset.addEventListener("click", () => {
        state.q = "";
        state.lang = "";
        state.sort = "rank";
        search.value = "";
        language.value = "";
        sort.value = "rank";
        apply(root, payload, state);
        search.focus();
      });
    } catch (networkError) {
      console.error(networkError);
      setHidden(unavailable, false);
      status.textContent = "Ranking data is unavailable; the server-rendered table remains available below.";
    } finally {
      setHidden(loading, true);
      root.removeAttribute("aria-busy");
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-ranking-explorer]").forEach(loadRankingExplorer);
  });
})();
