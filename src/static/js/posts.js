(function () {
  "use strict";

  var MONTH_NAMES = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december"
  ];

  function formatDisplayDate(isoDate) {
    var date = new Date(isoDate + "T00:00:00");
    var day = String(date.getDate()).padStart(2, "0");
    return MONTH_NAMES[date.getMonth()] + " " + day + ", " + date.getFullYear();
  }

  document.addEventListener("DOMContentLoaded", function () {
    var dataScript = document.getElementById("post-data");
    var list = document.getElementById("post-list");
    var tree = document.getElementById("archive-tree");

    if (!dataScript || !list) return;

    var posts;
    try {
      posts = JSON.parse(dataScript.textContent);
    } catch (err) {
      console.error("post-data is not valid JSON:", err);
      return;
    }

    posts.sort(function (a, b) { return b.date.localeCompare(a.date); });

    var countLabel = document.createElement("p");
    countLabel.className = "label";
    countLabel.textContent = posts.length + (posts.length === 1 ? " post" : " posts");
    list.parentNode.insertBefore(countLabel, list);
    list.appendChild(document.createElement("hr"));

    // year -> month -> entry elements, built as we render, so the archive
    // tree can scroll straight to a real DOM node with no anchors needed.
    var years = new Map();

    posts.forEach(function (post, index) {
      var date = new Date(post.date + "T00:00:00");
      if (isNaN(date.getTime())) return;

      var entry = document.createElement("div");
      entry.className = "post-entry";
      entry.dataset.date = post.date;

      var dateEl = document.createElement("p");
      dateEl.className = "meta-date";
      dateEl.textContent = formatDisplayDate(post.date);

      var heading = document.createElement("h2");
      var link = document.createElement("a");
      link.href = post.url;
      link.textContent = post.title;
      heading.appendChild(link);

      var excerpt = document.createElement("p");
      excerpt.textContent = post.excerpt;

      var readTime = document.createElement("p");
      readTime.className = "label";
      readTime.textContent = post.readTime;

      entry.appendChild(dateEl);
      entry.appendChild(heading);
      entry.appendChild(excerpt);
      entry.appendChild(readTime);
      list.appendChild(entry);

      if (index < posts.length - 1) {
        list.appendChild(document.createElement("hr"));
      }

      var year = date.getFullYear();
      var month = date.getMonth();
      if (!years.has(year)) years.set(year, new Map());
      var months = years.get(year);
      if (!months.has(month)) months.set(month, []);
      months.get(month).push(entry);
    });

    if (!tree) return;

    var sortedYears = Array.from(years.keys()).sort(function (a, b) { return b - a; });

    var archiveLabel = document.createElement("p");
    archiveLabel.className = "label";
    archiveLabel.textContent = "archive";
    tree.appendChild(archiveLabel);

    sortedYears.forEach(function (year, index) {
      var months = years.get(year);
      var total = Array.from(months.values()).reduce(function (sum, l) {
        return sum + l.length;
      }, 0);
      var isOpen = index === 0;

      var toggleButton = document.createElement("button");
      toggleButton.type = "button";
      toggleButton.className = "archive-year";
      toggleButton.setAttribute("aria-expanded", String(isOpen));

      var arrow = document.createElement("span");
      arrow.className = "archive-toggle";
      arrow.setAttribute("aria-hidden", "true");
      arrow.textContent = isOpen ? "\u25BE" : "\u25B8";

      var countSpan = document.createElement("span");
      countSpan.className = "archive-count";
      countSpan.textContent = "(" + total + ")";

      toggleButton.appendChild(arrow);
      toggleButton.appendChild(document.createTextNode(" " + year + " "));
      toggleButton.appendChild(countSpan);

      var monthList = document.createElement("ul");
      monthList.className = "archive-months";
      monthList.hidden = !isOpen;

      Array.from(months.keys()).sort(function (a, b) { return b - a; }).forEach(function (month) {
        var monthEntries = months.get(month);
        var item = document.createElement("li");
        var link = document.createElement("a");
        link.href = "#";
        link.textContent = MONTH_NAMES[month] + " (" + monthEntries.length + ")";
        link.addEventListener("click", function (event) {
          event.preventDefault();
          monthEntries[0].scrollIntoView({ behavior: "smooth", block: "start" });
        });
        item.appendChild(link);
        monthList.appendChild(item);
      });

      toggleButton.addEventListener("click", function () {
        var expanded = toggleButton.getAttribute("aria-expanded") === "true";
        toggleButton.setAttribute("aria-expanded", String(!expanded));
        arrow.textContent = expanded ? "\u25B8" : "\u25BE";
        monthList.hidden = expanded;
      });

      tree.appendChild(toggleButton);
      tree.appendChild(monthList);
    });
  });
})();
