from deep_translator import GoogleTranslator
import requests
import json
import urllib.parse
import sys
import os


def get_translation(text, source="et", target="en"):
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def main():
    if len(sys.argv) > 1:
        inp = sys.argv[1]
    else:
        sys.exit("Missing input")

    varb = f'https://api.sonapi.ee/v2/{inp}'
    response = requests.get(varb)
    
    if response.status_code in (400, 404, 500):
        messages = {
            404: "Vigane sisend",
            400: "Sõna ei leitud",
            500: "Midagi läks rappa"
        }
        sys.exit(messages[response.status_code])

    data = response.json()
    
    try:
        w = data['estonianWord']
        p = data['searchResult'][0]['meanings'][0]['partOfSpeech'][0]['value'].capitalize()
    except (KeyError, IndexError):
        sys.exit("Unexpected data format")

    p_eng_map = {
        "Nimisõna": "/Noun",
        "Omadussõna": "/Adjective",
        "Tegusõna": "/Verb",
        "Määrsõna": "/Adverb",
        "Omadussõna nimisõna": "/Adjective & Noun",
        "Sidesõna": "Conjunction",
        "Asesõna": "Pronoun",
        "Arvsõna": "Numeral"
    }
    p = p.split(' ', 1)[0]
    p = p.replace(',', '')
    p_eng = p_eng_map.get(p, "")

    filepath = os.path.expanduser(f"~/Documents/Projects/Coding/Genekas/{inp}.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"\n**Tänane WOTD**\n{w.capitalize()} - {p.capitalize()}{p_eng}\n")
        print(f"\n**Tänane WOTD**\n{w.capitalize()} - {p.capitalize()}{p_eng}")

        if p in ("Nimisõna", "Omadussõna", "Omadussõna nimisõna"):
            word_forms_dict = {
                form['morphValue']: form['value']
                for form in data['searchResult'][0]['wordForms']
                if form['morphValue'] in [
                    'ainsuse nimetav', 'ainsuse omastav', 'ainsuse osastav',
                    'mitmuse nimetav', 'mitmuse omastav', 'mitmuse osastav'
                ]
            }
            verb_str = (
              word_forms_dict['ainsuse nimetav'] + ', ' + 
              word_forms_dict['ainsuse omastav'] + ', ' + 
              word_forms_dict['ainsuse osastav'] + '; ' + 
              word_forms_dict['mitmuse nimetav'] + ', ' + 
              word_forms_dict['mitmuse omastav'] + ', ' + 
              word_forms_dict['mitmuse osastav'].replace(',', '/')
            )
            f.write(f"*{verb_str}*\n")
            print(f"*{verb_str}*\n")
        
        
        elif p == "Tegusõna":
            verb_forms_dict = {
                form['morphValue']: form['value']
                for form in data['searchResult'][0]['wordForms']
                if form['morphValue'] in [
                    'ma-infinitiiv e ma-tegevusnimi', 'da-infinitiiv e da-tegevusnimi', 
                    'kindla kõneviisi oleviku ainsuse 3.p.', 'kindla kõneviisi lihtmineviku ainsuse 3.p.',
                    'mitmeosalise verbi pööratud ja eitatud nud-kesksõna', 
                    'mineviku umbisikuline kesksõna e tud-kesksõna'
                ]
            }
            verb_str = (
              verb_forms_dict['ma-infinitiiv e ma-tegevusnimi'] + ', ' +
              verb_forms_dict['da-infinitiiv e da-tegevusnimi'] + '; ' +
              verb_forms_dict['kindla kõneviisi oleviku ainsuse 3.p.'] + ', ' +
              verb_forms_dict['kindla kõneviisi lihtmineviku ainsuse 3.p.'] + '; ' +
              verb_forms_dict['mitmeosalise verbi pööratud ja eitatud nud-kesksõna'] + ', ' +
              verb_forms_dict['mineviku umbisikuline kesksõna e tud-kesksõna']
            )
            f.write(f"*{verb_str}*\n")
            print(f"*{verb_str}*\n")

        elif p == "Määrsõna":
            f.write(f"*{w}*\n")
            print(f"*{w}*\n")

        f.write("\n**Tähendused/Meanings:**\n")
        print("**Tähendused/Meanings:**")
        meanings = data['searchResult'][0].get('meanings', [])
        all_examples = []
        for i, meaning in enumerate(meanings):
            est_def = f"🇪🇪 **{i + 1}.** {meaning['definition']}"
            eng_def = get_translation(meaning['definition'])
            f.write(f"{est_def}\n🇬🇧 **{i + 1}.** {eng_def}\n")
            print(f"{est_def}\n🇬🇧 **{i + 1}.** {eng_def}")
            examples = meaning.get('examples', [])
            all_examples.extend(examples)

        if all_examples:
            f.write("\n**Näited/Examples:**\n")
            print("\n**Näited/Examples:**")
            for example in all_examples:
                translation = get_translation(example)
                ex_line = f"● {example} ||{translation}||"
                f.write(ex_line + "\n")
                print(ex_line)

        f.write("\n**Sünonüümid/Synonyms:** \n#\n")
        print("**Sünonüümid/Synonyms:** \n#\n")

        sonaveeb_url = f"https://sonaveeb.ee/search/unif/dlall/dsall/{urllib.parse.quote(w)}/1/est\n"
        f.write("\n**Sõnaveeb:**\n" + sonaveeb_url)
        print("**Sõnaveeb:**\n" + sonaveeb_url)
        f.write("\nPalun öelge mulle, kui mõni tähendus puudub või on vale. Kui soovite kirjutada oma lause, tehke seda #wotd_writing.")

if __name__ == "__main__":
    main()

