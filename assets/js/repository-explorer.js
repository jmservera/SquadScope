(function () {
  "use strict";

  const validSorts = new Set(["momentum", "stars", "appearances", "name"]);
  const validPeriods = new Set(["all", "current", "recent"]);

  function normalized(value) {
    return String(value || "").trim().toLowerCase();
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

  window.initRepositoryExplorer = initRepositoryExplorer;
  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-repository-explorer]").forEach(initRepositoryExplorer);
  });
})();
