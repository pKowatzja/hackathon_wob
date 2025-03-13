document.getElementById("submitButton").addEventListener("click", function () {
  const question = document.getElementById("questionInput").value;

  fetch("/query", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question: question }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("result").innerHTML =
        "<strong>Antwort:</strong> " +
        data.answer +
        "<br>" +
        "<strong>Confidence:</strong> " +
        data.confidence;
    })
    .catch((error) => {
      console.error("Fehler:", error);
    });
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
