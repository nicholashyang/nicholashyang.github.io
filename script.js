const menuButton = document.querySelector(".menu-button");
const mobileNav = document.querySelector(".mobile-nav");
const themeToggle = document.querySelector(".theme-toggle");
const navLinks = [...document.querySelectorAll(".side-nav a")];
const sections = navLinks
  .map((link) => document.querySelector(link.getAttribute("href")))
  .filter(Boolean);

const applyTheme = (theme) => {
  const isDark = theme === "dark";
  document.documentElement.dataset.theme = theme;
  themeToggle?.setAttribute("aria-pressed", String(isDark));
  themeToggle?.setAttribute("aria-label", `Switch to ${isDark ? "light" : "dark"} mode`);
};

const getStoredTheme = () => {
  try {
    return localStorage.getItem("theme");
  } catch (error) {
    return null;
  }
};

const storeTheme = (theme) => {
  try {
    localStorage.setItem("theme", theme);
  } catch (error) {
    // Ignore storage failures; the current-page theme still updates.
  }
};

const initialTheme =
  getStoredTheme() ||
  document.documentElement.dataset.theme ||
  (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

applyTheme(initialTheme);

themeToggle?.addEventListener("click", () => {
  const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(nextTheme);
  storeTheme(nextTheme);
});

menuButton?.addEventListener("click", () => {
  const isOpen = mobileNav.classList.toggle("is-open");
  menuButton.setAttribute("aria-expanded", String(isOpen));
});

mobileNav?.addEventListener("click", (event) => {
  if (event.target instanceof HTMLAnchorElement) {
    mobileNav.classList.remove("is-open");
    menuButton?.setAttribute("aria-expanded", "false");
  }
});

const observer = new IntersectionObserver(
  (entries) => {
    const visible = entries
      .filter((entry) => entry.isIntersecting)
      .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

    if (!visible) {
      return;
    }

    navLinks.forEach((link) => {
      link.classList.toggle("is-active", link.getAttribute("href") === `#${visible.target.id}`);
    });
  },
  {
    rootMargin: "-20% 0px -62% 0px",
    threshold: [0.1, 0.35, 0.6],
  },
);

sections.forEach((section) => observer.observe(section));
