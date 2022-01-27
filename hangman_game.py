"""
COMP.CS.100 Hangman game/ Hirsipuu peli.

Tekijä:     Veeti Lukin
Sposti:     veeti.lukin@tuni.fi

Description of the program:
Hangman GUI game where you need to guess the secret word before you get hanged.
When the game starts you can see length of the word but every character is
hidden.
You need to guess what letters are part of the word by pressing buttons on
the screen.

App is divided in controller and scenes.
Every scene holds attributes and contains it's own widgets.
"""
import tkinter as tk
from random import choice
from string import ascii_uppercase

BIG_TEXT = ("TkDefaultFont", 20, "bold")
MEDIUM_TEXT = ("TkDefaultFont", 16)
ENG_WORD_FILE = "english_words.txt"
FIN_WORD_FILE = "finnish_words.txt"
# Amount of lives in game will depend of how many state images are listed here
STATE_PICS = ("state0.png", "state1.png", "state2.png", "state3.png",
              "state4.png", "state5.png")
STATE_LOST, STATE_WON = "state_l.png", "state_w.png"

class AppController:
    """
    This Class is the main controller for the app.
    Responsible for:
    Creating root window(tk.Tk object), Hosting and managing scenes of the app
    and holding important instance attributes(variables) and data.
    """

    def __init__(self):
        """
        Constructor to initialize object.
        Initializes root win and ManiMenu frame inside it.
        Also constructs a few instance attributes.
        """
        # language attribute. 0 = english 1 = finnish.
        self.__language_num = 0

        # root window initialization and configuration
        self.__root = tk.Tk()
        self.__root.geometry("720x480")
        self.__root.title("Hangman")

        # frames are different scenes of the app should be none or type
        # tk.Label or its child
        self.__frame = None
        self.switch_frame(MainMenuScene)

        # words
        self.__english_words = self.read_word_file(ENG_WORD_FILE)
        self.__finnsh_words = self.read_word_file(FIN_WORD_FILE)

        # kick off the event loop
        self.__root.mainloop()

    def switch_frame(self, frame_class, object_args=()):
        """
        Switches scene of the app by destroying current frame object and
        initializing
        *frame_class*(tk.Frame object or its child) object on it's place.

        :param frame_class: str, name of the class to switch to.
        :param object_args: tuple, arguments to give for new frame class
                            when object frame is initialized.
                            Can be left empty and is empty by default.
        """
        new_frame_object = frame_class(self.__root, self, self.__language_num,
                                       *object_args)
        # destroy current frame
        if self.__frame is not None:
            self.__frame.destroy()
        self.__frame = new_frame_object
        self.__frame.pack(fill="both", expand=True)

    def get_word(self):
        """
        Returns random word from one of the wordlists(Self.__english_words).
        Language setting(self.__language) will affect.

        :return: str, a word
        """
        wordlist = (self.__english_words, self.__finnsh_words)[self.__language_num]

        if wordlist is None:
            return "ERROR"

        return choice(wordlist).upper()

    def quit(self):
        """
        Quits application by destroying root window(self.__root)
        """
        self.__root.destroy()

    def read_word_file(self, file_name):
        """
        Reads words used in the game from the file with *file_name*
        and adds the to a list object.

        :param file_name:
        :return:
        """
        words = []
        try:
            with open(file_name, mode="r") as file_object:
                for word in file_object:
                    words.append(word.strip())
        except OSError:
            return None

        return words

    def get_language(self):
        return self.__language_num

    def set_language(self, value):
        self.__language_num = value


class MainMenuScene(tk.Frame):
    """
    Main menu scene of application, Children of tk.Frame.
    Used for holding widgets and attributes in main menu scene.

    Here game title is presented you can change language option and move to
    GameScene by pressing button.
    """

    def __init__(self, master, controller, lang):
        """
        Constructor to initialize object.
        Initializes frame and widgets inside of it

        :param master: tk.TK, root window
        :param controller: AppController, controller of the game
        """
        tk.Frame.__init__(self, master)
        self.__controller = controller

        # language selection / top right corner
        # middle
        self.__language_selector = tk.Scale(self, from_=0, to=1,
                                            orient=tk.HORIZONTAL, showvalue=0,
                                            command=self.change_language)
        self.__language_selector.set(lang)

        self.__language_selector.place(relx=0.75, rely=0.05)
        # left
        tk.Label(self, text="English").place(relx=0.675, rely=0.05)
        # right
        tk.Label(self, text="Suomi").place(relx=0.9, rely=0.05)

        # title Label / center of the screen
        self.__title = tk.Label(self, text=("HANGMAN", "HIRSIPUU")[lang],
                                font=BIG_TEXT)
        self.__title.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        # play button /  under title label
        self.__play_button = tk.Button(
            self, text=("Click here to play", "Klikka tästä pelataksesi")[lang],
            command=lambda: self.__controller.switch_frame(GameScene))
        self.__play_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def change_language(self, value):
        """
        """
        lang = self.__controller.get_language()
        value = int(value)
        if value != lang:
            self.__controller.set_language(value)
            self.__controller.switch_frame(MainMenuScene)


class GameScene(tk.Frame):
    """
    Game scene (aka. where the playing happens) of application, Children of
    tk.Frame.
    Used for holding widgets and attributes in game scene.

    Presents picture of hangman, word (as a combination of _ and revealed
    letters)
    and button for every letter.
    """

    def __init__(self, master, controller, lang):
        """
        Constructor to initialize object.
        Initializes frame and widgets inside of it
        Also constructs few attributes.

        :param master: tk.TK, root window
        :param controller: AppController, controller of the game
        """
        tk.Frame.__init__(self, master)
        self.__controller = controller

        # setting secret word
        self.__word = self.__controller.get_word()

        # used for sowing user only parts of the word that has been guessed
        self.__hidden_word = ["_" for _ in range(len(self.__word))]
        self.__word_label = tk.Label(self, text=self.__hidden_word,
                                     font=BIG_TEXT)
        self.__word_label.grid(row=0, column=0, columnspan=2, sticky="nesw")

        # hangman state and pictures modelling the state
        self.__hangman_state = 0
        self.__state_image_objects = []
        for pic in STATE_PICS:
            self.__state_image_objects.append(tk.PhotoImage(file=pic))

        # used for containing picture of representing how close we are being
        # hanged(aka. state)
        self.__state_label = tk.Label(self, image=self.__state_image_objects[
            self.__hangman_state])
        self.__state_label.grid(row=1, column=0, sticky="nesw")

        # used for containing button for every letter
        self.__buttons_per_row = 5
        self.__button_frame = tk.Frame(self)
        self.__button_frame.grid(row=1, column=1, sticky="nesw")

        self.__letters = ascii_uppercase
        if lang == 1:
            self.__letters += "ÄÖ"

        # making buttons for letters
        self.__letter_buttons = {}
        for index, char in enumerate(self.__letters):
            column_number = index % self.__buttons_per_row
            row_number = index // self.__buttons_per_row

            self.__letter_buttons[char] = tk.Button(
                self.__button_frame, text=char, relief=tk.GROOVE,
                command=lambda character=char: self.check_letter(character))

            self.__letter_buttons[char].grid(row=row_number,
                                             column=column_number,
                                             sticky="nesw", pady=1, padx=1)

        self.setup_grids_for_frames()

    def setup_grids_for_frames(self):
        """
        Setups weight for grids inside GameScene frame and button frame(
        self.__button_frame)
        So that they can resize and take desired amount of parent
        widget/window.
        """
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3)

        self.__button_frame.grid_columnconfigure(
            tuple(range(self.__buttons_per_row)), weight=1)
        self.__button_frame.rowconfigure(
            tuple(range(
                len(self.__letter_buttons) // self.__buttons_per_row + 1))
            , weight=1)

    def check_if_finished(self):
        """
        Checks if the game is over. Either you have won or "you have ran out
        of lives".(you are in last state picture)
        If game is over also calls controllers <switch frame> method
        ,to switch to game over scene.

        :return: True if game has finished , False otherwise
        """
        if "".join(self.__hidden_word) == self.__word:
            self.__controller.switch_frame(GameOverScene, ("won", self.__word))
            return True

        if self.__hangman_state == len(self.__state_image_objects):
            self.__controller.switch_frame(GameOverScene,
                                           ("lost", self.__word))
            return True

        return False

    def check_letter(self, char):
        """
        Checks if *char* is inside the word(self.__word)
        If *char* is not inside the word, raises hangman_state
        if *char* is inside, adds correctly guessed letters
        to right places in hidden word(self.__hidden_word)
        Calls <check_if_finished> to check if game ended after this button
        press
        Also calls <update_gui> if game did not end yet

        :param char: str, one letter or character
        """
        if char not in self.__word:
            # button configuration
            self.__letter_buttons[char].config(bg="red", relief=tk.SUNKEN,
                                               state=tk.DISABLED)
            self.__hangman_state += 1

        else:
            # button configuration
            self.__letter_buttons[char].config(bg="green", relief=tk.SUNKEN,
                                               state=tk.DISABLED)
            word_as_list = list(self.__word)

            for index, letter in enumerate(word_as_list):
                if char == letter:
                    self.__hidden_word[index] = letter

        if not self.check_if_finished():
            self.update_gui()

    def update_gui(self):
        """
        Updates Gui widgets.
        Updates hidden word to show already guessed letters(in
        self.__word_label)
        Updates state picture to represent current state
        """
        self.__word_label.configure(text=self.__hidden_word)
        self.__state_label.configure(
            image=self.__state_image_objects[self.__hangman_state])


class GameOverScene(tk.Frame):
    """
    Game Over scene(aka end game screen of the game) of the application,
    Children of tk.Frame.
    Used for holding widgets and attributes in game over scene.

    Presents text showing if user lost or won, picture of hangman and
    play again and quit buttons.
    """

    def __init__(self, master, controller, lang, result, word):
        """
        Constructor to initialize object.
        Initializes frame and widgets inside of it

        :param master: tk.TK, root window
        :param controller: AppController, controller of the game"""
        tk.Frame.__init__(self, master)
        self.__controller = controller

        # used for telling if user won or lost
        self.__result_label = tk.Label(self, text="", font=BIG_TEXT)
        self.__result_label.pack()

        if result == "won":
            self.__result_label.configure(
                text=("Congrats, You won!", "Onnittelut, Voitit pelin!")[lang])
            self.__photo = tk.PhotoImage(file=STATE_WON)
        if result == "lost":
            self.__result_label.configure(
                text=("You lost, you did not guess the word",
                      "Hävisit, et arvannut sanaa")[lang])
            self.__photo = tk.PhotoImage(file=STATE_LOST)

        tk.Label(self, text=(f"The word was {word}", f"Sana oli {word}")[lang],
                 font=MEDIUM_TEXT).pack()

        tk.Label(self, image=self.__photo).pack()

        tk.Button(self, text=("Play again", "Pelaa uudestaan")[lang],
                  command=lambda: controller.switch_frame(GameScene)).pack()

        tk.Button(self, text=("MainMenu", "Päävalikko")[lang],
                  command=lambda: self.__controller.switch_frame(MainMenuScene)).pack(pady=2)

        tk.Button(self, text=("Quit", "Poistu")[lang], bg="red", width=8,
                  command=self.__controller.quit).pack(pady=2)


def main():
    app = AppController()


if __name__ == "__main__":
    main()
