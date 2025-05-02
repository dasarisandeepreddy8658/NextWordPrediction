import os
import tkinter as tk
from tkinter import StringVar, ttk, messagebox
from textblob import TextBlob
train_data = "t1.txt" 
if not os.path.exists(train_data):
    messagebox.showerror("File Error", f"The file '{train_data}' was not found. Please check the path.")
    exit()
first_possible_words = {}
second_possible_words = {}
transitions = {}
def expandDict(dictionary, key, value):
    if key not in dictionary:
        dictionary[key] = []
    dictionary[key].append(value)
def get_next_probability(given_list):
    probability_dict = {}
    given_list_length = len(given_list)
    for item in given_list:
        probability_dict[item] = probability_dict.get(item, 0) + 1
    for key, value in probability_dict.items():
        probability_dict[key] = value / given_list_length
    return probability_dict
def trainMarkovModel():
    with open(train_data, 'r', encoding='utf-8') as file:
        for line in file:
            tokens = line.rstrip().lower().split()
            tokens_length = len(tokens)
            for i in range(tokens_length):
                token = tokens[i]
                if i == 0:
                    first_possible_words[token] = first_possible_words.get(token, 0) + 1
                else:
                    prev_token = tokens[i - 1]
                    if i == tokens_length - 1:
                        expandDict(transitions, (prev_token, token), 'END')
                    if i == 1:
                        expandDict(second_possible_words, prev_token, token)
                    else:
                        prev_prev_token = tokens[i - 2]
                        expandDict(transitions, (prev_prev_token, prev_token), token)
    total_first_words = sum(first_possible_words.values())
    for key in first_possible_words:
        first_possible_words[key] /= total_first_words
    for prev_word in second_possible_words:
        second_possible_words[prev_word] = get_next_probability(second_possible_words[prev_word])
    for word_pair in transitions:
        transitions[word_pair] = get_next_probability(transitions[word_pair])
    messagebox.showinfo("Training Complete", "Training completed successfully!")
def next_word(tpl):
    if isinstance(tpl, str):
        return list(second_possible_words.get(tpl, {}).keys())
    if isinstance(tpl, tuple):
        return list(transitions.get(tpl, {}).keys())
    return []
trainMarkovModel()
def check_spelling(word):
    corrected_word = str(TextBlob(word).correct())
    return corrected_word if word != corrected_word else None
def on_type(event):
    text = input_var.get()
    words = text.strip().lower().split()
    if not text.endswith(' '):
        suggestion_var.set("")
        error_var.set("")
        update_suggestions([])
        return
    if words:
        last_word = words[-1]
        corrected_word = check_spelling(last_word)
        if corrected_word:
            error_var.set(f"Did you mean: {corrected_word}?")
        else:
            error_var.set("")
        if len(words) == 1:
            suggestions = next_word(words[0])
        elif len(words) >= 2:
            suggestions = next_word((words[-2], words[-1]))
        else:
            suggestions = []
        suggestion_var.set(", ".join(suggestions[:5]) if suggestions else "No suggestions")
        update_suggestions(suggestions[:5])
    else:
        suggestion_var.set("")
        error_var.set("")
        update_suggestions([])
def update_suggestions(suggestions):
    for widget in suggestion_frame.winfo_children():
        widget.destroy()
    if suggestions:
        for suggestion in suggestions:
            def on_click(word=suggestion):
                current_text = input_var.get().strip()
                if not current_text.endswith(' '):
                    current_text += ' '
                new_text = current_text + word + ' '
                input_var.set(new_text)
                input_entry.icursor(tk.END)  # Move cursor to end
                update_suggestions([])
            btn = tk.Button(suggestion_frame, text=suggestion, font=("Poppins", 11), fg="blue", cursor="hand2",
                            bd=0, bg="#ffffff", activebackground="#f0f0f0", command=on_click)
            btn.pack(side=tk.LEFT, padx=4)
def autocomplete():
    suggestions = suggestion_var.get().split(", ")
    if suggestions and suggestions[0] != "No suggestions":
        current_text = input_var.get().strip()
        if not current_text.endswith(' '):
            current_text += ' '
        new_text = current_text + suggestions[0] + ' '
        input_var.set(new_text)
        input_entry.icursor(tk.END)
        suggestion_var.set("")
        update_suggestions([])
def blink_label():
    current_color = suggestion_label.cget("foreground")
    next_color = "blue" if current_color == "purple" else "purple"
    suggestion_label.config(foreground=next_color)
    root.after(500, blink_label)
root = tk.Tk()
root.title("Markov Text Predictor")
root.geometry("750x500")
root.configure(bg="#f9fafb")
style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", font=("Poppins", 12), padding=8)
style.map("TButton", background=[('active', '#4ade80')], foreground=[('active', 'black')])
frame = tk.Frame(root, bg="#ffffff", bd=8, relief=tk.RIDGE)
frame.pack(pady=30, padx=30, fill=tk.BOTH, expand=True)
title_label = tk.Label(frame, text="Markov Text Predictor", font=("Poppins", 20, "bold"), bg="#ffffff", fg="#6366f1")
title_label.pack(pady=10)
input_var = StringVar()
suggestion_var = StringVar()
error_var = StringVar()
input_entry = tk.Entry(frame, textvariable=input_var, font=("Poppins", 16), width=45, bd=5, relief=tk.GROOVE)
input_entry.pack(pady=10)
input_entry.bind("<KeyRelease>", on_type)
error_label = tk.Label(frame, textvariable=error_var, font=("Poppins", 12), fg="#ef4444", bg="#ffffff")
error_label.pack(pady=5)
suggestion_label = tk.Label(frame, textvariable=suggestion_var, font=("Poppins", 12, "italic"), fg="blue", bg="#ffffff")
suggestion_label.pack(pady=5)
suggestion_frame = tk.Frame(frame, bg="#ffffff")
suggestion_frame.pack(pady=5)
button_frame = tk.Frame(frame, bg="#ffffff")
button_frame.pack(pady=20)
autocomplete_button = ttk.Button(button_frame, text="Autocomplete ✨", command=autocomplete)
autocomplete_button.grid(row=0, column=0, padx=10)
exit_button = ttk.Button(button_frame, text="Exit ❌", command=root.quit)
exit_button.grid(row=0, column=1, padx=10)
blink_label()
root.mainloop()
