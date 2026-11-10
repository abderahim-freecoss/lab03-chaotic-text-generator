"""Interactive test bench for the Lab 03 text generators."""
import random
from pathlib import Path

import pandas as pd
import streamlit as st

from src.pipeline import HMM, NGramGenerator, generation_metrics, load_tagged, split_by_document


st.set_page_config(page_title="Générateur de texte chaotique", page_icon="🧪", layout="wide")


@st.cache_resource
def get_models():
    docs = load_tagged()
    train, _ = split_by_document(docs)
    return train, HMM(train), HMM(train, split_states=True), NGramGenerator([w for w, _ in train])


@st.cache_data
def get_evaluation():
    path = Path("results/metrics.json")
    if path.exists():
        import json
        return json.loads(path.read_text(encoding="utf-8"))
    return None


train, hmm_plain, hmm_split, trigram = get_models()
models = {"HMM simple": hmm_plain, "HMM à états séparés par rôle": hmm_split, "Trigramme": trigram}

st.title("Générateur de texte chaotique")
st.caption("Banc d’essai pour comparer trois générateurs, leurs structures grammaticales et leur diversité.")
st.warning(
    "Le corpus est synthétique et la grammaire est très limitée. Les métriques, comme la validité des structures, "
    "sont définies par rapport à ce corpus et ne mesurent pas la qualité de l’anglais réel.",
    icon="⚠️",
)

with st.sidebar:
    st.header("Paramètres de génération")
    model_name = st.selectbox("Modèle", list(models))
    temperature = st.slider("Température", 0.3, 3.0, 1.0, 0.1, help="Une valeur faible rend les tirages plus prévisibles.")
    seed = st.number_input("Graine aléatoire", min_value=0, max_value=10_000_000, value=42, step=1)
    count = st.number_input("Nombre de phrases", min_value=10, max_value=500, value=100, step=10)
    compare = st.checkbox("Comparer les trois modèles aux mêmes réglages", value=False)
    generate = st.button("Générer", type="primary", use_container_width=True)

if generate:
    chosen = list(models.items()) if compare else [(model_name, models[model_name])]
    results_by_model = {}
    for model_index, (name, model) in enumerate(chosen):
        rng = random.Random(int(seed) + model_index if compare else int(seed))
        samples = []
        rows = []
        for _ in range(int(count)):
            if name == "Trigramme":
                words = model.sample_sentence(rng, temperature)
                tags = hmm_split.viterbi(words)
            else:
                words, tags = model.sample_with_states(rng, temperature)
                tags = [tag.split("_")[0] for tag in tags]
            samples.append((words, tags))
            rows.append({"Phrase": " ".join(words), "Séquence de tags": " ".join(tags),
                         "Structure valide": "Oui" if " ".join(tags) in {" ".join(t) for _, t in train} else "Non"})
        metric_tagger = hmm_split if name == "Trigramme" else model
        metrics = generation_metrics(samples, train, metric_tagger)
        results_by_model[name] = (metrics, rows)

    st.session_state["bench_results"] = results_by_model

if "bench_results" in st.session_state:
    for name, (metrics, rows) in st.session_state["bench_results"].items():
        st.subheader(name)
        cols = st.columns(4)
        cols[0].metric("Structure valide", f"{metrics['valid_tag_pattern']:.1%}")
        cols[1].metric("Sujet-verbe plausible", f"{metrics['plausible_subject_verb']:.1%}")
        cols[2].metric("Phrases inédites", f"{metrics['novel_sentences']:.1%}")
        cols[3].metric("Distinct-2", f"{metrics['distinct_2']:.3f}")
        frame = pd.DataFrame(rows)
        st.dataframe(frame, use_container_width=True, hide_index=True, height=360,
                     column_config={
                         "Phrase": st.column_config.TextColumn("Phrase", width=260),
                         "Séquence de tags": st.column_config.TextColumn("Séquence de tags", width=280),
                         "Structure valide": st.column_config.TextColumn("Structure valide", width=130),
                     })
        st.download_button("Télécharger les phrases en CSV", frame.to_csv(index=False).encode("utf-8-sig"),
                           file_name=f"phrases_{name.lower().replace(' ', '_')}.csv", mime="text/csv",
                           key=f"download_{name}")

st.divider()
st.header("Étiqueteur Viterbi")
sentence = st.text_input("Saisis une phrase en anglais", placeholder="the cats watch the birds .")
if sentence.strip():
    words = sentence.lower().split()
    unknown = [word for word in words if word not in hmm_plain.vocab]
    if unknown:
        st.warning("Mot(s) absent(s) du vocabulaire d’entraînement : " + ", ".join(dict.fromkeys(unknown)) +
                   ". Le modèle attribue quand même les étiquettes avec le lissage statistique.")
    if words:
        tags = hmm_plain.viterbi(words)
        st.dataframe(pd.DataFrame({"Mot": words, "Étiquette Viterbi": tags}), use_container_width=True, hide_index=True)

st.divider()
st.header("Résultats de l’évaluation")
evaluation = get_evaluation()
if evaluation:
    t1 = {"HMM simple": evaluation["generation"]["hmm"]["1.0"],
          "HMM à états séparés par rôle": evaluation["generation"]["hmm_split"]["1.0"],
          "Trigramme": evaluation["generation"]["ngram"]["1.0"]}
    st.caption("Évaluation reproductible sur 500 phrases par modèle, à T = 1.0.")
    st.dataframe(pd.DataFrame(t1).T.rename(columns={"valid_tag_pattern": "Structure valide",
                 "plausible_subject_verb": "Sujet-verbe plausible", "novel_sentences": "Nouveauté",
                 "distinct_2": "Distinct-2"}).style.format("{:.1%}", subset=["Structure valide", "Sujet-verbe plausible", "Nouveauté"])
                 .format("{:.3f}", subset=["Distinct-2"]), use_container_width=True)
    import altair as alt
    chart_rows = []
    for label, key in (("HMM simple", "hmm"), ("HMM à états séparés par rôle", "hmm_split"), ("Trigramme", "ngram")):
        for temp, values in evaluation["generation"][key].items():
            chart_rows.append({"Température": float(temp), "Modèle": label,
                               "Structures valides": values["valid_tag_pattern"]})
    st.subheader("Structure valide selon la température")
    chart = alt.Chart(pd.DataFrame(chart_rows)).mark_line(point=True).encode(
        x=alt.X("Température:Q", scale=alt.Scale(domain=[0.5, 2.5])),
        y=alt.Y("Structures valides:Q", axis=alt.Axis(format="%"), scale=alt.Scale(domain=[0, 1])),
        color=alt.Color("Modèle:N"), tooltip=["Modèle", "Température", alt.Tooltip("Structures valides:Q", format=".1%")]
    ).properties(height=280)
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("Lance `python -m src.evaluate` pour afficher les résultats d’évaluation et le graphique.")

st.caption("Repères : à T=1, les états séparés atteignent 100 % de structures valides; le trigramme obtient "
           "une meilleure plausibilité sujet-verbe mais recopie parfois des phrases du corpus.")
