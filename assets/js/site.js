(() => {
  "use strict";

  if (window.lucide) window.lucide.createIcons();

  // Branch-based Pages hosting serves the source files without a build step.
  if (document.body.classList.contains("personal-page") && /^https?:$/.test(location.protocol)) {
    const links = document.querySelector(".profile-links");
    if (links && !links.querySelector('a[href="CV.pdf"]')) {
      fetch("CV.pdf", { method: "HEAD" }).then((response) => {
        if (!response.ok || !response.headers.get("content-type")?.includes("application/pdf")) return;
        const link = document.createElement("a");
        link.href = "CV.pdf";
        link.innerHTML = '<i data-lucide="file-text" aria-hidden="true"></i>CV';
        links.firstElementChild.after(link);
        if (window.lucide) window.lucide.createIcons();
      }).catch(() => {});
    }
    const profile = document.querySelector(".profile");
    if (profile && !profile.querySelector(".profile-photo")) {
      const filenames = ["profile.jpg", "profile.png", "profile.webp"];
      const tryPhoto = () => {
        const filename = filenames.shift();
        if (!filename) return;
        const photo = new Image(180, 220);
        photo.className = "profile-photo";
        photo.alt = "Shengze Jiang";
        photo.onload = () => profile.prepend(photo);
        photo.onerror = tryPhoto;
        photo.src = filename;
      };
      tryPhoto();
    }
  }

  // Avoid concurrent audio/video activity when a visitor plays another clip.
  const videos = Array.from(document.querySelectorAll("video"));
  videos.forEach((item) => item.addEventListener("play", () => {
    videos.forEach((other) => { if (other !== item) other.pause(); });
  }));

  const dialog = document.querySelector(".image-dialog");
  if (dialog) {
    const image = document.getElementById("dialog-image");
    const title = document.getElementById("dialog-title");
    const link = document.getElementById("dialog-download");
    document.querySelectorAll("[data-zoom]").forEach((button) => {
      button.addEventListener("click", () => {
        image.src = button.dataset.zoom;
        image.alt = button.querySelector("img").alt;
        title.textContent = button.dataset.zoomTitle;
        link.href = button.dataset.zoom;
        dialog.showModal();
      });
    });
    dialog.querySelector("[data-close-dialog]").addEventListener("click", () => dialog.close());
    dialog.addEventListener("click", (event) => {
      if (event.target !== dialog) return;
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right ||
          event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    });
  }
})();
