// Categorías ("vitrina"): entrada animada, panel activo y luz del cursor.
document.addEventListener("DOMContentLoaded", function() {
    const vitrina = document.getElementById("vitrina");
    if (!vitrina) return;

    // dispara las animaciones de entrada en el siguiente frame
    requestAnimationFrame(function() {
        requestAnimationFrame(function() {
            vitrina.classList.add("is-ready");
        });
    });

    const stage = document.getElementById("vitrinaStage");
    if (!stage) return;

    const paneles = Array.prototype.slice.call(stage.querySelectorAll(".panel"));
    const tactil = window.matchMedia("(max-width: 860px)");

    // activa un panel dentro de su fila (cada fila tiene su propio activo)
    function activarEnFila(panel) {
        panel.parentElement.querySelectorAll(".panel").forEach(function(p) {
            p.classList.toggle("is-active", p === panel);
        });
    }

    // en móvil solo hay un panel abierto en toda la página
    function activarUnico(panel) {
        paneles.forEach(function(p) {
            p.classList.toggle("is-active", p === panel);
        });
    }

    paneles.forEach(function(panel) {
        panel.addEventListener("mouseenter", function() {
            if (!tactil.matches) activarEnFila(panel);
        });
        panel.addEventListener("focus", function() {
            if (tactil.matches) activarUnico(panel);
            else activarEnFila(panel);
        });
    });

    // luz que sigue al cursor
    stage.addEventListener("mousemove", function(event) {
        const caja = stage.getBoundingClientRect();
        stage.style.setProperty("--mx", (event.clientX - caja.left) + "px");
        stage.style.setProperty("--my", (event.clientY - caja.top) + "px");
    });

    // móvil: se abre el panel que pasa por el centro de la pantalla
    if ("IntersectionObserver" in window) {
        const observador = new IntersectionObserver(function(entradas) {
            if (!tactil.matches) return;
            entradas.forEach(function(entrada) {
                if (entrada.isIntersecting) activarUnico(entrada.target);
            });
        }, { rootMargin: "-45% 0px -45% 0px" });

        paneles.forEach(function(panel) {
            observador.observe(panel);
        });
    }

    // al volver a escritorio, deja abierto el primero de cada fila
    tactil.addEventListener("change", function(e) {
        if (e.matches) return;
        stage.querySelectorAll(".vitrina-row").forEach(function(fila) {
            const primero = fila.querySelector(".panel");
            if (primero) activarEnFila(primero);
        });
    });
});
