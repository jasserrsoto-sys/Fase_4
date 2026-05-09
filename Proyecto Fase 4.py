import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from abc import ABC, abstractmethod


# 1. MOTOR DEL SISTEMA (LOGS Y EXCEPCIONES)

class GestorLogs:
    archivo_log = "software_fj_eventos.log"

    @staticmethod
    def registrar(nivel, mensaje):
        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{fecha_hora}] [{nivel}] {mensaje}\n"
        try:
            with open(GestorLogs.archivo_log, "a", encoding="utf-8") as archivo:
                archivo.write(linea)
        except IOError as e:
            print(f"Error crítico al escribir log: {e}")

    @staticmethod
    def info(mensaje):
        GestorLogs.registrar("INFO", mensaje)

    @staticmethod
    def error(mensaje):
        GestorLogs.registrar("ERROR", mensaje)


class SoftwareFJError(Exception):
    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje
        GestorLogs.error(self.mensaje) # Auto-guarda en el log

class ValidacionClienteError(SoftwareFJError): pass
class ServicioInvalidoError(SoftwareFJError): pass
class ReservaError(SoftwareFJError): pass



# 2. MODELO DE ENTIDADES (POO)


class EntidadBase(ABC):
    def __init__(self, identificador):
        self._identificador = identificador

    @abstractmethod
    def obtener_info(self):
        pass

class Cliente(EntidadBase):
    def __init__(self, documento, nombre, email):
        super().__init__(documento)
        self.nombre = nombre  
        self.email = email
        GestorLogs.info(f"Cliente registrado: {self.nombre} ID: {self._identificador}")

    @property
    def nombre(self): return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) == 0:
            raise ValidacionClienteError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def email(self): return self._email

    @email.setter
    def email(self, valor):
        if "@" not in valor or "." not in valor:
            raise ValidacionClienteError(f"El correo '{valor}' no es válido.")
        self._email = valor.strip()

    def obtener_info(self):
        return f"{self.nombre} (ID: {self._identificador})"


class Servicio(EntidadBase):
    def __init__(self, codigo, nombre, precio_base):
        super().__init__(codigo)
        if precio_base < 0:
            raise ServicioInvalidoError("El precio base no puede ser negativo.")
        self._nombre = nombre
        self._precio_base = precio_base
        self._codigo = codigo
        GestorLogs.info(f"Servicio registrado: {self._nombre} Código: {self._codigo}")

    @abstractmethod
    def calcular_costo(self, cantidad=1, aplicar_impuesto=False):
        pass

class ServicioSala(Servicio):
    def __init__(self, codigo, nombre, precio_base, capacidad):
        super().__init__(codigo, nombre, precio_base)
        if capacidad <= 0:
            raise ServicioInvalidoError("La capacidad debe ser mayor a 0.")
        self._capacidad = capacidad

    def calcular_costo(self, horas=1, aplicar_impuesto=False):
        if horas <= 0: raise ServicioInvalidoError("Horas deben ser > 0.")
        costo = self._precio_base * horas
        if aplicar_impuesto: costo *= 1.19
        return costo

    def obtener_info(self):
        return f"[Sala] {self._nombre} (Cap: {self._capacidad})"

class ServicioEquipo(Servicio):
    def __init__(self, codigo, nombre, precio_base, requiere_deposito=True):
        super().__init__(codigo, nombre, precio_base)
        self._requiere_deposito = requiere_deposito

    def calcular_costo(self, dias=1, aplicar_impuesto=False):
        if dias <= 0: raise ServicioInvalidoError("Días deben ser > 0.")
        costo = self._precio_base * dias
        if self._requiere_deposito: costo += 50000
        if aplicar_impuesto: costo *= 1.19
        return costo

    def obtener_info(self):
        return f"[Equipo] {self._nombre} ${self._precio_base} {self._requiere_deposito and '(Depósito requerido)' or ''}"
class ServicioAsesoria(Servicio):
    def __init__(self, codigo, nombre, precio_base, consultor):
        super().__init__(codigo, nombre, precio_base)
        self._consultor = consultor

    def calcular_costo(self, sesiones=1, aplicar_impuesto=False):
        if sesiones <= 0: raise ServicioInvalidoError("Sesiones deben ser > 0.")
        costo = self._precio_base * sesiones
        if sesiones >= 3: costo *= 0.90 
        if aplicar_impuesto: costo *= 1.19
        return costo

    def obtener_info(self):
        return f"[Asesoría] {self._nombre} (Por: {self._consultor})"

class Reserva:
    def __init__(self, cliente, servicio, duracion, aplicar_impuesto=False):
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.aplicar_impuesto = aplicar_impuesto
        self.estado = "PENDIENTE"
        self.costo_total = 0.0
        GestorLogs.info(f"Reserva registrada: {self.cliente.nombre} servicio {self.servicio._nombre}")


    def confirmar(self):
        self.estado = "CONFIRMADA"

    def procesar(self):
        try:
            self.confirmar()
            self.costo_total = self.servicio.calcular_costo(self.duracion, self.aplicar_impuesto)
        except SoftwareFJError as e:
            self.estado = "ERROR_LOGICO"
            raise e # Relanzamos para que la interfaz gráfica lo atrape
        except Exception as e:
            self.estado = "ERROR_CRITICO"
            raise e
        else:
            return self.costo_total



# 3. INTERFAZ GRÁFICA

class InterfazSoftwareFJ:    
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - SIG")
        self.root.geometry("650x550+600+200")
        self.root.config(bg='white')
        self.root.resizable(False,False)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Arial", 10, "bold", "italic"), background="red3", foreground="white",borderwidth=0)
        style.map("TButton", background=[("active", "darkred")])
        style.configure("TLabel", font=("Arial", 10, "bold"), background="white", foreground="black")
        style.map("TEntry", bordercolor=[("focus", "red3")],lightcolor=[("focus", "red3")], darkcolor=[("focus", "red3")])
        style.configure("TNotebook", background="white", borderwidth=0),
        style.configure("TNotebook.Tab", background="white", foreground="black", font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "red3")], foreground=[("selected", "white")],padding=[("selected", 5)])
        style.configure("TFrame", background="white")
        style.configure("C.TCombobox", font=("Arial", 10), padding=2)
        style.map("C.TCombobox", fieldbackground=[("readonly", "white")], foreground=[("readonly", "black")], background=[("active", "red3")],bordercolor=[("focus", "red3")])
        self.root.option_add('*TCombobox*Listbox.font', ('Arial', 10))
        self.root.option_add('*TCombobox*Listbox.background', 'white')
        self.root.option_add('*TCombobox*Listbox.foreground', 'black')
        self.root.option_add('*TCombobox*Listbox.selectBackground', 'red3')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        style.configure("TCheckbutton", font=("Arial", 10), background="white", foreground="black", padding=2)
        style.map("TCheckbutton", background=[("focus", "white")])

        # Base de datos en memoria (Listas)
        self.lista_clientes = []
        self.lista_servicios = []
        
        # --- TÍTULO PRINCIPAL ---
        tk.Label(root, text="|========| SISTEMA INTEGRAL DE GESTION |========|", font=("Arial", 15, "bold", "italic"), bg="black", fg= "white").pack(fill="x", pady=10)

        # --- SISTEMA DE PESTAÑAS (Notebook) ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(padx=20, pady=5, fill="both", expand=True)

        self.tab_clientes = ttk.Frame(self.notebook)
        self.tab_servicios = ttk.Frame(self.notebook)
        self.tab_reservas = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_clientes, text="Clientes")
        self.notebook.add(self.tab_servicios, text="Servicios")
        self.notebook.add(self.tab_reservas, text="Reservas")

        self._construir_tab_clientes()
        self._construir_tab_servicios()
        self._construir_tab_reservas()

        # --- CONSOLA VISUAL (Listbox) ---
        ttk.Label(root, text="Historial de Operaciones:").pack(anchor="w", padx=20)
        self.listbox_logs = tk.Listbox(root, height=8, bg="#f0f0f0")
        self.listbox_logs.pack(padx=20, pady=5, fill="x")

    # --- PESTAÑA 1: CLIENTES ---
    def _construir_tab_clientes(self):
        
        frame = tk.LabelFrame(self.tab_clientes, text="Registrar Nuevo Cliente",bg="white",font=("Arial", 12, "bold"), padx=10, pady=10)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="Documento:").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_doc = ttk.Entry(frame,width=50,font=("Arial", 10))
        self.entry_doc.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_nom = ttk.Entry(frame,width=50,font=("Arial", 10))
        self.entry_nom.grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_email = ttk.Entry(frame,width=50,font=("Arial", 10))
        self.entry_email.grid(row=2, column=1, padx=5)

        ttk.Button(frame, text="Guardar Cliente", command=self.registrar_cliente,cursor="hand2").grid(row=3, column=0, columnspan=2, pady=10)

    # --- PESTAÑA 2: SERVICIOS ---
    def _construir_tab_servicios(self):
        frame = tk.LabelFrame(self.tab_servicios, text="Registrar Nuevo Servicio", bg="white", font=("Arial", 12, "bold"), padx=10, pady=10)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="Tipo de Servicio:").grid(row=0, column=0, sticky="e", pady=0)
        self.combo_tipo_serv = ttk.Combobox(frame, values=["Sala", "Equipo", "Asesoría"], state="readonly", style="C.TCombobox")
        self.combo_tipo_serv.current(0)
        self.combo_tipo_serv.grid(row=0, column=1, sticky="w", padx=5)
        self.combo_tipo_serv.bind("<<ComboboxSelected>>", self._actualizar_label_extra)

        ttk.Label(frame, text="Código:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_cod_serv = ttk.Entry(frame,style="C.TEntry",width=50)
        self.entry_cod_serv.grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="Nombre:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_nom_serv = ttk.Entry(frame,style="C.TEntry",width=50)
        self.entry_nom_serv.grid(row=2, column=1, padx=5)

        ttk.Label(frame, text="Precio Base ($):").grid(row=3, column=0, sticky="e", pady=5)
        self.entry_precio_serv = ttk.Entry(frame,style="C.TEntry",width=50)
        self.entry_precio_serv.grid(row=3, column=1, padx=5)

        self.label_extra = ttk.Label(frame, text="Capacidad:")
        self.label_extra.grid(row=4, column=0, sticky="e", pady=5)
        self.entry_extra_serv = ttk.Entry(frame,style="C.TEntry",width=50)
        self.entry_extra_serv.grid(row=4, column=1, padx=5)
        
        self.var_deposito = tk.BooleanVar() # Variable que guarda True o False
        self.check_deposito = ttk.Checkbutton(frame, text="Sí", variable=self.var_deposito)

        ttk.Button(frame, text="Guardar Servicio", command=self.registrar_servicio,cursor="hand2").grid(row=5, column=0, columnspan=2, pady=10)

    def _actualizar_label_extra(self, event):
        tipo = self.combo_tipo_serv.get()
        if tipo == "Sala": 
                self.label_extra.config(text="Capacidad:")
                self.check_deposito.grid_remove() # Oculta el checkbox
                self.entry_extra_serv.grid()      # Muestra la caja de texto
        elif tipo == "Equipo": 
                self.label_extra.config(text="Requiere Depósito:")
                self.entry_extra_serv.grid_remove() # Oculta la caja de texto
                self.check_deposito.grid(row=4, column=1, padx=5, sticky="w") # Muestra el checkbox
        elif tipo == "Asesoría": 
                self.label_extra.config(text="Nombre Consultor:")
                self.check_deposito.grid_remove() # Oculta el checkbox
                self.entry_extra_serv.grid()      # Muestra la caja de texto

    # --- PESTAÑA 3: RESERVAS ---
    def _construir_tab_reservas(self):
        frame = tk.LabelFrame(self.tab_reservas, text="Generar Reserva", bg="white", font=("Arial", 12, "bold"), padx=10, pady=10)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="Seleccionar Cliente:").grid(row=0, column=0, sticky="e", pady=5)
        self.combo_clientes = ttk.Combobox(frame, state="readonly", width=30,style="C.TCombobox")
        self.combo_clientes.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(frame, text="Seleccionar Servicio:").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_servicios = ttk.Combobox(frame, state="readonly", width=30,style="C.TCombobox")
        self.combo_servicios.grid(row=1, column=1, padx=5, sticky="w")

        ttk.Label(frame, text="Cantidad/Duración:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_duracion = ttk.Entry(frame,style="C.TEntry",width=50)
        self.entry_duracion.grid(row=2, column=1, padx=5)

        self.var_impuesto = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Aplicar 19% IVA", variable=self.var_impuesto,).grid(row=3, column=1, sticky="w")

        ttk.Button(frame, text="Procesar Reserva", command=self.procesar_reserva,cursor="hand2").grid(row=4, column=0, columnspan=2, pady=10)

    # --- FUNCIONES DE LÓGICA CON MANEJO DE EXCEPCIONES ---
    def registrar_cliente(self):
        try:
            doc = self.entry_doc.get()
            nom = self.entry_nom.get()
            correo = self.entry_email.get()
            
            # Instanciamos. Si los datos son malos, la clase lanzará la excepción
            nuevo_cliente = Cliente(doc, nom, correo)
            self.lista_clientes.append(nuevo_cliente)
            
            # Actualizamos la lista desplegable de reservas
            self.combo_clientes['values'] = [c.obtener_info() for c in self.lista_clientes]
            
            self._log_gui(f"✅ Cliente {nom} registrado. ID: {doc}")
           #messagebox.showinfo("Éxito", "Cliente guardado correctamente.")
            
        except SoftwareFJError as e:
            messagebox.showerror("Error de Validación", e.mensaje)

    def registrar_servicio(self):
        try:
            tipo = self.combo_tipo_serv.get()
            cod = self.entry_cod_serv.get()
            nom = self.entry_nom_serv.get()
            precio = float(self.entry_precio_serv.get())

            # Leemos el dato dinámico según la categoría elegida
            if tipo == "Sala":
                extra = self.entry_extra_serv.get()
                serv = ServicioSala(cod, nom, precio, int(extra))
            elif tipo == "Equipo":
                # Leemos directamente si el Checkbox está marcado (True/False)
                req_dep = self.var_deposito.get() 
                serv = ServicioEquipo(cod, nom, precio, req_dep)
            else:
                extra = self.entry_extra_serv.get()
                serv = ServicioAsesoria(cod, nom, precio, extra)

            self.lista_servicios.append(serv)
            self.combo_servicios['values'] = [s.obtener_info() for s in self.lista_servicios]
            
            self._log_gui(f"✅ Servicio '{nom}' registrado. Código: {cod} Tipo: {tipo} Precio: ${precio:,.0f}")
            #messagebox.showinfo("Éxito", "Servicio creado correctamente.")
            
            # Limpiar campos después de guardar
            self.entry_cod_serv.delete(0, tk.END)
            self.entry_nom_serv.delete(0, tk.END)
            self.entry_precio_serv.delete(0, tk.END)
            self.entry_extra_serv.delete(0, tk.END)
            self.var_deposito.set(False) # Desmarcar el checkbox
            
        except ValueError:
            messagebox.showerror("Error de Formato", "El precio y capacidades deben ser números.")
        except SoftwareFJError as e:
            messagebox.showerror("Error de Negocio", e.mensaje)

    def procesar_reserva(self):
        idx_cli = self.combo_clientes.current()
        idx_ser = self.combo_servicios.current()

        if idx_cli == -1 or idx_ser == -1:
            messagebox.showwarning("Faltan datos", "Debes seleccionar un cliente y un servicio.")
            return

        try:
            cliente_obj = self.lista_clientes[idx_cli]
            servicio_obj = self.lista_servicios[idx_ser]
            duracion = int(self.entry_duracion.get())
            impuesto = self.var_impuesto.get()

            reserva = Reserva(cliente_obj, servicio_obj, duracion, impuesto)
            costo_final = reserva.procesar()

            self._log_gui(f"💰 Reserva cobrada a {cliente_obj.nombre}: ${costo_final:,.0f}")
            messagebox.showinfo("Reserva Exitosa", f"=== RECIBO FJ ===\n\nCliente: {cliente_obj.nombre}\nServicio: {servicio_obj._nombre}\nTotal Pagado: ${costo_final:,.0f}")

        except ValueError:
            messagebox.showerror("Error", "La cantidad o duración debe ser un número entero.")
            self._log_gui("❌ Intento de reserva fallido por formato de texto.")
        except SoftwareFJError as e:
            messagebox.showerror("Error de Reserva", e.mensaje)
            self._log_gui(f"❌ Error en reserva: {e.mensaje}")

    def _log_gui(self, mensaje):
        """Imprime mensajes de éxito o error en la cajita blanca inferior."""
        self.listbox_logs.insert(tk.END, mensaje)
        self.listbox_logs.yview(tk.END) # Auto-scroll hacia abajo



# BLOQUE DE EJECUCIÓN

if __name__ == "__main__":
    ventana_principal = tk.Tk()
    app = InterfazSoftwareFJ(ventana_principal)
    ventana_principal.mainloop()