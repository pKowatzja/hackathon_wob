document.addEventListener("DOMContentLoaded", function () {
  const submitButton = document.getElementById("submitButton");
  if (submitButton) {
    submitButton.addEventListener("click", async function () {
      const question = document.getElementById("questionInput").value;
      if (!question) return;

      const resultDiv = document.getElementById("result");
      resultDiv.innerHTML = "Verarbeite Anfrage...";

      try {
        const response = await fetch("/query", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ question }),
        });

        const data = await response.json();
        resultDiv.innerHTML = `<p><strong>Antwort:</strong> ${
          data.answer || data.error
        }</p>`;
      } catch (error) {
        resultDiv.innerHTML = `<p>Fehler: ${error.message}</p>`;
      }
    });
  }

  const reportForm = document.getElementById("damageReportForm");
  const imageInput = document.getElementById("images");
  const imagePreview = document.getElementById("imagePreview");
  const fileInfo = document.getElementById("fileInfo");

  if (imageInput) {
    imageInput.addEventListener("change", function () {
      imagePreview.innerHTML = "";

      if (this.files.length === 0) {
        fileInfo.textContent = "Keine Dateien ausgewählt";
      } else {
        fileInfo.textContent = `${this.files.length} Datei${
          this.files.length > 1 ? "en" : ""
        } ausgewählt`;
      }

      for (const file of this.files) {
        if (!file.type.startsWith("image/")) continue;

        const reader = new FileReader();
        const imgContainer = document.createElement("div");
        imgContainer.className = "preview-item";

        reader.onload = function (e) {
          imgContainer.innerHTML = `
            <img src="${e.target.result}" alt="Vorschau" />
            <span class="filename">${file.name}</span>
            <span class="remove-image" data-filename="${file.name}">×</span>
          `;
        };

        reader.readAsDataURL(file);
        imagePreview.appendChild(imgContainer);
      }

      setTimeout(() => {
        document.querySelectorAll(".remove-image").forEach((button) => {
          button.addEventListener("click", function () {
            this.closest(".preview-item").remove();

            const remainingPreviews =
              document.querySelectorAll(".preview-item").length;
            fileInfo.textContent = `${remainingPreviews} Datei${
              remainingPreviews > 1 ? "en" : ""
            } ausgewählt`;

            if (remainingPreviews === 0) {
              fileInfo.textContent = "Keine Dateien ausgewählt";
            }
          });
        });
      }, 100);
    });
  }

  if (reportForm) {
    reportForm.addEventListener("submit", async function (e) {
      e.preventDefault();

      const date = document.getElementById("date").value;
      const title = document.getElementById("title").value;
      const description = document.getElementById("description").value;
      const category = document.getElementById("category").value;
      const images = document.getElementById("images").files;

      const formData = new FormData();
      formData.append("date", date);
      formData.append("title", title);
      formData.append("description", description);
      formData.append("category", category);

      for (let i = 0; i < images.length; i++) {
        formData.append("images", images[i]);
      }

      const resultDiv = document.getElementById("reportResult");
      const analysisDiv = document.getElementById("analysisContent");
      resultDiv.classList.remove("hidden");
      analysisDiv.innerHTML = "Verarbeite Bericht...";

      try {
        const response = await fetch("/process_report", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error(
            `Server hat mit Status ${response.status} geantwortet`
          );
        }

        let data;
        try {
          data = await response.json();
        } catch (jsonError) {
          console.error("JSON parsing failed:", jsonError);
          const textResponse = await response.text();
          analysisDiv.innerHTML = `<p class="error">Fehler beim Verarbeiten der Antwort. Server-Antwort:</p><pre>${textResponse}</pre>`;
          return;
        }

        if (data.error) {
          analysisDiv.innerHTML = `<p class="error">Fehler: ${data.error}</p>`;
        } else if (data.answer) {
          analysisDiv.innerHTML = `
            <div class="analysis-result">
              <div class="analysis-content">${data.answer.replace(
                /\n/g,
                "<br>"
              )}</div>
            </div>
          `; // <h3>Validierung und Priorität:</h3>
        } else {
          analysisDiv.innerHTML = `<p class="error">Unerwartetes Antwortformat</p>`;
        }
      } catch (error) {
        analysisDiv.innerHTML = `<p class="error">Fehler bei der Übermittlung: ${error.message}</p>`;
      }
    });
  }

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
});
