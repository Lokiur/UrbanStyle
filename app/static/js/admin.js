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
