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

// Panel flotante de confirmación de pedido (carrito)
document.addEventListener("DOMContentLoaded", function() {
    const checkoutTrigger = document.getElementById("checkoutTrigger");
    const checkoutPanel = document.getElementById("checkoutPanel");
    const checkoutOverlay = document.getElementById("checkoutOverlay");
    const checkoutClose = document.getElementById("checkoutClose");

    if (!checkoutTrigger || !checkoutPanel || !checkoutOverlay) return;

    function abrirCheckout() {
        checkoutPanel.classList.add("active");
        checkoutOverlay.classList.add("active");
        checkoutPanel.setAttribute("aria-hidden", "false");
    }

    function cerrarCheckout() {
        checkoutPanel.classList.remove("active");
        checkoutOverlay.classList.remove("active");
        checkoutPanel.setAttribute("aria-hidden", "true");
    }

    checkoutTrigger.addEventListener("click", abrirCheckout);
    checkoutOverlay.addEventListener("click", cerrarCheckout);
    if (checkoutClose) checkoutClose.addEventListener("click", cerrarCheckout);

    const direccionRadios = checkoutPanel.querySelectorAll("input[name='direccion_id']");
    const nuevaDireccionFields = document.getElementById("nuevaDireccionFields");

    function actualizarCamposDireccion() {
        if (!nuevaDireccionFields) return;
        const seleccionada = checkoutPanel.querySelector("input[name='direccion_id']:checked");
        const mostrar = !seleccionada || seleccionada.value === "nueva";
        nuevaDireccionFields.classList.toggle("active", mostrar);
    }

    direccionRadios.forEach(function(radio) {
        radio.addEventListener("change", actualizarCamposDireccion);
    });

    actualizarCamposDireccion();

    // Acordeón: cada sección del panel se despliega/colapsa por separado
    const accordionItems = checkoutPanel.querySelectorAll(".checkout-accordion-item");

    accordionItems.forEach(function(item) {
        const header = item.querySelector(".checkout-accordion-header");
        if (!header) return;

        header.addEventListener("click", function() {
            const yaActivo = item.classList.contains("active");

            accordionItems.forEach(function(otro) {
                otro.classList.remove("active");
            });

            if (!yaActivo) item.classList.add("active");
        });
    });

    // Campos condicionales según el método de pago (tarjeta / PSE / billetera)
    const metodoPagoSelect = document.getElementById("metodoPagoSelect");

    const gruposMetodo = {
        tarjeta: document.getElementById("camposTarjeta"),
        pse: document.getElementById("camposPse"),
        billetera: document.getElementById("camposBilletera")
    };

    // Guarda qué campos nacieron obligatorios: el `required` se quita
    // mientras el grupo está oculto, porque un campo oculto y required
    // hace que el navegador cancele el envío sin poder mostrar el error.
    Object.values(gruposMetodo).forEach(function(grupo) {
        if (!grupo) return;
        grupo.querySelectorAll("[required]").forEach(function(campo) {
            campo.dataset.obligatorio = "1";
        });
    });

    function actualizarCamposMetodoPago() {
        if (!metodoPagoSelect) return;

        const opcion = metodoPagoSelect.options[metodoPagoSelect.selectedIndex];
        const tipo = opcion ? opcion.dataset.tipo : null;

        Object.keys(gruposMetodo).forEach(function(clave) {
            const grupo = gruposMetodo[clave];
            if (!grupo) return;

            const visible = clave === tipo;
            grupo.classList.toggle("active", visible);

            grupo.querySelectorAll("[data-obligatorio]").forEach(function(campo) {
                campo.required = visible;
                if (!visible) campo.setCustomValidity("");
            });
        });
    }

    if (metodoPagoSelect) {
        metodoPagoSelect.addEventListener("change", actualizarCamposMetodoPago);
        actualizarCamposMetodoPago();
    }

    // Formato de los campos de pago mientras se escriben
    const soloDigitos = function(valor) {
        return valor.replace(/\D/g, "");
    };

    const tarjetaNumero = checkoutPanel.querySelector("[name='tarjeta_numero']");
    const tarjetaVencimiento = checkoutPanel.querySelector("[name='tarjeta_vencimiento']");
    const tarjetaCvv = checkoutPanel.querySelector("[name='tarjeta_cvv']");
    const billeteraCelular = checkoutPanel.querySelector("[name='billetera_celular']");

    if (tarjetaNumero) {
        tarjetaNumero.addEventListener("input", function() {
            const digitos = soloDigitos(tarjetaNumero.value).slice(0, 16);
            tarjetaNumero.value = digitos.replace(/(\d{4})(?=\d)/g, "$1 ");

            tarjetaNumero.setCustomValidity(
                digitos.length >= 13 ? "" : "El número de tarjeta debe tener al menos 13 dígitos."
            );
        });
    }

    if (tarjetaVencimiento) {
        tarjetaVencimiento.addEventListener("input", function() {
            const digitos = soloDigitos(tarjetaVencimiento.value).slice(0, 4);

            tarjetaVencimiento.value = digitos.length > 2
                ? digitos.slice(0, 2) + "/" + digitos.slice(2)
                : digitos;

            const mes = parseInt(digitos.slice(0, 2), 10);
            const valido = digitos.length === 4 && mes >= 1 && mes <= 12;

            tarjetaVencimiento.setCustomValidity(valido ? "" : "Usa el formato MM/AA.");
        });
    }

    if (tarjetaCvv) {
        tarjetaCvv.addEventListener("input", function() {
            tarjetaCvv.value = soloDigitos(tarjetaCvv.value).slice(0, 4);

            tarjetaCvv.setCustomValidity(
                tarjetaCvv.value.length >= 3 ? "" : "El CVV debe tener 3 o 4 dígitos."
            );
        });
    }

    if (billeteraCelular) {
        billeteraCelular.addEventListener("input", function() {
            billeteraCelular.value = soloDigitos(billeteraCelular.value).slice(0, 10);

            billeteraCelular.setCustomValidity(
                billeteraCelular.value.length === 10 ? "" : "El celular debe tener 10 dígitos."
            );
        });
    }

    // Si algo quedó incompleto, abre el acordeón donde está el campo
    // para que el mensaje del navegador se vea junto al input.
    const checkoutForm = checkoutPanel.querySelector(".checkout-form");
    const checkoutSubmit = document.getElementById("checkoutSubmit");

    if (checkoutForm) {
        checkoutForm.addEventListener("invalid", function(evento) {
            const item = evento.target.closest(".checkout-accordion-item");
            if (!item) return;

            accordionItems.forEach(function(otro) {
                otro.classList.remove("active");
            });

            item.classList.add("active");
        }, true);

        // El pago se procesa en el servidor; se bloquea el botón para
        // que un doble clic no genere dos facturas.
        checkoutForm.addEventListener("submit", function() {
            if (checkoutSubmit) {
                checkoutSubmit.disabled = true;
                checkoutSubmit.textContent = "Procesando pago...";
            }
        });
    }
});

// Panel de pago aprobado (se muestra solo tras confirmar la compra)
document.addEventListener("DOMContentLoaded", function() {
    const confirmPanel = document.getElementById("confirmPanel");
    const confirmOverlay = document.getElementById("confirmOverlay");
    const confirmClose = document.getElementById("confirmClose");

    if (!confirmPanel || !confirmOverlay) return;

    function cerrarConfirmacion() {
        confirmPanel.classList.remove("active");
        confirmOverlay.classList.remove("active");
    }

    confirmOverlay.addEventListener("click", cerrarConfirmacion);
    if (confirmClose) confirmClose.addEventListener("click", cerrarConfirmacion);

    document.addEventListener("keydown", function(evento) {
        if (evento.key === "Escape") cerrarConfirmacion();
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

// Previsualiza la foto de perfil elegida antes de guardar
document.addEventListener("DOMContentLoaded", function() {
    const avatarInput = document.getElementById("avatarInput");
    const avatarPreview = document.getElementById("avatarPreview");

    if (!avatarInput || !avatarPreview) return;

    avatarInput.addEventListener("change", function() {
        const file = avatarInput.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function(event) {
            avatarPreview.src = event.target.result;
        };
        reader.readAsDataURL(file);
    });
});
