const htmlTag = document.getElementsByTagName("html")[0];

const setThemeIcons = (theme) => {
  const elements = safeGetElementsById(["sunIcon", "moonIcon"], true);
  const { sunIcon, moonIcon } = elements;

  if (!sunIcon || !moonIcon) {
    return;
  }

  if (theme === "light") {
    sunIcon.classList.replace("swap-on", "swap-off");
    moonIcon.classList.replace("swap-off", "swap-on");
    return;
  }

  moonIcon.classList.replace("swap-on", "swap-off");
  sunIcon.classList.replace("swap-off", "swap-on");
};

const getCurrentTheme = () => {
  const storedTheme = getLocalStorageItem("theme");
  if (storedTheme) {
    return storedTheme;
  }
  
  const htmlTag = document.getElementsByTagName("html")[0];
  if (htmlTag.hasAttribute("data-theme")) {
    const themeAttr = htmlTag.getAttribute("data-theme");
    setLocalStorageItem("theme", themeAttr);
    return themeAttr;
  }
  
  // Return system theme preference
  const prefersDark = window.matchMedia && 
    window.matchMedia("(prefers-color-scheme: dark)").matches;
  const systemTheme = prefersDark ? "dark" : "light";
  setLocalStorageItem("theme", systemTheme);
  return systemTheme;
};

const toggleTheme = () => {
  const htmlTag = document.getElementsByTagName("html")[0];
  const newTheme = getCurrentTheme() === "dark" ? "light" : "dark";
  
  setLocalStorageItem("theme", newTheme);
  htmlTag.setAttribute("data-theme", newTheme);
  setThemeIcons(newTheme);
};

const initializeTheme = () => {
  const theme = getCurrentTheme();
  const htmlTag = document.getElementsByTagName("html")[0];
  htmlTag.setAttribute("data-theme", theme);
  setThemeIcons(theme);
};

initializeTheme();
