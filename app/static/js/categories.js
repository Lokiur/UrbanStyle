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
    const filas = Array.prototype.slice.call(stage.querySelectorAll(".vitrina-row"));
    const tactil = window.matchMedia("(max-width: 860px)");
    const CRECE_ACTIVO = 4.2; // flex-grow de .panel.is-active
    const HUECO = 10;         // gap de .vitrina-row

    // terminada la entrada en cascada se quita el clip-path de los paneles
    // (recortar con máscara en cada frame del cambio de tamaño era lo que más pesaba)
    const entrada = 350 + Math.max(0, paneles.length - 1) * 90 + 1000;
    setTimeout(function() {
        vitrina.classList.add("is-settled");
    }, Math.min(entrada, 2400));

    // ancho que tiene un panel abierto: las fotos usan siempre ese ancho
    // y el panel solo las recorta, así no se reescalan mientras se anima
    function medirFilas() {
        filas.forEach(function(fila) {
            const n = fila.children.length;
            const libre = fila.clientWidth - HUECO * (n - 1);
            const abierto = libre * CRECE_ACTIVO / (CRECE_ACTIVO + n - 1);
            fila.style.setProperty("--open-w", Math.ceil(abierto) + "px");
        });
    }
    medirFilas();
    if ("ResizeObserver" in window) {
        new ResizeObserver(medirFilas).observe(stage);
    } else {
        window.addEventListener("resize", medirFilas);
    }

    // activa un panel dentro de su fila (cada fila tiene su propio activo)
    function activarEnFila(panel) {
        if (panel.classList.contains("is-active")) return;
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

    // al barrer el cursor por encima no se abre cada panel que toca:
    // solo el que se queda bajo el cursor un instante
    let esperaHover = null;

    paneles.forEach(function(panel) {
        panel.addEventListener("mouseenter", function() {
            if (tactil.matches) return;
            clearTimeout(esperaHover);
            esperaHover = setTimeout(function() {
                activarEnFila(panel);
            }, 70);
        });
        panel.addEventListener("focus", function() {
            if (tactil.matches) activarUnico(panel);
            else activarEnFila(panel);
        });
    });

    stage.addEventListener("mouseleave", function() {
        clearTimeout(esperaHover);
    });

    // luz que sigue al cursor: se mueve con transform una vez por frame
    // (cambiar variables CSS en el contenedor recalculaba todos los paneles)
    const luz = stage.querySelector(".vitrina-light");
    if (luz) {
        let lx = 0, ly = 0, pendiente = false;
        stage.addEventListener("mousemove", function(event) {
            const caja = stage.getBoundingClientRect();
            lx = event.clientX - caja.left;
            ly = event.clientY - caja.top;
            if (pendiente) return;
            pendiente = true;
            requestAnimationFrame(function() {
                pendiente = false;
                luz.style.transform = "translate3d(" + lx + "px," + ly + "px,0)";
            });
        });
    }

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
