(function () {
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem("nr-lang"); } catch (e) {}
  var lang = saved || ((navigator.language || "en").slice(0, 2) === "fr" ? "fr" : "en");

  function apply(l) {
    root.lang = l;
    var b = document.getElementById("lang");
    if (b) b.textContent = l === "fr" ? "English" : "Français";
  }
  apply(lang);

  document.addEventListener("DOMContentLoaded", function () {
    apply(lang);
    var b = document.getElementById("lang");
    if (b) b.addEventListener("click", function () {
      lang = lang === "fr" ? "en" : "fr";
      try { localStorage.setItem("nr-lang", lang); } catch (e) {}
      apply(lang);
    });
    var y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();
  });
})();
