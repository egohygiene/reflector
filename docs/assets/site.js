(function () {
  "use strict";

  var body = document.body;
  var manifestPath = body && body.dataset ? body.dataset.publicationManifest : "";
  if (!manifestPath) {
    return;
  }

  fetch(manifestPath, { credentials: "same-origin" })
    .then(function (response) {
      if (!response.ok) {
        throw new Error("Publication manifest request failed");
      }
      return response.json();
    })
    .then(function (publication) {
      if (typeof publication.version === "string") {
        document.querySelectorAll("[data-publication-version]").forEach(function (element) {
          element.textContent = "v" + publication.version;
        });
      }

      if (typeof publication.status === "string") {
        document.querySelectorAll("[data-publication-status]").forEach(function (element) {
          element.textContent = publication.status.charAt(0).toUpperCase() + publication.status.slice(1);
        });
      }

      if (typeof publication.release_tag === "string") {
        document.querySelectorAll("[data-release-link]").forEach(function (element) {
          element.href = "https://github.com/egohygiene/reflector/releases/tag/" +
            encodeURIComponent(publication.release_tag);
          var label = element.querySelector("[data-release-tag]");
          if (label) {
            label.textContent = publication.release_tag;
          }
        });
      }
    })
    .catch(function () {
      // Every publication fact has a complete static fallback in the HTML.
    });
}());
