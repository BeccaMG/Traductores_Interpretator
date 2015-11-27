********************************************************************************
***************************** README PROY FASE 4 *******************************
********************************************************************************
Elaborado por:

        - Oswaldo A. Jiménez 10-10368
        - Rebeca Machado     10-10406
        

A continuación se presenta un breve informe, resaltando en rasgos generales la
metodologia empleada para el desarrollo de la fase 4 del proyecto.


1_FORMULACIÓN:
==============

  El proyecto se formuló con los siguientes objetivos:
    
    -Interpretar un programa hecho en el lenguaje Rangex, incluyendo las
verificaciones dinámicas (a tiempo de ejecución).
    

1.1_IMPLEMENTACIÓN:
-------------------

    Utilizando lo desarrollado para las entregas anteriores, se modificaron las
clases utilizadas para representar las producciones del parser y se le
agregaron métodos como:
    
    *ejecutar: Ejecuta una instrucción.
               
    *evaluar: Evalua una expresión.
   
   Ademas, en la clase SymTable se agregaron los procedimiento necesarios para
actualizar el valor de una variable en la tabla de símbolos.


1.2_PROBLEMAS:
--------------
  
  -En la entrega anterior, la tabla de símbolos de la iteración determinada
debía copiarse y asignarse a sus instrucciones como una tabla nueva y no como
un apuntador, por lo que al actualizar el valor de la variable de iteración,
las tablas de las instrucciones no se veían afectadas. Se logró solucionar este
problema actualizando las tablas cada vez que se actualizaba la variable de
iteración, lo que es un poco ineficiente.

  
1.3_CONSIDERACIONES Y ARCHIVOS INCLUIDOS:
-----------------------------------------
    
  *** Documentación utilizada:
    PLY: http://www.dabeaz.com/ply/ply.html
    
  *** Librerías y herramientas necesarias:
    Paquete PLY - lex.py
                - yacc.py
    
  *** Archivos de implementación:
    rangex
    clases.py
    SymTable.py
    
  *** Archivos incluidos:
    rangex
    clases.py
    SymTable.py
    README.txt
    
  *** Modo de ejecución:
  ./rangex <archivo_de_entrada>
  
  *** El rango de las iteraciones determinadas (for) no es dinámico. Es decir,
en vista de que esto no aparece en la definición, se consideró que, aunque el
rango esté conformado por alguna variable y ésta cambia durante la ejecución de
la iteración, el rango no se verá afectado (evitando así ciclos infinitos). Por
ejemplo
    
    b = 5;
    for i in 1..b do
        b = b + 1;

    Hará que las instrucciones del ciclo se ejecuten solo 6 veces. Sin embargo,
la variable b tendrá el valor adecuado al terminar.
    
    
Para información más detallada revisar los archivos de implementación incluidos.


2_MODIFICACIONES A LA TERCERA ENTREGA:
======================================
    
    a) Se corrigieron los errores de falta de procedimientos "toString" en las
    funciones sobre rangos.
    
    b) Las cadenas de texto (strings) se muestran con los caracteres especiales
    debidamente escapados.

    c) Se eliminaron algunos procedimientos de impresión innecesarios.
    