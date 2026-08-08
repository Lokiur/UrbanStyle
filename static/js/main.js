// Evita el bug de Safari/iOS donde el primer toque en un elemento con
// estilos :hover solo dispara el hover y hace falta un segundo toque
// para que el click realmente funcione.
document.addEventListener("touchstart", function() {}, { passive: true });

// Menú desplegable de usuario (perfil / pedidos / cerrar sesión)
document.addEventListener("DOMContentLoaded", function() {
    const profileTrigger = document.getElementById("profileTrigger");
    const profileMenu = document.getElementById("profileMenu");

    if (!profileTrigger || !profileMenu) return;

    profileTrigger.addEventListener("click", function(event) {
        event.stopPropagation();
        profileMenu.classList.toggle("active");
    });

    document.addEventListener("click", function(event) {
        if (!profileMenu.contains(event.target) && !profileTrigger.contains(event.target)) {
            profileMenu.classList.remove("active");
        }
    });
});

// Menú hamburguesa responsive
document.addEventListener("DOMContentLoaded", function() {
    const navToggle = document.getElementById("navToggle");
    const mainNav = document.getElementById("mainNav");
    const icons = document.querySelector(".navbar .icons");

    if (!navToggle || !mainNav) return;

    navToggle.addEventListener("click", function() {
        const isOpen = navToggle.classList.toggle("active");
        mainNav.classList.toggle("active", isOpen);
        if (icons) icons.classList.toggle("active", isOpen);
        navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    mainNav.querySelectorAll("a").forEach(function(link) {
        link.addEventListener("click", function() {
            navToggle.classList.remove("active");
            mainNav.classList.remove("active");
            if (icons) icons.classList.remove("active");
            navToggle.setAttribute("aria-expanded", "false");
        });
    });

    window.addEventListener("resize", function() {
        if (window.innerWidth > 1100) {
            navToggle.classList.remove("active");
            mainNav.classList.remove("active");
            if (icons) icons.classList.remove("active");
            navToggle.setAttribute("aria-expanded", "false");
        }
    });
});

// Buscador desplegable
document.addEventListener("DOMContentLoaded", function() {
    const searchToggle = document.getElementById("searchToggle");
    const searchBox = document.getElementById("searchBox");

    if (!searchToggle || !searchBox) return;

    searchToggle.addEventListener("click", function(event) {
        event.stopPropagation();
        const isOpen = searchBox.classList.toggle("active");
        searchToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
        if (isOpen) {
            const input = searchBox.querySelector("input");
            if (input) input.focus();
        }
    });

    document.addEventListener("click", function(event) {
        if (!searchBox.contains(event.target) && !searchToggle.contains(event.target)) {
            searchBox.classList.remove("active");
            searchToggle.setAttribute("aria-expanded", "false");
        }
    });
});

// Actualiza el precio mostrado según la talla seleccionada
document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll(".size-selector input[type='radio']").forEach(function(radio) {
        radio.addEventListener("change", function() {
            if (!radio.checked) return;

            const card = radio.closest(".product-card");
            const precio = radio.dataset.precio;
            if (!card || !precio) return;

            const priceEl = card.querySelector(".price");
            if (!priceEl) return;

            const formateado = Math.round(parseFloat(precio))
                .toString()
                .replace(/\B(?=(\d{3})+(?!\d))/g, ",");

            priceEl.textContent = "$ " + formateado;
        });
    });
});
