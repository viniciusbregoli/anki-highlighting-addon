# import the main window object (mw) from aqt
from aqt import mw, gui_hooks
from aqt.reviewer import Reviewer
from anki.hooks import wrap
from bs4 import BeautifulSoup
import re
import html

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
            <script>
                var textarea = document.getElementById('highlight_words_input');
                if (textarea) {
                    textarea.addEventListener('keydown', function(event) {
                        if (event.ctrlKey && event.key === 'Enter') {
                            event.preventDefault();
                            pycmd('ans');
                        }
                    });
                }
            </script>
        """
        )
    return html


def store_and_show_answer(text: str, reviewer: Reviewer) -> None:
    global highlight_text
    highlight_text = text
    # Now that we have the text, call the original _showAnswer method
    original_show_answer(reviewer)


def highlight_words_in_answer(html_content: str, card, context) -> str:
    # Also check if the input is just whitespace
    if context == "reviewAnswer" and highlight_text and highlight_text.strip():
        soup = BeautifulSoup(html_content, "html.parser")

        # Highlight the original answer content first
        cleaned_text = re.sub(r"[^\w\s]", " ", highlight_text)
        all_words = cleaned_text.strip().split()
        words_to_highlight = [
            word for word in all_words if word.lower() not in STOP_WORDS
        ]

        if words_to_highlight:
            pattern = re.compile(
                r"(" + "|".join(re.escape(word) for word in words_to_highlight) + r")",
                re.IGNORECASE,
            )
            for text_node in soup.find_all(text=True):
                if text_node.parent.name in ["style", "script"]:
                    continue
                new_html = pattern.sub(
                    r'<span style="color: red;">\1</span>', text_node
                )
                if new_html != text_node:
                    text_node.replace_with(BeautifulSoup(new_html, "html.parser"))

        # Prepare the user's answer to be injected
        escaped_user_answer = html.escape(highlight_text)
        user_answer_html = f"""
            <div style='text-align: center; margin-top: 20px; margin-bottom: 20px;'>
                <b>Your Answer:</b>
                <div style='margin-top: 10px; margin-bottom: 20px;'>{escaped_user_answer}</div>
                <hr>
            </div>
        """
        user_answer_soup = BeautifulSoup(user_answer_html, "html.parser")

        # Find the answer separator and inject the user's answer after it
        hr_tag = soup.find("hr", id="answer")
        if hr_tag:
            hr_tag.insert_after(user_answer_soup)
        else:
            # Fallback if the separator is not found: append to the end
            soup.append(user_answer_soup)

        return str(soup)

    return html_content


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
