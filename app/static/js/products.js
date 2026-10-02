// Catálogo ("Nuevo"): panel de filtros plegable y barra de categorías fija.
document.addEventListener("DOMContentLoaded", function() {
    // ---------- FILTROS PLEGABLES ----------
    const toggle = document.getElementById("filtersToggle");
    const panel = document.getElementById("filtersPanel");

    if (toggle && panel) {
        toggle.addEventListener("click", function() {
            const abierto = panel.classList.toggle("is-open");
            toggle.classList.toggle("is-open", abierto);
            toggle.setAttribute("aria-expanded", abierto ? "true" : "false");

            if (abierto) {
                const primerCampo = panel.querySelector("select, input:not([type=hidden])");
                if (primerCampo) primerCampo.focus({ preventScroll: true });
            }
        });
    }

    // ---------- BARRA FIJA: fondo de cristal al quedar pegada ----------
    const barra = document.getElementById("productsToolbar");
    const sentinela = document.getElementById("toolbarSentinel");

    if (barra && sentinela && "IntersectionObserver" in window) {
        new IntersectionObserver(function(entradas) {
            barra.classList.toggle("is-stuck", !entradas[0].isIntersecting);
        }).observe(sentinela);
    }

    // ---------- la píldora activa siempre a la vista ----------
    // (solo desplaza la fila de píldoras, nunca la página)
    const activa = document.querySelector(".cat-pill.active");
    if (activa) {
        const fila = activa.parentElement;
        fila.scrollLeft = activa.offsetLeft - (fila.clientWidth - activa.offsetWidth) / 2;
    }
});
