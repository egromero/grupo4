# Grupo 4

Proyecto Robotica Movil

## Scripts
1 - control.py

Tiene dos clases:
..* Generic_Controller
  Como suena es un controlador generico, uno le pasa como parametro una direccion para el topico y listo
..* Control
  Necesita edicion si se quiere usar de otra manera. Actualmente usa dos controladores para lineal y angular. Y acepta *ESPECIFICAMENTE* dos parametros para cambiar estados. Documentare algun dia mejor sus metodos.

2- util.py

Posee timer(es un helper nomas y pi_fix

3 - states.py

Encargado de la odometria. Juro algun dia cambiar su nombre. Publica en 'our_state' un mensaje tipo std_msgs.msg -> String de un diccionario codificado por json. Basicamente necesita json.loads al otro lado

4 - writer.py
Escribe? Se subscribe a un topico cuyo nombre olvide (revisar), y lo que se publique tipo Strings (de std_msgs), sera escrito en un archivo. Al reiniciar el nodo se crea un nuevo archivo cuyo numero depende de, otro archivo constante llamado number.txt (que se modifica solo)

5 - Main.py

Hiper simple, solo crea una clase Control, y le pasa rutas.
