from tkinter import Toplevel, Label, Entry, Button, StringVar, messagebox, Frame, Tk
from tkinter import ttk
import os
import json
from logic.docx_handler import DocxHandler

class ManualEntryScreen(ttk.Frame):
    def __init__(self, master, open_settings_callback, on_submit_callback):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.master = master
        self.open_settings_callback = open_settings_callback
        self.on_submit_callback = on_submit_callback

        # Load placeholders and templates
        SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "..", "settings.json")
        with open(SETTINGS_PATH, "r") as f:
            settings = json.load(f)
        self.placeholders = settings.get("placeholders", [])
        self.template_names = settings.get("template_names", [])
        self.assets_path = settings.get("asset_path", "assets")

        # Build entry fields for all placeholders
        self.entries = {}
        for ph in self.placeholders:
            label = ttk.Label(self, text=f"{ph['name']} ({ph['syntax']})")
            label.pack()
            entry = ttk.Entry(self)
            entry.pack()
            self.entries[ph['syntax']] = entry

        # Submit button
        submit_btn = ttk.Button(self, text="Submit", command=self.populate_documents)
        submit_btn.pack(pady=10)

        # For previewing
        self.populated_docs = []
        self.current_preview = 0
        self.preview_label = ttk.Label(self, text="")
        self.preview_label.pack(pady=10)
        self.prev_btn = ttk.Button(self, text="Previous", command=self.prev_preview)
        self.next_btn = ttk.Button(self, text="Next", command=self.next_preview)
        self.save_all_btn = ttk.Button(self, text="Save All", command=self.save_all)
        # Buttons will be packed as needed

    def populate_documents(self):
        # Gather user input for all placeholders
        replacements = {syntax: entry.get() for syntax, entry in self.entries.items()}

        # Generate populated documents for each template
        self.populated_docs = []
        for template_name in self.template_names:
            template_path = os.path.join(self.assets_path, template_name)
            handler = DocxHandler(template_path)
            handler.replace_placeholders(replacements)
            self.populated_docs.append(handler)
        self.current_preview = 0
        self.show_preview()

        # After populating self.populated_docs in ManualEntryScreen
        for widget in self.master.winfo_children():
            widget.destroy()
        from gui.preview_screen import PreviewScreen
        PreviewScreen(self.master, self.populated_docs, self.on_submit_callback)

    def show_preview(self):
        if not self.populated_docs:
            self.preview_label.config(text="No documents to preview.")
            return
        handler = self.populated_docs[self.current_preview]
        # Show first paragraph as preview (or customize as needed)
        preview_text = handler.document.paragraphs[0].text if handler.document.paragraphs else "(Empty)"
        self.preview_label.config(
            text=f"Preview {self.current_preview+1}/{len(self.populated_docs)}:\n{preview_text}"
        )
        # Show/hide navigation and save buttons
        self.prev_btn.pack_forget()
        self.next_btn.pack_forget()
        self.save_all_btn.pack_forget()
        if self.current_preview > 0:
            self.prev_btn.pack(side="left", padx=10)
        if self.current_preview < len(self.populated_docs) - 1:
            self.next_btn.pack(side="right", padx=10)
        if self.current_preview == len(self.populated_docs) - 1:
            self.save_all_btn.pack(pady=10)

    def next_preview(self):
        if self.current_preview < len(self.populated_docs) - 1:
            self.current_preview += 1
            self.show_preview()

    def prev_preview(self):
        if self.current_preview > 0:
            self.current_preview -= 1
            self.show_preview()

    def save_all(self):
        from tkinter import filedialog, messagebox
        save_dir = filedialog.askdirectory(title="Select folder to save documents")
        if not save_dir:
            return
        for i, handler in enumerate(self.populated_docs):
            filename = f"populated_{i+1}.docx"
            handler.save(os.path.join(save_dir, filename))
        messagebox.showinfo("Saved", f"Saved {len(self.populated_docs)} documents.")
        self.on_submit_callback()

def main():
    root = Tk()
    root.title("Word Template Helper")
    # app = MainScreen(root, template_path)  # Uncomment and define MainScreen and template_path as needed
    root.mainloop()

if __name__ == "__main__":
    main()