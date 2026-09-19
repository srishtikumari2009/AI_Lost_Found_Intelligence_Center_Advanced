import os, shutil, csv
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from database import Database, BASE_DIR
from matcher import ImageMatcher, IMAGE_EXTENSIONS, confidence

LOST_DIR=BASE_DIR/"images"/"lost"
FOUND_DIR=BASE_DIR/"images"/"found"
LOST_DIR.mkdir(parents=True,exist_ok=True); FOUND_DIR.mkdir(parents=True,exist_ok=True)

db=Database()
matcher=ImageMatcher()

def copy_image(source,dest_dir):
    source=Path(source); dest_dir.mkdir(parents=True,exist_ok=True)
    dest=dest_dir/source.name
    i=1
    while dest.exists():
        dest=dest_dir/f"{source.stem}_{i}{source.suffix}"; i+=1
    shutil.copy2(source,dest)
    return dest

def parse_date(value):
    for fmt in ("%d-%m-%Y","%d/%m/%Y","%Y-%m-%d"):
        try: return datetime.strptime(value,fmt).strftime("%Y-%m-%d")
        except ValueError: pass
    return None

def resolve_image(value):
    p=Path(value)
    if p.exists(): return p
    for base in (LOST_DIR,FOUND_DIR):
        candidate=base/p.name
        if candidate.exists(): return candidate
    return p

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Lost & Found Intelligence Center")
        self.geometry("1120x760")
        self.minsize(1000,700)
        self.configure(bg="#eef2f7")
        self.protocol("WM_DELETE_WINDOW",self.close)
        self.style=ttk.Style(self)
        try:self.style.theme_use("clam")
        except:pass
        self.style.configure("Treeview",rowheight=32,font=("Segoe UI",10))
        self.style.configure("Treeview.Heading",font=("Segoe UI",10,"bold"))
        self.build()
        self.refresh_all()

    def header(self,parent,title,subtitle):
        f=tk.Frame(parent,bg="#17324d"); f.pack(fill="x")
        tk.Label(f,text=title,bg="#17324d",fg="white",font=("Segoe UI",22,"bold")).pack(anchor="w",padx=28,pady=(20,2))
        tk.Label(f,text=subtitle,bg="#17324d",fg="#d6e3ef",font=("Segoe UI",10)).pack(anchor="w",padx=30,pady=(0,18))

    def build(self):
        nav=tk.Frame(self,bg="#10283f",width=190); nav.pack(side="left",fill="y"); nav.pack_propagate(False)
        tk.Label(nav,text="LFIC",bg="#10283f",fg="white",font=("Segoe UI",25,"bold")).pack(pady=(28,2))
        tk.Label(nav,text="Intelligence Center",bg="#10283f",fg="#a9bfd3",font=("Segoe UI",9)).pack(pady=(0,25))
        for text,cmd in [("Dashboard",self.dashboard),("Report Lost",lambda:self.report("Lost")),
                         ("Report Found",lambda:self.report("Found")),("AI Match",self.match),
                         ("Records",self.records),("Export CSV",self.export)]:
            tk.Button(nav,text=text,command=cmd,bg="#10283f",fg="white",activebackground="#244966",
                      activeforeground="white",bd=0,font=("Segoe UI",11),anchor="w",padx=25,height=2).pack(fill="x",pady=2)
        tk.Label(nav,text="Hybrid ORB + Color\nSQLite • OpenCV",bg="#10283f",fg="#7f9bb1",
                 font=("Segoe UI",8),justify="left").pack(side="bottom",anchor="w",padx=22,pady=25)
        self.content=tk.Frame(self,bg="#eef2f7"); self.content.pack(side="left",fill="both",expand=True)
        self.dashboard()

    def clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def dashboard(self):
        self.clear(); self.header(self.content,"Dashboard","Monitor lost/found reports and matching activity.")
        s=db.stats()
        cards=tk.Frame(self.content,bg="#eef2f7"); cards.pack(fill="x",padx=28,pady=25)
        for label,key in [("TOTAL REPORTS","total"),("LOST ITEMS","lost"),("FOUND ITEMS","found"),("ACTIVE","active"),("RESOLVED","resolved")]:
            c=tk.Frame(cards,bg="white",width=150,height=100,highlightbackground="#d7dee8",highlightthickness=1)
            c.pack(side="left",fill="both",expand=True,padx=5); c.pack_propagate(False)
            tk.Label(c,text=label,bg="white",fg="#6c7a89",font=("Segoe UI",8,"bold")).pack(anchor="w",padx=14,pady=(15,0))
            tk.Label(c,text=str(s[key]),bg="white",fg="#17324d",font=("Segoe UI",23,"bold")).pack(anchor="w",padx=14,pady=5)
        box=tk.Frame(self.content,bg="white"); box.pack(fill="both",expand=True,padx=33,pady=5)
        tk.Label(box,text="Recent Reports",bg="white",fg="#17324d",font=("Segoe UI",14,"bold")).pack(anchor="w",padx=18,pady=15)
        self.table(box,db.get_all()[:10],compact=True)

    def table(self,parent,rows,compact=False):
        cols=("id","type","item","location","date","status")
        tree=ttk.Treeview(parent,columns=cols,show="headings")
        headings={"id":"ID","type":"Type","item":"Item","location":"Location","date":"Date","status":"Status"}
        widths={"id":50,"type":80,"item":190,"location":180,"date":100,"status":100}
        for c in cols:
            tree.heading(c,text=headings[c]); tree.column(c,width=widths[c],anchor="center" if c in ("id","type","date","status") else "w")
        for r in rows:
            tree.insert("", "end", values=(r["id"],r["item_type"],r["item_name"],r["location"],r["date"],r["status"]))
        tree.pack(fill="both",expand=True,padx=15,pady=(0,15))
        return tree

    def report(self,item_type):
        win=tk.Toplevel(self); win.title(f"Report {item_type} Item"); win.geometry("560x610"); win.transient(self); win.grab_set()
        tk.Label(win,text=f"REPORT {item_type.upper()} ITEM",font=("Segoe UI",19,"bold")).pack(pady=20)
        frm=tk.Frame(win); frm.pack(fill="x",padx=35)
        fields={}
        for label,key in [("Item Name","name"),("Description","description"),("Location","location"),("Date (DD-MM-YYYY)","date"),("Contact","contact")]:
            tk.Label(frm,text=label,font=("Segoe UI",10,"bold")).pack(anchor="w",pady=(8,2))
            e=tk.Entry(frm,font=("Segoe UI",11)); e.pack(fill="x"); fields[key]=e
        selected={"path":None}
        lab=tk.Label(win,text="No image selected",fg="#687888"); lab.pack(pady=15)
        def choose():
            p=filedialog.askopenfilename(parent=win,filetypes=[("Images","*.jpg *.jpeg *.png *.bmp *.webp")])
            if p:selected["path"]=p; lab.config(text=Path(p).name)
        tk.Button(win,text="Select Item Image",command=choose,font=("Segoe UI",10,"bold"),padx=18,pady=7).pack()
        def save():
            name=fields["name"].get().strip(); loc=fields["location"].get().strip(); date=fields["date"].get().strip(); contact=fields["contact"].get().strip()
            if not all([name,loc,date,contact,selected["path"]]): return messagebox.showwarning("Missing details","Please complete all required fields and select an image.",parent=win)
            date2=parse_date(date)
            if not date2:return messagebox.showwarning("Invalid date","Use DD-MM-YYYY, DD/MM/YYYY or YYYY-MM-DD.",parent=win)
            try:
                dest=copy_image(selected["path"],LOST_DIR if item_type=="Lost" else FOUND_DIR)
                db.add_item(item_type,name,fields["description"].get().strip(),loc,date2,contact,str(dest))
                messagebox.showinfo("Saved","Report saved successfully.",parent=win); win.destroy(); self.dashboard()
            except Exception as e: messagebox.showerror("Error",str(e),parent=win)
        tk.Button(win,text="SAVE REPORT",command=save,bg="#17324d",fg="white",font=("Segoe UI",11,"bold"),padx=30,pady=9).pack(pady=22)

    def match(self):
        self.clear(); self.header(self.content,"AI Match Engine","Upload a lost-item image and rank the most visually similar found reports.")
        top=tk.Frame(self.content,bg="white"); top.pack(fill="x",padx=30,pady=25)
        selected={"path":None}
        preview=tk.Label(top,text="Query image not selected",bg="white",fg="#71808f",width=40,height=8)
        preview.pack(side="left",padx=20,pady=20)
        info=tk.Frame(top,bg="white"); info.pack(side="left",fill="both",expand=True,padx=10)
        status=tk.Label(info,text="Ready",bg="white",fg="#17324d",font=("Segoe UI",14,"bold")); status.pack(anchor="w",pady=15)
        tk.Label(info,text="Ranking uses ORB local features (75%) + HSV color histogram (25%).\nThe score is a visual ranking metric, not a probability.",bg="white",fg="#5f6f7d",justify="left").pack(anchor="w")
        result_box=tk.Frame(self.content,bg="white"); result_box.pack(fill="both",expand=True,padx=30,pady=(0,25))
        tree=ttk.Treeview(result_box,columns=("rank","id","item","location","score","confidence","matches"),show="headings")
        for c,t,w in [("rank","#",45),("id","ID",55),("item","Found Item",180),("location","Location",150),("score","Score",90),("confidence","Confidence",100),("matches","ORB Matches",100)]:
            tree.heading(c,text=t); tree.column(c,width=w,anchor="center")
        tree.pack(fill="both",expand=True,padx=15,pady=15)
        details=tk.Label(result_box,text="",bg="white",fg="#334e68",font=("Segoe UI",10),justify="left"); details.pack(anchor="w",padx=18,pady=(0,12))
        def choose():
            p=filedialog.askopenfilename(filetypes=[("Images","*.jpg *.jpeg *.png *.bmp *.webp")])
            if not p:return
            selected["path"]=p; preview.config(text=Path(p).name)
            try:
                im=Image.open(p); im.thumbnail((300,180)); ph=ImageTk.PhotoImage(im); preview.config(image=ph); preview.image=ph
            except:pass
        def run():
            if not selected["path"]:return messagebox.showwarning("Image required","Select a lost-item image first.")
            rows=db.get_all(item_type="Found",status="Active")
            candidates=[]
            row_by_name={}
            for r in rows:
                p=resolve_image(r["image"])
                if p.exists():candidates.append(p); row_by_name[str(p)]=r
            if not candidates:return messagebox.showinfo("No candidates","No active found-item images are available.")
            for i in tree.get_children():tree.delete(i)
            ranked=matcher.rank(selected["path"],candidates,5)
            if not ranked:return messagebox.showinfo("No result","Could not process the images.")
            for idx,(score,p,metrics) in enumerate(ranked,1):
                r=row_by_name.get(str(p))
                if not r: continue
                tree.insert("", "end", values=(idx,r["id"],r["item_name"],r["location"],f"{score:.2f}%",confidence(score),metrics["good_matches"]))
            status.config(text=f"{len(ranked)} best candidates ranked")
            def show(event=None):
                sel=tree.selection()
                if not sel:return
                vals=tree.item(sel[0],"values"); rid=vals[1]; r=db.get_item(rid)
                details.config(text=f"Selected: {r['item_name']} | {r['location']} | {r['date']} | Contact: {r['contact']}\nDescription: {r['description']}")
            tree.bind("<<TreeviewSelect>>",show)
        tk.Button(info,text="Choose Lost Image",command=choose,padx=16,pady=7).pack(anchor="w",pady=20)
        tk.Button(info,text="RUN SMART MATCH",command=run,bg="#17324d",fg="white",font=("Segoe UI",11,"bold"),padx=18,pady=8).pack(anchor="w")

    def records(self):
        self.clear(); self.header(self.content,"Records","Search, review and manage submitted reports.")
        bar=tk.Frame(self.content,bg="#eef2f7"); bar.pack(fill="x",padx=30,pady=15)
        q=tk.Entry(bar,font=("Segoe UI",11)); q.pack(side="left",fill="x",expand=True,padx=(0,8))
        q.insert(0,"Search item, location, description or contact")
        typevar=tk.StringVar(value="All"); cb=ttk.Combobox(bar,textvariable=typevar,values=["All","Lost","Found"],state="readonly",width=10); cb.pack(side="left",padx=5)
        container=tk.Frame(self.content,bg="white"); container.pack(fill="both",expand=True,padx=30,pady=10)
        def load():
            search=q.get().strip()
            if search=="Search item, location, description or contact":search=""
            rows=db.get_all(None if typevar.get()=="All" else typevar.get(),search=search)
            for w in container.winfo_children():w.destroy()
            tree=self.table(container,rows)
            def action(event=None):
                sel=tree.selection()
                if not sel:return
                rid=tree.item(sel[0],"values")[0]
                menu=tk.Menu(self,tearoff=0)
                menu.add_command(label="Mark Resolved",command=lambda:[db.update_status(rid,"Resolved"),menu.destroy(),load()])
                menu.add_command(label="Mark Active",command=lambda:[db.update_status(rid,"Active"),menu.destroy(),load()])
                menu.add_command(label="Delete Record",command=lambda:self.delete_record(rid,load))
                menu.post(self.winfo_pointerx(),self.winfo_pointery())
            tree.bind("<Button-3>",action)
        tk.Button(bar,text="Search",command=load,bg="#17324d",fg="white",padx=16,pady=6).pack(side="left")
        tk.Label(self.content,text="Tip: Right-click a record to change status or delete it.",bg="#eef2f7",fg="#64748b").pack(anchor="w",padx=35)
        load()

    def delete_record(self,rid,reload):
        if messagebox.askyesno("Confirm","Delete this record?"):
            db.delete_item(rid); reload()

    def export(self):
        path=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")],initialfile="lost_found_reports.csv")
        if path:
            db.export_csv(path); messagebox.showinfo("Export complete",f"Reports exported to:\n{path}")

    def refresh_all(self): pass
    def close(self): db.close(); self.destroy()

if __name__=="__main__":
    App().mainloop()
