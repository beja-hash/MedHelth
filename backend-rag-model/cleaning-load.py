import os
import fitz
import re



def clean_text(text):
    text = re.sub(r"Стр\.?\s*\d+|Page\s*\d+", "", text)

    text = re.sub(r"(Министерство.+?\n)+", "", text)

    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    lines = text.split("\n")
    lines = [line for line in lines if len(line.strip()) > 20]
    
    return "\n".join(lines)


path_file = r'C:\\Users\\123\Desktop\\MedProject\data\\clean_data.txt'

with open(path_file, 'w', encoding='utf-8') as f:
    
    for file in os.listdir('./data'):
        if file.endswith('.pdf'):
            path = './data/'+file
            docs = fitz.open(path)
            text = ''
            for page in docs:
                text += page.get_text()
            cleaned_data = clean_text(text)

            f.write(cleaned_data + '\n')
