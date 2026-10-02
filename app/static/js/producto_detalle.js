// Ficha de producto: seleccion de color/talla, precio y stock en vivo, zoom.
document.addEventListener("DOMContentLoaded", function() {
    const datos = document.getElementById("pdData");
    const form = document.getElementById("pdForm");

    // ---------- ZOOM DE LA IMAGEN ----------
    const media = document.getElementById("pdMedia");
    const imagen = document.getElementById("pdImage");

    if (media && imagen && window.matchMedia("(hover: hover)").matches) {
        media.addEventListener("mousemove", function(event) {
            const caja = media.getBoundingClientRect();
            const x = ((event.clientX - caja.left) / caja.width) * 100;
            const y = ((event.clientY - caja.top) / caja.height) * 100;
            imagen.style.transformOrigin = x + "% " + y + "%";
            media.classList.add("zoom");
        });

        media.addEventListener("mouseleave", function() {
            media.classList.remove("zoom");
        });
    }

    // ---------- "GUIA DE TALLAS" ABRE SU ACORDEON ----------
    document.querySelectorAll("[data-open]").forEach(function(boton) {
        boton.addEventListener("click", function() {
            const destino = document.getElementById(boton.dataset.open);
            if (!destino) return;
            destino.open = true;
            destino.scrollIntoView({ behavior: "smooth", block: "center" });
        });
    });

    if (!datos || !form) return;

    // ---------- SELECCION COLOR / TALLA ----------
    const existencias = JSON.parse(datos.textContent);
    const swatches = form.querySelectorAll(".pd-swatch");
    const tallas = form.querySelectorAll(".pd-size");
    const campoExistencia = document.getElementById("pdExistencia");
    const precio = document.getElementById("pdPrice");
    const nombreColor = document.getElementById("pdColorName");
    const stock = document.getElementById("pdStock");
    const boton = document.getElementById("pdBuy");
    const textoBoton = boton.querySelector("span");

    const inicial = existencias.find(function(e) { return e.stock > 0; }) || existencias[0];
    let colorId = inicial ? inicial.color_id : null;
    let tallaId = inicial ? inicial.talla_id : null;

    function buscar(color, talla) {
        return existencias.find(function(e) {
            return e.color_id === color && e.talla_id === talla;
        });
    }

    function conStock(filtro) {
        return existencias.find(function(e) { return e.stock > 0 && filtro(e); });
    }

    const formatoPrecio = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });

    function pintar() {
        const actual = buscar(colorId, tallaId);
        const disponible = actual && actual.stock > 0;

        swatches.forEach(function(s) {
            const id = Number(s.dataset.color);
            s.classList.toggle("active", id === colorId);
            s.classList.toggle("sold-out", !conStock(function(e) { return e.color_id === id; }));
        });

        tallas.forEach(function(t) {
            const id = Number(t.dataset.talla);
            const existe = buscar(colorId, id);
            t.classList.toggle("active", id === tallaId);
            // tachada si no hay stock en el color elegido; sigue siendo
            // clicable porque puede haberla en otro color
            t.classList.toggle("sold-out", !existe || existe.stock <= 0);
        });

        const swatchActivo = form.querySelector('.pd-swatch[data-color="' + colorId + '"]');
        if (nombreColor && swatchActivo) nombreColor.textContent = swatchActivo.dataset.nombre;

        if (actual && precio) precio.textContent = formatoPrecio.format(actual.precio);

        campoExistencia.value = disponible ? actual.existencia_id : "";
        boton.disabled = !disponible;
        textoBoton.textContent = disponible ? "Añadir a la bolsa" : "No disponible";

        stock.classList.toggle("low", disponible && actual.stock <= 5);
        stock.classList.toggle("out", !disponible);
        if (!actual) {
            stock.innerHTML = '<i class="fa-solid fa-ban"></i> Esta combinación no existe';
        } else if (!disponible) {
            stock.innerHTML = '<i class="fa-solid fa-ban"></i> Agotado en este color y talla';
        } else if (actual.stock <= 5) {
            stock.innerHTML = '<i class="fa-solid fa-fire"></i> ¡Solo quedan ' + actual.stock + " unidades!";
        } else {
            stock.innerHTML = '<i class="fa-solid fa-circle-check"></i> Disponible para envío inmediato';
        }
    }

    swatches.forEach(function(s) {
        s.addEventListener("click", function() {
            colorId = Number(s.dataset.color);
            const actual = buscar(colorId, tallaId);
            if (!actual || actual.stock <= 0) {
                // mantiene el color y salta a la primera talla con stock en ese color
                const otra = conStock(function(e) { return e.color_id === colorId; });
                if (otra) tallaId = otra.talla_id;
            }
            pintar();
        });
    });

    tallas.forEach(function(t) {
        t.addEventListener("click", function() {
            tallaId = Number(t.dataset.talla);
            const actual = buscar(colorId, tallaId);
            if (!actual || actual.stock <= 0) {
                // mantiene la talla y cambia a un color que si la tenga
                const otra = conStock(function(e) { return e.talla_id === tallaId; });
                if (otra) colorId = otra.color_id;
            }
            pintar();
        });
    });

    pintar();
});
