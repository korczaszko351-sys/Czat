import json, os, threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

CONFIG=Path("config.json")
def load_config():
    if CONFIG.exists(): return json.loads(CONFIG.read_text(encoding="utf-8"))
    return {"api_url":"http://127.0.0.1:8000/v1/chat"}
def save_config(c): CONFIG.write_text(json.dumps(c,indent=2),encoding="utf-8")
class App(tk.Tk):
 def __init__(self):
  super().__init__(); self.title("Mój osobisty czat i App Builder"); self.geometry("900x650"); self.minsize(700,500); self.config=load_config(); self.make_ui()
 def make_ui(self):
  s=ttk.Style(self); s.theme_use("clam"); s.configure("Title.TLabel",font=("Arial",20,"bold")); s.configure("Header.TLabel",font=("Arial",12,"bold"))
  top=ttk.Frame(self,padding=14);top.pack(fill="x");ttk.Label(top,text="Mój osobisty czat + App Builder",style="Title.TLabel").pack(side="left");ttk.Button(top,text="Ustawienia API",command=self.settings).pack(side="right")
  self.tabs=ttk.Notebook(self);self.tabs.pack(fill="both",expand=True,padx=14,pady=(0,14));self.chat_tab=ttk.Frame(self.tabs,padding=12);self.builder_tab=ttk.Frame(self.tabs,padding=12);self.tabs.add(self.chat_tab,text="  Czat  ");self.tabs.add(self.builder_tab,text="  Builder aplikacji  ");self.chat_ui();self.builder_ui()
 def chat_ui(self):
  self.history=tk.Text(self.chat_tab,wrap="word",state="disabled",font=("Arial",11));self.history.pack(fill="both",expand=True);self.add("Asystent","Cześć. Opisz, co chcesz stworzyć, a pomogę zaplanować aplikację.")
  bottom=ttk.Frame(self.chat_tab);bottom.pack(fill="x",pady=(10,0));self.prompt=ttk.Entry(bottom,font=("Arial",11));self.prompt.pack(side="left",fill="x",expand=True);self.prompt.bind("<Return>",lambda e:self.send());ttk.Button(bottom,text="Wyślij",command=self.send).pack(side="left",padx=(8,0))
 def builder_ui(self):
  ttk.Label(self.builder_tab,text="Opisz aplikację",style="Header.TLabel").pack(anchor="w");self.idea=tk.Text(self.builder_tab,height=7,wrap="word",font=("Arial",11));self.idea.pack(fill="x",pady=(6,10));ttk.Button(self.builder_tab,text="Wygeneruj specyfikację",command=self.build_spec).pack(anchor="w");ttk.Label(self.builder_tab,text="Wynik",style="Header.TLabel").pack(anchor="w",pady=(16,4));self.spec=tk.Text(self.builder_tab,wrap="word",font=("Consolas",10));self.spec.pack(fill="both",expand=True)
 def add(self,who,text):
  self.history.configure(state="normal");self.history.insert("end",f"{who}:
{text}

");self.history.see("end");self.history.configure(state="disabled")
 def send(self):
  text=self.prompt.get().strip()
  if not text:return
  self.prompt.delete(0,"end");self.add("Ty",text);self.ask(text)
 def ask(self,text):
  self.add("Asystent","Myślę…")
  def work():
   try:
    data=json.dumps({"text":text}).encode();req=Request(self.config["api_url"],data=data,headers={"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=100) as r: answer=json.loads(r.read())["answer"]
   except (URLError,HTTPError,KeyError,json.JSONDecodeError) as e: answer=f"Nie udało się połączyć z API. Ustaw adres backendu w Ustawieniach API.

Szczegóły: {e}"
   self.after(0,lambda:self.add("Asystent",answer))
  threading.Thread(target=work,daemon=True).start()
 def build_spec(self):
  idea=self.idea.get("1.0","end").strip()
  if not idea:return messagebox.showinfo("Brak opisu","Najpierw opisz aplikację.")
  self.spec.delete("1.0","end");self.spec.insert("end","Generowanie…")
  def work():
   prompt="Stwórz szczegółową specyfikację MVP aplikacji: "+idea+". Podaj ekrany, dane, API, technologię i plan etapów."
   try:
    data=json.dumps({"text":prompt}).encode();req=Request(self.config["api_url"],data=data,headers={"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=100) as r: out=json.loads(r.read())["answer"]
   except Exception as e: out=f"Błąd API: {e}"
   self.after(0,lambda:(self.spec.delete("1.0","end"),self.spec.insert("end",out)))
  threading.Thread(target=work,daemon=True).start()
 def settings(self):
  w=tk.Toplevel(self);w.title("Ustawienia API");w.transient(self);w.grab_set();ttk.Label(w,text="Adres endpointu czatu:").pack(padx=18,pady=(18,5),anchor="w");v=tk.StringVar(value=self.config["api_url"]);ttk.Entry(w,textvariable=v,width=60).pack(padx=18);ttk.Button(w,text="Zapisz",command=lambda:(self.config.update(api_url=v.get().strip()),save_config(self.config),w.destroy())).pack(pady=18)
if __name__=="__main__": App().mainloop()
