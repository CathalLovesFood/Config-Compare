import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import difflib


class CompareApp:

    def __init__(self, root):
        self.root = root
        self.root.title("File & Folder Compare")
        self.root.geometry("1500x900")

        self.folder1 = ""
        self.folder2 = ""

        self.file1 = ""
        self.file2 = ""

        self.differences = []
        self.current_difference = -1

        self.ignore_whitespace = tk.BooleanVar(value=False)
        self.ignore_case = tk.BooleanVar(value=False)

        self.create_gui()

    # =========================================================
    # GUI
    # =========================================================

    def create_gui(self):

        # -----------------------------------------------------
        # Top notebook
        # -----------------------------------------------------

        notebook = ttk.Notebook(self.root)
        notebook.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        # Two tabs
        self.file_tab = ttk.Frame(notebook)
        self.folder_tab = ttk.Frame(notebook)

        notebook.add(
            self.file_tab,
            text="Compare Two Files"
        )

        notebook.add(
            self.folder_tab,
            text="Compare Two Folders"
        )

        self.create_file_tab()
        self.create_folder_tab()

        # -----------------------------------------------------
        # Status bar
        # -----------------------------------------------------

        self.status = tk.StringVar(
            value="Select two files to compare."
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

    # =========================================================
    # FILE COMPARISON TAB
    # =========================================================

    def create_file_tab(self):

        # -----------------------------------------------------
        # File selection
        # -----------------------------------------------------

        selection_frame = ttk.LabelFrame(
            self.file_tab,
            text="Files to Compare",
            padding=10
        )

        selection_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        selection_frame.columnconfigure(
            1,
            weight=1
        )

        # File 1

        ttk.Label(
            selection_frame,
            text="File 1:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.file1_entry = ttk.Entry(
            selection_frame
        )

        self.file1_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=5
        )

        ttk.Button(
            selection_frame,
            text="Browse...",
            command=self.select_file1
        ).grid(
            row=0,
            column=2,
            padx=5
        )

        # File 2

        ttk.Label(
            selection_frame,
            text="File 2:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        self.file2_entry = ttk.Entry(
            selection_frame
        )

        self.file2_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5
        )

        ttk.Button(
            selection_frame,
            text="Browse...",
            command=self.select_file2
        ).grid(
            row=1,
            column=2,
            padx=5
        )

        # Compare button

        ttk.Button(
            selection_frame,
            text="COMPARE FILES",
            command=self.compare_files
        ).grid(
            row=0,
            column=3,
            rowspan=2,
            padx=15,
            ipadx=15,
            ipady=8
        )

        # -----------------------------------------------------
        # Options
        # -----------------------------------------------------

        options_frame = ttk.Frame(
            self.file_tab
        )

        options_frame.pack(
            fill="x",
            padx=10
        )

        ttk.Checkbutton(
            options_frame,
            text="Ignore whitespace",
            variable=self.ignore_whitespace
        ).pack(
            side="left",
            padx=5
        )

        ttk.Checkbutton(
            options_frame,
            text="Ignore case",
            variable=self.ignore_case
        ).pack(
            side="left",
            padx=5
        )

        # Navigation buttons

        ttk.Button(
            options_frame,
            text="◀ Previous Difference",
            command=self.previous_difference
        ).pack(
            side="right",
            padx=5
        )

        ttk.Button(
            options_frame,
            text="Next Difference ▶",
            command=self.next_difference
        ).pack(
            side="right",
            padx=5
        )

        # -----------------------------------------------------
        # Comparison panes
        # -----------------------------------------------------

        comparison_frame = ttk.LabelFrame(
            self.file_tab,
            text="File Contents",
            padding=5
        )

        comparison_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        pane = ttk.PanedWindow(
            comparison_frame,
            orient=tk.HORIZONTAL
        )

        pane.pack(
            fill="both",
            expand=True
        )

        # =====================================================
        # LEFT
        # =====================================================

        left_frame = ttk.Frame(pane)

        pane.add(
            left_frame,
            weight=1
        )

        self.left_header = ttk.Label(
            left_frame,
            text="File 1",
            font=("Arial", 10, "bold"),
            background="#eeeeee"
        )

        self.left_header.pack(
            fill="x"
        )

        self.left_text = tk.Text(
            left_frame,
            wrap="none",
            font=("Consolas", 10),
            background="white"
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
        # RIGHT
        # =====================================================

        right_frame = ttk.Frame(pane)

        pane.add(
            right_frame,
            weight=1
        )

        self.right_header = ttk.Label(
            right_frame,
            text="File 2",
            font=("Arial", 10, "bold"),
            background="#eeeeee"
        )

        self.right_header.pack(
            fill="x"
        )

        self.right_text = tk.Text(
            right_frame,
            wrap="none",
            font=("Consolas", 10),
            background="white"
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

        # -----------------------------------------------------
        # Horizontal scrollbar
        # -----------------------------------------------------

        horizontal = ttk.Scrollbar(
            comparison_frame,
            orient="horizontal",
            command=self.horizontal_scroll
        )

        horizontal.pack(
            fill="x"
        )

        self.left_text.configure(
            xscrollcommand=horizontal.set
        )

        self.right_text.configure(
            xscrollcommand=horizontal.set
        )

        # -----------------------------------------------------
        # Colours
        # -----------------------------------------------------

        self.configure_text_tags()

    # =========================================================
    # FOLDER TAB
    # =========================================================

    def create_folder_tab(self):

        selection_frame = ttk.LabelFrame(
            self.folder_tab,
            text="Folders to Compare",
            padding=10
        )

        selection_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        selection_frame.columnconfigure(
            1,
            weight=1
        )

        # Folder 1

        ttk.Label(
            selection_frame,
            text="Folder 1:"
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        self.folder1_entry = ttk.Entry(
            selection_frame
        )

        self.folder1_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=5
        )

        ttk.Button(
            selection_frame,
            text="Browse...",
            command=self.select_folder1
        ).grid(
            row=0,
            column=2
        )

        # Folder 2

        ttk.Label(
            selection_frame,
            text="Folder 2:"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        self.folder2_entry = ttk.Entry(
            selection_frame
        )

        self.folder2_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5
        )

        ttk.Button(
            selection_frame,
            text="Browse...",
            command=self.select_folder2
        ).grid(
            row=1,
            column=2
        )

        ttk.Button(
            selection_frame,
            text="COMPARE FOLDERS",
            command=self.compare_folders
        ).grid(
            row=0,
            column=3,
            rowspan=2,
            padx=15,
            ipadx=15,
            ipady=8
        )

        # -----------------------------------------------------
        # File list
        # -----------------------------------------------------

        list_frame = ttk.LabelFrame(
            self.folder_tab,
            text="Files",
            padding=5
        )

        list_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.file_tree = ttk.Treeview(
            list_frame,
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
            width=500
        )

        self.file_tree.column(
            "status",
            width=180
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.file_tree.yview
        )

        self.file_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.file_tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Double click a matching file
        self.file_tree.bind(
            "<Double-1>",
            self.folder_file_double_click
        )

    # =========================================================
    # Text formatting
    # =========================================================

    def configure_text_tags(self):

        # Removed from File 1
        self.left_text.tag_configure(
            "removed",
            background="#ffc7ce",
            foreground="#9c0006"
        )

        # Added to File 2
        self.right_text.tag_configure(
            "added",
            background="#c6efce",
            foreground="#006100"
        )

        # Changed
        self.left_text.tag_configure(
            "changed",
            background="#ffeb9c",
            foreground="#9c6500"
        )

        self.right_text.tag_configure(
            "changed",
            background="#ffeb9c",
            foreground="#9c6500"
        )

        # Line numbers
        self.left_text.tag_configure(
            "line_number",
            foreground="#888888"
        )

        self.right_text.tag_configure(
            "line_number",
            foreground="#888888"
        )

        # Current difference
        self.left_text.tag_configure(
            "current_difference",
            background="#ff9900"
        )

        self.right_text.tag_configure(
            "current_difference",
            background="#ff9900"
        )

    # =========================================================
    # Select files
    # =========================================================

    def select_file1(self):

        filename = filedialog.askopenfilename(
            title="Select File 1"
        )

        if filename:

            self.file1 = filename

            self.file1_entry.delete(
                0,
                tk.END
            )

            self.file1_entry.insert(
                0,
                filename
            )

    def select_file2(self):

        filename = filedialog.askopenfilename(
            title="Select File 2"
        )

        if filename:

            self.file2 = filename

            self.file2_entry.delete(
                0,
                tk.END
            )

            self.file2_entry.insert(
                0,
                filename
            )

    # =========================================================
    # Select folders
    # =========================================================

    def select_folder1(self):

        folder = filedialog.askdirectory(
            title="Select Folder 1"
        )

        if folder:

            self.folder1 = folder

            self.folder1_entry.delete(
                0,
                tk.END
            )

            self.folder1_entry.insert(
                0,
                folder
            )

    def select_folder2(self):

        folder = filedialog.askdirectory(
            title="Select Folder 2"
        )

        if folder:

            self.folder2 = folder

            self.folder2_entry.delete(
                0,
                tk.END
            )

            self.folder2_entry.insert(
                0,
                folder
            )

    # =========================================================
    # Read file
    # =========================================================

    def read_file(self, filename):

        try:

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as f:

                return f.readlines()

        except UnicodeDecodeError:

            with open(
                filename,
                "r",
                encoding="latin-1"
            ) as f:

                return f.readlines()

    # =========================================================
    # Normalise
    # =========================================================

    def normalise_line(self, line):

        if self.ignore_whitespace.get():

            line = "".join(
                line.split()
            )

        if self.ignore_case.get():

            line = line.lower()

        return line

    # =========================================================
    # COMPARE TWO FILES
    # =========================================================

    def compare_files(self):

        file1 = self.file1_entry.get().strip()
        file2 = self.file2_entry.get().strip()

        if not os.path.isfile(file1):

            messagebox.showerror(
                "Error",
                "File 1 does not exist."
            )

            return

        if not os.path.isfile(file2):

            messagebox.showerror(
                "Error",
                "File 2 does not exist."
            )

            return

        self.file1 = file1
        self.file2 = file2

        self.left_header.config(
            text=f"File 1: {os.path.basename(file1)}"
        )

        self.right_header.config(
            text=f"File 2: {os.path.basename(file2)}"
        )

        left_lines = self.read_file(file1)
        right_lines = self.read_file(file2)

        # Clear old comparison

        self.left_text.delete(
            "1.0",
            tk.END
        )

        self.right_text.delete(
            "1.0",
            tk.END
        )

        self.differences = []
        self.current_difference = -1

        # Normalised copies used for comparison

        compare_left = [
            self.normalise_line(line)
            for line in left_lines
        ]

        compare_right = [
            self.normalise_line(line)
            for line in right_lines
        ]

        matcher = difflib.SequenceMatcher(
            None,
            compare_left,
            compare_right
        )

        left_number = 1
        right_number = 1

        difference_number = 0

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():

            # -------------------------------------------------
            # IDENTICAL
            # -------------------------------------------------

            if tag == "equal":

                for offset in range(i2 - i1):

                    self.insert_line(
                        self.left_text,
                        left_number,
                        left_lines[i1 + offset]
                    )

                    self.insert_line(
                        self.right_text,
                        right_number,
                        right_lines[j1 + offset]
                    )

                    left_number += 1
                    right_number += 1

            # -------------------------------------------------
            # REMOVED
            # -------------------------------------------------

            elif tag == "delete":

                difference_number += 1

                self.differences.append(
                    (
                        difference_number,
                        left_number,
                        right_number
                    )
                )

                for line in left_lines[i1:i2]:

                    self.insert_line(
                        self.left_text,
                        left_number,
                        line,
                        "removed"
                    )

                    left_number += 1

            # -------------------------------------------------
            # ADDED
            # -------------------------------------------------

            elif tag == "insert":

                difference_number += 1

                self.differences.append(
                    (
                        difference_number,
                        left_number,
                        right_number
                    )
                )

                for line in right_lines[j1:j2]:

                    self.insert_line(
                        self.right_text,
                        right_number,
                        line,
                        "added"
                    )

                    right_number += 1

            # -------------------------------------------------
            # CHANGED
            # -------------------------------------------------

            elif tag == "replace":

                difference_number += 1

                self.differences.append(
                    (
                        difference_number,
                        left_number,
                        right_number
                    )
                )

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
                            left_number,
                            left_chunk[n],
                            "changed"
                        )

                        left_number += 1

                    if n < len(right_chunk):

                        self.insert_line(
                            self.right_text,
                            right_number,
                            right_chunk[n],
                            "changed"
                        )

                        right_number += 1

        # -----------------------------------------------------
        # Result
        # -----------------------------------------------------

        if compare_left == compare_right:

            self.status.set(
                "FILES ARE IDENTICAL"
            )

        else:

            self.status.set(
                f"DIFFERENCES FOUND: "
                f"{len(self.differences)} difference blocks"
            )

    # =========================================================
    # Insert line
    # =========================================================

    def insert_line(
        self,
        widget,
        number,
        text,
        tag=None
    ):

        widget.insert(
            tk.END,
            f"{number:6}  ",
            "line_number"
        )

        if tag:

            widget.insert(
                tk.END,
                text,
                tag
            )

        else:

            widget.insert(
                tk.END,
                text
            )

    # =========================================================
    # Next difference
    # =========================================================

    def next_difference(self):

        if not self.differences:

            return

        self.current_difference += 1

        if self.current_difference >= len(
            self.differences
        ):

            self.current_difference = 0

        self.go_to_difference()

    # =========================================================
    # Previous difference
    # =========================================================

    def previous_difference(self):

        if not self.differences:

            return

        self.current_difference -= 1

        if self.current_difference < 0:

            self.current_difference = (
                len(self.differences) - 1
            )

        self.go_to_difference()

    # =========================================================
    # Go to difference
    # =========================================================

    def go_to_difference(self):

        _, left_line, right_line = (
            self.differences[
                self.current_difference
            ]
        )

        # Remove old current highlight

        self.left_text.tag_remove(
            "current_difference",
            "1.0",
            tk.END
        )

        self.right_text.tag_remove(
            "current_difference",
            "1.0",
            tk.END
        )

        # Highlight

        self.left_text.tag_add(
            "current_difference",
            f"{left_line}.0",
            f"{left_line}.end"
        )

        self.right_text.tag_add(
            "current_difference",
            f"{right_line}.0",
            f"{right_line}.end"
        )

        # Scroll to difference

        self.left_text.see(
            f"{left_line}.0"
        )

        self.right_text.see(
            f"{right_line}.0"
        )

        self.status.set(
            f"Difference "
            f"{self.current_difference + 1} "
            f"of {len(self.differences)}"
        )

    # =========================================================
    # Horizontal scroll
    # =========================================================

    def horizontal_scroll(self, *args):

        self.left_text.xview(*args)
        self.right_text.xview(*args)

    # =========================================================
    # Compare folders
    # =========================================================

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

        files1 = self.get_files(folder1)
        files2 = self.get_files(folder2)

        all_files = sorted(
            set(files1) | set(files2)
        )

        identical = 0
        different = 0
        only1 = 0
        only2 = 0

        for filename in all_files:

            if filename in files1 and filename in files2:

                try:

                    content1 = self.read_file(
                        files1[filename]
                    )

                    content2 = self.read_file(
                        files2[filename]
                    )

                    normal1 = [
                        self.normalise_line(line)
                        for line in content1
                    ]

                    normal2 = [
                        self.normalise_line(line)
                        for line in content2
                    ]

                    if normal1 == normal2:

                        status = "IDENTICAL"
                        identical += 1

                    else:

                        status = "DIFFERENT"
                        different += 1

                except Exception:

                    status = "ERROR"

            elif filename in files1:

                status = "ONLY IN FOLDER 1"
                only1 += 1

            else:

                status = "ONLY IN FOLDER 2"
                only2 += 1

            item = self.file_tree.insert(
                "",
                "end",
                text=filename,
                values=(status,)
            )

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
            f"Folder comparison complete | "
            f"Files: {len(all_files)} | "
            f"Identical: {identical} | "
            f"Different: {different} | "
            f"Only Folder 1: {only1} | "
            f"Only Folder 2: {only2}"
        )

    # =========================================================
    # Get files recursively
    # =========================================================

    def get_files(self, folder):

        result = {}

        for root, directories, filenames in os.walk(folder):

            for filename in filenames:

                if not filename.lower().endswith(".txt"):
                    continue

                full_path = os.path.join(
                    root,
                    filename
                )

                relative_path = os.path.relpath(
                    full_path,
                    folder
                )

                result[relative_path] = full_path

        return result

    # =========================================================
    # Double-click folder comparison result
    # =========================================================

    def folder_file_double_click(self, event):

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
            return

        if not os.path.isfile(path2):
            return

        self.file1_entry.delete(
            0,
            tk.END
        )

        self.file1_entry.insert(
            0,
            path1
        )

        self.file2_entry.delete(
            0,
            tk.END
        )

        self.file2_entry.insert(
            0,
            path2
        )

        self.file1 = path1
        self.file2 = path2

        # Switch to file comparison tab

        # Get notebook from parent hierarchy
        notebook = self.file_tab.master

        notebook.select(
            self.file_tab
        )

        # Perform actual content comparison

        self.compare_files()


# =============================================================
# Start application
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CompareApp(root)

    root.mainloop()
