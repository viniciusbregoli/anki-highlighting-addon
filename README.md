# Anki Word Highlighter Add-on

This Anki add-on enhances the study process by allowing you to dynamically color specific words or phrases in the answer of a flashcard.

## Features

-   **On-the-fly Highlighting**: A text area is displayed on the question side of your cards.
-   **Text Coloring**: Enter any words or phrases into the text area. When you reveal the answer, any matching text will be colored red.
-   **Case-Insensitive & Substring Matching**: The matching is case-insensitive and supports partial matches (e.g., typing "proto" will color "protocol").

## How to Use

1.  When studying a card, you will see a text area below the question.
2.  Type the text you want to find in the answer into this box. You can enter multiple words separated by spaces.
3.  Click "Show Answer".
4.  The add-on will find and color all occurrences of your specified text in the card's answer.

## Installation

1.  Go to `Tools` > `Add-ons` > `View Files` in Anki to open the add-ons folder.
2.  Place the `my_addon` folder inside the `addons21` directory.
3.  Restart Anki.

### For Flatpak Users (Linux)

If you installed Anki via Flatpak, the add-on installation path is different, and you'll need to grant an extra permission.

1.  **Find your addons folder**: The path is typically `~/.var/app/net.ankiweb.Anki/data/Anki2/addons21/`.
2.  **Install the add-on**: Copy or symlink the `my_addon` folder to this location.
3.  **Grant permission**: Anki needs permission to access the add-on's files if they are located outside of the sandbox. Run the following command in your terminal:
    ```sh
    flatpak override --user --filesystem=/path/to/your/anki-addon-project:ro net.ankiweb.Anki
    ```
    Replace `/path/to/your/anki-addon-project` with the actual path to this project's folder.
4.  Restart Anki. 