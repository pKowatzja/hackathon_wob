import os
import json
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def encode_image(image_path):
    """
    Liest eine Bilddatei und gibt einen Base64-encodierten String zurück.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_damage_report(report):
    """
    Verarbeitet einen Mangelbericht, validiert die Kategorie und ordnet eine Priorität zu.

    Args:
        report (dict): Ein Dictionary mit den Schlüsseln:
            - "date": Datum des Berichts
            - "title": Titel des Berichts
            - "description": Beschreibung des Mangels
            - "category": Vorgeschlagene Kategorie
            - "image_data": (Optional) Liste von Base64-codierten Bildstrings
            - alternativ "image_paths": Liste von Dateipfaden (Fallback)

    Returns:
        dict: Dictionary mit der LLM-Antwort, z.B.:
              {
                  "answer": "Validierung und Priorität",
                  "raw_response": { ... }
              }
    """
    ranking_system_prompt = """
        - Rolle -
        Du bist ein KI-System zur Validierung, Klassifizierung und Einstufung von Schadensmeldungen im Dienst einer Stadtverwaltung.

        - Ziel -
        Du erhälst eine Schadensmeldung bestehend aus einem Bild, einer Kategorie und einer Beschreibung des Schadens.
        Deine Aufgabe ist es diese Schadensmeldung zunächst zu validieren, ggf. neu zu kategorisieren und anschließend die Bearbeitungspriorität 
        zu ranken.

        - Input-Daten -
        Datum
        Titel: Titel der Schadensmeldung (kann relevante Informationen beinhalten).
        Bild: Ein Bild des festgestellten Schaden.
        Beschreibung: Freitextfeld für den User zur beschreibung des Schadens.
        Kategorie: Einordnung des Schadens durch den User in ein der folgenden Kategorien:
            - Straßen bzw. Wegschäden, 
            - Straßenbeleuchtung, 
            - Defekte Ampel, 
            - Abfallentsorgung, 
            - Vandalismus, 
            - Grünfläche/Unkraut/Eichenprozessionsspinner, 
            - Schaden an Brunnen, 
            - Verstopfter Gulli,
            - Tiere, 
            - Verkehrshinweise, 
            - Straßenreinigung/Winterdienst, 
            - Spielplatz verunreinigt/defekt.,
            - Bürgeranregungen

        - Vorgehensweise -
        1. Validiere anhand des Bildes, der Kategorie und der Beschreibung, ob der Schaden korrekt gemeldet wurde, dass es keine 
        Fehlbeschreibung des im Bild zusehenden Schadens gibt (Bild und beschriebener Schaden passen nicht zusammen) und, ob eine passende Kategorie
        zum Schaden gewählt wurde.
        2. Falls die Kategorie FALSCH gewählt wurde, ändere diese zu einer passenderen Beschreibung ab. Sollte diese nicht falsch gewählt worden sein 
        oder es keine passende Kategorie gibt überspringe diesen Schritt und ändere die Kategorie nicht ab.
        3. Ordne den Schaden einer der untenstehenden Prioritätsstufen zu.

        - Prioritätstypen -
        **High-Priority** (Sofortige Bearbeitung <24h)
        Kriterien:
        - Lebensgefahr
        - Elektrische Defekte (freiliegende Kabel, schmorende Leitungen)
        - Einsturzgefahr (tiefe Schlaglöcher >20cm, einsturzgefährdete Mauern)
        - Akute Vergiftungsgefahr (auslaufende Chemikalien)
        - Verkehrssicherheit
        - Ampeln komplett ausgefallen (>4h)
        - Unfallschwerpunkte mit >3 Meldungen/Tag
        - Sichtbehinderungen für Fußgänger/LKW
        - Kritische Infrastruktur
        - Wasseraustritt an Stromkästen
        - Gullydeckel fehlend in Hauptverkehrszeiten
        - Notausgänge blockiert

        **Medium-Priority** (Bearbeitung <72h)
        Kriterien:
        - Gesundheitsrisiken
        - Müllüberlauf mit Madenbefall
        - Rattenbefall in Wohngebieten
        - Stark veralgte Gehwege (>30% Fläche)
        - Funktionseinschränkungen
        - Straßenlaternen mit Flackereffekt (>10% der Nacht)
        - Spielgeräte mit lockeren Schrauben
        - Parkbänke mit abstehenden Splintern
        - Kapazitätsprobleme
        - Gullyverstopfung mit beginnender Überflutung
        - 3+ beschädigte Fahrradständer
        - Vandalierte Müllcontainer im Hochhausgebiet
        - Wenn dadurch auch materielle Schäden entstehen können

        **Low-Priority** (Bearbeitung <14 Tage)
        Kriterien:
        - Kosmetische Mängel
        - Einzelne Graffitis an Wänden
        - Leichter Unkrautwuchs (<10cm Höhe)
        - Oberflächenkorrosion ohne Stabilitätsrisiko
        - Natürliche Prozesse
        - Laubansammlungen außerhalb der Rutschgefahr
        - Vogelnester in nicht frequentierten Bereichen
        - Saisonaler Pollenflug
        - Planbare Arbeiten
        - Wunsch nach zusätzlichen Mülleimern
        - Präventive Baumpflege
        - Farbabblätterungen an Schildern

        - Output-
        Die Validierung, also ob der Schadensfall zu dem Bild passt, und die Priorität im folgenden Format:
        Validierung:
        ### Antwort ###
        Priorität:
        ### Antwort ###

        - Beispiele -

        Beispiel 1:
        Titel: Flackernde Straßenlaterne
        Bild: Bild einer ausgeschalteten Straßenlaterne.
        Kategorie: Straßenbeleuchtung
        Geo-Position: Ort des festgestellten Schadens.
        Beschreibung: Straßenlaterne vor meinem Haus flackert

        Priorität: 
        medium
        Begründung:
        Störeffekt bei Nacht.

        Beispiel 2:
        Titel: Überfüllter Mülleimer
        Bild: Bild eines überfüllten Mülleimers.
        Kategorie: Stadtreinigung
        Geo-Position: Ort des festgestellten Schadens.
        Beschreibung: Mülleimer im Park ist überfüllt

        Priorität:
        low
        Begründung: 
        nervig, aber nicht Lebensgefährlich.

        Beispiel 3:
        Titel: Scharfkantige Eisen an Grundschule
        Bild: Bild eines abgeknickten Laternenmastes.
        Kategorie: Straßen bzw. Wegschäden
        Geo-Position: Ort des festgestellten Schadens.
        Beschreibung: An der Grundschule ragen scharfkantige Armierungseisen aus einem umgestürzten Laternenmast

        Priorität:
        high
        Begründung:
        Verletzungsgefahr für Kinder

        - Hinweise -
        Antworte kurz und Prägnant und Begründe deine Entscheidung in jeweils einem Satz.
        """

    text_content = (
        f"Bitte validiere und priorisiere diesen Schadensfall:\n"
        f"Datum: {report.get('date', '')}\n"
        f"Titel: {report.get('title', '')}\n"
        f"Beschreibung: {report.get('description', '')}\n"
        f"Vorgeschlagene Kategorie: {report.get('category', '')}\n\n"
    )

    user_content = [{"type": "text", "text": text_content}]

    if "image_data" in report:
        for b64 in report["image_data"]:
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                }
            )
    elif "image_paths" in report:
        for path in report["image_paths"]:
            encoded = encode_image(path)
            user_content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{encoded}"},
                }
            )

    messages = [
        {
            "role": "system",
            "content": ranking_system_prompt,
        },
        {"role": "user", "content": user_content},
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        answer = completion.choices[0].message.content.strip()
        return {"answer": answer, "raw_response": None}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    damage_report = {
        "date": "2024-08-15",
        "title": "Kaputte Parkbank",
        "description": "Die Parkbank im Stadtpark ist beschädigt und unbrauchbar. Es gibt offensichtliche Brüche und lose Sitzflächen.",
        "category": "Instandhaltung",
        "image_paths": ["templates/images/defekte-parkbank.jpg"],
    }

    response = process_damage_report(damage_report)
    print(response)
