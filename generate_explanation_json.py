import os
import importlib.util
import json

LANG_FOLDER = "src/astronomical_watch/lang"
OUTFILE = "backend/explanation_texts.json"

def get_lang_from_filename(filename):
    # Npr. explanation_en_card.py → en
    return filename.split("_")[1]

def load_explanation_text(filepath):
    spec = importlib.util.spec_from_file_location("temp_module", filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # podržava i dict i string
    return getattr(mod, "EXPLANATION_TEXT", None)

def main():
    explanations = {}
    for fname in os.listdir(LANG_FOLDER):
        if fname.startswith("explanation_") and fname.endswith("_card.py"):
            lang = get_lang_from_filename(fname)
            path = os.path.join(LANG_FOLDER, fname)
            text = load_explanation_text(path)
            if text:
                explanations[lang] = text

    # Snimi kao JSON sa utf-8
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(explanations, f, ensure_ascii=False, indent=2)

    print(f"Generated {OUTFILE} with {len(explanations)} languages.")

if __name__ == "__main__":
    main()
