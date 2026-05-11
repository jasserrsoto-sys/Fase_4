# Proyecto Fase 4_Grupo 325 - SIG (Sistema Integral de Gestión)
# Desarrollado por: Jasson Serrano (líder), Jazmin Saavedra


import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from abc import ABC, abstractmethod

# LOGS Y EXCEPCIONES AL REGISTRAR EL CLIENTE O SERVICIO, O AL PROCESAR LA RESERVA

class GestorLogs:
    archivo_log = "Log_eventos.log"

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


class SIGError(Exception):
    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje
        GestorLogs.error(self.mensaje) # Auto-guarda en el log

class ValidacionClienteError(SIGError): pass
class ServicioInvalidoError(SIGError): pass
class ReservaError(SIGError): pass

# CLASES DE CLIENTES, SERVICIOS Y RESERVAS

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
        self.documento = documento
        GestorLogs.info(f"Cliente registrado: {self.nombre} ID: {self.documento}")

    @property
    def documento(self): return self._documento

    @documento.setter
    def documento(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) == 0:
            raise ValidacionClienteError("El documento no puede estar vacío.")
        self._documento = valor.strip()
        
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
        deposito_texto = "(Depósito requerido)" if self._requiere_deposito else ""
        return f"[Equipo] {self._nombre} ${self._precio_base} {deposito_texto}"

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
        except SIGError as e:
            self.estado = "ERROR_LOGICO"
            raise e # Relanzamos para que la interfaz gráfica lo atrape
        except Exception as e:
            self.estado = "ERROR_CRITICO"
            raise e
        else:
            return self.costo_total

# INTERFAZ GRÁFICA CON TKINTER

class SIGFront:    
    def __init__(self, root):
        self.root = root
        self.root.title("Software FJ - SIG")
        self.root.geometry("650x550+600+200")
        self.root.config(bg='white')
        self.root.resizable(False,False)
        #Aplicacion de Estilos Personalizados
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Montserrat", 10, "bold", "italic"), background="red3", foreground="white",borderwidth=0)
        style.map("TButton", background=[("active", "darkred")])
        style.configure("TLabel", font=("Montserrat", 10, "bold"), background="white", foreground="black")
        style.map("TEntry", bordercolor=[("focus", "red3")],lightcolor=[("focus", "red3")], darkcolor=[("focus", "red3")])
        style.configure("TNotebook", background="white", borderwidth=0)
        style.configure("TNotebook.Tab", background="white", foreground="black", font=("Montserrat", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "red3")], foreground=[("selected", "white")],padding=[("selected", 5)])
        style.configure("TFrame", background="white")
        style.configure("C.TCombobox", font=("Montserrat", 10), padding=2)
        style.map("C.TCombobox", fieldbackground=[("readonly", "white")], foreground=[("readonly", "black")], background=[("active", "red3")],bordercolor=[("focus", "red3")])
        self.root.option_add('*TCombobox*Listbox.font', ('Montserrat', 10))
        self.root.option_add('*TCombobox*Listbox.background', 'white')
        self.root.option_add('*TCombobox*Listbox.foreground', 'black')
        self.root.option_add('*TCombobox*Listbox.selectBackground', 'red3')
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        style.configure("TCheckbutton", font=("Montserrat", 10), background="white", foreground="black", padding=2)
        style.map("TCheckbutton", background=[("focus", "white")])

        # Listas para almacenar clientes y servicios registrados
        self.lista_clientes = []
        self.lista_servicios = []
        
        tk.Label(root, text="|========| SISTEMA INTEGRAL DE GESTION |========|", font=("Montserrat", 15, "bold", "italic"), bg="black", fg= "white").pack(fill="x", pady=10)

        # SISTEMA DE PESTAÑAS CON NOTEBOOK
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

        # LISTBOX PARA MOSTRAR HISTORIAL DE OPERACIONES
        ttk.Label(root, text="Historial de Operaciones:").pack(anchor="w", padx=20)
        self.listbox_logs = tk.Listbox(root, height=8, bg="#f0f0f0")
        self.listbox_logs.pack(padx=20, pady=5, fill="x")

    # PESTAÑA 1: CLIENTES
    def _construir_tab_clientes(self):
        
        frame = tk.LabelFrame(self.tab_clientes, text="Registrar Nuevo Cliente",bg="white",font=("Montserrat", 12, "bold"), padx=10, pady=10)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="Documento:").grid(row=0, column=0, sticky="e", pady=5)
        self.entry_doc = ttk.Entry(frame,width=50,font=("Montserrat", 10))
        self.entry_doc.grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_nom = ttk.Entry(frame,width=50,font=("Montserrat", 10))
        self.entry_nom.grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="Email:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_email = ttk.Entry(frame,width=50,font=("Montserrat", 10))
        self.entry_email.grid(row=2, column=1, padx=5)

        ttk.Button(frame, text="Guardar Cliente", command=self.registrar_cliente,cursor="hand2").grid(row=3, column=0, columnspan=2, pady=10)

    # PESTAÑA 2: SERVICIOS
    def _construir_tab_servicios(self):
        frame = tk.LabelFrame(self.tab_servicios, text="Registrar Nuevo Servicio", bg="white", font=("Montserrat", 12, "bold"), padx=10, pady=10)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="Tipo de Servicio:").grid(row=0, column=0, sticky="e", pady=0)
        self.combo_tipo_serv = ttk.Combobox(frame, values=["Sala", "Equipo", "Asesoría"], state="readonly", style="C.TCombobox")        
        self.combo_tipo_serv.grid(row=0, column=1, sticky="w", padx=5)
        self.combo_tipo_serv.bind("<<ComboboxSelected>>", self._actualizar_label_extra)

        ttk.Label(frame, text="Código:").grid(row=1, column=0, sticky="e", pady=5)
        self.entry_cod_serv = ttk.Entry(frame, style="C.TEntry", width=50)
        self.entry_cod_serv.grid(row=1, column=1, padx=5)

        ttk.Label(frame, text="Nombre:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_nom_serv = ttk.Entry(frame, style="C.TEntry", width=50)
        self.entry_nom_serv.grid(row=2, column=1, padx=5)

        ttk.Label(frame, text="Precio Base ($):").grid(row=3, column=0, sticky="e", pady=5)
        self.entry_precio_serv = ttk.Entry(frame, style="C.TEntry", width=50)
        self.entry_precio_serv.grid(row=3, column=1, padx=5)

        self.label_extra = ttk.Label(frame, text="Capacidad:")
        self.label_extra.grid(row=4, column=0, sticky="e", pady=5)
        self.entry_extra_serv = ttk.Entry(frame, style="C.TEntry", width=50)
        self.entry_extra_serv.grid(row=4, column=1, padx=5)
        
        self.var_deposito = tk.BooleanVar() # Variable que guarda True o False
        self.check_deposito = ttk.Checkbutton(frame, text="Sí", variable=self.var_deposito)
        self.check_deposito.grid(row=4, column=1, padx=5, sticky="w")
        self.check_deposito.grid_remove()

        ttk.Button(frame, text="Guardar Servicio", command=self.registrar_servicio,cursor="hand2").grid(row=5, column=0, columnspan=2, pady=10)

    # Función que actualiza el label y el campo extra según el tipo de servicio seleccionado
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
        if not tipo:
            messagebox.showerror("Error", "Debes seleccionar un tipo de servicio")
        return
    
    # PESTAÑA 3: RESERVAS
    def _construir_tab_reservas(self):
        frame = tk.LabelFrame(self.tab_reservas, text="Generar Reserva", bg="white", font=("Montserrat", 12, "bold"), padx=10, pady=10)
        frame.pack(padx=20, pady=20, fill="x")

        ttk.Label(frame, text="Seleccionar Cliente:").grid(row=0, column=0, sticky="e", pady=5)
        self.combo_clientes = ttk.Combobox(frame, state="readonly", width=30,style="C.TCombobox")
        self.combo_clientes.grid(row=0, column=1, padx=5, sticky="w")

        ttk.Label(frame, text="Seleccionar Servicio:").grid(row=1, column=0, sticky="e", pady=5)
        self.combo_servicios = ttk.Combobox(frame, state="readonly", width=30,style="C.TCombobox")
        self.combo_servicios.grid(row=1, column=1, padx=5, sticky="w")

        ttk.Label(frame, text="Cantidad/Duración:").grid(row=2, column=0, sticky="e", pady=5)
        self.entry_duracion = ttk.Entry(frame, style="C.TEntry", width=50)
        self.entry_duracion.grid(row=2, column=1, padx=5)

        self.var_impuesto = tk.BooleanVar()
        ttk.Checkbutton(frame, text="Aplicar 19% IVA", variable=self.var_impuesto,).grid(row=3, column=1, sticky="w")

        ttk.Button(frame, text="Procesar Reserva", command=self.procesar_reserva,cursor="hand2").grid(row=4, column=0, columnspan=2, pady=10)

    # FUNCIONES DE LÓGICA CON MANEJO DE EXCEPCIONES
    def registrar_cliente(self):
        try:
            doc = self.entry_doc.get()
            nom = self.entry_nom.get()
            correo = self.entry_email.get()            

            if not doc or not nom or not correo:
                messagebox.showerror("Error", "Todos los campos son obligatorios")
                return
            
            if any(c.documento == doc for c in self.lista_clientes):
                messagebox.showwarning("Advertencia", 
                    "Ya existe un cliente con este documento")
                return 
            
            nuevo_cliente = Cliente(doc, nom, correo)
            self.lista_clientes.append(nuevo_cliente)
            
            self.combo_clientes['values'] = [c.obtener_info() for c in self.lista_clientes]
            
            self._log_gui(f"Cliente {nom} registrado. ID: {doc}")
           
            # Limpiar campos después de guardar
            self.entry_doc.delete(0, tk.END)
            self.entry_nom.delete(0, tk.END)
            self.entry_email.delete(0, tk.END)
            
        except ValueError:
            msg = "Error en el Registro del Cliente"
            messagebox.showerror("Error de Formato", msg)            
        
        except SIGError as e:
            messagebox.showerror("Error de Validación", e.mensaje)
            self._log_gui(f"Error Cliente: {e.mensaje}")

    def registrar_servicio(self):
        try:
            tipo = self.combo_tipo_serv.get()
            cod = self.entry_cod_serv.get()
            nom = self.entry_nom_serv.get()
            precio = float(self.entry_precio_serv.get())

            if not tipo:                                                                   #Validación de selección
                messagebox.showerror("Error", "Debes seleccionar un tipo de servicio")
                return
            
            if not cod or not nom:                                                         #Validación de campos vacíos
                messagebox.showerror("Error", "Código y nombre son obligatorios")
                return
            
            if any(s.codigo == cod for s in self.lista_servicios):                         #Validación de duplicados de código
                messagebox.showwarning("Advertencia", 
                    "Ya existe un servicio con este código")
                return
            
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
            
            self._log_gui(f"Servicio '{nom}' registrado. Código: {cod} Tipo: {tipo} Precio: ${precio:,.0f}")
          
            # Limpiar campos después de guardar
            self.entry_cod_serv.delete(0, tk.END)
            self.entry_nom_serv.delete(0, tk.END)
            self.entry_precio_serv.delete(0, tk.END)
            self.entry_extra_serv.delete(0, tk.END)
            self.var_deposito.set(False)
            
        except ValueError:
            msg = "El precio y capacidades deben ser números o no pueden estar vacíos."
            messagebox.showerror("Error de Formato", msg)
            GestorLogs.error(msg) # Se guarda en el .log
            self._log_gui("Error de formato al registrar servicio.")
        except SIGError as e:
            messagebox.showerror("Error", e.mensaje)
            self._log_gui(f"Error servicio: {e.mensaje}")

    def procesar_reserva(self):
        idx_cli = self.combo_clientes.current()
        idx_ser = self.combo_servicios.current()

        if idx_cli == -1 or idx_ser == -1:
            msg = "Intento de reserva sin seleccionar cliente o servicio."
            messagebox.showwarning("Faltan datos", "Debes seleccionar un cliente y un servicio.")
            GestorLogs.error(msg) # Se guarda en el .log
            self._log_gui("Error: Faltan datos para la reserva.")
            return

        try:
            duracion_str = self.entry_duracion.get().strip()
            if not duracion_str:
                messagebox.showerror("Error", "Ingresa la cantidad o duración")
                return
            
            cliente_obj = self.lista_clientes[idx_cli]
            servicio_obj = self.lista_servicios[idx_ser]
            duracion = int(self.entry_duracion.get())
            impuesto = self.var_impuesto.get() 
            
            reserva = Reserva(cliente_obj, servicio_obj, duracion, impuesto)
            costo_final = reserva.procesar()

            self._log_gui(f"Reserva cobrada a {cliente_obj.nombre}: ${costo_final:,.0f}")
            messagebox.showinfo("Reserva Exitosa", f"=== Reserva Procesada ===\n\nCliente: {cliente_obj.nombre}\nServicio: {servicio_obj._nombre}\nTotal Pagado: ${costo_final:,.0f}")
            
            # Limpiar campos después de guardar
            self.combo_clientes.set('') 
            self.combo_servicios.set('')
            self.entry_duracion.delete(0, tk.END) 
            self.var_impuesto.set(False)

        except ValueError:
            msg = "La cantidad o duración debe ser un número entero."
            messagebox.showerror("Error", msg)
            GestorLogs.error(f"Fallo de interfaz (Reserva): {msg}")
            self._log_gui("Intento de reserva fallido por formato de texto.")
        except SIGError as e:
            messagebox.showerror("Error de Reserva", e.mensaje)
            self._log_gui(f"Error en reserva: {e.mensaje}")
            
    # FUNCION PARA MOSTRAR LOS LOGS EN LA INTERFAZ GRÁFICA
    def _log_gui(self, mensaje):        
        self.listbox_logs.insert(tk.END, mensaje)
        self.listbox_logs.yview(tk.END) # Auto-scroll hacia abajo

# BLOQUE DE EJECUCIÓN
if __name__ == "__main__":
    ventana_principal = tk.Tk()
    app = SIGFront(ventana_principal)
    ventana_principal.mainloop()
