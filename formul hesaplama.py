import sympy as sp
import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

FORMULA_FILE = "formulas.json"

# Formülleri yükleme ve kaydetme
def load_formulas():
    if os.path.exists(FORMULA_FILE):
        with open(FORMULA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_formulas(formulas):
    with open(FORMULA_FILE, "w") as file:
        json.dump(formulas, file)

# Global değişkenler
formulas = load_formulas()
entry_widgets = {}  # Mevcut giriş widget'larını değişken adına göre takip eder
label_widgets = {}  # Değişkenlere ait etiketleri takip eder

def calculate_formula():
    formula_input = formula_entry.get().strip()
    formula_input = formula_input.replace("^", "**")  # ^ yerine ** kullanımı için dönüşüm
    try:
        lhs, rhs = formula_input.split("=")
        rhs_expr = sp.sympify(rhs)
    except Exception as e:
        messagebox.showerror("Hata", f"Formül hatalı: {e}")
        return

    variables = rhs_expr.free_symbols
    if isinstance(variables, sp.Basic):
        variables = {variables}

    subs = {}
    for var in variables:
        if str(var) == "pi":
            subs[var] = 3.14
            continue

        var_value = entry_widgets.get(var, None)
        if var_value:
            try:
                value = var_value.get()
                if value == "":
                    raise ValueError(f"{var} için değer girilmedi.")
                subs[var] = sp.sympify(value)  # Matematiksel ifade olarak değerlendir
            except Exception as e:
                messagebox.showerror("Hata", f"Lütfen geçerli bir ifade girin. {var} için tekrar deneyin. Hata: {e}")
                return

    result = rhs_expr.subs(subs)
    result_value = result.evalf()

    messagebox.showinfo("Sonuç", f"{lhs.strip()} = {result_value}")

def create_input_fields(*args):
    global entry_widgets, label_widgets

    formula_input = formula_entry.get().strip()

    # Formül değiştiyse mevcut değişkenleri güncelle
    formula_input = formula_input.replace("^", "**")
    try:
        lhs, rhs = formula_input.split("=")
        rhs_expr = sp.sympify(rhs)
    except Exception:
        return  # Hatalı formül için alan oluşturma

    # Formül tamamen silinmişse, değişken alanlarını temizle
    if not formula_input:  # Formül tamamen silindiyse
        # Tüm giriş alanlarını temizle
        for var in list(entry_widgets.keys()):
            entry_widgets[var].destroy()
            label_widgets[var].destroy()
        entry_widgets.clear()
        label_widgets.clear()
        return

    variables = rhs_expr.free_symbols
    if isinstance(variables, sp.Basic):
        variables = {variables}

    # Yeni değişkenler
    new_vars = set(variables)
    existing_vars = set(entry_widgets.keys())

    # Eklenmesi gereken yeni değişkenler
    added_vars = new_vars - existing_vars
    for var in added_vars:
        if str(var) == "pi":
            continue  # Pi sabit olduğu için giriş istemiyoruz

        label = tk.Label(root, text=f"{var} değişkeninin değerini girin:")
        label.pack()
        label_widgets[var] = label

        entry = tk.Entry(root)
        entry.pack(pady=5)
        entry_widgets[var] = entry

    # Silinmesi gereken değişkenler
    removed_vars = existing_vars - new_vars
    for var in removed_vars:
        widget = entry_widgets.pop(var, None)
        if widget:
            widget.destroy()

        label = label_widgets.pop(var, None)
        if label:
            label.destroy()

def save_formula():
    formula_input = formula_entry.get().strip()
    if "=" not in formula_input:
        messagebox.showerror("Hata", "Formül geçerli bir eşittir işareti içermelidir.")
        return

    name = simpledialog.askstring("Formül Kaydet", "Formül için bir ad girin:")
    if not name:
        return

    formulas[name] = formula_input
    save_formulas(formulas)
    messagebox.showinfo("Başarılı", f"{name} adlı formül kaydedildi.")

def load_formula():
    if not formulas:
        messagebox.showinfo("Bilgi", "Kaydedilmiş formül bulunamadı.")
        return

    def select_formula():
        selected = formula_listbox.curselection()
        if selected:
            formula_name = formula_listbox.get(selected).split(" | ")[0]
            formula_entry.delete(0, tk.END)
            formula_entry.insert(0, formulas[formula_name])
            formula_window.destroy()
        else:
            messagebox.showerror("Hata", "Lütfen bir formül seçin.")

    def delete_formula():
        selected = formula_listbox.curselection()
        if selected:
            formula_name = formula_listbox.get(selected).split(" | ")[0]
            if messagebox.askyesno("Sil", f"{formula_name} adlı formülü silmek istediğinizden emin misiniz?"):
                formulas.pop(formula_name)
                save_formulas(formulas)
                formula_window.destroy()
                load_formula()
        else:
            messagebox.showerror("Hata", "Lütfen bir formül seçin.")

    def update_formula():
        selected = formula_listbox.curselection()
        if selected:
            formula_name = formula_listbox.get(selected).split(" | ")[0]
            updated_formula = simpledialog.askstring("Formül Güncelle", "Yeni formülü girin:", initialvalue=formulas[formula_name])
            if updated_formula and "=" in updated_formula:
                formulas[formula_name] = updated_formula
                save_formulas(formulas)
                formula_window.destroy()
                load_formula()
            else:
                messagebox.showerror("Hata", "Geçerli bir formül girin.")
        else:
            messagebox.showerror("Hata", "Lütfen bir formül seçin.")

    # Yeni bir pencere oluştur
    formula_window = tk.Toplevel(root)
    formula_window.title("Kaydedilmiş Formüller")

    tk.Label(formula_window, text="Bir formül seçin:").pack(pady=10)

    # Formülleri listeleyen bir liste kutusu
    formula_listbox = tk.Listbox(formula_window, width=50, height=10)
    for name, formula in formulas.items():
        formula_listbox.insert(tk.END, f"{name} | {formula}")
    formula_listbox.pack(pady=10)

    button_frame = tk.Frame(formula_window)
    button_frame.pack(pady=5)

    select_button = tk.Button(button_frame, text="Seç", command=select_formula)
    select_button.pack(side=tk.LEFT, padx=5)

    delete_button = tk.Button(button_frame, text="Sil", command=delete_formula)
    delete_button.pack(side=tk.LEFT, padx=5)

    update_button = tk.Button(button_frame, text="Güncelle", command=update_formula)
    update_button.pack(side=tk.LEFT, padx=5)

# Tkinter arayüzü
root = tk.Tk()
root.title("Formül Hesaplama")

instruction_label = tk.Label(root, text="Formül yazarken çarpma için '*' işaretini, ve üssü için '**' ifadesini kullanın.\nÖrnek: a = b**2 + c / (K * 2)\n 3,14 yerine 'pi' yazabilirsiniz.")
instruction_label.pack(pady=10)

formula_label = tk.Label(root, text="Formülünüzü girin:")
formula_label.pack()

formula_var = tk.StringVar()  # Formül giriş alanını izlemek için
formula_var.trace_add("write", create_input_fields)  # Değişiklikleri takip et
formula_entry = tk.Entry(root, textvariable=formula_var, width=40)
formula_entry.pack(pady=5)

calculate_button = tk.Button(root, text="Hesapla", command=calculate_formula)
calculate_button.pack(pady=5)

save_button = tk.Button(root, text="Formülü Kaydet", command=save_formula)
save_button.pack(pady=5)

load_button = tk.Button(root, text="Kaydedilmiş Formüller", command=load_formula)
load_button.pack(pady=5)

root.mainloop()
