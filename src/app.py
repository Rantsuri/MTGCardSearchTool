import customtkinter as ctk
import requests
import mtgSearch as mtgsearch


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("MTGCardSearchTool/src/theme_assets/custom_theme.json")

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
        self.button_frame.grid_columnconfigure(0, weight=1, uniform="btns")
        self.button_frame.grid_columnconfigure(1, weight=1, uniform="btns")

        self.filter_button = ctk.CTkButton(self.button_frame, text="Filter")
        self.filter_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        self.back_button = ctk.CTkButton(self.button_frame, text="Back", command=master.show_main_frame)
        self.back_button.grid(row=0, column=1, sticky="ew", padx=(5, 0))

        self.results = ctk.CTkTextbox(self)
        self.results.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))

        self.image_box = ctk.CTkTextbox(self)
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

class SetSearchFrame(ctk.CTkFrame):
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

        self.results = ctk.CTkTextbox(self)
        self.results.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))

        self.image_box = ctk.CTkTextbox(self)
        self.image_box.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))

    def on_search(self, event = None):
        set_name = self.searh.get().strip()
        if not set_name:
            return
        self.results.delete("1.0", "end")
        try:
            matches = mtgsearch._find_sets(set_name)
            if not matches:
                self.results.insert("end", "Set not found.")
            elif len(matches) > 1:
                self.results.insert("end", "Multiple sets match:\n")
                for s in matches:
                    self.results.insert("end", f"{s['code']}: {s['name']}\n")
            else:
                cards = mtgsearch._get_set_cards(matches[0])
                self.results.insert("end", f"{matches[0]['name']}: {len(cards)} cards\n\n")
                for c in cards:
                    self.results.insert("end", f"#{c['collector_number']} {c['name']}\n")
        except requests.RequestException as error:
            self.results.insert("end", f"Network error: {error}")




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

        self.results = ctk.CTkTextbox(self)
        self.results.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=(0, 20))
        keywords = mtgsearch._get_keywords()
        for key in keywords:
            self.results.insert("end", f"{key}\n")

        
        self.image_box = ctk.CTkTextbox(self)
        self.image_box.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=(0, 20))

    

    def on_search(self, event = "Tab"):
        keyword_name = self.search.get().strip()
        if not keyword_name:
            return
        self.results.delete("1,0")

    


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