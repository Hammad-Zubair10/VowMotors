document.addEventListener('DOMContentLoaded', function () {
  // Mobile nav toggle
  var toggle = document.getElementById('navToggle');
  var navList = document.getElementById('navList');
  if (toggle && navList) {
    toggle.addEventListener('click', function () {
      var open = navList.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // Vehicle detail gallery: click a thumbnail to swap the main photo
  var mainImg = document.getElementById('galleryMainImg');
  document.querySelectorAll('.vehicle-gallery__thumbs img').forEach(function (thumb) {
    thumb.addEventListener('click', function () {
      if (mainImg && thumb.dataset.full) {
        mainImg.src = thumb.dataset.full;
      }
    });
  });
});
