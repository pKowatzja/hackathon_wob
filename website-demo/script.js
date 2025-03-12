const meldungen = [
  {
    id: 1,
    title: "Baustelle blockiert Gehweg",
    description:
      "Der Gehweg vor der Bäckerei ist blockiert durch Baustellenmaterialien.",
    image: "images/gehweg.jpg",
    lat: 52.52,
    lng: 13.405,
    priority: "hoch",
  },
  {
    id: 2,
    title: "Defekte Straßenbeleuchtung",
    description:
      "Mehrere Straßenlaternen in der Innenstadt funktionieren nicht.",
    image: "images/Defekte_Strassenlaterne.jpg",
    lat: 52.5205,
    lng: 13.4095,
    priority: "mittel",
  },
  {
    id: 3,
    title: "Schäden an Parkbank",
    description: "Die Parkbank im Stadtpark ist beschädigt.",
    image: "images/defekte-parkbank.jpg",
    lat: 52.519,
    lng: 13.402,
    priority: "niedrig",
  },
];

function createCards(data) {
  const dashboard = document.getElementById("dashboard");
  dashboard.innerHTML = "";
  data.forEach((item) => {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
        <img src="${item.image}" alt="${item.title}">
        <h3>${item.title}</h3>
        <p>${item.description}</p>
        <p><strong>Priorität:</strong> ${item.priority}</p>
      `;
    card.addEventListener("click", () => openModal(item));
    dashboard.appendChild(card);
  });
}

document.getElementById("search").addEventListener("input", function () {
  const query = this.value.toLowerCase();
  const filtered = meldungen.filter(
    (item) =>
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query)
  );
  createCards(filtered);
});

const modal = document.getElementById("modal");
const modalClose = document.getElementById("modalClose");

function openModal(item) {
  document.getElementById("modalTitle").innerText = item.title;
  document.getElementById("modalImage").src = item.image;
  document.getElementById("modalDescription").innerText = item.description;
  modal.style.display = "block";
}

modalClose.addEventListener("click", () => {
  modal.style.display = "none";
});

window.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.style.display = "none";
  }
});

createCards(meldungen);

const map = L.map("map").setView([52.52, 13.405], 13);
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

meldungen.forEach((item) => {
  const marker = L.marker([item.lat, item.lng]).addTo(map);
  marker.bindPopup(`<strong>${item.title}</strong><br>${item.description}`);
  marker.on("click", () => openModal(item));
});

function generateBubbles(count) {
  const container = document.getElementById("bubbles");
  for (let i = 0; i < count; i++) {
    const bubble = document.createElement("div");
    bubble.classList.add("bubble");

    bubble.style.left = Math.random() * 100 + "%";
    bubble.style.top = Math.random() * 100 + "%";

    const size = Math.floor(Math.random() * 100) + 50;
    bubble.style.width = size + "px";
    bubble.style.height = size + "px";

    const duration = Math.floor(Math.random() * 5) + 6;
    bubble.style.animationDuration = duration + "s";

    const delay = Math.floor(Math.random() * 2);
    bubble.style.animationDelay = delay + "s";
    container.appendChild(bubble);
  }
}

generateBubbles(15);
