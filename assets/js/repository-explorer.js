(function () {
  "use strict";

  const validSorts = new Set(["momentum", "stars", "appearances", "name"]);
  const validPeriods = new Set(["all", "current", "recent"]);

  function normalized(value) {
    return String(value || "").trim().toLowerCase();
  }

  function appendTextElement(parent, tag, className, text) {
    const element = document.createElement(tag);
    if (className) {
      element.className = className;
    }
    element.textContent = text;
    parent.appendChild(element);
    return element;
  }

  function githubUrl(value) {
    const parsed = new URL(value);
    if (parsed.protocol !== "https:" || parsed.hostname !== "github.com") {
      throw new Error(`Repository URL is outside GitHub: ${value}`);
    }
    return parsed.href;
  }

  function renderRecord(record, recentPeriods) {
    const item = document.createElement("li");
    const history = Array.isArray(record.star_history) ? record.star_history : [];
    const topics = Array.isArray(record.topics) ? record.topics : [];
    const latest = history.length ? Number(history[history.length - 1].stars) || 0 : 0;
    const momentum = Number(record.recent_momentum) || 0;
    item.className = "repository-index__record";
    item.setAttribute("data-repo-record", "");
    item.setAttribute("data-name", normalized(record.full_name));
    item.setAttribute(
      "data-search",
      normalized(`${record.full_name} ${record.context_summary} ${topics.join(" ")}`),
    );
    item.setAttribute("data-language", normalized(record.language));
    item.setAttribute("data-topics", normalized(topics.join("|")));
    item.setAttribute("data-status", normalized(record.status));
    item.setAttribute("data-last-period", record.last_seen_period || "");
    item.setAttribute(
      "data-recent",
      recentPeriods.has(record.last_seen_period) ? "true" : "false",
    );
    item.setAttribute("data-momentum", String(momentum));
    item.setAttribute("data-stars", String(latest));
    item.setAttribute("data-appearances", String(history.length));

    const details = document.createElement("div");
    const heading = appendTextElement(details, "h3", "repository-index__heading", "");
    const link = document.createElement("a");
    link.href = githubUrl(record.github_url);
    link.rel = "noopener";
    link.textContent = record.full_name;
    heading.appendChild(link);
    appendTextElement(
      details,
      "p",
      "repository-index__summary",
      record.context_summary || "No summary available.",
    );
    const evidence = appendTextElement(details, "p", "repository-index__evidence", "");
    [
      record.language || "Language unavailable",
      record.status,
      `${record.first_seen_period}–${record.last_seen_period}`,
      `${history.length} weekly observations`,
    ].forEach((value) => appendTextElement(evidence, "span", "", value));
    item.appendChild(details);

    const signal = document.createElement("div");
    signal.className = "repository-index__signal";
    signal.setAttribute(
      "aria-label",
      `${momentum} stars of recent observed momentum`,
    );
    appendTextElement(
      signal,
      "strong",
      "",
      `${momentum >= 0 ? "+" : ""}${new Intl.NumberFormat().format(momentum)}`,
    );
    appendTextElement(signal, "span", "", "4-week signal");
    item.appendChild(signal);
    return item;
  }

  function addOptions(select, values) {
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    });
  }

  function numberValue(item, name) {
    return Number(item.getAttribute(name)) || 0;
  }

  function setSelect(select, value, allowed) {
    if (allowed.has(value)) {
      select.value = value;
    }
  }

  function readState(root) {
    const params = new URLSearchParams(window.location.search);
    const controls = {
      search: root.querySelector("[data-repo-search]"),
      language: root.querySelector("[data-repo-language]"),
      topic: root.querySelector("[data-repo-topic]"),
      status: root.querySelector("[data-repo-status]"),
      period: root.querySelector("[data-repo-period]"),
      sort: root.querySelector("[data-repo-sort]"),
    };
    controls.search.value = params.get("q") || "";
    controls.language.value = params.get("language") || "";
    controls.topic.value = params.get("topic") || "";
    controls.status.value = params.get("status") || "";
    setSelect(controls.period, params.get("period") || "all", validPeriods);
    setSelect(controls.sort, params.get("sort") || "momentum", validSorts);
    return controls;
  }

  function writeState(controls, mode) {
    const params = new URLSearchParams();
    const entries = [
      ["q", controls.search.value],
      ["language", controls.language.value],
      ["topic", controls.topic.value],
      ["status", controls.status.value],
    ];
    entries.forEach(([name, value]) => {
      if (value) {
        params.set(name, value);
      }
    });
    if (controls.period.value !== "all") {
      params.set("period", controls.period.value);
    }
    if (controls.sort.value !== "momentum") {
      params.set("sort", controls.sort.value);
    }
    const query = params.toString();
    window.history[mode]({}, "", `${window.location.pathname}${query ? `?${query}` : ""}`);
  }

  function matchesPeriod(item, value, latestPeriod) {
    if (value === "current") {
      return item.getAttribute("data-last-period") === latestPeriod;
    }
    if (value === "recent") {
      return item.getAttribute("data-recent") === "true";
    }
    return true;
  }

  function comparator(sort) {
    if (sort === "name") {
      return (left, right) =>
        left.getAttribute("data-name").localeCompare(right.getAttribute("data-name"));
    }
    const attribute = {
      appearances: "data-appearances",
      momentum: "data-momentum",
      stars: "data-stars",
    }[sort];
    return (left, right) => {
      const difference = numberValue(right, attribute) - numberValue(left, attribute);
      return difference || left.getAttribute("data-name").localeCompare(right.getAttribute("data-name"));
    };
  }

  function apply(root, controls, historyMode) {
    const list = root.querySelector("[data-repo-results]");
    const status = root.querySelector("[data-repo-result-status]");
    const latestPeriod = root.getAttribute("data-latest-period");
    const query = normalized(controls.search.value);
    const language = normalized(controls.language.value);
    const topic = normalized(controls.topic.value);
    const lifecycle = normalized(controls.status.value);
    const items = Array.from(list.querySelectorAll("[data-repo-record]"));
    const visible = items.filter((item) => {
      const haystack = normalized(item.getAttribute("data-search"));
      const topics = normalized(item.getAttribute("data-topics")).split("|");
      return (
        (!query || haystack.includes(query)) &&
        (!language || normalized(item.getAttribute("data-language")) === language) &&
        (!topic || topics.includes(topic)) &&
        (!lifecycle || normalized(item.getAttribute("data-status")) === lifecycle) &&
        matchesPeriod(item, controls.period.value, latestPeriod)
      );
    });

    const visibleSet = new Set(visible);
    items.forEach((item) => {
      item.hidden = !visibleSet.has(item);
    });
    visible.sort(comparator(controls.sort.value)).forEach((item) => list.appendChild(item));
    status.textContent = visible.length
      ? `Showing ${visible.length} of ${items.length} repositories.`
      : "No repositories match these filters. Reset filters to return to the full index.";
    if (historyMode) {
      writeState(controls, historyMode);
    }
  }

  function initRepositoryExplorer(root) {
    let controls = readState(root);
    let searchHistoryTimer;
    root.addEventListener("input", () => {
      apply(root, controls, null);
      window.clearTimeout(searchHistoryTimer);
      searchHistoryTimer = window.setTimeout(() => writeState(controls, "pushState"), 300);
    });
    root.addEventListener("change", () => apply(root, controls, "pushState"));
    root.querySelector("[data-repo-reset]").addEventListener("click", () => {
      controls.search.value = "";
      controls.language.value = "";
      controls.topic.value = "";
      controls.status.value = "";
      controls.period.value = "all";
      controls.sort.value = "momentum";
      apply(root, controls, "pushState");
      controls.search.focus();
    });
    window.addEventListener("popstate", () => {
      controls = readState(root);
      apply(root, controls, null);
    });
    apply(root, controls, "replaceState");
  }

  async function loadRepositoryExplorer(root) {
    const status = root.querySelector("[data-repo-result-status]");
    try {
      const response = await fetch(root.getAttribute("data-repository-data-url"), {
        credentials: "same-origin",
      });
      if (!response.ok) {
        throw new Error(`Repository dataset returned HTTP ${response.status}`);
      }
      const payload = await response.json();
      if (!payload || !Array.isArray(payload.records)) {
        throw new Error("Repository dataset has no records array");
      }
      const periods = Array.from(
        new Set(payload.records.map((record) => record.last_seen_period).filter(Boolean)),
      ).sort().reverse();
      const latestPeriod = periods[0] || "";
      const recentPeriods = new Set(periods.slice(0, 4));
      root.setAttribute("data-latest-period", latestPeriod);
      root.querySelector("[data-repo-covered-period]").textContent =
        payload.covered_period?.label || "Observation window unavailable";
      root.querySelector("[data-repo-current-period]").textContent =
        latestPeriod ? `Seen in ${latestPeriod}` : "Seen in latest period";

      addOptions(
        root.querySelector("[data-repo-language]"),
        Array.from(
          new Set(payload.records.map((record) => record.language).filter(Boolean)),
        ).sort(),
      );
      addOptions(
        root.querySelector("[data-repo-topic]"),
        Array.from(
          new Set(payload.records.flatMap((record) => record.topics || [])),
        ).sort(),
      );
      const list = root.querySelector("[data-repo-results]");
      const fragment = document.createDocumentFragment();
      payload.records.forEach((record) =>
        fragment.appendChild(renderRecord(record, recentPeriods)),
      );
      list.replaceChildren(fragment);
      initRepositoryExplorer(root);
    } catch (error) {
      status.textContent =
        "Repository data could not be loaded. Open the dataset link or try again.";
      root.setAttribute("data-load-error", "");
      console.error(error);
    }
  }

  window.initRepositoryExplorer = initRepositoryExplorer;
  window.loadRepositoryExplorer = loadRepositoryExplorer;
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-repository-explorer]").forEach(loadRepositoryExplorer);
  });
})();
