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

// Cubiculo "Ticket promedio de compra" del resumen: el <select> cambia
// que estado se muestra sin recargar; cada <option> lleva el valor ya
// calculado en data-valor.
function actualizarTicketPromedio(select) {
  const opcion = select.options[select.selectedIndex];
  const valor = document.getElementById("ticket-promedio-valor");
  if (!opcion || !valor) return;

  valor.textContent = opcion.dataset.valor;
  valor.setAttribute(
    "title",
    "Promedio de " +
      opcion.dataset.cantidad +
      " pedidos " +
      opcion.dataset.etiqueta,
  );
}

function filtrarPedidos() {
  const tabla = document.getElementById("tabla-pedidos");
  if (!tabla) return;

  const texto = (document.getElementById("pedidos-buscar")?.value || "")
    .trim()
    .toLowerCase();
  const estadoActivo =
    document.querySelector(".pedido-tab.active")?.dataset.estado || "todos";
  const filas = tabla.querySelectorAll("tbody tr[data-estado]");

  let visibles = 0;

  filas.forEach((fila) => {
    const coincideEstado =
      estadoActivo === "todos" || fila.dataset.estado === estadoActivo;
    const coincideTexto = !texto || fila.dataset.buscar.includes(texto);
    const visible = coincideEstado && coincideTexto;

    fila.style.display = visible ? "" : "none";
    if (visible) visibles++;
  });

  const contador = document.getElementById("pedidos-contador");
  if (contador) {
    contador.textContent =
      visibles === filas.length
        ? filas.length + " en total"
        : visibles + " de " + filas.length;
  }

  const vacio = document.getElementById("pedidos-vacio");
  if (vacio) vacio.style.display = visibles === 0 ? "flex" : "none";
}

function filtrarPedidosPorEstado(estado, btn) {
  document
    .querySelectorAll(".pedido-tab")
    .forEach((tab) => tab.classList.remove("active"));
  btn.classList.add("active");
  filtrarPedidos();
}

// Tooltip nativo con el valor exacto de cada cubiculo de estadisticas:
// al pasar el cursor la tarjeta se amplia (CSS) y ademas el navegador
// muestra el numero completo aunque en pantalla se hubiera recortado.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".stat-value").forEach((el) => {
    const exacto = el.textContent.replace(/\s+/g, " ").trim();
    if (exacto && !el.hasAttribute("title")) {
      el.setAttribute("title", exacto);
    }
  });
});

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
