import customtkinter as ctk
import requests
from io import BytesIO
from PIL import Image
import os
import mtgSearch as mtgsearch

DIR = os.path.dirname(os.path.abspath(__file__))
THEME_PATH = os.path.join(DIR, "theme_assets", "custom_theme.json")
ctk.set_appearance_mode("light")
ctk.set_default_color_theme(THEME_PATH)

class MainFrame(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1)
        self.title_label = ctk.CTkLabel(self, text="MTG Card Database", font=ctk.CTkFont(size=28, weight="bold"))
        self.title_label.grid(row=0, column=1, pady=(80, 6))

        self.subtitle_label = ctk.CTkLabel(self, text="Powered by Scryfall API")
        self.subtitle_label.grid(row=1, column=1, pady=(0, 40))

        #fuzzy card search
        self.search_button = ctk.CTkButton(self, text="Card search", width=200, height=40, command=master.show_search_frame)
        self.search_button.grid(row=2, column=0)
        
        #set search button
        self.set_search_button = ctk.CTkButton(self, text="Set search", width=200, height=40,command=master.show_set_search_frame)
        self.set_search_button.grid(row = 2, column=2, padx= 10)

        #keyword searchbutton
        self.keyword_search_button = ctk.CTkButton(self, text= "keyword search", width=200, height=40, command=master.show_keyword_search_frame)
        self.keyword_search_button.grid(row = 2, column =1)

   

class FuzzySearchFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(0, weight=1, uniform="cols")
        self.grid_columnconfigure(1, weight=1, uniform="cols")
        self.grid_rowconfigure(1, weight=1)

        self.search = ctk.CTkEntry(self, placeholder_text="Search for a card...")
        self.search.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=20)
        self.search.bind("<Return>", self.on_search)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=0, column=1, sticky="ew", padx=(10, 20), pady=20)
        self.button_frame.grid_columnconfigure(0, weight=1)
        
        self.back_button = ctk.CTkButton(self.button_frame, text="Back", command=master.show_main_frame)
        self.back_button.grid(row=0, column=0, sticky="ew", padx=(5, 0))

        self.results = ctk.CTkTextbox(self)
        self.results.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))

        self.image_box = ctk.CTkLabel(self, text= "")
        self.image_box.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))

    def on_filter(self):
        return

    def on_search(self, event=None):
        card_name = self.search.get().strip()
        if not card_name:
            return
        self.results.delete("1.0", "end")
        try:
            card = mtgsearch._get('/cards/named', fuzzy = card_name)
        except requests.RequestException as error:
            self.results.insert("end", f"Network error: {error}")
            return
        if card is None:
            self.results.insert("end", "No card found.")
            return
        self.results.insert("end", mtgsearch._parse_json(card))
        self.show_card_image(mtgsearch._get_card_image_uri(card))

    def show_card_image(self, uri):
            try:
                data = mtgsearch._get_image_bytes(uri)
            except requests.RequestException:
                self.image_box.configure(text="Could not load image")
                return
            if data is None:
                self.image_box.configure(text="Could not load image")
                return
            pil_image = Image.open(BytesIO(data))
            self.card_image = ctk.CTkImage(light_image=pil_image, size=(220, 306))
            self.image_box.configure(image=self.card_image, text="")



class SetSearchFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
       
        self.grid_columnconfigure(0, weight=1, uniform="cols")
        self.grid_columnconfigure(1, weight=1, uniform="cols")
        self.grid_rowconfigure(1, weight=1)

        self.search = ctk.CTkEntry(self, placeholder_text="Search for a set (e.g. ltr)...")
        self.search.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=20)
        self.search.bind("<Return>", self._create_buttons)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=0, column=1, sticky="ew", padx=(10, 20), pady=20)
        self.button_frame.grid_columnconfigure(0, weight=1, uniform="btns")
        self.button_frame.grid_columnconfigure(1, weight=1, uniform="btns")

        self.filter_button = ctk.CTkOptionMenu(self.button_frame, values=["Any", "Creature", "Legendary"], command=self.filter_by_selection)
        self.filter_button.set("Any")
        self.cards = []


        self.filter_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.back_button = ctk.CTkButton(self.button_frame, text="Back", command=master.show_main_frame)
        self.back_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))
      
        self.results = ctk.CTkScrollableFrame(self)
        self.results.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))
        self._create_buttons()


        self.image_box = ctk.CTkLabel(self, text= "")
        self.image_box.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))

    def _create_buttons(self, event = None):
        #TODO: multi-thread processing for better efficiency
        set_name = self.search.get().strip()
        if not set_name:
            return
        for widget in self.results.winfo_children():
            widget.destroy()
        matches = mtgsearch._find_sets(set_name)
        if not matches:
            return
        self.cards = mtgsearch._get_set_cards(matches[0])
        self.filter_by_selection()

    def _filter_cards(self, cards):
        if not cards:
            self.filter_button.configure(text = "nothing to filter")


    def _on_card_click(self, card):
        uri = mtgsearch._get_card_image_uri(card)
        try:
            data = mtgsearch._get_image_bytes(uri)
        except requests.RequestException:
            self.image_box.configure(text="Could not load image")
            return
        if data is None:
            self.image_box.configure(text="Could not load image")
            return
        pil_image = Image.open(BytesIO(data))
        self.card_image = ctk.CTkImage(light_image=pil_image, size=(220, 306))
        self.image_box.configure(image=self.card_image, text="")
        
    def filter_by_selection(self, event = None):
        choice = self.filter_button.get()

        for widget in self.results.winfo_children():
            widget.destroy()

        for card in self.cards:
            type_line = card.get("type_line", "")
            if choice == "Creature" and "Creature" not in type_line:
                continue
            if choice == "Legendary" and "Legendary" not in type_line:
                continue
         

            _button = ctk.CTkButton(
                self.results,
                text=card['name'],
                anchor="w",
                command= lambda c = card: self._on_card_click(c)
            )
            _button.pack(fill = "x", pady =2)


    #def _get_card_image():


   

  


class keywordsFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        
        self.grid_columnconfigure(0, weight=1, uniform="cols")
        self.grid_columnconfigure(1, weight=1, uniform="cols")
        self.grid_rowconfigure(1, weight=1)

        self.search = ctk.CTkEntry(self, placeholder_text="Search for a card...")
        self.search.grid(row=0, column=0, sticky="ew", padx=(20, 10), pady=20)
        self.search.bind("<Return>", self.on_search)

        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=0, column=1, sticky="ew", padx=(10, 20), pady=20)
        self.button_frame.grid_columnconfigure(0, weight=1, uniform="btns")
        self.button_frame.grid_columnconfigure(1, weight=1, uniform="btns")

        self.filter_button = ctk.CTkButton(self.button_frame, text="Filter")
        self.filter_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.back_button = ctk.CTkButton(self.button_frame, text="Back", command=master.show_main_frame)
        self.back_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.results = ctk.CTkScrollableFrame(self)
        self.results.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))
       
        self._create_buttons()
        
        self.image_box = ctk.CTkTextbox(self, state="disabled", wrap = "word")
        self.image_box.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))

    def _create_buttons(self):
        keywords = mtgsearch._get_keywords()
        for key in keywords:
            _button = ctk.CTkButton(
                self.results,
                text=key,
                anchor="w",
                command=lambda k=key: self.on_key_word_click(k)
                    )
            _button.pack(fill = "x", pady=2) 


    def _get_keyword_definition_(self, key):
        keyword = mtgsearch._get_keywords()
        definition = keyword[key]
        return definition

    
    def on_key_word_click(self, key):
        self.image_box.configure(state="normal")
        self.image_box.delete("1.0", "end")
        self.image_box._textbox.tag_config("title", font=("Arial", 20, "bold"))
        self.image_box.insert("end", key + "\n", "title")
        self.image_box.insert("end", self._get_keyword_definition_(key))
        self.image_box.configure(state="disabled")

    def on_search(self, event = "Tab"):
        keyword_name = self.search.get().strip()
        if not keyword_name:
            return
        
    


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MTG Search tool")
        self.geometry("720x460")
        self.minsize(720,460)
        self.maxsize(720, 460)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = MainFrame(self)
        self.search_frame = FuzzySearchFrame(self)
        self.set_search_frame = SetSearchFrame(self)
        self.keyword_frame = keywordsFrame(self)
        self.show_main_frame()

        self.bind("<Key-1>", lambda event: self._show(self.search_frame))
        self.bind("<Key-2>", lambda event: self._show(self.keyword_frame))
        self.bind("<Key-3>", lambda event: self._show(self.set_search_frame))
        self.bind("<Escape>", lambda event: self._show(self.main_frame))

    def _show(self, frame):
        for f in (self.main_frame, self.search_frame, self.set_search_frame, self.keyword_frame):
            f.grid_forget()
        frame.grid(row=0, column=0, sticky="nsew")

    def show_main_frame(self):
        self._show(self.main_frame)

    def show_search_frame(self):
        self._show(self.search_frame)

    def show_set_search_frame(self):
        self._show(self.set_search_frame)

    def show_keyword_search_frame(self):
        self._show(self.keyword_frame)