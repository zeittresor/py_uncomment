# Source: github.com/zeittresor

import ast
import io
import os
import shutil
import tokenize
import tkinter as tk
from tkinter import filedialog, messagebox


def read_source_with_encoding(path):
    with open(path, "rb") as f:
        raw = f.read()
    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    text = raw.decode(encoding)
    return text, encoding


def find_string_statement_positions(source):
    positions = set()
    pos_to_string = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return positions, pos_to_string

    class StringStmtVisitor(ast.NodeVisitor):
        def visit_Expr(self, node):
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                pos = (node.lineno, node.col_offset)
                positions.add(pos)
                pos_to_string[pos] = node.value.value
            self.generic_visit(node)

    StringStmtVisitor().visit(tree)
    return positions, pos_to_string


def is_probable_shader(text):
    snippet = text.lower()
    keywords = [
        "void main",
        "gl_fragcolor",
        "gl_fragcoord",
        "gl_position",
        "sampler2d",
        "uniform",
        "varying",
        "#version",
        "precision mediump float",
        "vec2",
        "vec3",
        "vec4",
        "mat3",
        "mat4",
    ]
    score = sum(1 for kw in keywords if kw in snippet)
    return score >= 2


def squeeze_empty_lines(text, max_consecutive=1):
    lines = text.splitlines(keepends=True)
    new_lines = []
    empty_count = 0
    for line in lines:
        if line.strip() == "":
            empty_count += 1
            if empty_count <= max_consecutive:
                new_lines.append(line)
        else:
            empty_count = 0
            new_lines.append(line)
    return "".join(new_lines)


def remove_backslash_placeholder_lines(text):
    lines = text.splitlines(keepends=True)
    result = []
    for line in lines:
        if line.strip() == "\\":
            continue
        result.append(line)
    return "".join(result)


def remove_comments_and_docstrings(
    source,
    keep_shader_strings=False,
    squeeze_blank_lines=False,
    keep_todo_comments=False,
    remove_backslash_placeholders=False,
):
    string_stmt_positions, pos_to_string = find_string_statement_positions(source)
    out_tokens = []
    sio = io.StringIO(source)
    try:
        tokens = list(tokenize.generate_tokens(sio.readline))
    except tokenize.TokenError:
        return source
    for tok in tokens:
        tok_type, tok_string, start, end, line = tok
        srow, scol = start
        if tok_type == tokenize.COMMENT:
            if srow == 1 and tok_string.startswith("#!"):
                out_tokens.append(tok)
                continue
            if srow <= 2 and ("coding:" in tok_string or "coding=" in tok_string):
                out_tokens.append(tok)
                continue
            if keep_todo_comments:
                upper_comment = tok_string.upper()
                if "TODO" in upper_comment or "FIXME" in upper_comment:
                    out_tokens.append(tok)
                    continue
            continue
        if tok_type == tokenize.STRING and (srow, scol) in string_stmt_positions:
            if keep_shader_strings:
                value = pos_to_string.get((srow, scol), "")
                if is_probable_shader(value):
                    out_tokens.append(tok)
                    continue
            continue
        out_tokens.append(tok)
    new_source = tokenize.untokenize(out_tokens)
    if squeeze_blank_lines:
        new_source = squeeze_empty_lines(new_source, max_consecutive=1)
    if remove_backslash_placeholders:
        new_source = remove_backslash_placeholder_lines(new_source)
    return new_source


def make_backup(path):
    backup_path = path + ".bak"
    counter = 1
    while os.path.exists(backup_path):
        backup_path = f"{path}.bak{counter}"
        counter += 1
    shutil.copy2(path, backup_path)
    return backup_path


def process_file(
    path,
    keep_shader_strings=False,
    squeeze_blank_lines=False,
    keep_todo_comments=False,
    remove_backslash_placeholders=False,
):
    source, encoding = read_source_with_encoding(path)
    cleaned = remove_comments_and_docstrings(
        source,
        keep_shader_strings=keep_shader_strings,
        squeeze_blank_lines=squeeze_blank_lines,
        keep_todo_comments=keep_todo_comments,
        remove_backslash_placeholders=remove_backslash_placeholders,
    )
    backup_path = make_backup(path)
    with open(path, "w", encoding=encoding, newline="") as f:
        f.write(cleaned)
    return backup_path


class CommentStripperApp:
    def __init__(self, master):
        self.master = master
        master.title("Python Comment Cleaner")
        master.geometry("600x280")
        description = (
            "Select a Python file to remove comments and documentation:\n"
            "  • # comments (except shebang and encoding line)\n"
            "  • bare triple-quoted docstrings or blocks\n\n"
            "All options below are disabled by default."
        )
        self.label = tk.Label(master, text=description, justify="left", anchor="w")
        self.label.pack(padx=10, pady=10, fill="x")
        self.var_keep_shaders = tk.IntVar(value=0)
        self.var_squeeze_blank = tk.IntVar(value=0)
        self.var_keep_todo = tk.IntVar(value=0)
        self.var_remove_backslash = tk.IntVar(value=0)
        self.chk_keep_shaders = tk.Checkbutton(
            master,
            text="Do not remove probable shader strings",
            variable=self.var_keep_shaders,
            anchor="w",
            justify="left",
        )
        self.chk_keep_shaders.pack(padx=20, anchor="w")
        self.chk_squeeze_blank = tk.Checkbutton(
            master,
            text="Remove duplicated empty lines",
            variable=self.var_squeeze_blank,
            anchor="w",
            justify="left",
        )
        self.chk_squeeze_blank.pack(padx=20, anchor="w")
        self.chk_keep_todo = tk.Checkbutton(
            master,
            text="Keep TODO/FIXME comments",
            variable=self.var_keep_todo,
            anchor="w",
            justify="left",
        )
        self.chk_keep_todo.pack(padx=20, anchor="w")
        self.chk_remove_backslash = tk.Checkbutton(
            master,
            text="Remove backslash placeholder lines",
            variable=self.var_remove_backslash,
            anchor="w",
            justify="left",
        )
        self.chk_remove_backslash.pack(padx=20, anchor="w")
        self.select_button = tk.Button(
            master,
            text="Select Python file...",
            command=self.select_file,
            width=25,
        )
        self.select_button.pack(pady=10)
        self.status_var = tk.StringVar()
        self.status_label = tk.Label(
            master,
            textvariable=self.status_var,
            fg="gray",
        )
        self.status_label.pack(pady=5)

    def select_file(self):
        filepath = filedialog.askopenfilename(
            title="Choose a Python file",
            filetypes=[("Python files", "*.py"), ("All files", "*.*")],
        )
        if not filepath:
            return
        keep_shaders = bool(self.var_keep_shaders.get())
        squeeze_blank = bool(self.var_squeeze_blank.get())
        keep_todo = bool(self.var_keep_todo.get())
        remove_backslash = bool(self.var_remove_backslash.get())
        try:
            backup_path = process_file(
                filepath,
                keep_shader_strings=keep_shaders,
                squeeze_blank_lines=squeeze_blank,
                keep_todo_comments=keep_todo,
                remove_backslash_placeholders=remove_backslash,
            )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
            self.status_var.set("Error while processing file.")
            return
        msg = (
            "Processing finished.\n\n"
            f"Backup created:\n{backup_path}\n\n"
            f"Cleaned file:\n{filepath}"
        )
        self.status_var.set("Done. Backup created.")
        messagebox.showinfo("Success", msg)


def main():
    root = tk.Tk()
    app = CommentStripperApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
