import customtkinter
import re
import xml.etree.ElementTree as ET
from tkinter import filedialog
from CTkMessagebox import CTkMessagebox
from PIL import Image
import os

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Editor de NFe (XML)")
        self.geometry("900x750")
        self.configure(fg_color="#0f0f0f")

        # Configure theme
        customtkinter.set_appearance_mode("Dark")

        # Load images
        image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")
        self.upload_icon = customtkinter.CTkImage(Image.open(os.path.join(image_path, "upload_icon.png")), size=(50, 50))
        self.download_icon = customtkinter.CTkImage(Image.open(os.path.join(image_path, "download_icon.png")), size=(20, 20))
        self.document_icon = customtkinter.CTkImage(Image.open(os.path.join(image_path, "document_icon.png")), size=(20, 20))
        self.cogwheel_icon = customtkinter.CTkImage(Image.open(os.path.join(image_path, "cogwheel_icon.png")), size=(20, 20))
        self.column_chart_icon = customtkinter.CTkImage(Image.open(os.path.join(image_path, "column_chart_icon.png")), size=(20, 20))

        # --- Top Section: Upload and Export ---
        self.top_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=20, padx=20, fill="x")

        # Upload Area
        self.upload_frame = customtkinter.CTkFrame(self.top_frame, fg_color="#1a1a1a", corner_radius=10, border_width=2, border_color="#ff6b9d")
        self.upload_frame.pack(side="left", padx=(0, 20), fill="both", expand=True)
        self.upload_frame.bind("<Button-1>", lambda e: self.load_xml())

        self.upload_icon_label = customtkinter.CTkLabel(self.upload_frame, text="", image=self.upload_icon)
        self.upload_icon_label.pack(pady=(20, 5))
        self.upload_icon_label.bind("<Button-1>", lambda e: self.load_xml())

        self.upload_main_text = customtkinter.CTkLabel(self.upload_frame, text="Carregar arquivo XML da NFe", font=customtkinter.CTkFont(size=16, weight="bold"), text_color="#E0E0E0")
        self.upload_main_text.pack()
        self.upload_main_text.bind("<Button-1>", lambda e: self.load_xml())

        self.upload_sub_text = customtkinter.CTkLabel(self.upload_frame, text="Clique aqui ou arraste o arquivo para esta área", text_color="#A0A0A0")
        self.upload_sub_text.pack()
        self.upload_sub_text.bind("<Button-1>", lambda e: self.load_xml())

        self.upload_format_text = customtkinter.CTkLabel(self.upload_frame, text="Formatos aceitos: .xml", text_color="#A0A0A0")
        self.upload_format_text.pack(pady=(5, 20))
        self.upload_format_text.bind("<Button-1>", lambda e: self.load_xml())

        # Export XML Button
        self.export_frame = customtkinter.CTkFrame(self.top_frame, fg_color="#1a1a1a", corner_radius=10)
        self.export_frame.pack(side="right", fill="both", expand=True)

        self.export_button = customtkinter.CTkButton(self.export_frame, text="Exportar XML", image=self.download_icon, compound="top", 
                                                     command=self.save_xml, fg_color="#ff6b9d", hover_color="#E8628D",
                                                     font=customtkinter.CTkFont(size=16, weight="bold"))
        self.export_button.pack(pady=20, padx=20, fill="both", expand=True)

        self.export_sub_text = customtkinter.CTkLabel(self.export_frame, text="Baixar arquivo editado", text_color="#A0A0A0")
        self.export_sub_text.pack(pady=(0, 20))

        # --- Tab Navigation ---
        self.tab_nav_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.tab_nav_frame.pack(pady=(0, 10), padx=20, fill="x")

        self.dest_tab_button = customtkinter.CTkButton(self.tab_nav_frame, text="Dados do Destinatário", image=self.document_icon, compound="left",
                                                      command=lambda: self.select_tab("destinatario"), fg_color="#ff6b9d", hover_color="#E8628D",
                                                      font=customtkinter.CTkFont(size=14, weight="bold"), corner_radius=0)
        self.dest_tab_button.pack(side="left", expand=True, fill="x")

        self.prod_serv_tab_button = customtkinter.CTkButton(self.tab_nav_frame, text="Produtos e Serviços", image=self.cogwheel_icon, compound="left",
                                                          command=lambda: self.select_tab("produtos_servicos"), fg_color="#2a2a2a", hover_color="#3a3a3a",
                                                          font=customtkinter.CTkFont(size=14, weight="bold"), corner_radius=0)
        self.prod_serv_tab_button.pack(side="left", expand=True, fill="x")

        self.totais_tab_button = customtkinter.CTkButton(self.tab_nav_frame, text="Totais", image=self.column_chart_icon, compound="left",
                                                       command=lambda: self.select_tab("totais"), fg_color="#2a2a2a", hover_color="#3a3a3a",
                                                       font=customtkinter.CTkFont(size=14, weight="bold"), corner_radius=0)
        self.totais_tab_button.pack(side="left", expand=True, fill="x")

        # --- Content Area ---
        self.content_frame = customtkinter.CTkFrame(self, fg_color="#1a1a1a", corner_radius=10)
        self.content_frame.pack(pady=(0, 20), padx=20, fill="both", expand=True)

        # Tab Content Frames
        self.dest_tab_content = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")
        self.prod_serv_tab_content = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")
        self.totais_tab_content = customtkinter.CTkFrame(self.content_frame, fg_color="transparent")

        # --- Widgets for Destinatário Tab ---
        self.create_destinatario_widgets(self.dest_tab_content)

        # Initial tab selection
        self.select_tab("destinatario")

    def select_tab(self, name):
        # Hide all tab contents
        self.dest_tab_content.pack_forget()
        self.prod_serv_tab_content.pack_forget()
        self.totais_tab_content.pack_forget()

        # Reset button colors
        self.dest_tab_button.configure(fg_color="#2a2a2a", hover_color="#3a3a3a")
        self.prod_serv_tab_button.configure(fg_color="#2a2a2a", hover_color="#3a3a3a")
        self.totais_tab_button.configure(fg_color="#2a2a2a", hover_color="#3a3a3a")

        # Show selected tab content and highlight button
        if name == "destinatario":
            self.dest_tab_content.pack(fill="both", expand=True)
            self.dest_tab_button.configure(fg_color="#ff6b9d", hover_color="#E8628D")
        elif name == "produtos_servicos":
            self.prod_serv_tab_content.pack(fill="both", expand=True)
            self.prod_serv_tab_button.configure(fg_color="#ff6b9d", hover_color="#E8628D")
        elif name == "totais":
            self.totais_tab_content.pack(fill="both", expand=True)
            self.totais_tab_button.configure(fg_color="#ff6b9d", hover_color="#E8628D")

    def create_destinatario_widgets(self, tab_content_frame):
        # Define styles
        label_color = "#E0E0E0"
        entry_fg_color = "#2a2a2a"
        entry_border_color = "#ff6b9d"
        entry_text_color = "#E0E0E0"

        # --- Identificação da Empresa ---
        id_frame = customtkinter.CTkFrame(tab_content_frame, fg_color="transparent")
        id_frame.pack(padx=20, pady=(20, 10), fill="x")
        customtkinter.CTkLabel(id_frame, text="# Identificação da Empresa", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#ff6b9d").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        fields_id = {
            "CNPJ": (1, 0), "xNome": (1, 2),
            "IE": (2, 0), "UF": (2, 2),
            "cMun": (3, 0)
        }
        field_labels_id = {
            "CNPJ": "CNPJ:", "xNome": "Nome/Razão Social:",
            "IE": "Inscrição Estadual:", "UF": "UF:",
            "cMun": "Código Município:"
        }

        self.entries = {}
        for field, (row, col) in fields_id.items():
            label = customtkinter.CTkLabel(id_frame, text=field_labels_id[field], text_color=label_color)
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = customtkinter.CTkEntry(id_frame, width=250, fg_color=entry_fg_color, border_color=entry_border_color, text_color=entry_text_color)
            entry.grid(row=row, column=col + 1, padx=10, pady=5, sticky="ew")
            self.entries[field] = entry

        # Special validations
        self.entries["UF"].configure(validate="key", validatecommand=(self.register(self.validate_uf), "%P"))
        self.entries["IE"].configure(validate="key", validatecommand=(self.register(self.validate_ie), "%P"))

        # --- Localização Endereço ---
        loc_frame = customtkinter.CTkFrame(tab_content_frame, fg_color="transparent")
        loc_frame.pack(padx=20, pady=(10, 10), fill="x")
        customtkinter.CTkLabel(loc_frame, text="# Localização Endereço", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#ff6b9d").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        fields_loc = {
            "xMun": (1, 0), "CEP": (1, 2),
            "xBairro": (2, 0), "xLgr": (2, 2)
        }
        field_labels_loc = {
            "xMun": "Município:", "CEP": "CEP:",
            "xBairro": "Bairro:", "xLgr": "Logradouro:"
        }

        for field, (row, col) in fields_loc.items():
            label = customtkinter.CTkLabel(loc_frame, text=field_labels_loc[field], text_color=label_color)
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = customtkinter.CTkEntry(loc_frame, width=250, fg_color=entry_fg_color, border_color=entry_border_color, text_color=entry_text_color)
            entry.grid(row=row, column=col + 1, padx=10, pady=5, sticky="ew")
            self.entries[field] = entry

        # --- Telefone Informações Adicionais ---
        tel_frame = customtkinter.CTkFrame(tab_content_frame, fg_color="transparent")
        tel_frame.pack(padx=20, pady=(10, 20), fill="x")
        customtkinter.CTkLabel(tel_frame, text="# Telefone Informações Adicionais", font=customtkinter.CTkFont(size=14, weight="bold"), text_color="#ff6b9d").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        fields_tel = {
            "cPais": (1, 0), "xPais": (1, 2),
            "fone": (2, 0)
        }
        field_labels_tel = {
            "cPais": "Código País:", "xPais": "País:",
            "fone": "Telefone:"
        }

        for field, (row, col) in fields_tel.items():
            label = customtkinter.CTkLabel(tel_frame, text=field_labels_tel[field], text_color=label_color)
            label.grid(row=row, column=col, padx=10, pady=5, sticky="w")
            entry = customtkinter.CTkEntry(tel_frame, width=250, fg_color=entry_fg_color, border_color=entry_border_color, text_color=entry_text_color)
            entry.grid(row=row, column=col + 1, padx=10, pady=5, sticky="ew")
            self.entries[field] = entry

    def validate_uf(self, value):
        return len(value) <= 2

    def validate_ie(self, value):
        return bool(re.match("^[0-9]*$", value))

    def load_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not file_path:
            return
        try:
            self.tree = ET.parse(file_path)
            self.root = self.tree.getroot()
            
            ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

            dest_path = ".//nfe:infNFe/nfe:dest"
            dest = self.root.find(dest_path, ns)

            if dest is not None:
                for field, entry_widget in self.entries.items():
                    entry_widget.delete(0, "end")
                    
                    element = dest.find(f"nfe:{field}", ns)
                    if element is not None:
                        entry_widget.insert(0, element.text)
                    elif field in ["xLgr", "xBairro", "cMun", "xMun", "UF", "CEP", "cPais", "xPais", "fone"]:
                        ender_dest = dest.find("nfe:enderDest", ns)
                        if ender_dest is not None:
                            addr_element = ender_dest.find(f"nfe:{field}", ns)
                            if addr_element is not None:
                                entry_widget.insert(0, addr_element.text)
                CTkMessagebox(title="Sucesso", message="XML carregado com sucesso!", icon="check", option_1="OK")
            else:
                CTkMessagebox(title="Erro", message="O XML não contém a tag <dest> ou não é uma NFe válida.", icon="cancel")
        except ET.ParseError:
            CTkMessagebox(title="Erro", message="Arquivo XML inválido ou corrompido.", icon="cancel")

    def save_xml(self):
        if not hasattr(self, 'tree'):
            CTkMessagebox(title="Aviso", message="Nenhum arquivo XML foi carregado. Carregue um arquivo antes de salvar.", icon="warning", option_1="OK")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")])
        if not file_path:
            return

        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        dest_path = ".//nfe:infNFe/nfe:dest"
        dest = self.root.find(dest_path, ns)

        if dest is None:
            CTkMessagebox(title="Erro", message="Elemento <dest> não encontrado no XML. Não é possível salvar.", icon="cancel")
            return

        ender_dest = dest.find("nfe:enderDest", ns)
        if ender_dest is None and any(field in ["xLgr", "xBairro", "cMun", "xMun", "UF", "CEP", "cPais", "xPais", "fone"] for field in self.entries):
            ender_dest = ET.SubElement(dest, f"{{{ns['nfe']}}}enderDest")

        for field, entry_widget in self.entries.items():
            new_value = entry_widget.get()
            parent = ender_dest if field in ["xLgr", "xBairro", "cMun", "xMun", "UF", "CEP", "cPais", "xPais", "fone"] else dest

            if parent is not None:
                element = parent.find(f"nfe:{field}", ns)
                if element is not None:
                    element.text = new_value
                elif new_value:
                    new_element = ET.SubElement(parent, f"{{{ns['nfe']}}}{field}")
                    new_element.text = new_value
        
        ET.register_namespace('', ns['nfe'])
        self.tree.write(file_path, encoding='utf-8', xml_declaration=True)
        CTkMessagebox(title="Sucesso", message=f"Arquivo salvo com sucesso em:\n{file_path}", icon="check", option_1="OK")

if __name__ == "__main__":
    app = App()
    app.mainloop()