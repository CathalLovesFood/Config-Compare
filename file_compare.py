import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import difflib


class CompareApp:

    def __init__(self, root):
        self.root = root
        self.root.title("File & Folder Compare")
        self.root.geometry("1700x900")

        self.folder1 = ""
        self.folder2 = ""

        # Up to 4 files
        self.files = ["", "", "", ""]

        self.text_widgets = []

        self.differences = []
        self.current_difference = -1

        self.ignore_whitespace = tk.BooleanVar(value=False)
        self.ignore_case = tk.BooleanVar(value=False)

        self.create_gui()

    # =========================================================
    # MAIN GUI
    # =========================================================

    def create_gui(self):

        notebook = ttk.Notebook(self.root)
        notebook.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.file_tab = ttk.Frame(notebook)
        self.folder_tab = ttk.Frame(notebook)

        notebook.add(
            self.file_tab,
            text="Compare Files"
        )

        notebook.add(
            self.folder_tab,
            text="Compare Folders"
        )

        self.create_file_tab()
        self.create_folder_tab()

        self.status = tk.StringVar(
            value="Select 2 to 4 files to compare."
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
    # FILE TAB
    # =========================================================

    def create_file_tab(self):

        # -----------------------------------------------------
        # File selection
        # -----------------------------------------------------

        selection_frame = ttk.LabelFrame(
            self.file_tab,
            text="Files to Compare (2-4)",
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

        self.file_entries = []

        for i in range(4):

            ttk.Label(
                selection_frame,
                text=f"File {i + 1}:"
            ).grid(
                row=i,
                column=0,
                sticky="w",
                pady=3
            )

            entry = ttk.Entry(
                selection_frame
            )

            entry.grid(
                row=i,
                column=1,
                sticky="ew",
                padx=5
            )

            self.file_entries.append(
                entry
            )

            ttk.Button(
                selection_frame,
                text="Browse...",
                command=lambda index=i:
                    self.select_file(index)
            ).grid(
                row=i,
                column=2,
                padx=5
            )

        # -----------------------------------------------------
        # Compare button
        # -----------------------------------------------------

        ttk.Button(
            selection_frame,
            text="COMPARE FILES",
            command=self.compare_files
        ).grid(
            row=0,
            column=3,
            rowspan=2,
            padx=20,
            ipadx=20,
            ipady=10
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
        # Comparison area
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

        # Create four comparison panes

        self.comparison_pane = ttk.PanedWindow(
            comparison_frame,
            orient=tk.HORIZONTAL
        )

        self.comparison_pane.pack(
            fill="both",
            expand=True
        )

        self.text_widgets = []

        for i in range(4):

            frame = ttk.Frame(
                self.comparison_pane
            )

            self.comparison_pane.add(
                frame,
                weight=1
            )

            header = ttk.Label(
                frame,
                text=f"File {i + 1}",
                font=("Arial", 10, "bold"),
                background="#eeeeee"
            )

            header.pack(
                fill="x"
            )

            text = tk.Text(
                frame,
                wrap="none",
                font=("Consolas", 10)
            )

            text.pack(
                side="left",
                fill="both",
                expand=True
            )

            scrollbar = ttk.Scrollbar(
                frame,
                orient="vertical",
                command=text.yview
            )

            scrollbar.pack(
                side="right",
                fill="y"
            )

            text.configure(
                yscrollcommand=scrollbar.set
            )

            self.text_widgets.append(
                text
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

        for text in self.text_widgets:

            text.configure(
                xscrollcommand=horizontal.set
            )

        self.configure_tags()

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
            width=600
        )

        self.file_tree.column(
            "status",
            width=200
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

        self.file_tree.bind(
            "<Double-1>",
            self.folder_file_double_click
        )

    # =========================================================
    # Text tags
    # =========================================================

    def configure_tags(self):

        for text in self.text_widgets:

            text.tag_configure(
                "removed",
                background="#ffc7ce",
                foreground="#9c0006"
            )

            text.tag_configure(
                "added",
                background="#c6efce",
                foreground="#006100"
            )

            text.tag_configure(
                "changed",
                background="#ffeb9c",
                foreground="#9c6500"
            )

            text.tag_configure(
                "line_number",
                foreground="#888888"
            )

            text.tag_configure(
                "current_difference",
                background="#ff9900"
            )

    # =========================================================
    # Select file
    # =========================================================

    def select_file(self, index):

        filename = filedialog.askopenfilename(
            title=f"Select File {index + 1}"
        )

        if filename:

            self.files[index] = filename

            self.file_entries[index].delete(
                0,
                tk.END
            )

            self.file_entries[index].insert(
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
    # COMPARE 2-4 FILES
    # =========================================================

    def compare_files(self):

        selected_files = []

        for i in range(4):

            filename = self.file_entries[i].get().strip()

            if filename:

                if not os.path.isfile(filename):

                    messagebox.showerror(
                        "Error",
                        f"File {i + 1} does not exist:\n\n"
                        f"{filename}"
                    )

                    return

                selected_files.append(
                    filename
                )

        # Need at least 2

        if len(selected_files) < 2:

            messagebox.showwarning(
                "Not Enough Files",
                "Please select at least 2 files."
            )

            return

        self.files = selected_files

        # Clear panes

        for text in self.text_widgets:

            text.delete(
                "1.0",
                tk.END
            )

        self.differences = []
        self.current_difference = -1

        # Update headers

        for i, filename in enumerate(selected_files):

            parent = self.text_widgets[i].master

            children = parent.winfo_children()

            if children:

                header = children[0]

                header.config(
                    text=os.path.basename(filename)
                )

        # -----------------------------------------------------
        # Read files
        # -----------------------------------------------------

        all_lines = []

        for filename in selected_files:

            all_lines.append(
                self.read_file(filename)
            )

        # -----------------------------------------------------
        # Create normalised versions
        # -----------------------------------------------------

        normalised = []

        for lines in all_lines:

            normalised.append(
                [
                    self.normalise_line(line)
                    for line in lines
                ]
            )

        # -----------------------------------------------------
        # Find maximum number of lines
        # -----------------------------------------------------

        max_lines = max(
            len(lines)
            for lines in all_lines
        )

        # -----------------------------------------------------
        # Compare every line position
        # -----------------------------------------------------

        difference_count = 0

        for line_number in range(max_lines):

            values = []

            for file_index in range(
                len(selected_files)
            ):

                if line_number < len(
                    normalised[file_index]
                ):

                    values.append(
                        normalised[file_index][line_number]
                    )

                else:

                    values.append(
                        None
                    )

            # Are all files identical at this line?

            if len(set(values)) == 1:

                # Same everywhere

                for i in range(
                    len(selected_files)
                ):

                    self.insert_line(
                        self.text_widgets[i],
                        line_number + 1,
                        all_lines[i][line_number]
                    )

                continue

            # -------------------------------------------------
            # Difference found
            # -------------------------------------------------

            difference_count += 1

            self.differences.append(
                difference_count
            )

            for i in range(
                len(selected_files)
            ):

                text_widget = self.text_widgets[i]

                if line_number >= len(
                    all_lines[i]
                ):

                    # File doesn't have this line

                    self.insert_line(
                        text_widget,
                        line_number + 1,
                        "",
                        "added"
                    )

                else:

                    current_line = normalised[i][
                        line_number
                    ]

                    # Check whether this value occurs
                    # in another file at this position

                    if values.count(
                        current_line
                    ) == len(values):

                        tag = None

                    elif current_line == "" and \
                            values[i] is None:

                        tag = "removed"

                    else:

                        # Determine whether this file
                        # differs from the others

                        other_values = [
                            value
                            for n, value in enumerate(values)
                            if n != i
                        ]

                        if current_line in other_values:

                            tag = None

                        else:

                            tag = "changed"

                    self.insert_line(
                        text_widget,
                        line_number + 1,
                        all_lines[i][line_number],
                        tag
                    )

        # -----------------------------------------------------
        # Result
        # -----------------------------------------------------

        if difference_count == 0:

            self.status.set(
                f"ALL {len(selected_files)} FILES ARE IDENTICAL"
            )

        else:

            self.status.set(
                f"{len(selected_files)} files compared | "
                f"{difference_count} differences found"
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
    # Difference navigation
    # =========================================================

    def next_difference(self):

        if not self.differences:

            return

        self.current_difference += 1

        if self.current_difference >= len(
            self.differences
        ):

            self.current_difference = 0

        self.highlight_difference()

    def previous_difference(self):

        if not self.differences:

            return

        self.current_difference -= 1

        if self.current_difference < 0:

            self.current_difference = (
                len(self.differences) - 1
            )

        self.highlight_difference()

    def highlight_difference(self):

        # Remove previous highlight

        for text in self.text_widgets:

            text.tag_remove(
                "current_difference",
                "1.0",
                tk.END
            )

        line = self.differences[
            self.current_difference
        ]

        for text in self.text_widgets:

            text.tag_add(
                "current_difference",
                f"{line}.0",
                f"{line}.end"
            )

            text.see(
                f"{line}.0"
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

        for text in self.text_widgets:

            text.xview(*args)

    # =========================================================
    # Folder comparison
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
    # Recursive files
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
    # Double-click folder file
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

        # Put files into first two slots

        self.file_entries[0].delete(
            0,
            tk.END
        )

        self.file_entries[0].insert(
            0,
            path1
        )

        self.file_entries[1].delete(
            0,
            tk.END
        )

        self.file_entries[1].insert(
            0,
            path2
        )

        self.files[0] = path1
        self.files[1] = path2

        # Switch to file tab

        notebook = self.file_tab.master

        notebook.select(
            self.file_tab
        )

        # Compare contents

        self.compare_files()


# =============================================================
# Start application
# =============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CompareApp(root)

    root.mainloop()
