import re
import spacy
import logging

from spacy import Language

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def filename_finder(text):
    # Load the spacy model and create a nlp object
    nlp = spacy.load('en_core_web_sm')

    # Define a custom entity label for filenames
    label = 'FILENAME'

    # Define a custom extension attribute to store the extracted filenames
    spacy.tokens.Token.set_extension('filename', default=None)

    # Define a list of valid file extensions
    extensions = ['cpp', 'h', 'js', 'ini', 'cc', 'rs', 'html', 'build',
                  'py', 'jsm', 'txt', 'java', 'css', 'c', 'json', 'yml',
                  'gn', 'toml', 'md', 'list', 'yaml', 'idl', 'mm', 'xhtml',
                  'xml', 'sh', 'rst', 'in', 'webidl']

    pattern = fr'([\w/-]*[\w]+\.({"|".join(extensions)}))'

    # Define a custom function to identify and label filenames
    @Language.component('label_filenames')
    def label_filenames(doc):
      # Iterate over the tokens in the doc
      for token in doc:
        # Check if the token text matches the pattern of a filename with a valid extension
        if re.match(f'[\\w/-]*[\\w]+\\.({"|".join(extensions)})[^\\w]*$', token.text):
          # Set the `filename` attribute of the token to the token text
          token._.filename = token.text
          # Set the entity label of the token to the custom label
          token.ent_type = label
      return doc

    # Add the custom function to the pipeline
    nlp.add_pipe('label_filenames', after='ner')

    # Define a regular expression pattern to match file paths that end with a filename with a valid extension
    pattern = fr'([\w/-]*[\w]+\.({"|".join(extensions)})[^\w]*$)'

    # Process the text
    doc = nlp.make_doc(text)

    # Iterate over the tokens in the doc and extract the filenames and file paths
    filenames = []
    file_paths = []
    for token in doc:
      if token._.filename is not None:
        filenames.append(token._.filename)
      elif re.match(pattern, token.text):
        file_paths.append(token.text)

    # Print the filenames and file paths
    print('Filenames:', filenames)
    print('File paths:', file_paths)


def filename_finder2(text):
    extensions = ['cpp', 'h', 'js', 'ini', 'cc', 'rs', 'html', 'build',
                  'py', 'jsm', 'txt', 'java', 'css', 'c', 'json', 'yml',
                  'gn', 'toml', 'md', 'list', 'yaml', 'idl', 'mm', 'xhtml',
                  'xml', 'sh', 'rst', 'in', 'webidl']

    pattern = fr'([\w/-]*[\w]+\.({"|".join(extensions)})[^\w]*$)'
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\'', ' ').replace('"', ' ').replace('(', ' ').\
        replace(')', ' ').replace('[', ' ').replace(']', ' ').replace('{', ' ').replace('}', ' ').replace(':', ' ').\
        replace(',', ' ').replace(';', ' ').replace('|', ' ').replace('!', ' ').replace('?', ' ').replace('\t', ' ').\
        replace('//', ' ').replace(' /', ' ').replace('. ', ' ')

    for el in text.split():
        if re.match(pattern, el):
            print(el)

    my_regex = re.compile(pattern)
    tokens = my_regex.findall(text)
    print(tokens)


def main():
    filename_finder2("The report is saved in the file report.java. Please send me a copy of the spreadsheet data.xlsx "
                     "from /home/user/documents/. I'm checking if I can fine file\path.c or "
                     "file/path/complex/12-test.css. text/python.py:12")


if __name__ == "__main__":
    main()
