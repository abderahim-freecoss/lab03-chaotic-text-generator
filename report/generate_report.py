"""Build the one-page French Lab 03 report from the evaluated result files."""
import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).with_name("farahi_abderahim_rapport_lab03.pdf")
metrics = json.loads((ROOT / "results/metrics.json").read_text(encoding="utf-8"))
real = json.loads((ROOT / "results/ewt_results.json").read_text(encoding="utf-8"))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleFr", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17,
                          leading=20, textColor=colors.HexColor("#183153"), alignment=TA_LEFT, spaceAfter=3))
styles.add(ParagraphStyle(name="Sub", parent=styles["Normal"], fontSize=8.5, leading=11,
                          textColor=colors.HexColor("#526173"), spaceAfter=6))
styles.add(ParagraphStyle(name="SectionFr", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10,
                          leading=12, textColor=colors.HexColor("#183153"), spaceBefore=4, spaceAfter=3))
styles.add(ParagraphStyle(name="BodyFr", parent=styles["BodyText"], fontSize=8.1, leading=10.5, spaceAfter=3))
styles.add(ParagraphStyle(name="SmallFr", parent=styles["BodyText"], fontSize=7.4, leading=9.1, spaceAfter=1))
styles.add(ParagraphStyle(name="Cell", parent=styles["BodyText"], fontSize=7.2, leading=8.5))
styles.add(ParagraphStyle(name="CellHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.2,
                          leading=8.5, textColor=colors.white))


def pct(value):
    return f"{value * 100:.1f}%".replace(".", ",")


def make_table(headers, rows, widths):
    data = [[Paragraph(x, styles["CellHead"]) for x in headers]]
    data += [[Paragraph(str(x), styles["Cell"]) for x in row] for row in rows]
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#24476B")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F0F4F8")]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7E0E8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return table


gen = metrics["generation"]
synthetic_rows = [
    ["HMM simple", pct(gen["hmm"]["1.0"]["valid_tag_pattern"]), pct(gen["hmm"]["1.0"]["plausible_subject_verb"]),
     pct(gen["hmm"]["1.0"]["novel_sentences"]), f'{gen["hmm"]["1.0"]["distinct_2"]:.3f}'.replace(".", ",")],
    ["HMM états par rôle", pct(gen["hmm_split"]["1.0"]["valid_tag_pattern"]), pct(gen["hmm_split"]["1.0"]["plausible_subject_verb"]),
     pct(gen["hmm_split"]["1.0"]["novel_sentences"]), f'{gen["hmm_split"]["1.0"]["distinct_2"]:.3f}'.replace(".", ",")],
    ["Trigramme", pct(gen["ngram"]["1.0"]["valid_tag_pattern"]), pct(gen["ngram"]["1.0"]["plausible_subject_verb"]),
     pct(gen["ngram"]["1.0"]["novel_sentences"]), f'{gen["ngram"]["1.0"]["distinct_2"]:.3f}'.replace(".", ",")],
]
base = real["models"]["most-frequent tag"]
hmm = real["models"]["HMM + Viterbi"]
real_rows = [
    ["Tag le plus fréquent", pct(base["accuracy"]), pct(base["known_words"]), pct(base["unknown_words"]), pct(base["whole_sentence"])],
    ["HMM + Viterbi", pct(hmm["accuracy"]), pct(hmm["known_words"]), pct(hmm["unknown_words"]), pct(hmm["whole_sentence"])],
]

story = [
    Paragraph("Lab 03 — Générateur de texte chaotique", styles["TitleFr"]),
    Paragraph("Réalisé par Farahi Abderahim · HMM, Viterbi et trigramme · Corpus synthétique et UD English EWT", styles["Sub"]),
    Paragraph("Problème et solution (5 lignes)", styles["SectionFr"]),
    Paragraph("La génération produit des phrases sans réponse de référence; quelques exemples ne suffisent donc pas à en mesurer la qualité.<br/>"
              "Un HMM génère d’abord une suite d’étiquettes grammaticales, puis les mots correspondants.<br/>"
              "Le modèle trigramme prédit les mots à partir du contexte et peut reprendre des phrases d’entraînement.<br/>"
              "Les métriques automatiques évaluent structure, plausibilité sujet-verbe, nouveauté et diversité sur 500 phrases.<br/>"
              "L’application compare les modèles et utilise Viterbi pour attribuer une étiquette à chaque mot saisi.", styles["BodyFr"]),
    Paragraph("Résultats synthétiques à T = 1.0 (500 phrases par modèle)", styles["SectionFr"]),
    make_table(["Modèle", "Structure valide", "Sujet-verbe", "Nouveauté", "Distinct-2"], synthetic_rows,
               [42*mm, 30*mm, 27*mm, 25*mm, 21*mm]),
    Spacer(1, 3),
    Paragraph("Le HMM simple obtient peu de structures valides (16,2 %), car un état NOUN ne distingue pas le sujet de l’objet. "
              "La séparation des états par rôle fait passer la structure à 100 %, mais n’ajoute pas la connaissance du sens : sa plausibilité sujet-verbe (60,6 %) reste sous celle du trigramme (76,0 %). "
              "Viterbi atteint 100 % sur le test synthétique, dont watch : 37/37, grâce aux 16 patrons réguliers. Pour un jouet d’écriture, T=1,5 avec les états par rôle donne plus de diversité tout en gardant la structure; pour l’autocomplétion, T=0,5 favorise des sorties plus prudentes.", styles["BodyFr"]),
    Paragraph("Exemples générés", styles["SectionFr"]),
    Paragraph("<b>Réussite (structure et association plausibles) :</b> « the happy doctors eat behind the market . » — phrase nouvelle dont le couple sujet-verbe est observé dans l’entraînement. "
              "<b>Échec de sens :</b> « the foxes lose by the school . » — patron valide, mais association sémantique étrange; les états mémorisent les rôles, pas le sens.", styles["BodyFr"]),
    Paragraph("Test sur texte réel — UD English EWT", styles["SectionFr"]),
    make_table(["Modèle", "Exactitude", "Mots connus", "Mots inconnus", "Phrase entière"], real_rows,
               [42*mm, 27*mm, 27*mm, 30*mm, 27*mm]),
    Spacer(1, 3),
    Paragraph(f"Le HMM obtient {pct(hmm['accuracy'])} sur EWT contre 100 % sur le corpus synthétique, et seulement {pct(hmm['unknown_words'])} sur les mots inconnus (7,5 % des tokens). "
              "EWT compte 17 étiquettes, 16 654 mots connus à l’entraînement et 10 359 séquences d’étiquettes distinctes : la langue réelle est bien moins régulière et contient des mots absents de l’apprentissage. "
              f"La mesure actuelle est {pct(hmm['accuracy'])} alors que le guide indique 88,1 %; l’écart de 0,1 point est conservé tel qu’observé. Le HMM ne dépasse le tagueur majoritaire que d’environ 1,9 point.", styles["BodyFr"]),
    Paragraph("Limite : les métriques structurelles sont définies par rapport aux 16 patrons du corpus synthétique et ne mesurent pas la qualité de l’anglais réel.", styles["SmallFr"]),
    PageBreak(),
    Paragraph("Captures de l’application", styles["TitleFr"]),
    Paragraph("Interface du générateur et test du tagueur Viterbi avec un mot hors vocabulaire.", styles["Sub"]),
]

# Keep both application captures together on a dedicated page so they remain
# large enough to read without making the results page cramped.
shot_width, shot_height = 150 * mm, 102.1 * mm
for filename, caption in [
    ("01_generation.png", "Génération de phrases et métriques"),
    ("02_taggueur_mot_inconnu.png", "Tagueur Viterbi et détection d’un mot inconnu"),
]:
    img = Image(str(ROOT / "screenshots" / filename), width=shot_width, height=shot_height)
    img.hAlign = "CENTER"
    story.extend([img, Paragraph(caption, styles["SmallFr"]), Spacer(1, 2 * mm)])

doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                        topMargin=12*mm, bottomMargin=12*mm, title="Rapport Lab 03 — Farahi Abderahim")
doc.build(story)
print(OUT)
