from tkinter import Toplevel, Label, Button, Text, Scrollbar, filedialog, messagebox
from tkinter import ttk
import os

from docx import Document

class PreviewScreen(ttk.Frame):
    def __init__(self, master, populated_docs, on_done_callback):
        super().__init__(master)
        self.pack(fill="both", expand=True)
        self.master = master
        self.populated_docs = populated_docs  # List of DocxHandler objects
        self.on_done_callback = on_done_callback
        self.current_index = 0

        self.preview_label = ttk.Label(self, text="")
        self.preview_label.pack(pady=10)

        nav_frame = ttk.Frame(self)
        nav_frame.pack(pady=10)
        self.prev_btn = Button(nav_frame, text="Previous", command=self.prev_doc)
        self.next_btn = Button(nav_frame, text="Next", command=self.next_doc)
        self.save_btn = Button(self, text="Save", command=self.save_current)  # <-- NEW
        self.save_all_btn = Button(self, text="Save All", command=self.save_all)

        self.prev_btn.pack(side="left", padx=5)
        self.next_btn.pack(side="left", padx=5)
        self.save_btn.pack(pady=10)  # <-- Always visible

        self.update_preview()

    def update_preview(self):
        doc = self.populated_docs[self.current_index]
        preview_text = doc.document.paragraphs[0].text if doc.document.paragraphs else "(Empty)"
        self.preview_label.config(
            text=f"Preview {self.current_index+1}/{len(self.populated_docs)}:\n{preview_text}"
        )
        # Show/hide navigation and save buttons
        self.prev_btn["state"] = "normal" if self.current_index > 0 else "disabled"
        self.next_btn["state"] = "normal" if self.current_index < len(self.populated_docs) - 1 else "disabled"
        if self.current_index == len(self.populated_docs) - 1:
            self.save_all_btn.pack(pady=10)
        else:
            self.save_all_btn.pack_forget()

    def next_doc(self):
        if self.current_index < len(self.populated_docs) - 1:
            self.current_index += 1
            self.update_preview()

    def prev_doc(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.update_preview()

    def save_current(self):
        handler = self.populated_docs[self.current_index]
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")],
            initialfile=f"populated_{self.current_index+1}.docx",
            title="Save current document"
        )
        if file_path:
            handler.save(file_path)
            messagebox.showinfo("Saved", f"Document {self.current_index+1} saved.")

    def save_all(self):
        save_dir = filedialog.askdirectory(title="Select folder to save documents")
        if not save_dir:
            return
        for i, handler in enumerate(self.populated_docs):
            filename = f"populated_{i+1}.docx"
            handler.save(os.path.join(save_dir, filename))
        messagebox.showinfo("Saved", f"Saved {len(self.populated_docs)} documents.")
        self.on_done_callback()