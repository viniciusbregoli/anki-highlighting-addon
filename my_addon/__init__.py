# import the main window object (mw) from aqt
from aqt import mw, gui_hooks
from aqt.reviewer import Reviewer
from anki.hooks import wrap
from bs4 import BeautifulSoup
import re

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
}

highlight_text = ""


def add_input_field(html: str, card, context) -> str:
    if context == "reviewQuestion":
        return (
            html
            + """
            <div style='text-align: center; margin-top: 20px;'>
                <textarea id='highlight_words_input' placeholder='Type your answer here...' style='width: 80%; height: 80px;'></textarea>
            </div>
        """
        )
    return html


def store_and_show_answer(text: str, reviewer: Reviewer) -> None:
    global highlight_text
    highlight_text = text
    # Now that we have the text, call the original _showAnswer method
    original_show_answer(reviewer)


def highlight_words_in_answer(html: str, card, context) -> str:
    if context == "reviewAnswer" and highlight_text:
        soup = BeautifulSoup(html, "html.parser")

        # Clean the input by removing punctuation
        cleaned_text = re.sub(r"[^\w\s]", " ", highlight_text)

        # Split into words and filter out stop words
        all_words = cleaned_text.strip().split()
        words_to_highlight = [
            word for word in all_words if word.lower() not in STOP_WORDS
        ]

        if not words_to_highlight:
            return html

        pattern = re.compile(
            r"(" + "|".join(re.escape(word) for word in words_to_highlight) + r")",
            re.IGNORECASE,
        )

        for text_node in soup.find_all(text=True):
            if text_node.parent.name in ["style", "script"]:
                continue

            new_html = pattern.sub(r'<span style="color: red;">\1</span>', text_node)
            if new_html != text_node:
                text_node.replace_with(BeautifulSoup(new_html, "html.parser"))

        return str(soup)
    return html


# Wrap the original _showAnswer function
original_show_answer = Reviewer._showAnswer


def patched_show_answer(reviewer: Reviewer, _old):
    def get_text_and_then(text):
        global highlight_text
        highlight_text = text
        _old(reviewer)

    reviewer.web.evalWithCallback(
        "document.getElementById('highlight_words_input').value || ''",
        get_text_and_then,
    )


Reviewer._showAnswer = wrap(Reviewer._showAnswer, patched_show_answer, "around")

gui_hooks.card_will_show.append(add_input_field)
gui_hooks.card_will_show.append(highlight_words_in_answer)
