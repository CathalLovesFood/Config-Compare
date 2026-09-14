import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import difflib


class TextCompareApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text File Comparison Tool")
        self.root.geometry("1400x800")

        self.folder1 = ""
        self.folder2 = ""

        self.create_gui()

    # ---------------------------------------------------------
    # GUI
    # ---------------------------------------------------------

    def create_gui(self):

        # =====================================================
        # TOP: Folder selection
        # =====================================================

        folder_frame = ttk.LabelFrame(
            self.root,
            text="Folders to Compare",
            padding=10
        )
        folder_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(folder_frame, text="Folder 1:").grid(
            row=0, column=0, sticky="w"
        )

        self.folder1_entry = ttk.Entry(folder_frame, width=90)
        self.folder1_entry.grid(
            row=0, column=1, padx=5, sticky="ew"
        )

        ttk.Button(
            folder_frame,
            text="Browse...",
            command=self.select_folder1
        ).grid(row=0, column=2, padx=5)

        ttk.Label(folder_frame, text="Folder 2:").grid(
            row=1, column=0, sticky="w", pady=5
        )

        self.folder2_entry = ttk.Entry(folder_frame, width=90)
        self.folder2_entry.grid(
            row=1, column=1, padx=5, sticky="ew"
        )

        ttk.Button(
            folder_frame,
            text="Browse...",
            command=self.select_folder2
        ).grid(row=1, column=2, padx=5)

        folder_frame.columnconfigure(1, weight=1)

        ttk.Button(
            folder_frame,
            text="Compare Folders",
            command=self.compare_folders
        ).grid(row=0, column=3, rowspan=2, padx=15)

        # =====================================================
        # OPTIONS
        # =====================================================

        options_frame = ttk.Frame(self.root)
        options_frame.pack(fill="x", padx=10)

        self.ignore_whitespace = tk.BooleanVar(value=False)
        self.ignore_case = tk.BooleanVar(value=False)

        ttk.Checkbutton(
            options_frame,
            text="Ignore whitespace",
            variable=self.ignore_whitespace
        ).pack(side="left", padx=5)

        ttk.Checkbutton(
            options_frame,
            text="Ignore case",
            variable=self.ignore_case
        ).pack(side="left", padx=5)

        # =====================================================
        # MAIN AREA
        # =====================================================

        main_pane = ttk.PanedWindow(
            self.root,
            orient=tk.HORIZONTAL
        )
        main_pane.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # -----------------------------------------------------
        # LEFT: File list
        # -----------------------------------------------------

        file_frame = ttk.LabelFrame(
            main_pane,
            text="Files",
            padding=5
        )

        main_pane.add(file_frame, weight=1)

        self.file_tree = ttk.Treeview(
            file_frame,
            columns=("status",),
            show="tree headings"
        )

        self.file_tree.heading(
            "#0",
            text="File"
        )

        self.file_tree.heading(
            "status",
            text="Status"
        )

        self.file_tree.column(
            "#0",
            width=250
        )

        self.file_tree.column(
            "status",
            width=100
        )

        tree_scroll = ttk.Scrollbar(
            file_frame,
            orient="vertical",
            command=self.file_tree.yview
        )

        self.file_tree.configure(
            yscrollcommand=tree_scroll.set
        )

        self.file_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        tree_scroll.pack(
            side="right",
            fill="y"
        )

        self.file_tree.bind(
            "<Double-1>",
            self.compare_selected_file
        )

        # -----------------------------------------------------
        # RIGHT: Comparison
        # -----------------------------------------------------

        compare_frame = ttk.LabelFrame(
            main_pane,
            text="Comparison",
            padding=5
        )

        main_pane.add(compare_frame, weight=4)

        # Comparison panes

        compare_pane = ttk.PanedWindow(
            compare_frame,
            orient=tk.HORIZONTAL
        )
        compare_pane.pack(
            fill="both",
            expand=True
        )

        # =====================================================
        # LEFT TEXT
        # =====================================================

        left_frame = ttk.Frame(compare_pane)
        compare_pane.add(left_frame, weight=1)

        ttk.Label(
            left_frame,
            text="Folder 1",
            background="#f0f0f0"
        ).pack(fill="x")

        self.left_text = tk.Text(
            left_frame,
            wrap="none",
            font=("Consolas", 10),
            undo=False
        )

        self.left_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        left_scroll = ttk.Scrollbar(
            left_frame,
            orient="vertical",
            command=self.left_text.yview
        )

        left_scroll.pack(
            side="right",
            fill="y"
        )

        self.left_text.configure(
            yscrollcommand=left_scroll.set
        )

        # =====================================================
        # RIGHT TEXT
        # =====================================================

        right_frame = ttk.Frame(compare_pane)
        compare_pane.add(right_frame, weight=1)

        ttk.Label(
            right_frame,
            text="Folder 2",
            background="#f0f0f0"
        ).pack(fill="x")

        self.right_text = tk.Text(
            right_frame,
            wrap="none",
            font=("Consolas", 10),
            undo=False
        )

        self.right_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        right_scroll = ttk.Scrollbar(
            right_frame,
            orient="vertical",
            command=self.right_text.yview
        )

        right_scroll.pack(
            side="right",
            fill="y"
        )

        self.right_text.configure(
            yscrollcommand=right_scroll.set
        )

        # =====================================================
        # Horizontal scrolling
        # =====================================================

        horizontal_scroll = ttk.Scrollbar(
            compare_frame,
            orient="horizontal",
            command=self.horizontal_scroll
        )

        horizontal_scroll.pack(
            fill="x"
        )

        self.left_text.configure(
            xscrollcommand=horizontal_scroll.set
        )

        self.right_text.configure(
            xscrollcommand=horizontal_scroll.set
        )

        # =====================================================
        # Status bar
        # =====================================================

        self.status = tk.StringVar(
            value="Select two folders to begin."
        )

        ttk.Label(
            self.root,
            textvariable=self.status,
            relief="sunken",
            anchor="w"
        ).pack(
            fill="x",
            side="bottom"
        )

        # =====================================================
        # Text colours
        # =====================================================

        self.left_text.tag_configure(
            "removed",
            background="#ffd6d6"
        )

        self.right_text.tag_configure(
            "added",
            background="#d6ffd6"
        )

        self.left_text.tag_configure(
            "changed",
            background="#fff2a8"
        )

        self.right_text.tag_configure(
            "changed",
            background="#fff2a8"
        )

    # ---------------------------------------------------------
    # Folder selection
    # ---------------------------------------------------------

    def select_folder1(self):

        folder = filedialog.askdirectory(
            title="Select Folder 1"
        )

        if folder:
            self.folder1 = folder
            self.folder1_entry.delete(0, tk.END)
            self.folder1_entry.insert(0, folder)

    def select_folder2(self):

        folder = filedialog.askdirectory(
            title="Select Folder 2"
        )

        if folder:
            self.folder2 = folder
            self.folder2_entry.delete(0, tk.END)
            self.folder2_entry.insert(0, folder)

    # ---------------------------------------------------------
    # Compare folders
    # ---------------------------------------------------------

    def compare_folders(self):

        folder1 = self.folder1_entry.get().strip()
        folder2 = self.folder2_entry.get().strip()

        if not os.path.isdir(folder1):
            messagebox.showerror(
                "Error",
                "Folder 1 does not exist."
            )
            return

        if not os.path.isdir(folder2):
            messagebox.showerror(
                "Error",
                "Folder 2 does not exist."
            )
            return

        self.folder1 = folder1
        self.folder2 = folder2

        self.file_tree.delete(
            *self.file_tree.get_children()
        )

        files1 = self.get_text_files(folder1)
        files2 = self.get_text_files(folder2)

        all_files = sorted(
            set(files1) | set(files2)
        )

        identical = 0
        different = 0
        missing = 0

        for filename in all_files:

            exists1 = filename in files1
            exists2 = filename in files2

            if exists1 and exists2:

                try:
                    content1 = self.read_file(
                        os.path.join(folder1, filename)
                    )

                    content2 = self.read_file(
                        os.path.join(folder2, filename)
                    )

                    if self.normalise(content1) == self.normalise(content2):
                        status = "IDENTICAL"
                        identical += 1
                    else:
                        status = "DIFFERENT"
                        different += 1

                except Exception:
                    status = "ERROR"

            elif exists1:
                status = "ONLY IN FOLDER 1"
                missing += 1

            else:
                status = "ONLY IN FOLDER 2"
                missing += 1

            item = self.file_tree.insert(
                "",
                "end",
                text=filename,
                values=(status,)
            )

            # Colours

            if status == "IDENTICAL":
                self.file_tree.item(
                    item,
                    tags=("identical",)
                )

            elif status == "DIFFERENT":
                self.file_tree.item(
                    item,
                    tags=("different",)
                )

            else:
                self.file_tree.item(
                    item,
                    tags=("missing",)
                )

        self.file_tree.tag_configure(
            "identical",
            foreground="green"
        )

        self.file_tree.tag_configure(
            "different",
            foreground="red"
        )

        self.file_tree.tag_configure(
            "missing",
            foreground="orange"
        )

        self.status.set(
            f"Files: {len(all_files)} | "
            f"Identical: {identical} | "
            f"Different: {different} | "
            f"Missing: {missing}"
        )

    # ---------------------------------------------------------
    # Get text files
    # ---------------------------------------------------------

    def get_text_files(self, folder):

        return {
            filename
            for filename in os.listdir(folder)
            if filename.lower().endswith(".txt")
            and os.path.isfile(
                os.path.join(folder, filename)
            )
        }

    # ---------------------------------------------------------
    # Read file
    # ---------------------------------------------------------

    def read_file(self, path):

        try:
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:
                return f.readlines()

        except UnicodeDecodeError:

            with open(
                path,
                "r",
                encoding="latin-1"
            ) as f:
                return f.readlines()

    # ---------------------------------------------------------
    # Normalise text for comparison
    # ---------------------------------------------------------

    def normalise(self, text):

        if isinstance(text, list):
            text = "".join(text)

        if self.ignore_whitespace.get():
            text = "".join(text.split())

        if self.ignore_case.get():
            text = text.lower()

        return text

    # ---------------------------------------------------------
    # Compare selected file
    # ---------------------------------------------------------

    def compare_selected_file(self, event=None):

        selection = self.file_tree.selection()

        if not selection:
            return

        item = selection[0]

        filename = self.file_tree.item(
            item,
            "text"
        )

        path1 = os.path.join(
            self.folder1,
            filename
        )

        path2 = os.path.join(
            self.folder2,
            filename
        )

        if not os.path.isfile(path1):
            messagebox.showwarning(
                "File missing",
                f"{filename} does not exist in Folder 1."
            )
            return

        if not os.path.isfile(path2):
            messagebox.showwarning(
                "File missing",
                f"{filename} does not exist in Folder 2."
            )
            return

        self.show_comparison(
            filename,
            path1,
            path2
        )

    # ---------------------------------------------------------
    # Show comparison
    # ---------------------------------------------------------

    def show_comparison(
        self,
        filename,
        path1,
        path2
    ):

        left_lines = self.read_file(path1)
        right_lines = self.read_file(path2)

        self.left_text.delete(
            "1.0",
            tk.END
        )

        self.right_text.delete(
            "1.0",
            tk.END
        )

        matcher = difflib.SequenceMatcher(
            None,
            left_lines,
            right_lines
        )

        left_line = 1
        right_line = 1

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():

            if tag == "equal":

                for line in left_lines[i1:i2]:

                    self.insert_line(
                        self.left_text,
                        line,
                        left_line
                    )

                    self.insert_line(
                        self.right_text,
                        line,
                        right_line
                    )

                    left_line += 1
                    right_line += 1

            elif tag == "delete":

                for line in left_lines[i1:i2]:

                    self.insert_line(
                        self.left_text,
                        line,
                        left_line,
                        "removed"
                    )

                    left_line += 1

            elif tag == "insert":

                for line in right_lines[j1:j2]:

                    self.insert_line(
                        self.right_text,
                        line,
                        right_line,
                        "added"
                    )

                    right_line += 1

            elif tag == "replace":

                left_chunk = left_lines[i1:i2]
                right_chunk = right_lines[j1:j2]

                max_lines = max(
                    len(left_chunk),
                    len(right_chunk)
                )

                for n in range(max_lines):

                    if n < len(left_chunk):

                        self.insert_line(
                            self.left_text,
                            left_chunk[n],
                            left_line,
                            "changed"
                        )

                        left_line += 1

                    if n < len(right_chunk):

                        self.insert_line(
                            self.right_text,
                            right_chunk[n],
                            right_line,
                            "changed"
                        )

                        right_line += 1

        self.status.set(
            f"Comparing: {filename}"
        )

    # ---------------------------------------------------------
    # Insert numbered line
    # ---------------------------------------------------------

    def insert_line(
        self,
        widget,
        line,
        line_number,
        tag=None
    ):

        line_number_text = f"{line_number:6}  "

        widget.insert(
            tk.END,
            line_number_text,
            "line_number"
        )

        if tag:
            widget.insert(
                tk.END,
                line,
                tag
            )
        else:
            widget.insert(
                tk.END,
                line
            )

        widget.tag_configure(
            "line_number",
            foreground="#888888"
        )

    # ---------------------------------------------------------
    # Horizontal scroll both panes
    # ---------------------------------------------------------

    def horizontal_scroll(self, *args):

        self.left_text.xview(*args)
        self.right_text.xview(*args)


# =============================================================
# Start application
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = TextCompareApp(root)

    root.mainloop()
