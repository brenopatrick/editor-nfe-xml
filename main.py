
import customtkinter
import re
import xml.etree.ElementTree as ET
from tkinter import filedialog

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("Editor de NFe (XML)")
        self.geometry("850x700")
        self.configure(fg_color="#0f0f0f")

        # Configure theme
        customtkinter.set_appearance_mode("Dark")

        # Create tabs
        self.tab_view = customtkinter.CTkTabview(self, width=800, fg_color="#1a1a1a")
        self.tab_view.pack(padx=20, pady=(20, 5), fill="both", expand=True)

        self.dest_tab = self.tab_view.add("Dados do Destinatário")

        # --- Widgets for Destinatário Tab ---
        self.create_destinatario_widgets(self.dest_tab)

        # --- Buttons Frame ---
        self.button_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10, padx=20, fill="x")

        self.load_button = customtkinter.CTkButton(self.button_frame, text="Carregar XML", command=self.load_xml, fg_color="#ff6b9d", hover_color="#E8628D")
        self.load_button.pack(side="left", padx=10, pady=10)

        self.save_button = customtkinter.CTkButton(self.button_frame, text="Salvar XML", command=self.save_xml, fg_color="#ff6b9d", hover_color="#E8628D")
        self.save_button.pack(side="right", padx=10, pady=10)

    def create_destinatario_widgets(self, tab):
        # Define styles
        label_color = "#E0E0E0"
        entry_fg_color = "#2a2a2a"
        entry_border_color = "#ff6b9d"
        entry_text_color = "#E0E0E0"

        # Create a frame to hold the widgets
        frame = customtkinter.CTkFrame(tab, fg_color="transparent")
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- Fields ---
        fields = {
            "CNPJ": (0, 0), "xNome": (0, 2),
            "IE": (1, 0), "UF": (1, 2),
            "cMun": (2, 0), "xMun": (2, 2),
            "CEP": (3, 0), "xBairro": (3, 2),
            "xLgr": (4, 0), "cPais": (5, 0),
            "xPais": (5, 2), "fone": (6, 0)
        }
        
        field_labels = {
            "CNPJ": "CNPJ:", "xNome": "Nome/Razão Social:",
            "IE": "Inscrição Estadual:", "UF": "UF:",
            "cMun": "Código Município:", "xMun": "Município:",
            "CEP": "CEP:", "xBairro": "Bairro:",
            "xLgr": "Logradouro:", "cPais": "Código País:",
            "xPais": "País:", "fone": "Telefone:"
        }

        self.entries = {}

        for field, (row, col) in fields.items():
            label = customtkinter.CTkLabel(frame, text=field_labels[field], text_color=label_color)
            label.grid(row=row, column=col, padx=10, pady=10, sticky="w")
            
            entry = customtkinter.CTkEntry(frame, width=250, fg_color=entry_fg_color, 
                                           border_color=entry_border_color, text_color=entry_text_color)
            entry.grid(row=row, column=col + 1, padx=10, pady=10, sticky="ew")
            self.entries[field] = entry

        # Special validations
        self.entries["UF"].configure(validate="key", validatecommand=(self.register(self.validate_uf), "%P"))
        self.entries["IE"].configure(validate="key", validatecommand=(self.register(self.validate_ie), "%P"))

    def validate_uf(self, value):
        return len(value) <= 2

    def validate_ie(self, value):
        return bool(re.match("^[0-9]*$", value))

    def load_xml(self):
        file_path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not file_path:
            return

        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}

        dest_path = ".//nfe:infNFe/nfe:dest"
        dest = self.root.find(dest_path, ns)

        if dest is not None:
            for field, entry_widget in self.entries.items():
                # Clear previous content
                entry_widget.delete(0, "end")
                
                element = dest.find(f"nfe:{field}", ns)
                if element is not None:
                    entry_widget.insert(0, element.text)
                # Handle address fields inside 'enderDest'
                elif field in ["xLgr", "xBairro", "cMun", "xMun", "UF", "CEP", "cPais", "xPais", "fone"]:
                    ender_dest = dest.find("nfe:enderDest", ns)
                    if ender_dest is not None:
                        addr_element = ender_dest.find(f"nfe:{field}", ns)
                        if addr_element is not None:
                            entry_widget.insert(0, addr_element.text)

    def save_xml(self):
        if not hasattr(self, 'tree'):
            # TODO: Show a message box to the user
            print("Nenhum arquivo XML carregado.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".xml",
                                               filetypes=[("XML files", "*.xml")])
        if not file_path:
            return

        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        dest_path = ".//nfe:infNFe/nfe:dest"
        dest = self.root.find(dest_path, ns)

        if dest is None:
            # TODO: Show a message box to the user
            print("Elemento <dest> não encontrado no XML.")
            return

        ender_dest = dest.find("nfe:enderDest", ns)
        # Create enderDest if it doesn't exist and address fields need to be saved
        if ender_dest is None and any(field in ["xLgr", "xBairro", "cMun", "xMun", "UF", "CEP", "cPais", "xPais", "fone"] for field in self.entries):
            ender_dest = ET.SubElement(dest, f"{{{ns['nfe']}}}enderDest")

        for field, entry_widget in self.entries.items():
            new_value = entry_widget.get()
            parent = None
            element = None

            # Determine the correct parent element for the field
            if field in ["xLgr", "xBairro", "cMun", "xMun", "UF", "CEP", "cPais", "xPais", "fone"]:
                parent = ender_dest
            else:
                parent = dest

            if parent is not None:
                element = parent.find(f"nfe:{field}", ns)

                if element is not None:
                    element.text = new_value
                # If the element doesn't exist, create it, but only if there's a value.
                elif new_value:
                    new_element = ET.SubElement(parent, f"{{{ns['nfe']}}}{field}")
                    new_element.text = new_value
        
        # Register namespace to avoid ns0 prefixes in the output file
        ET.register_namespace('', ns['nfe'])
        self.tree.write(file_path, encoding='utf-8', xml_declaration=True)
        # TODO: Show a success message box
        print(f"Arquivo salvo com sucesso em: {file_path}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
