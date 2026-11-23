(() => {
  "use strict";

  if (window.lucide) window.lucide.createIcons();

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
