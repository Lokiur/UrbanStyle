const cards = document.querySelectorAll(".floating-card");

document.addEventListener("mousemove", (e) => {

  let x = e.clientX / window.innerWidth;
  let y = e.clientY / window.innerHeight;

  cards.forEach((card) => {

    card.style.transform = `
      translate(
        ${x * 15}px,
        ${y * 15}px
      )
    `;

  });

});