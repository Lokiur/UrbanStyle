function toggleMenu() {
    const menu = document.getElementById("profileMenu");
    if (!menu) return;

    menu.style.display = (menu.style.display === "block") ? "none" : "block";
}

document.addEventListener("click", function(event) {
    const container = document.querySelector(".profile-container");
    const menu = document.getElementById("profileMenu");

    if (!container || !menu) return;

    if (!container.contains(event.target)) {
        menu.style.display = "none";
    }
});