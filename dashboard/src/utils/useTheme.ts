import { onMounted, ref } from "vue";

type Theme = "light" | "dark" | "system";

/*
const getSystemTheme = (): "light" | "dark" => {
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
};
*/

// Reactive mirror of the data-theme attribute, so menus and labels can show
// the active theme (a checkmark, a toggle state) without reading the DOM.
// The attribute stays the source of truth for CSS; this ref is kept in sync
// by setTheme, the only writer.
export const themeName = ref<Theme>(
	(typeof localStorage !== "undefined" &&
		(localStorage.getItem("theme") as Theme)) ||
		"light",
);

export const getTheme = (): Theme => themeName.value;

export const setTheme = (name: Theme) => {
  document.documentElement.classList.add('no-transition');

  // let themeType = name == "system" ? getSystemTheme() : name;
  document.documentElement.setAttribute("data-theme", name);
  localStorage.setItem("theme", name);
  themeName.value = name;

    requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      document.documentElement.classList.remove('no-transition');
    });
  });
};

export const initTheme = () => {
  onMounted(() => {
    // let storedTheme = localStorage.getItem("theme") as Theme || 'system';
    let storedTheme = localStorage.getItem("theme") as Theme || 'light';
    setTheme(storedTheme);

    /* 

    TODO: add back when dark theme is stable

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

    const handleSystemThemeChange = () => {
      if (localStorage.theme === "system") setTheme("system");
    };

    mediaQuery.addEventListener("change", handleSystemThemeChange);

    return () => {
      mediaQuery.removeEventListener("change", handleSystemThemeChange);
    };
    */
  });
};
