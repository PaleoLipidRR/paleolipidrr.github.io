// assets/js/cv.js
// Behaviour of the CV page (/cv/), loaded with defer by _layouts/cv_page.liquid only. Plain JavaScript, no dependencies.
//
// Without this script every section shows, one after another, the panel links are in-page jumps and the filter bar
// stays hidden. With it:
// - one section at a time: the address (#<section id> or #<entry id>) picks the section; with no usable address the
//   wrapper's data-landing section shows. Panel clicks switch sections and push the address, so back and forward work.
// - the publication filters filter the cards of the section that holds the bar.
// - "Show all": in a section with data-collapse-after="N", each group shows its first N cards and a button for the rest.
// - printing shows every section, every card and every <details>, and puts the page back afterwards.
//
// Filters and "Show all" compose by one rule: a card is hidden when the active filter rejects it, or when it is past a
// "Show all" cut and the filter is "all". While a filter other than "all" is active, every matching card shows,
// cut or not, and the section's "Show all" buttons are hidden.
//
// The script does nothing when the page's elements are missing, and it never reads the address with querySelector.
(() => {
  "use strict";

  const CUT = "data-cv-cut"; // a card hidden by "Show all", until its group is expanded
  const PAPER_STATUSES = ["published", "under-review"];

  // --- Pure decisions -------------------------------------------------------------------------------------------

  // The id named by an address hash ("#a%20b" -> "a b"); a malformed escape is kept as written, never thrown.
  function idFromHash(hash) {
    const raw = (hash || "").replace(/^#/, "");
    try {
      return decodeURIComponent(raw);
    } catch (error) {
      return raw;
    }
  }

  // What an id points at: { section, card }, both possibly null. `byId` looks an id up; `isSection` and `isCard` say
  // what an element is; `sectionOf` finds the section holding an element. An id that exists but is neither a section
  // nor a card (a "-heading" or "-title" id, say) resolves to the section that holds it.
  function resolveId(id, lookup) {
    const element = id ? lookup.byId(id) : null;
    if (!element) return { section: null, card: null };
    if (lookup.isSection(element)) return { section: element, card: null };
    const section = lookup.sectionOf(element);
    if (!section) return { section: null, card: null };
    return { section, card: lookup.isCard(element) ? element : null };
  }

  // Whether a card with these data attributes passes a filter. Only papers (data-status "published" or "under-review")
  // pass a filter other than "all"; the technical report, which has no data-status, shows only under "all".
  function matchesFilter(filter, status, firstAuthor) {
    if (filter === "all") return true;
    if (!PAPER_STATUSES.includes(status)) return false;
    if (filter === "first-author") return firstAuthor === "true";
    if (filter === "co-author") return firstAuthor === "false";
    return status === filter;
  }

  // --- The page -------------------------------------------------------------------------------------------------

  function init() {
    const page = document.querySelector(".cv-page");
    const sections = page ? Array.from(page.querySelectorAll("section.cv-section[id]")) : [];
    if (!page || sections.length === 0) return;

    const nav = page.querySelector(".cv-nav");
    const navLinks = nav ? Array.from(nav.querySelectorAll("a.cv-nav-link[data-section]")) : [];
    const live = page.querySelector(".cv-live");
    const bar = page.querySelector(".cv-filters");
    const filterSection = bar ? bar.closest("section.cv-section") : null;
    const filterButtons = bar ? Array.from(bar.querySelectorAll("button.cv-filter[data-filter]")) : [];
    const landingId = page.getAttribute("data-landing");
    const landing = sections.find((s) => s.id === landingId) || sections[0];
    const lookup = {
      byId: (id) => {
        const element = document.getElementById(id);
        return element && page.contains(element) ? element : null;
      },
      isSection: (element) => sections.includes(element),
      isCard: (element) => element.classList.contains("cv-card"),
      sectionOf: (element) => sections.find((s) => s.contains(element)) || null,
    };

    let active = null;
    let activeFilter = "all";
    let lastHash = null;
    let closedForPrint = null;

    const motion = () => (window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth");
    const clearance = () => parseFloat(getComputedStyle(page).getPropertyValue("--cv-navbar-clearance")) || 76;
    const cardsOf = (group) => Array.from(group.children).filter((c) => c.classList.contains("cv-card"));
    const groupsOf = (section) => Array.from(section.querySelectorAll(".cv-group"));
    const filterIsOn = (section) => section === filterSection && activeFilter !== "all";

    // Which cards, group headings and "Show all" buttons of a section show, from the filter and the cuts.
    function applyVisibility(section) {
      const filtering = filterIsOn(section);
      for (const group of groupsOf(section)) {
        const cards = cardsOf(group);
        for (const card of cards) {
          const rejected =
            section === filterSection && !matchesFilter(activeFilter, card.getAttribute("data-status"), card.getAttribute("data-first-author"));
          card.hidden = rejected || (card.hasAttribute(CUT) && !filtering);
        }
        const title = group.querySelector(":scope > .cv-group-title");
        if (title) title.hidden = cards.length > 0 && cards.every((c) => c.hidden);
        const button = group.querySelector(":scope > .cv-show-all");
        if (button) button.hidden = filtering;
      }
    }

    // Keeps the active panel link visible inside the panel (the phone's horizontal row, or a tall panel) without
    // scrolling the page itself.
    function revealNavLink(link) {
      if (!nav || !link) return;
      const box = nav.getBoundingClientRect();
      const r = link.getBoundingClientRect();
      let left = nav.scrollLeft;
      let top = nav.scrollTop;
      if (r.left < box.left || r.right > box.right) left += r.left - box.left - (box.width - r.width) / 2;
      if (r.top < box.top || r.bottom > box.bottom) top += r.top - box.top - (box.height - r.height) / 2;
      if (left !== nav.scrollLeft || top !== nav.scrollTop) nav.scrollTo({ left, top, behavior: motion() });
    }

    // Brings the top of an element into view when it is above the viewport (under the fixed navbar); otherwise leaves
    // the page where it is.
    function scrollTopIntoViewIfAbove(element) {
      const top = element.getBoundingClientRect().top;
      if (top < clearance()) window.scrollTo({ top: window.scrollY + top - clearance(), behavior: motion() });
    }

    function showSection(section, push) {
      active = section;
      for (const s of sections) s.hidden = s !== section;
      for (const link of navLinks) {
        if (link.getAttribute("data-section") === section.id) {
          link.setAttribute("aria-current", "true");
          revealNavLink(link);
        } else {
          link.removeAttribute("aria-current");
        }
      }
      if (push && location.hash !== "#" + encodeURIComponent(section.id)) {
        history.pushState(null, "", "#" + encodeURIComponent(section.id));
      }
      lastHash = location.hash;
    }

    // After a switch the user asked for: focus the section's heading and bring the content's top into view if needed.
    function settleOnSection(section) {
      const heading = section.querySelector(".cv-section-title");
      if (heading) heading.focus({ preventScroll: true });
      scrollTopIntoViewIfAbove(section);
    }

    function expandGroup(group) {
      const revealed = cardsOf(group).filter((c) => c.hasAttribute(CUT));
      for (const card of revealed) card.removeAttribute(CUT);
      const button = group.querySelector(":scope > .cv-show-all");
      if (button) button.remove();
      applyVisibility(group.closest("section.cv-section"));
      return revealed;
    }

    function focusCard(card) {
      card.setAttribute("tabindex", "-1");
      card.focus({ preventScroll: true });
    }

    // Shows what the address names. `user` is true for back/forward and hash changes, false on first load.
    function applyAddress(user) {
      if (user && location.hash === lastHash) return;
      const target = resolveId(idFromHash(location.hash), lookup);
      const section = target.section || landing;
      showSection(section, false);
      const card = target.card;
      if (card) {
        if (card.hasAttribute(CUT)) expandGroup(card.parentElement);
        if (card.hidden && section === filterSection) setFilter("all", false);
        const details = card.querySelector(":scope > details.cv-details");
        if (details) details.open = true;
        focusCard(card);
        card.scrollIntoView({ block: "start", behavior: user ? motion() : "auto" });
      } else if (user) {
        settleOnSection(section);
      } else if (target.section) {
        // Loaded with a section's address: the browser may already have scrolled to where it sat in the full page.
        scrollTopIntoViewIfAbove(section);
      }
    }

    function setFilter(filter, announce) {
      activeFilter = filterButtons.some((b) => b.getAttribute("data-filter") === filter) ? filter : "all";
      for (const button of filterButtons) {
        button.setAttribute("aria-pressed", String(button.getAttribute("data-filter") === activeFilter));
      }
      applyVisibility(filterSection);
      if (announce && live) {
        const cards = groupsOf(filterSection).flatMap(cardsOf);
        const shown = cards.filter((c) => !c.hidden).length;
        live.textContent = "Showing " + shown + " of " + cards.length + " publications";
      }
    }

    // "Show all": cut each long group of a section with data-collapse-after.
    function setUpCollapse(section) {
      const keep = parseInt(section.getAttribute("data-collapse-after"), 10);
      if (!(keep >= 0)) return;
      for (const group of groupsOf(section)) {
        const cards = cardsOf(group);
        if (cards.length <= keep) continue;
        for (const card of cards.slice(keep)) card.setAttribute(CUT, "");
        const button = document.createElement("button");
        button.type = "button";
        button.className = "cv-show-all";
        button.textContent = "Show all " + cards.length;
        cards[keep].before(button);
      }
      applyVisibility(section);
    }

    // Printing shows everything; afterwards the section, the cards and the closed <details> are put back.
    function beforePrint() {
      if (closedForPrint) return;
      closedForPrint = Array.from(page.querySelectorAll("details.cv-details:not([open])"));
      for (const details of closedForPrint) details.open = true;
      for (const s of sections) s.hidden = false;
      for (const el of page.querySelectorAll(".cv-card[hidden], .cv-group-title[hidden]")) el.hidden = false;
    }

    function afterPrint() {
      if (!closedForPrint) return;
      for (const details of closedForPrint) details.open = false;
      closedForPrint = null;
      for (const s of sections) applyVisibility(s);
      showSection(active, false);
    }

    // --- Start-up; cv-js goes on before the first section is hidden. ---
    page.classList.add("cv-js");
    for (const s of sections) if (s.hasAttribute("data-collapse-after")) setUpCollapse(s);
    if (bar && filterSection && filterButtons.length > 0) {
      const pressed = filterButtons.find((b) => b.getAttribute("aria-pressed") === "true");
      setFilter(pressed ? pressed.getAttribute("data-filter") : "all", false);
      bar.hidden = false;
      bar.addEventListener("click", (event) => {
        const button = event.target.closest("button.cv-filter[data-filter]");
        if (button && bar.contains(button)) setFilter(button.getAttribute("data-filter"), true);
      });
    }
    applyAddress(false);

    if (nav) {
      nav.addEventListener("click", (event) => {
        const link = event.target.closest("a.cv-nav-link[data-section]");
        if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        const section = sections.find((s) => s.id === link.getAttribute("data-section"));
        if (!section) return;
        event.preventDefault();
        showSection(section, true);
        settleOnSection(section);
      });
    }
    page.addEventListener("click", (event) => {
      const button = event.target.closest("button.cv-show-all");
      if (!button || !page.contains(button)) return;
      const revealed = expandGroup(button.parentElement);
      const first = revealed.find((c) => !c.hidden);
      if (first) focusCard(first);
    });
    window.addEventListener("popstate", () => applyAddress(true));
    window.addEventListener("hashchange", () => applyAddress(true));
    window.addEventListener("beforeprint", beforePrint);
    window.addEventListener("afterprint", afterPrint);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
