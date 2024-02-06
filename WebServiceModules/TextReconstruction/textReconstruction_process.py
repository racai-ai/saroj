import os
import re
import shutil
import tempfile
import zipfile
from xml.sax.saxutils import escape
import traceback

def read_conllup(conllup_file):
    # Initialize an empty list to store the CONLLUP data as dictionaries
    conllup_data = []

    # Open the CONLLUP file for reading
    with open(conllup_file, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            # Skip empty lines and lines starting with "#" (comments)
            if not line.strip() or line.startswith("#"):
                continue

            # Split the line into fields
            fields = [token.strip() for token in re.split(r'(\t|  {2})', line) if token.strip()]

            # Ensure that the line contains at least 14 fields (assuming NER and ANONYMIZED are present)
            if len(fields) < 14:
                raise ValueError("ConLLU-P missing a column")

            # Create a dictionary for the token's features
            token_data = {
                "ID": fields[0],
                "FORM": fields[1],
                "LEMMA": fields[2],
                "UPOS": fields[3],
                "XPOS": fields[4],
                "FEATS": fields[5],
                "HEAD": fields[6],
                "DEPREL": fields[7],
                "DEPS": fields[8],
                "MISC": fields[9],
                "START": fields[10],
                "END": fields[11],
                "NER": fields[12],
                "ANONYMIZED": fields[-1]  # always last column
            }

            # Append the token's dictionary to the list
            conllup_data.append(token_data)

    return conllup_data


def anonymize(conllup_list, input_path, output_path, save_internal_files=False, input_type="docx"):
    # Create a unique temporary file to extract the DOCX content
    temp_file_path = tempfile.mkdtemp(dir='.')
    delta_t = 0
    try:
        if input_type == "docx":
            # Extract the DOCX file
            with zipfile.ZipFile(input_path, "r") as zip_ref:
                zip_ref.extractall(temp_file_path)

            content_path = os.path.join(temp_file_path, "word", "document.xml")
            with open(content_path, "rb") as content_file:
                docx_content = content_file.read()
        else:
            docx_content="<d>"
            with open(input_path, "r", encoding="utf-8", errors='ignore') as fin:
                for line in fin:
                    docx_content+="<w:t>"+escape(line)+"</w:t>"
            docx_content+="</d>"
            docx_content=docx_content.encode("utf-8")

        filtered_conllup_list = [row for row in conllup_list if row["ANONYMIZED"] != "_"]
        for row in filtered_conllup_list:
            start = int(row["START"])
            end = int(row["END"])

            if input_type == "txt": start-=1; end-=1

            anonym = row["ANONYMIZED"].encode("utf-8")
            len_form = len(row["FORM"].encode("utf-8"))

            if anonym == "!DELETE!".encode("utf-8"):
                docx_content = docx_content[:start + delta_t] + docx_content[end + delta_t:]
                delta_t -= end - start
                continue
            else:
                docx_content = docx_content[:start + delta_t] + anonym + docx_content[end + delta_t:]

            if len(anonym) >= end - start:
                delta_t += len(anonym) - len_form
            else:
                delta_t -= end - start - len(anonym)

        if input_type == "docx":
            # Write the modified content back to the file
            with open(content_path, "wb") as content_file:
                content_file.write(docx_content)

            # Recreate the modified DOCX file
            with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=-1) as new_zip_ref:
                for root, _, files in os.walk(temp_file_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_file_path)
                        new_zip_ref.write(file_path, arcname=arcname)
        else:
            docx_content=docx_content.decode()
            docx_content=docx_content.replace("<d>","").replace("</d>","").replace("<w:t>","").replace("</w:t>","")
            with open(output_path, "w", encoding='utf-8') as fout:
                fout.write(docx_content)
    #except Exception as inst:
    #    traceback.print_exc()
    #    raise inst

    finally:
        # Clean up the temporary directory
        if not save_internal_files:
            shutil.rmtree(temp_file_path, ignore_errors=True)
