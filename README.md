# TicketList

TicketList es una herramienta que sirve para el realizar el seguimiento de tickets que reportan inconvientes en productos o servicios

## Getting Started

Estas instrucciones le permitirán obtener una copia del proyecto en funcionamiento en su máquina local para fines de desarrollo y prueba.

### Features

* Python 2.7
* DJango 1.10
* PostgreSQL

### Configuración de desarrollo

```
mkdir TicketList
cd TicketList
virtualenv .
/Scripts/activate
```

Instalación de DJango

```
pip install django==1.10
pip install psycopg2
```

Clonar el proyecto

```
git clone https://github.com/desarrollapy/ticketList.git
```

Ejecutar el proyecto
```
cd ticketList
python manage.py migrate
// run tickelist-script.sql in your SGBD
python manage.py runserver
```


Luego ingrese a [localhost](http://localhost:8000/)


### Autores

* **Juan Britez** - [desarrolla](https://github.com/juanrybritez)
* **Emilce Fernandez** - [desarrolla](https://github.com/juanrybritez)