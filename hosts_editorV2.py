# Geliştirilmiş Kod (hosts_editor_v2.py)

import customtkinter as ctk
import os
import sys
import ctypes
import traceback

# --- Platforma Özel Ayarlar ve Fonksiyonlar ---

def get_hosts_path():
    """İşletim sistemine göre hosts dosyasının yolunu döndürür."""
    if sys.platform.startswith('win'):
        return os.path.join(os.environ['SystemRoot'], 'System32', 'drivers', 'etc', 'hosts')
    elif sys.platform.startswith('linux') or sys.platform == 'darwin':
        return '/etc/hosts'
    return None

def is_admin():
    """Uygulamanın yönetici izinleriyle çalışıp çalışmadığını kontrol eder."""
    try:
        if sys.platform.startswith('win'):
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        elif sys.platform.startswith('linux') or sys.platform == 'darwin':
            return os.geteuid() == 0
    except Exception:
        return False
    return False

def show_admin_error_and_exit():
    """Yönetici izni hatasını gösteren bir pencere oluşturur ve çıkar."""
    error_app = ctk.CTk()
    error_app.withdraw() # Ana pencereyi gizle

    error_window = ctk.CTkToplevel(error_app)
    error_window.title("Hata: Yönetici İzinleri Gerekli")
    error_window.geometry("480x180")
    error_window.transient()
    error_window.grab_set()

    error_text = ("Bu uygulamanın hosts dosyasını düzenleyebilmesi için\n"
                  "Yönetici (Administrator/root) olarak çalıştırılması gerekmektedir.\n\n"
                  "Lütfen uygulamayı şu şekilde yeniden başlatın:\n"
                  "- Windows: Terminal'e sağ tıklayıp 'Yönetici olarak çalıştır' deyin.\n"
                  "- Linux/macOS: Komutun başına 'sudo' ekleyin.")
    
    label = ctk.CTkLabel(error_window, text=error_text, font=ctk.CTkFont(size=13))
    label.pack(expand=True, padx=20, pady=10)

    button = ctk.CTkButton(error_window, text="Anladım, Kapat", command=error_app.destroy)
    button.pack(pady=10, padx=20)
    
    error_app.mainloop()
    sys.exit(1)


class HostsEditorApp(ctk.CTk):
    def __init__(self, hosts_path):
        super().__init__()
        self.HOSTS_PATH = hosts_path
        self.title("Hosts Dosya Düzenleyici : Önder AKÖZ")
        self.geometry("750x600")

        self.setup_ui()
        self.load_hosts_file()

    def setup_ui(self):
        """Uygulamanın arayüzünü oluşturur."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        top_frame = ctk.CTkFrame(self, corner_radius=0)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(top_frame, text="Hosts Dosyası Girdileri", font=ctk.CTkFont(size=16, weight="bold"))
        title_label.grid(row=0, column=0, padx=10, pady=10)

        theme_switch = ctk.CTkSwitch(top_frame, text="Koyu Tema", command=lambda: ctk.set_appearance_mode("Light" if ctk.get_appearance_mode() == "Dark" else "Dark"))
        theme_switch.grid(row=0, column=1, padx=10, pady=10)
        theme_switch.select()

        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Girdiler")
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.scrollable_frame.grid_columnconfigure((1, 2), weight=1)
        
        button_frame = ctk.CTkFrame(self, corner_radius=0)
        button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.add_button = ctk.CTkButton(button_frame, text="Yeni Ekle", command=self.add_new_entry)
        self.add_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        self.reload_button = ctk.CTkButton(button_frame, text="Yenile", command=self.load_hosts_file)
        self.reload_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        self.save_button = ctk.CTkButton(button_frame, text="Değişiklikleri Kaydet", command=self.save_hosts_file, fg_color="green", hover_color="darkgreen")
        self.save_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        self.status_label = ctk.CTkLabel(self, text="Başlatıldı. Yönetici olarak çalışıyor.", text_color="gray")
        self.status_label.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 5))
        
        self.entries = []

    def load_hosts_file(self):
        """Hosts dosyasını okur ve arayüzde listeler."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        try:
            with open(self.HOSTS_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in lines:
                self.create_entry_widget(line.strip())
            
            self.update_status("Hosts dosyası başarıyla yüklendi.", "green")

        except Exception as e:
            self.update_status(f"Hata: Hosts dosyası okunamadı: {e}", "red")
            traceback.print_exc()

    def create_entry_widget(self, line_text, is_new=False):
        """Verilen satır için bir girdi arayüz bileşeni oluşturur."""
        # Yorumlanmış veya devre dışı bırakılmış girdileri de doğru ayrıştır
        is_commented = line_text.startswith('#')
        effective_line = line_text.lstrip('# ').strip()
        parts = effective_line.split()

        # Bir IP ve hostname içeriyor mu diye kontrol et
        is_parseable = len(parts) >= 2 and (parts[0].replace('.', '').isdigit() or ':' in parts[0])
        
        entry_data = {
            'is_comment_or_empty': not is_parseable,
            'original_line': line_text
        }

        frame = ctk.CTkFrame(self.scrollable_frame)
        frame.grid(sticky="ew", padx=5, pady=2)
        frame.grid_columnconfigure(2, weight=1)

        if not is_parseable and not is_new:
            label = ctk.CTkLabel(frame, text=line_text, text_color="gray", anchor="w")
            label.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=2)
            entry_data['widgets'] = {'frame': frame, 'label': label}
        else:
            ip = parts[0] if is_parseable else ("127.0.0.1" if is_new else "")
            hostname = " ".join(parts[1:]) if is_parseable else ("ornek.site.com" if is_new else "")
            
            active_switch = ctk.CTkSwitch(frame, text="", width=0)
            active_switch.grid(row=0, column=0, padx=5, pady=5)
            if not is_commented:
                active_switch.select()

            ip_entry = ctk.CTkEntry(frame, placeholder_text="IP Adresi", width=150)
            ip_entry.grid(row=0, column=1, padx=5, pady=5)
            ip_entry.insert(0, ip)

            hostname_entry = ctk.CTkEntry(frame, placeholder_text="Hostname(s)")
            hostname_entry.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
            hostname_entry.insert(0, hostname)

            delete_button = ctk.CTkButton(frame, text="Sil", width=50, fg_color="red", hover_color="darkred", command=lambda f=frame: self.delete_entry(f))
            delete_button.grid(row=0, column=3, padx=5, pady=5)
            
            entry_data['widgets'] = {'frame': frame, 'active_switch': active_switch, 'ip_entry': ip_entry, 'hostname_entry': hostname_entry}
            entry_data['is_comment_or_empty'] = False # Artık düzenlenebilir

        self.entries.append(entry_data)
        
    def add_new_entry(self):
        """Arayüze yeni, boş bir girdi satırı ekler."""
        self.create_entry_widget("", is_new=True)
        self.update_status("Yeni girdi satırı eklendi. Doldurup kaydedin.", "blue")

    def delete_entry(self, frame_to_delete):
        """Bir girdiyi ve ilgili arayüz bileşenini siler."""
        entry_to_remove = next((e for e in self.entries if e['widgets']['frame'] == frame_to_delete), None)
        if entry_to_remove:
            self.entries.remove(entry_to_remove)
            frame_to_delete.destroy()
            self.update_status("Girdi silindi. Değişiklikleri kaydetmeyi unutmayın.", "orange")

    def save_hosts_file(self):
        """Arayüzdeki güncel durumu hosts dosyasına yazar."""
        new_content = []
        try:
            for entry_data in self.entries:
                if entry_data.get('is_comment_or_empty', False):
                    new_content.append(entry_data['original_line'])
                else:
                    widgets = entry_data['widgets']
                    is_active = widgets['active_switch'].get() == 1
                    ip = widgets['ip_entry'].get().strip()
                    hostname = widgets['hostname_entry'].get().strip()

                    if ip and hostname:
                        line = f"{ip}\t{hostname}"
                        if not is_active:
                            line = f"# {line}"
                        new_content.append(line)
            
            with open(self.HOSTS_PATH, 'w', encoding='utf-8') as f:
                f.write("\n".join(new_content))
            
            self.update_status("Hosts dosyası başarıyla kaydedildi!", "green")
            self.load_hosts_file()

        except Exception as e:
            self.update_status(f"Hata: Dosya kaydedilemedi: {e}", "red")
            traceback.print_exc()

    def update_status(self, message, color):
        """Durum çubuğunu günceller."""
        self.status_label.configure(text=message, text_color=color)


if __name__ == "__main__":
    # Yüksek DPI ayarları
    if sys.platform.startswith('win'):
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    
    # Kodu çalıştırmadan önce kütüphanenin kurulu olduğundan emin olun
    try:
        import customtkinter as ctk
    except ImportError:
        print("Hata: customtkinter kütüphanesi bulunamadı.")
        print("Lütfen 'pip install customtkinter' komutu ile yükleyin.")
        sys.exit(1)
        
    ctk.set_appearance_mode("Dark") # Varsayılan tema
    
    # 1. Adım: Yönetici izinlerini kontrol et
    if not is_admin():
        show_admin_error_and_exit() # Hata penceresi göster ve çık

    # 2. Adım: Hosts dosyasının yolunu al
    HOSTS_PATH = get_hosts_path()
    if not HOSTS_PATH or not os.path.exists(HOSTS_PATH):
        # Bu pek olası değil ama yine de kontrol edelim
        print(f"Hata: Hosts dosyası bulunamadı: {HOSTS_PATH}")
        sys.exit(1)
        
    # 3. Adım: Her şey yolundaysa uygulamayı başlat
    app = HostsEditorApp(hosts_path=HOSTS_PATH)
    app.mainloop()
