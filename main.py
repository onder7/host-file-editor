import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import platform
import subprocess
import re
from datetime import datetime

class HostsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Hosts Dosya Düzenleyici")
        self.root.geometry("900x700")
        self.root.configure(bg='#2b2b2b')
        
        # Modern tema ayarları
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()
        
        # Hosts dosya yolu
        self.hosts_path = self.get_hosts_path()
        self.hosts_entries = []
        
        self.create_widgets()
        self.load_hosts_file()
        
    def configure_styles(self):
        """Modern tema stilleri"""
        self.style.configure('Title.TLabel', 
                           background='#2b2b2b', 
                           foreground='#ffffff', 
                           font=('Arial', 16, 'bold'))
        
        self.style.configure('Modern.TFrame', 
                           background='#2b2b2b')
        
        self.style.configure('Modern.TButton',
                           background='#404040',
                           foreground='#ffffff',
                           borderwidth=1,
                           focuscolor='none',
                           font=('Arial', 9))
        
        self.style.map('Modern.TButton',
                      background=[('active', '#505050'),
                                ('pressed', '#353535')])
        
        self.style.configure('Add.TButton',
                           background='#28a745',
                           foreground='#ffffff')
        
        self.style.map('Add.TButton',
                      background=[('active', '#34ce57'),
                                ('pressed', '#1e7e34')])
        
        self.style.configure('Delete.TButton',
                           background='#dc3545',
                           foreground='#ffffff')
        
        self.style.map('Delete.TButton',
                      background=[('active', '#e74c3c'),
                                ('pressed', '#c82333')])
        
        self.style.configure('Edit.TButton',
                           background='#007bff',
                           foreground='#ffffff')
        
        self.style.map('Edit.TButton',
                      background=[('active', '#0056b3'),
                                ('pressed', '#004085')])
    
    def get_hosts_path(self):
        """İşletim sistemine göre hosts dosya yolunu döndür"""
        system = platform.system()
        if system == "Windows":
            return r"C:\Windows\System32\drivers\etc\hosts"
        else:
            return "/etc/hosts"
    
    def create_widgets(self):
        """GUI bileşenlerini oluştur"""
        # Ana frame
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🖥️ Hosts Dosya Düzenleyici", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Üst buton çerçevesi
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Butonlar
        ttk.Button(button_frame, text="➕ Yeni Giriş Ekle", 
                  command=self.add_entry, style='Add.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="✏️ Düzenle", 
                  command=self.edit_entry, style='Edit.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🗑️ Sil", 
                  command=self.delete_entry, style='Delete.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="🔄 Yenile", 
                  command=self.load_hosts_file, style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 Kaydet", 
                  command=self.save_hosts_file, style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="📂 Yedekle", 
                  command=self.backup_hosts, style='Modern.TButton').pack(side=tk.LEFT)
        
        # Hosts listesi frame
        list_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview (liste)
        columns = ('Durum', 'IP Adresi', 'Host Adı', 'Açıklama')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Sütun başlıkları
        self.tree.heading('Durum', text='Durum')
        self.tree.heading('IP Adresi', text='IP Adresi')
        self.tree.heading('Host Adı', text='Host Adı')
        self.tree.heading('Açıklama', text='Açıklama')
        
        # Sütun genişlikleri
        self.tree.column('Durum', width=80, anchor='center')
        self.tree.column('IP Adresi', width=150)
        self.tree.column('Host Adı', width=200)
        self.tree.column('Açıklama', width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree ve scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Alt bilgi çerçevesi
        info_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        info_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.info_label = ttk.Label(info_frame, text=f"Hosts dosyası: {self.hosts_path}", 
                                   background='#2b2b2b', foreground='#cccccc')
        self.info_label.pack(side=tk.LEFT)
        
        # Çift tıklama olayı
        self.tree.bind('<Double-1>', lambda e: self.edit_entry())
    
    def load_hosts_file(self):
        """Hosts dosyasını yükle"""
        try:
            self.hosts_entries.clear()
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            if not os.path.exists(self.hosts_path):
                messagebox.showerror("Hata", f"Hosts dosyası bulunamadı: {self.hosts_path}")
                return
            
            with open(self.hosts_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
            
            for line_num, line in enumerate(lines, 1):
                original_line = line.rstrip('\n\r')
                line = line.strip()
                
                if not line:
                    continue
                
                is_comment = line.startswith('#')
                
                if is_comment:
                    # Yorumlu satır
                    comment_match = re.match(r'#\s*(.+)', line)
                    if comment_match:
                        comment_text = comment_match.group(1)
                        # Eğer IP ve host içeriyorsa parse et
                        parts = comment_text.split()
                        if len(parts) >= 2 and self.is_valid_ip(parts[0]):
                            ip = parts[0]
                            hostname = parts[1]
                            description = ' '.join(parts[2:]) if len(parts) > 2 else ""
                            self.add_to_tree("❌ Devre Dışı", ip, hostname, description, original_line)
                        else:
                            self.add_to_tree("💬 Yorum", "", "", comment_text, original_line)
                else:
                    # Aktif hosts girişi
                    parts = line.split()
                    if len(parts) >= 2 and self.is_valid_ip(parts[0]):
                        ip = parts[0]
                        hostname = parts[1]
                        description = ' '.join(parts[2:]) if len(parts) > 2 else ""
                        self.add_to_tree("✅ Aktif", ip, hostname, description, original_line)
                    else:
                        # Geçersiz format
                        self.add_to_tree("⚠️ Geçersiz", "", "", line, original_line)
            
            self.info_label.config(text=f"Hosts dosyası yüklendi: {len(self.hosts_entries)} giriş")
            
        except PermissionError:
            messagebox.showerror("Hata", "Hosts dosyasını okumak için yetki gerekli!")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya yüklenirken hata: {str(e)}")
    
    def add_to_tree(self, status, ip, hostname, description, original_line):
        """Treeview'e giriş ekle"""
        item_id = self.tree.insert('', 'end', values=(status, ip, hostname, description))
        self.hosts_entries.append({
            'item_id': item_id,
            'status': status,
            'ip': ip,
            'hostname': hostname,
            'description': description,
            'original_line': original_line
        })
    
    def is_valid_ip(self, ip):
        """IP adresinin geçerli olup olmadığını kontrol et"""
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        return re.match(pattern, ip) is not None
    
    def add_entry(self):
        """Yeni hosts girişi ekle"""
        dialog = HostEntryDialog(self.root, "Yeni Giriş Ekle")
        result = dialog.get_result()
        
        if result:
            ip, hostname, description, is_active = result
            status = "✅ Aktif" if is_active else "❌ Devre Dışı"
            
            # Treeview'e ekle
            self.add_to_tree(status, ip, hostname, description, "")
            
            messagebox.showinfo("Başarılı", "Yeni giriş eklendi. Değişiklikleri kaydetmeyi unutmayın!")
    
    def edit_entry(self):
        """Seçili girişi düzenle"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen düzenlemek için bir giriş seçin!")
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if values[0] == "💬 Yorum":
            # Yorum düzenleme
            new_comment = tk.simpledialog.askstring("Yorumu Düzenle", 
                                                   "Yorum:", 
                                                   initialvalue=values[3])
            if new_comment:
                self.tree.item(item, values=("💬 Yorum", "", "", new_comment))
                self.update_hosts_entry(item, "", "", new_comment, "💬 Yorum")
        else:
            # Normal giriş düzenleme
            current_active = values[0] == "✅ Aktif"
            dialog = HostEntryDialog(self.root, "Girişi Düzenle", 
                                   values[1], values[2], values[3], current_active)
            result = dialog.get_result()
            
            if result:
                ip, hostname, description, is_active = result
                status = "✅ Aktif" if is_active else "❌ Devre Dışı"
                
                self.tree.item(item, values=(status, ip, hostname, description))
                self.update_hosts_entry(item, ip, hostname, description, status)
                
                messagebox.showinfo("Başarılı", "Giriş güncellendi. Değişiklikleri kaydetmeyi unutmayın!")
    
    def update_hosts_entry(self, item_id, ip, hostname, description, status):
        """Hosts giriş listesini güncelle"""
        for entry in self.hosts_entries:
            if entry['item_id'] == item_id:
                entry['ip'] = ip
                entry['hostname'] = hostname
                entry['description'] = description
                entry['status'] = status
                break
    
    def delete_entry(self):
        """Seçili girişi sil"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir giriş seçin!")
            return
        
        if messagebox.askyesno("Onay", "Seçili girişi silmek istediğinizden emin misiniz?"):
            item = selection[0]
            self.tree.delete(item)
            
            # Listeden de kaldır
            self.hosts_entries = [entry for entry in self.hosts_entries if entry['item_id'] != item]
            
            messagebox.showinfo("Başarılı", "Giriş silindi. Değişiklikleri kaydetmeyi unutmayın!")
    
    def save_hosts_file(self):
        """Hosts dosyasını kaydet"""
        try:
            # Yedek oluştur
            backup_path = f"{self.hosts_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(self.hosts_path):
                import shutil
                shutil.copy2(self.hosts_path, backup_path)
            
            # Yeni içerik oluştur
            lines = []
            lines.append("# Hosts dosyası - Python Hosts Editor ile düzenlendi")
            lines.append(f"# Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            
            for entry in self.hosts_entries:
                if entry['status'] == "💬 Yorum":
                    lines.append(f"# {entry['description']}")
                elif entry['status'] == "✅ Aktif":
                    line = f"{entry['ip']}\t{entry['hostname']}"
                    if entry['description']:
                        line += f"\t# {entry['description']}"
                    lines.append(line)
                elif entry['status'] == "❌ Devre Dışı":
                    line = f"# {entry['ip']}\t{entry['hostname']}"
                    if entry['description']:
                        line += f"\t# {entry['description']}"
                    lines.append(line)
                elif entry['status'] == "⚠️ Geçersiz":
                    lines.append(f"# {entry['description']}")
            
            # Dosyaya yaz
            with open(self.hosts_path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(lines))
            
            messagebox.showinfo("Başarılı", f"Hosts dosyası kaydedildi!\nYedek: {backup_path}")
            
        except PermissionError:
            messagebox.showerror("Hata", "Hosts dosyasını kaydetmek için yönetici yetkileri gerekli!")
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya kaydedilirken hata: {str(e)}")
    
    def backup_hosts(self):
        """Hosts dosyasını yedekle"""
        try:
            backup_path = filedialog.asksaveasfilename(
                title="Hosts Dosyasını Yedekle",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if backup_path:
                import shutil
                shutil.copy2(self.hosts_path, backup_path)
                messagebox.showinfo("Başarılı", f"Hosts dosyası yedeklendi: {backup_path}")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Yedekleme hatası: {str(e)}")


class HostEntryDialog:
    def __init__(self, parent, title, ip="", hostname="", description="", is_active=True):
        self.result = None
        
        # Dialog penceresi
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x300")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Ortalama
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        # Frame
        main_frame = ttk.Frame(self.dialog, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # IP Adresi
        ttk.Label(main_frame, text="IP Adresi:", background='#2b2b2b', foreground='#ffffff').pack(anchor='w')
        self.ip_entry = ttk.Entry(main_frame, width=40, font=('Arial', 10))
        self.ip_entry.pack(fill=tk.X, pady=(0, 10))
        self.ip_entry.insert(0, ip)
        
        # Host Adı
        ttk.Label(main_frame, text="Host Adı:", background='#2b2b2b', foreground='#ffffff').pack(anchor='w')
        self.hostname_entry = ttk.Entry(main_frame, width=40, font=('Arial', 10))
        self.hostname_entry.pack(fill=tk.X, pady=(0, 10))
        self.hostname_entry.insert(0, hostname)
        
        # Açıklama
        ttk.Label(main_frame, text="Açıklama (opsiyonel):", background='#2b2b2b', foreground='#ffffff').pack(anchor='w')
        self.description_entry = ttk.Entry(main_frame, width=40, font=('Arial', 10))
        self.description_entry.pack(fill=tk.X, pady=(0, 10))
        self.description_entry.insert(0, description)
        
        # Aktif checkbox
        self.active_var = tk.BooleanVar(value=is_active)
        self.active_check = ttk.Checkbutton(main_frame, text="Aktif (hosts dosyasında etkin olsun)", 
                                          variable=self.active_var)
        self.active_check.pack(anchor='w', pady=(0, 20))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Tamam", command=self.ok_clicked, 
                  style='Add.TButton').pack(side=tk.RIGHT, padx=(10, 0))
        ttk.Button(button_frame, text="İptal", command=self.cancel_clicked, 
                  style='Modern.TButton').pack(side=tk.RIGHT)
        
        # Enter tuşu
        self.dialog.bind('<Return>', lambda e: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda e: self.cancel_clicked())
        
        # Focus
        self.ip_entry.focus()
    
    def ok_clicked(self):
        ip = self.ip_entry.get().strip()
        hostname = self.hostname_entry.get().strip()
        description = self.description_entry.get().strip()
        is_active = self.active_var.get()
        
        if not ip or not hostname:
            messagebox.showerror("Hata", "IP adresi ve host adı zorunludur!")
            return
        
        # IP formatını kontrol et
        pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        if not re.match(pattern, ip):
            messagebox.showerror("Hata", "Geçerli bir IP adresi girin!")
            return
        
        self.result = (ip, hostname, description, is_active)
        self.dialog.destroy()
    
    def cancel_clicked(self):
        self.dialog.destroy()
    
    def get_result(self):
        self.dialog.wait_window()
        return self.result


def main():
    root = tk.Tk()
    app = HostsEditor(root)
    
    # Windows'ta yönetici kontrolü
    if platform.system() == "Windows":
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                messagebox.showwarning("Uyarı", 
                    "Bu uygulama hosts dosyasını düzenlemek için yönetici yetkileri gerektirir.\n"
                    "Lütfen uygulamayı 'Yönetici olarak çalıştır' seçeneği ile başlatın.")
        except:
            pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
