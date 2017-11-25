import os

import readability
import whoosh.index
import whoosh.fields
import whoosh.qparser
import whoosh.writing

INDEX_DIR = os.environ.get("INDEX_DIR", "index")

class Index(object):
    def __init__(self):
        # Initialize schema for index creation
        schema = whoosh.fields.Schema(title=whoosh.fields.TEXT(stored=True),
                                      url=whoosh.fields.ID(stored=True),
                                      body_text=whoosh.fields.TEXT)

        # Create index and index object. self.index can be shared between threads.
        if not os.path.exists(INDEX_DIR):
            print("Creating search index at {}".format(INDEX_DIR))
            os.mkdir(INDEX_DIR)
            self.index = whoosh.index.create_in(INDEX_DIR, schema)
        else:
            print("Loading search index at {}".format(INDEX_DIR))
            self.index = whoosh.index.open_dir(INDEX_DIR)

    def index_html(self, html_file_path):
        # TODO(ajayjain): Switch to boilerpipe / a python wrapper
        # TODO(ajayjain): Deduplicate with Luis's code

        # Load HTML file
        content = ""
        with open(html_file_path, 'r') as html_file:
            content = html_file.read()

        # Parse out title and summary
        document = readability.Document(content)
        # TODO(ajayjain): use document.short_title()?
        title = document.title()
        body_text = document.summary()

        # Add to the index
        index_parsed(title, url, body_text)

    def index_parsed(self, title, url, body_text):
        # TODO(ajayjain): Bulk write documents to the index
        writer = whoosh.writing.AsyncWriter(self.index)
        writer.add_document(title=title, url=url, body_text=body_text)
        writer.commit()

    def search(self, query_string):
        # Parse user query string
        query_parser = whoosh.qparser.QueryParser("body_text", self.index.schema)
        query = query_parser.parse(query_string)

        # Search for results in the index
        searcher = self.index.searcher()
        results = searcher.search(query)

        return results

