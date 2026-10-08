// Ficha de producto: seleccion de talla, precio y stock en vivo, zoom.
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

    // ---------- SELECCION DE TALLA ----------
    const existencias = JSON.parse(datos.textContent);
    const tallas = form.querySelectorAll(".pd-size");
    const campoExistencia = document.getElementById("pdExistencia");
    const precio = document.getElementById("pdPrice");
    const precioAntes = document.getElementById("pdPriceBefore"); // solo si esta en oferta
    const stock = document.getElementById("pdStock");
    const boton = document.getElementById("pdBuy");
    const textoBoton = boton.querySelector("span");

    const inicial = existencias.find(function(e) { return e.stock > 0; }) || existencias[0];
    let tallaId = inicial ? inicial.talla_id : null;

    function buscar(talla) {
        return existencias.find(function(e) { return e.talla_id === talla; });
    }

    const formatoPrecio = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });

    function pintar() {
        const actual = buscar(tallaId);
        const disponible = actual && actual.stock > 0;

        tallas.forEach(function(t) {
            const id = Number(t.dataset.talla);
            const existe = buscar(id);
            t.classList.toggle("active", id === tallaId);
            t.classList.toggle("sold-out", !existe || existe.stock <= 0);
        });

        if (actual && precio) precio.textContent = formatoPrecio.format(actual.precio);
        if (actual && precioAntes) precioAntes.textContent = formatoPrecio.format(actual.precio_original);

        campoExistencia.value = disponible ? actual.existencia_id : "";
        boton.disabled = !disponible;
        textoBoton.textContent = disponible ? "Añadir a la bolsa" : "No disponible";

        stock.classList.toggle("low", disponible && actual.stock <= 5);
        stock.classList.toggle("out", !disponible);
        if (!actual) {
            stock.innerHTML = '<i class="fa-solid fa-ban"></i> Esta talla no existe';
        } else if (!disponible) {
            stock.innerHTML = '<i class="fa-solid fa-ban"></i> Agotado en esta talla';
        } else if (actual.stock <= 5) {
            stock.innerHTML = '<i class="fa-solid fa-fire"></i> ¡Solo quedan ' + actual.stock + " unidades!";
        } else {
            stock.innerHTML = '<i class="fa-solid fa-circle-check"></i> Disponible para envío inmediato';
        }
    }

    tallas.forEach(function(t) {
        t.addEventListener("click", function() {
            tallaId = Number(t.dataset.talla);
            pintar();
        });
    });

    pintar();
});
