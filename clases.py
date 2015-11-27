#
# Elaborado por:
#    Oswaldo A. Jimenez 10-10368
#    Rebeca Machado     10-10406
#

import SymTable as SymbolTable
import sys
import re

global error
error = False

#******************************************************************************#
#-----------------------------------Clases-------------------------------------#
#******************************************************************************#

# Procedimiento que calcula la columna de un token en una produccion, respecto
# al archivo de entrada
def calcularColumna(file,pos):
    newline = file.rfind('\n',0,pos)
    if (newline < 0):
            newline = 0          
    numColumna = (pos - newline)
    return numColumna


# Procedimiento que determina si un valor excede los 32 bits de representacion
# Retorna true si produce un desbordamento (si sobrepasa los 32 bits), false
# en caso contrario
def hayOverflow(miNumero):
    return ((miNumero > sys.maxint) or (miNumero < (-sys.maxint - 1)))
    
#******************************* Terminales ***********************************#
# Super clase de constante_entera, constante_booleana y cadena
class terminal:
    def __init__(self,valor):
        self.valor = valor
        self.Tabla = None

    def setTable(self,tabla):
        self.Tabla = tabla
        
    def toString_2(self):
      return "%s" %(self.valor)         
    
#----------------------------------------------------- Constantes enteras NUMBER
class constante_entera(terminal):
    def toString(self):
        return "el valor \"%s\"" %(self.valor)
        
    def getTipo(self):
        return 'int'
        
    def evaluar(self):
        return self.valor    
        
#---------------------------------------------------------- Constantes booleanas
class constante_booleana(terminal):
    def toString(self):
        return "el valor \"%s\"" %(self.valor)
        
    def getTipo(self):
        return 'bool'

    def evaluar(self):
        return (self.valor == 'true')
        
#---------------------------------------------------------------- Cadenas STRING
class constante_cadena(terminal):
    def getTipo(self):
        pass      
    
    #Retorna el valor de la constante cadena
    def evaluar(self):
        t = self.valor[1:-1]
        t = t.replace("\\\\","\\")
        t = t.replace("\\\"","\"")
        t = t.replace("\\n","\n")
        return t

        
#******************************* Variables ID *********************************#
class variable:
    def __init__(self,valor,p):
        self.valor = valor
        self.Tabla = None
        self.linea = p.lineno(1)
        self.pos   = p.lexpos(1)
        
    def toString(self):
        return "la variable \"%s\"" %(self.valor)   
        
    def toString_2(self):
       return "%s" %(self.valor)       
        
    def setTable(self,tabla):
        self.Tabla = tabla
        if not tabla.isMemberLoop(self.valor):
            print "Error en linea %i, columna %i: no puede usar la variable \"%s\" pues no ha sido declarada." % (self.linea,calcularColumna(data,self.pos),self.valor)
            global error
            error = True
            
    def getTipo(self):
        if self.Tabla:
            estaInicializada = 0
            tipo = ''
            infoVar = self.Tabla.findLoop(self.valor)
            if infoVar:
                tipo = infoVar.tipo 
                estaInicializada = infoVar.estaInicializada
            else:
                if self.Tabla.TablaFor:
                    estaInicializada = self.Tabla.isMemberFor(self.valor)
                    tipo = 'int'
                    
            return tipo

    #retorna el valor indicado en la tabla de simbolos de la variable
    def evaluar(self):
        infoVar = self.Tabla.findLoop(self.valor)
        
        if infoVar.valorAsignado is None:
           print "Error en linea %i, columna %i: no puede usar la variable \"%s\" pues no ha sido inicializada" %(self.linea,calcularColumna(data,self.pos),self.valor)
           #Se aborta la ejecucion del programa
           sys.exit()
           
        return infoVar.valorAsignado



#********************************** Rango *************************************#

#-------------------------------------------------------------- Estructura Rango
# Implementa el tipo abstracto de dato Range
class Range:
    def __init__(self,cotaInferior,cotaSuperior):
        self.cotaInferior = cotaInferior
        self.cotaSuperior = cotaSuperior
    
    #Representacion ASCII de una instancia Range
    def __repr__(self):
        return "%s..%s" %(self.cotaInferior,self.cotaSuperior)
               
               
               
#******************************* Input_Output *********************************#

#-------------------------------------------------------------- Lectura de Datos
class read:
    def __init__(self,symbol,var,p):
        self.symbol = symbol
        self.var    = var
        self.Tabla  = None
        self.linea  = p.lineno(1)
        self.pos    = p.lexpos(1)
        self.esValida = True
        
    def setTable(self,tabla):
        self.Tabla = tabla
        global error
        if not self.Tabla.isMemberLoop(self.var):
            print "Error en linea %i, columna %i: no puede usar la variable \"%s\" pues no ha sido declarada." % (self.linea,calcularColumna(data,self.pos),self.var)
            error = True
            self.esValida = False
        if self.Tabla.isMemberFor(self.var):
            print "Error en linea %i, columna %i: se intenta modificar la variable \"%s\" la cual pertenece a una iteracion." % (self.linea,calcularColumna(data,self.pos),self.var)
            error = True
            self.esValida = False
            
        #si la variable es valida se coloca como inicializada    
        if self.esValida:
           self.Tabla.update_Inicializacion(self.var,1)
    
    #En la verificacion estatica no se chequea el tipo de la variable leida        
    def checkTipos(self):
        pass
        
    #Ejecucion de la instruccion read
    def ejecutar(self):
        #se recupera el tipo de la variable
        infoVar   = self.Tabla.findLoop(self.var)
        tipoVar   = infoVar.tipo
        solicitud = ""
        
        entradaValida = False
        
        #bucle que solicita al usuario la variable a ser leida. se detiene en 
        #cuanto la entrada sea valida
        while not entradaValida:
            #obtenemos el valor ingresado por el usuario
            entrada   = raw_input(solicitud)
            #eliminamos los espacios en blanco de la entrada
            entrada   = re.sub(r'\s', '', entrada)
            
            #Caso en el que la variable a leer es de tipo int
            if (tipoVar == 'int'):
                try:
                   entrada = int(entrada)
                   if (hayOverflow(entrada)):
                      print("Error: el numero ingresado no debe superar los 32 bits.")
                   else:
                      entradaValida = True 
                      
                #se capta el ingreso de una entrada que no corresponde a un entero    
                except ValueError:
                   print("Error: debe ingresar un numero entero valido.")
                   
            #Caso en el que la variable a leer es de tipo range
            elif (tipoVar == 'range'):
                #Caso en el que la entrada fue ingresada empleando la construccion
                if (".." in entrada):
                    #se obtiene el par de cotas separadas por '..'
                    cotas = entrada.split("..")
                    
                #Caso en el que la entrada fue ingresada empleado una ',' como separador
                elif ("," in entrada):
                    #se obtiene el par de cotas separadas por ','
                    cotas = entrada.split(",")
                #Caso en el que la entrada es directamente invalida
                else:
                    print("Error: entrada invalida, las cotas deben separarse por '..' o por ','")
                    continue 
                #produccion del rango correspondiente
                try:
                    #instanciacion de las cotas ingresadas a enteros
                    cotaInferior = int(cotas[0])
                    cotaSuperior = int(cotas[1])
                        
                    #se verifica que ninguno de los valores exceda los 32 bits
                    if ((hayOverflow(cotaInferior)) or (hayOverflow(cotaSuperior))):
                        print("Error: los numeros ingresados no deben superar los 32 bits.")
                    else:
                         #se verifica que la cota superior sea mayor o igual que la 
                         #inferior
                         if (cotaInferior <= cotaSuperior):
                            
                            #se construye el rango con las cotas capturadas
                            miRango = Range(cotaInferior,cotaSuperior)
                            entrada = miRango
                            #Se actualiza la variable como inicializada
                            entradaValida = True
                            
                         #Caso en el que el rango es invalido, pues si cota
                         #inferior excede a la superior
                         else:
                              print("La cota inferior debe ser menor o igual a la superior.")
                      
                #se capta el ingreso de una entrada incorrecta
                except ValueError:
                     print("Error: debe ingresar un rango valido.")
            #Caso en el que la variable a leer es de tipo bool
            elif (tipoVar == 'bool'):
                #Caso en el que el valor ingresado fue 'true' o 'false'
                if ((entrada == 'true') or (entrada == 'false')):
                    #la entrada sera true o false dependiendo del valor insertado
                    miBooleano = (entrada == 'true')
                    entrada = miBooleano
                    #Se actualiza la variable como inicializada
                    entradaValida = True
                else:
                    print "Error: entrada invalida. Debe ingresar true o false."
                    
            #fin del if principal
                    
        #fin del ciclo            
                    
                    
        #actualizamos la variable como asignada    
        self.Tabla.update_Inicializacion(self.var,1)
        #actualizamos a la variable con el valor ingresado por el usuario
        self.Tabla.update_Valor(self.var,entrada)
        
#----------------------------------------------------------- Salida por pantalla
class escritura:
    def __init__(self,symbol,var):
        self.symbol = symbol
        self.var    = var   
        self.Tabla  = None
    
    def setTable(self,tabla):
        self.Tabla = tabla
        self.var.setTable(self.Tabla)
        
    def checkTipos(self):
        self.var.getTipo()

    #Ejecucion de la escritura por salida estandar
    def ejecutar(self):
        if (self.symbol == 'writeln'):
            print "%s" %(self.var.evaluar())
        elif (self.symbol == 'write'):
            sys.stdout.write(str(self.var.evaluar()))
            
        
#----------------------------------------------- Lista de expresiones a imprimir
class listaEscritura:
    def __init__(self,expr,symbol_comma,listaExpr):
        self.expr         = expr
        self.symbol_comma = symbol_comma
        self.listaExpr    = listaExpr
        self.Tabla        = None
        
    def setTable(self,tabla):
        self.Tabla = tabla
        self.expr.setTable(self.Tabla)
        self.listaExpr.setTable(self.Tabla)
    
    def getTipo(self):
        self.expr.getTipo()
        self.listaExpr.getTipo()    

    #se retorna la concatenacion resultante de haber evaluado todas las expresiones
    def evaluar(self):
        return "%s%s" %(self.expr.evaluar(),self.listaExpr.evaluar())
    
    
    
#************************** Separadores SEMICOLOM ; ***************************#
class separador:
    def __init__(self,leftTerm,separador,rightTerm):
        self.leftTerm  = leftTerm
        self.separador = separador
        self.rightTerm = rightTerm
        self.Tabla     = None
    
    def setTable(self,tabla):
        self.Tabla = tabla
        self.leftTerm.setTable(self.Tabla)
        self.rightTerm.setTable(self.Tabla)
        
    def checkTipos(self):
        self.leftTerm.checkTipos()
        self.rightTerm.checkTipos()

    #se invoca a la ejecucion de las instrucciones que componen al separador
    def ejecutar(self):
        self.leftTerm.ejecutar()
        self.rightTerm.ejecutar()


#*************************** Asignacion de variables **************************#

class asignacion:
    def __init__(self,variable,symbol,value,p):
        self.variable = variable
        self.symbol   = symbol
        self.value    = value
        self.Tabla    = None
        self.linea    = p.lineno(1)
        self.pos      = p.lexpos(1)
        self.varValida= True ##indica si se puede proceder a asignar un valor
                    
    def setTable(self,tabla):
        self.Tabla = tabla
        global error
        if not tabla.isMemberLoop(self.variable):
            print "Error en linea %i, columna %i: no puede usar la variable \"%s\" pues no ha sido declarada." % (self.linea,calcularColumna(data,self.pos),self.variable)
            error = True
            self.varValida = False
        if self.Tabla.isMemberFor(self.variable):
            print "Error en linea %i, columna %i: se intenta modificar la variable \"%s\" la cual pertenece a una iteracion." % (self.linea,calcularColumna(data,self.pos),self.variable)
            error = True
            self.varValida = False
            
        #si la variable es valida, entonces se le asigna el valor respectivo    
        if self.varValida:
            self.Tabla.update_Inicializacion(self.variable,1)
            
        self.value.setTable(self.Tabla)
        
    def checkTipos(self): 
        tipoVar = ''
        tipoExpr = self.value.getTipo()
        variable = self.Tabla.findLoop(self.variable)
        if variable:
            tipoVar  = variable.tipo
        if tipoVar and tipoExpr:
            if (tipoExpr != tipoVar):
                print "Error en linea %i, columna %i: La variable \"%s\" no es de tipo %s." %(self.linea,calcularColumna(data,self.pos),self.variable,tipoExpr)
                global error
                error = True
        
    #Ejecucion de la asignacion
    def ejecutar(self):
        valorAsignable = self.value.evaluar()
        self.Tabla.update_Valor(self.variable,valorAsignable)

        
        
#********************************* Operador ***********************************#
# Super clase de OperadorBin y OperadorUnario
class Operador:
    def __init__(self,operador):
        self.operador = operador 
        self.Tabla    = None
        self.string   = ''
        if (self.operador == '+'):
           self.string = 'mas'
        elif (self.operador == '*'):
           self.string = 'por'
        elif (self.operador == '/'):
           self.string = 'division'        
        elif (self.operador == '%'):
           self.string = 'modulo'
        elif (self.operador == '..'):
           self.string = 'construccion'
        elif (self.operador == '-'):
           self.string = 'restar'
        elif (self.operador == '<>'):
           self.string = 'interseccion'
        elif (self.operador == '=='):
           self.string = 'igual a'
        elif (self.operador == '/='):
           self.string = 'no igual a'
        elif (self.operador == '>'):
           self.string = 'mayor que'
        elif (self.operador == '<'):
           self.string = 'menor que'
        elif (self.operador == '>='):
           self.string = 'mayor o igual que'
        elif (self.operador == '<='):
           self.string = 'menor o igual que'
        elif (self.operador == '>>'):
           self.string = 'pertenencia'
        elif (self.operador == 'and'):
           self.string = 'conjuncion'
        elif (self.operador == 'or'):
           self.string = 'disyuncion'
        elif (self.operador == 'not'):
           self.string = 'negacion'
              
#----------------------------------------------------------- Operadores Binarios
class operadorBin(Operador):
    def cargarOperando(self,opIzq,opDer,p):
        self.operadorIzq = opIzq
        self.operadorDer = opDer
        self.linea       = p.lineno(2)
        self.pos         = p.lexpos(2) 
        
    def toString_2(self):
        return "%s %s %s" %(self.operadorIzq.toString_2(),self.operador,self.operadorDer.toString_2())
    
    def toString(self):
        return "la expresion \"%s %s %s\"" %(self.operadorIzq.toString_2(),self.operador,self.operadorDer.toString_2())
             
    def setTable(self,tabla):
        self.Tabla = tabla
        self.operadorIzq.setTable(self.Tabla)
        self.operadorDer.setTable(self.Tabla)
        
    def getTipo(self):
        tipoBin = ''
        boolAdmitido = False
        none = False
        tipoIzq = self.operadorIzq.getTipo()
        tipoDer = self.operadorDer.getTipo()
        none = (not tipoIzq or not tipoDer)
        errorR = False
         
        #Caso en el que los operadores son relacionales
        if ((self.operador == '>') or (self.operador == '<') or (self.operador == '>=') or (self.operador == '<=') or (self.operador == '==') or (self.operador == '/=')):
            tipoBin = 'bool' 
            #Si los operadores son == o \= entonces los bool son admitidos
            boolAdmitido = (self.operador == '==') or (self.operador == '/=')
            errorR = ((tipoIzq != tipoDer) or ((tipoIzq == tipoDer) and ((tipoIzq == 'bool') and (not boolAdmitido))))
                            
        #Caso en el que los operadores son or and not
        elif ((self.operador == 'or') or (self.operador == 'and')):     
            tipoBin = 'bool'      
            errorR = ((tipoIzq != 'bool') or (tipoDer != 'bool'))
         
        #Caso en el que el operador es belongs >>
        elif (self.operador == '>>'):
            tipoBin = 'bool'
            errorR = ((tipoIzq != 'int' ) or (tipoDer != 'range'))
         
        #Caso en el que el operador remite unicamente a operaciones con enteros o con rangos
        elif ((self.operador == '+') or (self.operador == '-') or (self.operador == '*') or (self.operador == '/') or (self.operador == '%') or (self.operador == '..') or (self.operador == '<>')):
            #Operadores que aplican unicamente a enteros y devuelven entero
            if ((self.operador == '%') or (self.operador == '/') or (self.operador == '-')): 
                tipoBin = 'int'
                errorR = ((tipoIzq != 'int') or (tipoDer != 'int'))
                      
            #Operadores que devuelven rangos
            elif ((self.operador == '..')):
                tipoBin = 'range'
                errorR = ((tipoIzq != 'int') or (tipoDer != 'int'))
            
            elif ((self.operador == '+')):
                #por defecto se toma el tipo de la expresion mas izquierda
                tipoBin = tipoIzq
                if ((tipoIzq != tipoDer) or ((tipoIzq=='bool') or (tipoDer=='bool'))):
                    if (tipoIzq == 'int'):
                        self.string = 'sumar'
                    elif tipoIzq == 'range': 
                        self.string = 'unir'
                    tipoBin = 'int'
                    if (tipoIzq != 'int' and tipoDer != 'int') and (tipoIzq == 'range' or tipoDer == 'range'):
                        tipoBin = 'range'
                    errorR = True    
            #El operador interseccion recibe dos ranges y devuelve range
            elif (self.operador == '<>'):
                tipoBin = 'range'
                errorR = ((tipoIzq != 'range') or (tipoDer != 'range'))
            
            elif (self.operador == '*'):      
                #Caso en el que el * remite a una operador que usa un rango de lado izquierdo
                if ((tipoIzq == 'range') or (tipoIzq == 'int')):
                    if (tipoIzq == 'int'):
                        self.string = 'multiplicar'
                    else:
                        self.string = 'escalar'
                    tipoBin = tipoIzq
                    errorR = (tipoDer != 'int')
                     #Caso en el que hay un tipo bool involucrado      
                else:
                    tipoBin = 'int'
                    errorR = True
                        
        if not none:
            if errorR:
                global error
                error = True
                print "Error en linea %i, columna %i: intento de \'%s\' %s de tipo \"%s\" con %s de tipo \"%s\"." %(self.linea,calcularColumna(data,self.pos),self.string,self.operadorIzq.toString(),tipoIzq,self.operadorDer.toString(),tipoDer)
            
        return tipoBin
        
        
    #metodo que ejecuta una operacion binaria, dependiendo de cual esta sea
    def evaluar(self):
        #se obtienen los tipos respectos a la expresion izquierda y derecha 
        #del operador
        tipoIzq = self.operadorIzq.getTipo()
        tipoDer = self.operadorDer.getTipo()
        
        #Caso en el que el operador es una cruz '+'
        if (self.operador == '+'):
           #Caso en el que se debe proceder a operar una suma entre enteros
           if ((tipoIzq == 'int') and (tipoDer == 'int')):
              return self.sumar(self.operadorIzq,self.operadorDer)
           #Caso en el que se debe proceder a operar una union entre rangos
           elif ((tipoIzq == 'range') and (tipoDer == 'range')):
              return self.union(self.operadorIzq,self.operadorDer)
              
        #Caso en el que el operador es un menos '-'      
        elif (self.operador == '-'):      
           #Caso en el que se debe proceder a operar una resta entre enteros
           if ((tipoIzq == 'int') and (tipoDer == 'int')):
              return self.restar(self.operadorIzq,self.operadorDer)
              
        #Caso en el que el operador es un slash '/'      
        elif (self.operador == '/'):            
           #Caso en el que se debe proceder a operar una resta entre enteros
           if ((tipoIzq == 'int') and (tipoDer == 'int')):
               return self.dividir(self.operadorIzq,self.operadorDer)
               
        #Caso en el que el operador es un asterisco '*'
        elif (self.operador == '*'):
            #Caso en el que se debe proceder a operar una multiplicacion entre enteros
           if ((tipoIzq == 'int') and (tipoDer == 'int')):
               return self.multiplicar(self.operadorIzq,self.operadorDer)
           #Caso en el que se debe proceder a operar una escala entre rango y entero
           elif ((tipoIzq == 'range') and (tipoDer == 'int')):
              return self.escala(self.operadorIzq,self.operadorDer)        
               
        #Caso en el que el operador es un asterisco '*'
        elif (self.operador == '%'):
            #Caso en el que se debe proceder a operar una multiplicacion entre enteros
            if ((tipoIzq == 'int') and (tipoDer == 'int')):
               return self.modulo(self.operadorIzq,self.operadorDer)       
        
        #Caso en el que el operador es una doble igualdad '=='
        elif (self.operador == '=='):
            #Caso en el que se debe proceder a operar una equivalencia entre enteros
            #o entre booleanos
            if (((tipoIzq == 'int') and (tipoDer == 'int')) or 
               ((tipoIzq == 'bool') and (tipoDer == 'bool'))):
               return self.equivalencia_Int_Bool(self.operadorIzq,self.operadorDer)
            #Caso en el que se debe proceder a operar una equivalencia entre rangos
            elif ((tipoIzq == 'range') and (tipoDer == 'range')):
               return self.equivalencia_Rangos(self.operadorIzq,self.operadorDer) 
         
       #Caso en el que el operador es una desigualdad '/='
        elif (self.operador == '/='):
            #Caso en el que se debe proceder a operar una desigualdad entre enteros
            #o entre booleanos
            if (((tipoIzq == 'int') and (tipoDer == 'int')) or 
               ((tipoIzq == 'bool') and (tipoDer == 'bool'))):
               return self.desigualdad_Int_Bool(self.operadorIzq,self.operadorDer)  
            #Caso en el que se debe proceder a operar una desigualdad entre rangos
            elif ((tipoIzq == 'range') and (tipoDer == 'range')):
               return self.desigualdad_Rangos(self.operadorIzq,self.operadorDer)     
                            
       #Caso en el que el operador es un punto doble '..'
        elif (self.operador == '..'):
            #Caso en el que se debe proceder a operar una construccion entre enteros
            if ((tipoIzq == 'int') and (tipoDer == 'int')):
               #Se invoca a la construccion de una instancia del tipo abstracto de datos range
               return self.construirRango(self.operadorIzq,self.operadorDer)
                       
       #Caso en el que el operador es una conjuncion 'and'
        elif (self.operador == 'and'): 
            #Caso en el que se debe proceder a operar una conjuncion entre booleanos
            if ((tipoIzq == 'bool') and (tipoDer == 'bool')):
               #Se invoca a la conjuncion de booleanos
               return self.conjuncion(self.operadorIzq,self.operadorDer)
               
        #Caso en el que el operador es una disyuncion 'or'
        elif (self.operador == 'or'): 
            #Caso en el que se debe proceder a operar una conjuncion entre booleanos
            if ((tipoIzq == 'bool') and (tipoDer == 'bool')):
               #Se invoca a la disyuncion de booleanos
               return self.disyuncion(self.operadorIzq,self.operadorDer)       
                       
        #Caso en el que el operador es un mayor estricto '>'
        elif (self.operador == '>'):
            #Caso en el que se debe proceder a operar una comparacion de enteros
            if ((tipoIzq == 'int') and (tipoDer == 'int')):
               return self.mayor_Estricto_Int(self.operadorIzq,self.operadorDer)
            #Caso en el que se debe proceder a operar una comparacion entre rangos
            elif ((tipoIzq == 'range') and (tipoDer == 'range')):
               return self.mayor_Estricto_Rangos(self.operadorIzq,self.operadorDer)
               
        #Caso en el que el operador es un mayor igual '>='
        elif (self.operador == '>='):
            #Caso en el que se debe proceder a una comparacion entre enteros
            if ((tipoIzq == 'int') and (tipoDer == 'int')):
               return self.mayor_Igual_Int(self.operadorIzq,self.operadorDer)
            #Caso en el que se debe proceder a operar una comparacion entre rangos
            elif ((tipoIzq == 'range') and (tipoDer == 'range')):
               return self.mayor_Igual_Rangos(self.operadorIzq,self.operadorDer)   
              
        #Caso en el que el operador es un menor estricto '<'
        elif (self.operador == '<'):
            #Caso en el que se debe proceder a operar una comparacion de enteros
            if ((tipoIzq == 'int') and (tipoDer == 'int')):
               return self.menor_Estricto_Int(self.operadorIzq,self.operadorDer)
            #Caso en el que se debe proceder a operar una comparacion entre rangos
            elif ((tipoIzq == 'range') and (tipoDer == 'range')):
               return self.menor_Estricto_Rangos(self.operadorIzq,self.operadorDer)
               
        #Caso en el que el operador es menor igual '<='
        elif (self.operador == '<='):
            #Caso en el que se debe proceder a una comparacion entre enteros
            if ((tipoIzq == 'int') and (tipoDer == 'int')):
               return self.menor_Igual_Int(self.operadorIzq,self.operadorDer)
            #Caso en el que se debe proceder a operar una comparacion entre rangos
            elif ((tipoIzq == 'range') and (tipoDer == 'range')):
               return self.menor_Igual_Rangos(self.operadorIzq,self.operadorDer)  
               
        #Caso en el que el operador es mayor mayor '>>'
        elif (self.operador == '>>'):
            #Caso en el que se debe proceder a aplicar la pertenencia entre un entero y un rango
            if ((tipoIzq == 'int') and (tipoDer == 'range')):
               return self.pertenece(self.operadorIzq,self.operadorDer)
               
        #Caso en el que el operador es interseccion '<>'
        elif (self.operador == '<>'):
            #Caso en el que se debe proceder a aplicar la interseccion entre rangos
            if ((tipoIzq == 'range') and (tipoDer == 'range')):
               return self.interseccion(self.operadorIzq,self.operadorDer)       
        
    #implementacion de la suma de enteros
    def sumar(self,exprIzquierda,exprDerecha):
        #Se calcula la suma de los enteros
        suma = exprIzquierda.evaluar() + exprDerecha.evaluar()
        #Verificacion dinamica, chequea si la suma es representable en 32 bits
        if (hayOverflow(suma)):
            print "Error: Resultado no puede representarse en 32 bits."
            #se aborta el programa
            sys.exit()
        
        #de no haber overflow, se retorna la suma
        return suma
        
    #implementacion de la union de rangos
    def union(self,exprIzquierda,exprDerecha):
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()

        cotaInferior = min(rangoIzquierdo.cotaInferior,rangoDerecho.cotaInferior)
        cotaSuperior = max(rangoDerecho.cotaSuperior,rangoIzquierdo.cotaSuperior)
        
        miRango = Range(cotaInferior,cotaSuperior)
        return miRango
     
    #implementacion de la interseccion entre rangos
    def interseccion(self,exprIzquierda,exprDerecha):
        #se calculan los rangos izquierdo y derecho a ser comparados
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()
        
        #Verificacion dinamica, chequea que la interseccion no sea vacia
        if ((rangoIzquierdo.cotaSuperior < rangoDerecho.cotaInferior) or
            (rangoIzquierdo.cotaInferior > rangoDerecho.cotaSuperior)):
            print "Error: interseccion vacia entre los rangos %r y %r" %(rangoIzquierdo,rangoDerecho)
            #se aborta el programa
            sys.exit()
        #se crea un nuevo rango cuya cota inferior es el maximo de las cotas minimas
        #y cuya cota superior es el minimo de las cotas maximas
        miRango = Range(max(rangoIzquierdo.cotaInferior,rangoDerecho.cotaInferior),
                        min(rangoIzquierdo.cotaSuperior,rangoDerecho.cotaSuperior))
        return miRango    
        
        
    #Implementacion de la resta entre enteros
    def restar(self,exprIzquierda,exprDerecha):
        #se calcula la resta de los enteros
        resta = exprIzquierda.evaluar() - exprDerecha.evaluar()
    
        #Verificacion dinamica, chequea si la suma es representable en 32 bits
        if (hayOverflow(resta)):
            print "Error: Resultado no puede representarse en 32 bits."
            #se aborta el programa
            sys.exit()
                    
        #de no haber overflow, se retorna la suma
        return resta
        
    #Implementacion de la resta entre enteros
    def dividir(self,exprIzquierda,exprDerecha):
        #se calcula primero la expresion derecha
        valorDerecho = exprDerecha.evaluar()
        #verificacion dinamica. Impide la division entre 0 
        if (valorDerecho == 0):
            print "Error: Intento de division por 0" 
            #se aborta la corrida
            sys.exit()
        
        return exprIzquierda.evaluar() / valorDerecho  
          
    #Implementacion de la multiplicacion entre enteros    
    def multiplicar(self,exprIzquierda,exprDerecha):
        multi = exprIzquierda.evaluar() * exprDerecha.evaluar()
        #Verificacion dinamica, chequea si la suma es representable en 32 bits
        if (hayOverflow(multi)):
            print "Error: Resultado no puede representarse en 32 bits."
            #se aborta el programa
            sys.exit()
            
        return multi
    
    #Implementacion de la multiplicacion entre enteros    
    def escala(self,exprIzquierda,exprDerecha):
        #se calcula el rango a escalar
        rango = exprIzquierda.evaluar()
        #se calcula el entero empleado para la escala
        valor = exprDerecha.evaluar()
        
        #Se multiplican las cotas por el valor obtenido
        cotaSuperior = rango.cotaSuperior*valor
        cotaInferior = rango.cotaInferior*valor
        #Verificacion dinamica, chequea que las cotas sean representables en 32 bits
        if (hayOverflow(cotaSuperior) or hayOverflow(cotaInferior)):
            print "Error: Resultado no puede representarse en 32 bits."
            #se aborta el programa
            sys.exit()
        
        #Si valor es menor que 0, se invierten las cotas
        if (valor<0):
            AuxCota = cotaSuperior
            cotaSuperior = cotaInferior
            cotaInferior = AuxCota
        
        miRango = Range(cotaInferior,cotaSuperior)
        return miRango
        
    
    #Implementacion del modulo entre enteros    
    def modulo(self,exprIzquierda,exprDerecha):
        #se calcula primero la expresion derecha
        valorDerecho = exprDerecha.evaluar()
        #verificacion dinamica. Impide la division entre 0 
        if (valorDerecho == 0):
            print "Error: Intento de division por 0" 
            #se aborta la corrida
            sys.exit()
        
        return exprIzquierda.evaluar() % valorDerecho      
           
    #Implementacion de la equivalencia entre enteros y booleanos    
    def equivalencia_Int_Bool(self,exprIzquierda,exprDerecha):
        return (exprIzquierda.evaluar() == exprDerecha.evaluar())
    
    
    #Implementacion de la desigualdad entre enteros y booleanos    
    def desigualdad_Int_Bool(self,exprIzquierda,exprDerecha):
        return (exprIzquierda.evaluar() != exprDerecha.evaluar())
            
    #Implementacion de la equivalencia entre rangos   
    def equivalencia_Rangos(self,exprIzquierda,exprDerecha):
        #se calculan los rangos izquierdo y derecho a ser comparados
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()
        
        #Rangos equivalentes determina si los rangos son identicos.
        #esto solo ocurre si las cotas superior e inferior de cada rango coinciden
        RangosEquivalentes = ((rangoIzquierdo.cotaInferior == rangoDerecho.cotaInferior)
                               and (rangoIzquierdo.cotaSuperior == rangoDerecho.cotaSuperior))
        return RangosEquivalentes
    
    #Implementacion de la desigualdad entre rangos   
    def desigualdad_Rangos(self,exprIzquierda,exprDerecha):
        #se calculan los rangos izquierdo y derecho a ser comparados
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()
        
        #Rangos desiguales determina si los rangos difieren en sus cotas.
        #esto ocurre si las cotas de a no son identicas a las de b
        RangosDesiguales = ((rangoIzquierdo.cotaInferior != rangoDerecho.cotaInferior)
                               or (rangoIzquierdo.cotaSuperior != rangoDerecho.cotaSuperior))
        return RangosDesiguales
    
    #Implementacion de la construccion entre enteros
    def construirRango(self,exprIzquierda,exprDerecha):
        #se calculan primero las expresiones izquierda y derecha 
        valorIzquierdo = exprIzquierda.evaluar()
        valorDerecho   = exprDerecha.evaluar()
    
        #verificacion dinamica. Impide la construccion de un rango cuya
        #cota inferior sea mayor a la superior
        if (valorIzquierdo > valorDerecho):
            print "Error: Intento de construccion de un rango cuya cota inferior \"%s\" es mayor a la superior \"%s\"" %(valorIzquierdo,valorDerecho)  
            #se aborta la corrida
            sys.exit()
    
        #Se construye una instancia del tipo abstracto de datos range
        miRango = Range(valorIzquierdo,valorDerecho)
        return miRango
    
    #Implementacion de la conjuncion entre enteros
    def conjuncion(self,exprIzquierda,exprDerecha):
        #se calculan primero los valores booleanos izquierdos y derechos
        boolIzquierdo = exprIzquierda.evaluar()
        boolDerecho   = exprDerecha.evaluar()
        
        #se retorna la conjuncion entre los booleanos
        return (boolIzquierdo and boolDerecho) 
    
    #Implementacion de la disyuncion entre enteros    
    def disyuncion(self,exprIzquierda,exprDerecha):
        #se calculan primero los valores booleanos izquierdos y derechos
        boolIzquierdo = exprIzquierda.evaluar()
        boolDerecho   = exprDerecha.evaluar()
        
        #se retorna la disyuncion entre los booleanos
        return (boolIzquierdo or boolDerecho)                   
        
    
    #Implementacion del mayor estricto entre enteros 
    def mayor_Estricto_Int(self,exprIzquierda,exprDerecha):
         return (exprIzquierda.evaluar() > exprDerecha.evaluar())
    
    
    #Implementacion del mayor igual entre enteros 
    def mayor_Igual_Int(self,exprIzquierda,exprDerecha):
         return (exprIzquierda.evaluar() >= exprDerecha.evaluar())
    
    #Implementacion del menor estricto entre enteros 
    def menor_Estricto_Int(self,exprIzquierda,exprDerecha):
         return (exprIzquierda.evaluar() < exprDerecha.evaluar())
    
    #Implementacion del menor igual entre enteros 
    def menor_Igual_Int(self,exprIzquierda,exprDerecha):
         return (exprIzquierda.evaluar() <= exprDerecha.evaluar())
    
    #Implementacion del mayor estricto entre rangos
    def mayor_Estricto_Rangos(self,exprIzquierda,exprDerecha):
        #se calculan los rangos izquierdo y derecho a ser comparados
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()
        
        #retorna true si la cota inferior de a es mayor a la cota superior de b
        return ((rangoIzquierdo.cotaInferior > rangoDerecho.cotaSuperior))                           
     
    #Implementacion del mayor igual entre rangos
    def mayor_Igual_Rangos(self,exprIzquierda,exprDerecha):
        #se calculan los rangos izquierdo y derecho a ser comparados
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()
        
         #retorna true si la cota inferior de a es mayor o igual a la cota superior de b
        return ((rangoIzquierdo.cotaInferior >= rangoDerecho.cotaSuperior))  
                               
    #Implementacion del menor estricto entre rangos
    def menor_Estricto_Rangos(self,exprIzquierda,exprDerecha):
        #se calculan los rangos izquierdo y derecho a ser comparados
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()
        
        #retorna true si la cota superior de a es menor a la cota inferior de b
        return ((rangoIzquierdo.cotaSuperior < rangoDerecho.cotaInferior))  
        
    #Implementacion del menor igual entre rangos
    def menor_Igual_Rangos(self,exprIzquierda,exprDerecha):
        #se calculan los rangos izquierdo y derecho a ser comparados
        rangoIzquierdo = exprIzquierda.evaluar()
        rangoDerecho   = exprDerecha.evaluar()
        
        #retorna true si la cota superior de a es menor o igual a la cota inferior de b
        return ((rangoIzquierdo.cotaSuperior <= rangoDerecho.cotaInferior))  
        
    #Implementacion del operador binario pertenencia entre entero y rango
    def pertenece(self,exprIzquierda,exprDerecha):
        #se obtiene el valor del entero    
        valorInt = exprIzquierda.evaluar()
        #se obtiene el rango a evaluar
        Rango    = exprDerecha.evaluar()
        
        #retorna true si valorInt esta contenido entre las cotas del rango,
        #false en caso contrario
        return ((valorInt >= Rango.cotaInferior) and (valorInt <= Rango.cotaSuperior))
                                         
#------------------------------------------------------------ Operadores Unarios
class operadorUnario(Operador):
    def cargarOperando(self,operando,p):
        self.operando = operando
        self.linea    = p.lineno(1)
        self.pos      = p.lexpos(1)
        if (self.operador == '-'):
            self.string = 'menos unario'
   
    def toString_2(self):
        return "%s %s" %(self.operador,self.operando.toString_2())
    
    def toString(self):
        return "la expresion \"%s %s\"" %(self.operador,self.operando.toString_2())
         
   
    def __repr__(self,identacion):
        return "EXPRESION_UN\n%soperador: %s\n%soperando: %s" % (identacion+"\t",self.string,identacion+"\t",self.operando.__repr__(identacion+"\t"))
        
    def getTipo(self):
        tipo = ''
        tipoOp = self.operando.getTipo()        
        global error
        if (self.operador == '-'):
            tipo = 'int'           
            if tipoOp and (tipoOp!='int'):
               print "Error en linea %i, columna %i: intento de \'%s\' %s de tipo \"%s\"." %(self.linea,calcularColumna(data,self.pos),self.string,self.operando.toString(),tipoOp)
               error = True     
        elif (self.operador == 'not'):
            tipo = 'bool'            
            if tipoOp and (tipoOp!='bool'):
               print "Error en linea %i, columna %i: intento de \'%s\' %s de tipo \"%s\"." %(self.linea,calcularColumna(data,self.pos),self.string,self.operando.toString(),tipoOp)
               error = True 
        return tipo
        
    def setTable(self,tabla):
        self.Tabla = tabla
        self.operando.setTable(self.Tabla)
        
        
    #Evaluacion de una operacion de tipo unaria
    def evaluar(self):
        #obtenemos el tipo del operando
        tipoOperando = self.operando.getTipo()
        
        #Caso en el que el operador es un menos unario '-'
        if (self.operador == '-'):
            #Caso en el que se debe proceder a aplicar un menos unario a un entero
            if (tipoOperando == 'int'):
               return self.menos_Unario(self.operando)
        #Caso en el que el operador es una negacion 'not'       
        elif (self.operador == 'not'):
            #Caso en el que se debe proceder a aplicar una negacion a un booleano
            if (tipoOperando == 'bool'):
               return self.negacion(self.operando)
        
    
    #Implementacion de la operacion menos_Unario a un entero
    def menos_Unario(self,operando):
        #se obtiene el valor del operando y se retorna su inverso negativo
        valorInt = operando.evaluar()
        return (-valorInt)
        
    #Implementacion de la operacion negacion a un booleano
    def negacion(self,operando):    
        #se obtiene el valor del operando y se retorna su negado
        valorBool = operando.evaluar()
        return (not valorBool) 
        
#*************************** Bloque de Instrucciones **************************#
class bloque:
    def __init__(self,symbol_begin,ins,symbol_end):
        self.symbol_begin = symbol_begin
        self.ins          = ins
        self.symbol_end   = symbol_end
        self.Tabla        = None
        
    def __repr__(self,identacion):
        return "BLOQUE\n%s%s%s" % (self.Tabla.__repr__(identacion+"\t"),identacion+"\t",self.ins.__repr__(identacion+"\t"))
        
    def setTable(self,tabla):
        self.Tabla = SymbolTable.SymTable()
        self.Tabla.new()
        self.Tabla.setTablaAnterior(tabla)
        self.Tabla.copyFor(tabla.TablaFor)
        self.ins.setTable(self.Tabla)
        
    def checkTipos(self):
        return self.ins.checkTipos()
    
    def ejecutar(self):
        self.ins.ejecutar()
        
#----------------------------------------------------------------- Declaraciones
class declaracion:
    def __init__(self,symbol_dec,listDec,listIns):
        self.symbol_dec = symbol_dec
        self.listDec    = listDec
        self.listIns    = listIns
        self.Tabla      = None
                
    def __repr__(self,identacion):
        return "%s%s" % (self.listDec.__repr__(identacion),self.listIns.__repr__(identacion))
        
    def setTable(self,tabla):
        self.Tabla = tabla
        self.listDec.setTable(self.Tabla)
        self.listIns.setTable(self.Tabla)
        
    def checkTipos(self):
        return self.listIns.checkTipos()
        
    #se llama a la ejecucion de las instrucciones que siguen en el bloque               
    def ejecutar(self):
        self.listIns.ejecutar()
                                
#-------------------------------------------------------- Lista de declaraciones
class listaDeclaraciones:
    def __init__(self,listVar,symbol_as,tipo):
        self.listVar   = listVar
        self.symbol_as = symbol_as
        self.tipo      = tipo    
        self.Tabla     = None     
    
    def __repr__(self,identacion):
        return ""
        
    def setTable(self,tabla):
        self.Tabla = tabla
        self.listVar.insertInTable(self.Tabla,self.tipo)
        
#------------------------------------------------------------ Variable declarada
class Var:
    def __init__(self,identificador,p):
        self.identificador = identificador
        self.linea = p.lineno(1)
        self.pos = p.lexpos(1)
           
    def insertInTable(self,tabla,tipo):
        if tabla.isMember(self.identificador):
            print "Error en linea %i, columna %i: la variable \"%s\" ya ha sido declarada." % (self.linea,calcularColumna(data,self.pos),self.identificador)
            global error
            error = True
        tabla.insert(self.identificador,tipo)
        tabla.deleteFor(self.identificador)

#------------------------------------------------------------ Lista de variables
class listaVariables:
    def __init__(self,identificador,symbol_comma,listVar,p):
        self.listVar       = listVar
        self.symbol_comma  = symbol_comma
        self.identificador = identificador 
        self.linea         = p.lineno(1)
        self.pos           = p.lexpos(1)
        
    def __repr__(self,identacion):
        return "%r %r" %(self.identificador,self.listVar)
        
    def insertInTable(self,tabla,tipo):
        if tabla.isMember(self.identificador):
            print "Error en linea %i, columna %i: la variable \"%s\" ya ha sido declarada." % (self.linea,calcularColumna(data,self.pos),self.identificador)
            global error
            error = True
        tabla.insert(self.identificador,tipo)
        tabla.deleteFor(self.identificador)
        self.listVar.insertInTable(tabla,tipo)


        
#******************************* SWITCH CASE **********************************#
class case:
    def __init__(self,symbol_c,expr,symbol_o,casos,symbol_ee,p):
        self.symbol_c  = symbol_c 
        self.expr      = expr
        self.symbol_o  = symbol_o
        self.casos     = casos
        self.symbol_ee = symbol_ee
        self.Tabla     = None
        self.linea     = p.lineno(1)
        self.pos       = p.lexpos(1)
        
    def __repr__(self,identacion):
        return "CASE\n%sexp: %s\n%s" % (identacion+"\t",self.expr.__repr__(identacion+"\t"),self.casos.__repr__(identacion+"\t"))
        
    def setTable(self,tabla):
        self.Tabla = tabla
        self.expr.setTable(self.Tabla)
        self.casos.setTable(self.Tabla)
        
    def checkTipos(self):
        tipoExpr = self.expr.getTipo()
        if tipoExpr and (tipoExpr!='int'):
            print "Error en linea %i, columna %i: la condicion del 'case' es una expresion de tipo %s" %(self.linea,calcularColumna(data,self.pos),tipoExpr)   
            global error
            error = True 
        self.casos.checkTipos()

    #Ejecucion de un condicional case
    def ejecutar(self):
        #se obtiene el valor entero de la expresion case
        expresionCase = self.expr.evaluar()
        self.casos.setExpr(expresionCase)
        self.casos.ejecutar()
        

#------------------------------------------------------ Lista de casos a evaluar
class listaCasos:
    def __init__(self,ran,symbol_o,ins,p):
        self.ran   = ran 
        self.ins   = ins
        self.Tabla = None
        self.linea = p.lineno(2)
        self.pos   = p.lexpos(2)
        self.exprCase = None
        
    def __repr__(self,identacion):
        return "%scaso:\n%sran: %s \n%sins: %s\n" % (identacion,identacion+"\t",self.ran.__repr__(identacion+"\t"),identacion+"\t",self.ins.__repr__(identacion+"\t"))
    
    def setTable(self,tabla):
        self.Tabla = tabla
        self.ran.setTable(self.Tabla)
        self.ins.setTable(self.Tabla)
        
    def checkTipos(self):
        tipoRan = self.ran.getTipo()
        if tipoRan and (tipoRan!='range'):
            print "Error en linea %i, columna %i: la guardia 'case' es una expresion de tipo %s" %(self.linea,calcularColumna(data,self.pos),tipoRan)   
            global error
            error = True 
        self.ins.checkTipos()    

    #Hereda el atributo de su padre correspondiente al valor del case
    def setExpr(self,expr):
        self.exprCase = expr
    
    #Implementa la ejecucion del condicional case
    def ejecutar(self):
        #se obtiene el valor del rango a evaluar
        Rango = self.ran.evaluar()
        #Si la expresion entera del case esta contenida en el rango actual,
        #se ejecuta la instruccion correspondiente
        if ((self.exprCase >= Rango.cotaInferior) and (self.exprCase <= Rango.cotaSuperior)):
           self.ins.ejecutar()
        
#******************************* Condicional IF *******************************#
class condicional_if:
    def __init__(self,symbol_in,expr,symbol_then,ins,p):
        self.symbol_in   = symbol_in
        self.expr        = expr
        self.symbol_then = symbol_then
        self.ins         = ins
        self.Tabla       = None
        self.linea       = p.lineno(1)
        self.pos         = p.lexpos(1)
        
    def __repr__(self,identacion):
        return "CONDICIONAL:\n%scondicion: %s\n%sverdadero: %s" % (identacion+"\t",self.expr.__repr__(identacion+"\t"),identacion+"\t",self.ins.__repr__(identacion+"\t"))
    
    def setTable(self,tabla):
        self.Tabla = tabla
        self.expr.setTable(self.Tabla)
        self.ins.setTable(self.Tabla)
        
    def checkTipos(self):
        tipoCond = self.expr.getTipo()
        if tipoCond and (tipoCond!='bool'):
            print "Error en linea %i, columna %i: la condicion del 'if' es una expresion de tipo %s" %(self.linea,calcularColumna(data,self.pos),tipoCond)   
            global error
            error = True 
        self.ins.checkTipos()
        
        
    #Ejecucion del condicional if
    def ejecutar(self):
        #se obtiene la condicion del if
        condicion = self.expr.evaluar()
        if condicion:
           self.ins.ejecutar()
        
#---------------------------------------------------------- Lista de condiciones
class condicional_if_else:
    def __init__(self,symbol_if,expr,symbol_then,true_ins,symbol_else,false_ins,p):
        self.symbol_if   = symbol_if
        self.expr        = expr
        self.symbol_then = symbol_then
        self.true_ins    = true_ins 
        self.symbol_else = symbol_else
        self.false_ins   = false_ins
        self.Tabla       = None
        self.linea       = p.lineno(1)
        self.pos         = p.lexpos(1)
        
    def __repr__(self,identacion):
        return "CONDICIONAL:\n%scondicion: %s\n%sverdadero: %s\n%sfalso: %s" % (identacion+"\t",self.expr.__repr__(identacion+"\t"),identacion+"\t",self.true_ins.__repr__(identacion),identacion+"\t",self.false_ins.__repr__(identacion))
    
    def setTable(self,tabla):
        self.Tabla = tabla
        self.expr.setTable(self.Tabla)
        self.true_ins.setTable(self.Tabla)
        self.false_ins.setTable(self.Tabla)    
        
    def checkTipos(self):
        tipoCond = self.expr.getTipo()
        if tipoCond and (tipoCond!='bool'):
            print "Error en linea %i, columna %i: la condicion del 'if' es una expresion de tipo %s" %(self.linea,calcularColumna(data,self.pos),tipoCond)   
            global error
            error = True 
        self.true_ins.checkTipos()
        self.false_ins.checkTipos()
    
    #Implementacion de la ejecucion de un if then else
    def ejecutar(self):
        condicion = self.expr.evaluar()
        if condicion:
            self.true_ins.ejecutar()
        else:
            self.false_ins.ejecutar()
        
#******************************** Iteracion ***********************************#
# Super clase de iteracionDeterminada e iteracionIndeterminada
class Iteracion:
    def __init__(self,first_symbol,symbol_do,ins):
        self.first_symbol = first_symbol
        self.symbol_do    = symbol_do
        self.ins          = ins
        self.Tabla        = None
        
#----------------------------------------------------- Iteracion determinada FOR
class iteracionDeterminada(Iteracion):
    def cargarRango(self,var,symbol_in,rango,p):
        self.var       = var
        self.symbol_in = symbol_in  
        self.rango     = rango
        self.linea     = p.lineno(1)
        self.pos       = p.lexpos(1)
        
    def __repr__(self,identacion):
        return "ITERACION_DET:\n%svariable: %s\n%srango: %s\n%sinstruccion: %s" % (identacion+"\t",self.var,identacion+"\t",self.rango.__repr__(identacion+"\t"),identacion+"\t",self.ins.__repr__(identacion+"\t"))
        
    # Esta funcion en particular crea una tabla nueva, coloca la que le pasan 
    # como parametro en tabla anterior y duplica la tabla nueva, en dos
    # instancias distintas. Esto debido a que el rango del for no debe contener
    # a la variable de iteracion, pero el resto de las instrucciones si.
    def setTable(self,tabla):
        self.Tabla = SymbolTable.SymTable()
        self.Tabla.new()
        self.Tabla.setTablaAnterior(tabla)
        self.Tabla.copyFor(tabla.TablaFor)
        
        Tabla2 = SymbolTable.SymTable()
        Tabla2.new()
        Tabla2.copy(self.Tabla)
        
        self.rango.setTable(Tabla2)
        self.Tabla.insertFor(self.var,'int',1)
        self.ins.setTable(self.Tabla)
        
    def checkTipos(self):
        tipoRango = self.rango.getTipo()
        if tipoRango and (tipoRango != 'range'):
            print "Error en linea %i, columna %i: el rango del 'for' es una expresion de tipo %s" %(self.linea,calcularColumna(data,self.pos),tipoRango)   
            global error
            error = True         
        self.ins.checkTipos()
        
     
    #Implementacion de la ejecucion de una iteracion determinada
    def ejecutar(self):
        #se obtiene el valor del rango
        Rango = self.rango.evaluar()
        #ejecutamos el bucle. Este debe incluir las cotas superior e inferior
        valorVar    = Rango.cotaInferior
        #La condicion inicial debe ser consolidad con un menor igual, dado
        #el caso en el que las cotas del rango sean iguales
        condicion   = valorVar <= Rango.cotaSuperior
        
        #el bucle se detiene cuando el valor actual de la variable sea igual
        #a la cota superior del rango
        while condicion:
            #ejecutamos la instruccion
            self.Tabla.update_Valor(self.var,valorVar)
            self.ins.Tabla.update_Valor(self.var,valorVar)
            self.setTable(self.Tabla)
            self.ins.ejecutar()
            #incrementa en una unidad el valor de la variable de iteracion
            valorVar = valorVar + 1 
            #se actualiza el valor de la variable de iteracion
            
            #se actualiza la condicion de iteracion
            condicion = (valorVar <= Rango.cotaSuperior)
        
#------------------------------------------------- Iteracion indeterminada WHILE
class iteracionIndeterminada(Iteracion):
    def cargarCondicion(self,expr,p):
        self.condicion = expr
        self.linea     = p.lineno(1)
        self.pos       = p.lexpos(1)
        
    def __repr__(self,identacion):
        return "ITERACION_INDET:\n%scondicion: %s\n%sinstruccion: %s" % (identacion+"\t",self.condicion.__repr__(identacion+"\t"),identacion+"\t",self.ins.__repr__(identacion+"\t"))
    
    def setTable(self,tabla):
        self.Tabla = tabla
        self.condicion.setTable(self.Tabla)
        self.ins.setTable(self.Tabla)    
        
    def checkTipos(self):
        tipoCond = self.condicion.getTipo()
        if tipoCond and (tipoCond != 'bool'):
            print "Error en linea %i, columna %i: la condicion del 'while' es una expresion de tipo %s" %(self.linea,calcularColumna(data,self.pos),tipoCond)   
            global error
            error = True
        self.ins.checkTipos()      

    #Ejecucion de la iteracion indeterminada
    def ejecutar(self):
        #se obtiene la condicion de iteracion, que corresponde a un booleano
        condicion = self.condicion.evaluar()
        while condicion:
            #ejecucion de la instruccion
            self.ins.ejecutar()
            #actualizacion de la condicion
            condicion = self.condicion.evaluar()

#***************************** Funciones con rangos ***************************#

class funcion:
    def __init__(self,nombre_fun,expr,p):
        self.nombre_fun = nombre_fun
        self.expr       = expr
        self.Tabla      = None
        self.linea      = p.lineno(1)
        self.pos        = p.lexpos(1)
        
    def __repr__(self,identacion):
        return "FUNCION_EMB:\n%snombre: %s \n%sargumento: %s" % (identacion+"\t",self.nombre_fun,identacion+"\t",self.expr.__repr__(identacion+"\t"))

    def toString(self):
        return "la funcion \"%s\"" %(self.nombre_fun)   
        
    def toString_2(self):
       return "%s" %(self.nombre_fun) 

        
    def setTable(self,tabla):
        self.Tabla = tabla
        self.expr.setTable(tabla)

    def getTipo(self):
        tipo = 'int' 
        tipoExpr = self.expr.getTipo()
        if tipoExpr and (tipoExpr != 'range'):
              print "Error en linea %i, columna %i: intento de aplicar la funcion \'%s\' a una expresion de tipo %s." %(self.linea,calcularColumna(data,self.pos),self.nombre_fun,tipoExpr)                          
              global error
              error = True
        return tipo
   
    #Implementa la evaluacion de una funcion          
    def evaluar(self):
        #se obtiene el rango al cual aplicar la funcion
        Rango = self.expr.evaluar()
        #Caso en el que se aplica la funcion rtoi 
        if (self.nombre_fun == 'rtoi'):
            return self.fun_rtoi(Rango)
        #Caso en el que se aplica la funcion length    
        elif (self.nombre_fun == 'length'):
            return self.fun_length(Rango)   
        #Caso en el que se aplica la funcion top   
        elif (self.nombre_fun == 'top'):
            return self.fun_top(Rango)   
        #Caso en el que se aplica la funcion bottom    
        elif (self.nombre_fun == 'bottom'):
            return self.fun_bottom(Rango)           
            
    #Implementacion de la funcion rtoi aplicada a un rango       
    def fun_rtoi(self,Rango):
      #Verificacion dinamica, la funcion solo es aplicable si las cotas son iguales 
      if (Rango.cotaSuperior != Rango.cotaInferior):
         print "Error: Intento de aplicar la funcion rtoi a un rango cuyas cotas son diferentes" 
         #se aborta la corrida
         sys.exit()
      #Si las cotas son iguales se retorna cualquiera de ellas
      return Rango.cotaSuperior            

    #Implementacion ed la funcion length aplicada a u un rango
    def fun_length(self,Rango):
        #retorna el tamanio relativo del rango
        tamRango = abs(Rango.cotaInferior - Rango.cotaSuperior)
        return tamRango
    
    #Implementacion de la funcion top aplicada a u un rango
    def fun_top(self,Rango):
        #retorna la cota superior del rango
        return Rango.cotaSuperior
    
    #Implementacion de la funcion bottom aplicada a u un rango
    def fun_bottom(self,Rango):
        #retorna la cota inferior del rango
        return Rango.cotaInferior
    

#***************************** Impresor auxiliar ******************************#
class myPrint:
    def __init__(self,hijos):
      self.hijos         = hijos
      self.Tabla         = None
        
    def __repr__(self,identacion):
       string = ''
       for i in self.hijos:
           string = string + "%s" % (i.__repr__(identacion))
       return string
   
    def toString_2(self):
        string = ''
        for i in self.hijos:
            string = string + "%s" % (i.toString_2())
        return string
        
    def toString(self):   
        string = ''
        for i in self.hijos:
            string = string + "%s" % (i.toString())
        return string
       
    def setTable(self,tabla):
        self.Tabla = tabla    
        for i in self.hijos:
            i.setTable(self.Tabla)
            
    def getTipo(self):    
        for i in self.hijos:
            return i.getTipo()
            
    def checkTipos(self):
        for i in self.hijos:
            if i.checkTipos():
                return True
        if error:
            return True
            
    def setExpr(self,expr):
        for i in self.hijos:
            i.setExpr(expr)        
            
    def ejecutar(self):
        for i in self.hijos:
            i.ejecutar()
            
    def evaluar(self): 
        for i in self.hijos:
            return i.evaluar()       
                     
            
#***************************** Programa principal *****************************#
class program:
    def __init__(self,hijos):
        self.hijos         = hijos
        self.Tabla         = None
    
    def __repr__(self,identacion):
        string = ''
        for i in self.hijos:
            string = string + "%s" % (i.__repr__(identacion))
        return string
       
    def setData(self,archivo):
        global data
        data = archivo
        
    def setTable(self,tabla):
        self.Tabla = tabla    
        for i in self.hijos:
            i.setTable(self.Tabla)
        return error
        
    def getTipo(self):    
        for i in self.hijos:
            return i.getTipo()
            
    def checkTipos(self):
        for i in self.hijos:
            if i.checkTipos():
                return True
        if error:
            return True
    
    #Ejecucion del programa rangex        
    def ejecutar(self):
        for i in self.hijos:
            i.ejecutar()
            
