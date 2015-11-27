#
# Elaborado por:
#    Oswaldo A. Jimenez 10-10368
#    Rebeca Machado     10-10406
#

class miVariable:
    def __init__(self,tipo,estaInicializada=0,valorAsignado=None):
        self.tipo             = tipo
        self.estaInicializada = estaInicializada
        self.valorAsignado    = valorAsignado
        
    def __repr__(self):
        string = 'Tipo=%s | Ini=%s | Valor=%s' % (self.tipo,self.estaInicializada,self.valorAsignado)
        return string
        

class SymTable:

    # Creacion del una tabla de simbolos vacia usando un diccionario
    # como tipo abstracto de datos para el almacenamiento de las variables
    def new(self):
        self.TablaAnterior  = None
        self.TablaFor       = {}
        self.TablaVariables = {}

#------------------------------------------------------------------ Modificacion
    # Metodo que inserta una nueva variable en el diccionario de simbolos
    def insert(self,nombre,tipo,estaInicializada=0,valorAsignado=None):
        exists = self.isMember(nombre)
        if not exists:
           estadoVar = miVariable(tipo,estaInicializada,valorAsignado)
           self.TablaVariables[nombre] = estadoVar
           
    # Metodo que inserta una nueva variable de iteracion en la tabla
    def insertFor(self,nombre,tipo,estaInicializada=0,valorAsignado=None):
        exists = self.isMemberFor(nombre)
        if not exists:
           estadoVar = miVariable(tipo,estaInicializada,valorAsignado)
           self.TablaFor[nombre] = estadoVar
        
    # Devuelve una copia exacta de una tabla pasada como parametro
    def copy(self,tabla):
        if tabla:
            self.TablaAnterior = tabla.TablaAnterior
            for var,value in tabla.TablaVariables.items():
                self.insert(var,value.tipo,value.estaInicializada,value.valorAsignado)
            self.copyFor(tabla.TablaFor)
    
    # Devuelve una copia exacta de la tabla de variables de iteracion
    def copyFor(self,tabla):
        for var,value in tabla.items():
            self.insertFor(var,value.tipo,value.estaInicializada,value.valorAsignado)
    
    # Elimina de una variable dentro de la tabla de simbolos   
    def delete(self,var):        
        if self.isMember(var):
            del self.TablaVariables[var]
        
    # Elimina variables de iteracion de la tabla de variables de iteracion
    def deleteFor(self,var):
        if self.isMemberFor(var):
            del self.TablaFor[var]
            
    # Modifica el valor de una variable contenida en la tabla actual. Si no se
    # encuentra, se busca en los padres
    def update_Inicializacion(self,var,inicializada):
    
        if self.isMemberLoop(var):
           current = self
        if current and current.TablaFor:
            if current.isMemberFor(var):
                current.TablaFor[var].estaInicializada=inicializada
                return
        while (current is not None) and (current.TablaVariables is not None):
            currentTabla = current.TablaVariables
            for currentVar,value in currentTabla.items():
                if (currentVar == var):
                    current.TablaVariables[var].estaInicializada=inicializada   
                    return
            current = current.TablaAnterior

    def update_Valor(self,var,valor):
        if self.isMemberLoop(var):
           current = self
        if current and current.TablaFor:
            if current.isMemberFor(var):
                current.TablaFor[var].valorAsignado=valor
                return
        while (current is not None) and (current.TablaVariables is not None):
            currentTabla = current.TablaVariables
            for currentVar,value in currentTabla.items():
                if (currentVar == var):
                    current.TablaVariables[var].valorAsignado=valor
                    return
            current = current.TablaAnterior
    
    # Asigna Tabla anterior     
    def setTablaAnterior(self,Tabla):
        self.TablaAnterior = Tabla
        
        
#---------------------------------------------------------------------- Consulta
    # Determina si una variable pertenece o no a la tabla de simbolos
    def isMember(self,var):
        return var in self.TablaVariables
    
    # Determina si una variable pertenece a la tablaFor
    def isMemberFor(self,var):
        return var in self.TablaFor

    # Verifica en forma iterativa que una variable pertenezca a la tabla de
    # de simbolos y a sus tablas anteriores
    def isMemberLoop(self,var):
        declarada = False
        currentTabla = self
        while currentTabla and not declarada:
            declarada = currentTabla.isMember(var) or currentTabla.isMemberFor(var)
            currentTabla = currentTabla.TablaAnterior
        return declarada
                
    # Devuelve la informacion asociada a la variable buscada en el diccionario
    def find(self,var):
        for currentVar,value in self.TablaVariables.items():
            if (currentVar == var):
                return currentVar,value
                
    # Devuelve la informacion encontrada en la tabla de simbolos propia y las
    # anteriores
    def findLoop(self,var):        
        current = self
        
        # Si es miembro de la tabla for, devuelve
        if current and current.TablaFor:
            if current.isMemberFor(var):
                return current.TablaFor[var]
                
        while (current is not None) and (current.TablaVariables is not None):
            currentTabla = current.TablaVariables
            for currentVar,value in currentTabla.items():
                if (currentVar == var):
                    return value
            if current.isMemberFor(var):
                return current.TablaFor[var]
            current = current.TablaAnterior
        