import xml.parsers.expat as expat
import html

class XMLParserWithPosition:
    """
    A custom XML parser that records the position of words inside text elements.

    This class is designed to parse XML files and identify word boundaries within the "w:t" elements
    (representing text) while maintaining the position information for each word. The parsing is performed
    using the "expat" XML parser provided by the "xml.parsers.expat" module.

    Attributes:
        parser (xml.parsers.expat.ParserCreate): The expat XML parser object used for parsing the XML content.
        current_text_span (str): A temporary variable used to store the text content of the current "w:t" element.
        words (list): A list of tuples containing word forms and their corresponding start and end offsets
                     inside the XML text.

    Methods:
        start_element(name, attrs): Callback method invoked when the parser encounters a start tag.
        end_element(name): Callback method invoked when the parser encounters an end tag.
        char_data(data): Callback method invoked when the parser encounters character data.

        find_words(text): Helper method that identifies word boundaries within the provided text.
    """
    def __init__(self):
        self.parser = expat.ParserCreate()
        self.current_text_span = ""
        self.words = []

        self.parser.StartElementHandler = self.start_element
        self.parser.EndElementHandler = self.end_element
        self.parser.CharacterDataHandler = self.char_data

    def start_element(self, name, attrs):
        if name == "w:t":
            self.current_text_span = ""

    def end_element(self, name):
        if name == "w:p" and self.words and self.words[-1][0] != " ":
            self.words.append((" ", 0, 0))
        if name == "w:t":
            cursor = 0
            # escape text span to get the correct length of the text, because the text can contain special characters
            # dont escape quotes as they have unicode representation in XML, not like & or <,>
            escaped_text_span = html.escape(self.current_text_span, quote=False)
            # get words without escaping because we need to find them in the original text
            words = self.find_words(self.current_text_span)
            position = self.parser.CurrentByteIndex - len(escaped_text_span.encode())
            for word in words:
                escaped_word = html.escape(word, quote=False).encode()
                self.words.append((word, position + cursor, position + cursor + len(escaped_word)))
                cursor += escaped_text_span.encode()[cursor:].find(escaped_word) + len(escaped_word)
            self.current_text_span = ""

    def char_data(self, data):
        self.current_text_span += data

    def find_words(self, text):
        segments = []
        current_segment_start = 0

        for i, char in enumerate(text):
            if char.isalnum():
                if current_segment_start is None:
                    current_segment_start = i
            else:
                if current_segment_start is not None:
                    segments.append(text[current_segment_start:i])
                    current_segment_start = None

                segments.append(char)

        # In case the text ends with a word
        if current_segment_start is not None:
            segments.append(text[current_segment_start:])

        return segments
