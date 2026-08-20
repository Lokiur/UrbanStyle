function openModal(id) {
  document.getElementById("modal-" + id).style.display = "flex";
}

function closeModal(id) {
  document.getElementById("modal-" + id).style.display = "none";
}

function showAdminSection(id, btn) {
  document.querySelectorAll(".admin-section").forEach((section) => {
    section.classList.remove("active");
  });
  document.querySelectorAll(".admin-nav-btn").forEach((navBtn) => {
    navBtn.classList.remove("active");
  });

  document.getElementById(id).classList.add("active");
  btn.classList.add("active");

  if (window.location.hash !== "#" + id) {
    history.replaceState(null, "", "#" + id);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const navButtons = document.querySelectorAll(".admin-nav-btn");
  if (!navButtons.length) return;

  const requested = window.location.hash.replace("#", "");
  const target = [...navButtons].find(
    (btn) => btn.dataset.section === requested,
  );

  if (target) {
    showAdminSection(requested, target);
  }
});
