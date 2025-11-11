from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.storage.jsonstore import JsonStore
from kivy.core.audio import SoundLoader
import random
import os

store = JsonStore("score.json")

class MenuScreen(Screen):
    best_moves = NumericProperty(0)
    def on_pre_enter(self):
        self.best_moves = store.get("best")["moves"] if store.exists("best") else 0

class GameScreen(Screen):
    cards = ListProperty([])
    first_card = ObjectProperty(None)
    lock = BooleanProperty(False)
    moves = NumericProperty(0)
    matched = NumericProperty(0)
    win_sound = None

    def on_pre_enter(self):
        app_dir = os.path.dirname(os.path.abspath(__file__))
        sound_path = os.path.join(app_dir, "mission_passed.mp3")
        if not os.path.exists(sound_path):
            sound_path = os.path.join(app_dir, "mission_passed.wav")
        self.win_sound = SoundLoader.load(sound_path) if os.path.exists(sound_path) else None
        self.reset_game()

    def reset_game(self):
        self.ids.grid.clear_widgets()
        self.moves = 0
        self.matched = 0
        self.first_card = None
        self.lock = False
        icons = ["🍎","🍐","🍊","🍉","🍇","🍓","🍒","🥝"] * 2
        random.shuffle(icons)
        self.cards = icons
        for icon in self.cards:
            card = Card(icon=icon)
            card.game = self
            self.ids.grid.add_widget(card)

    def check_match(self, clicked_card):
        if self.lock:
            return
        if not self.first_card:
            self.first_card = clicked_card
            return
        self.lock = True
        self.moves += 1
        if clicked_card.icon == self.first_card.icon:
            clicked_card.revealed = True
            self.first_card.revealed = True
            self.first_card = None
            self.lock = False
            self.matched += 2
            if self.matched == len(self.cards):
                Clock.schedule_once(self.end_game, 0.5)
        else:
            first = self.first_card
            Clock.schedule_once(lambda dt: self.hide_cards(first, clicked_card), 1)
            self.first_card = None

    def hide_cards(self, c1, c2):
        c1.reveal(False)
        c2.reveal(False)
        self.lock = False

    def end_game(self, dt):
        if not store.exists("best") or self.moves < store.get("best")["moves"]:
            store.put("best", moves=self.moves)
        if self.win_sound:
            self.win_sound.play()
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "menu"), 1.5)

class Card(Screen):
    icon = ObjectProperty("")
    revealed = BooleanProperty(False)
    game = ObjectProperty(None)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.revealed and not self.game.lock:
            self.reveal(True)
            self.game.check_match(self)
        return super().on_touch_down(touch)
    def reveal(self, state):
        self.revealed = state

class MemoryApp(App):
    def build(self):
        return ScreenManager()

if __name__ == "__main__":
    MemoryApp().run()