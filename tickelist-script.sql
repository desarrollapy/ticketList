-- Insertar datos de la tabla motivos
insert into ticket_motivo values (1, 'LINEA SULTA O TELÉFONO DESCONECTADO');
insert into ticket_motivo values (2, 'CORTO EN LINEA');
insert into ticket_motivo values (3, 'PROBLEMAS DE MÓDULO');
insert into ticket_motivo values (4, 'SIN ESPACIO PARA REUBICACIÓN');
insert into ticket_motivo values (5, 'PROBLEMA ADMINISTRATIVO');

-- Insertar datos de la tabla incoveniente
INSERT INTO ticket_inconveniente (id,descripcion) VALUES (1,'SIN TONO');
INSERT INTO ticket_inconveniente (id,descripcion) VALUES (2,'NO REALIZA LLAMADA');
INSERT INTO ticket_inconveniente (id,descripcion) VALUES (3,'NO RECIBE LLAMADA');
INSERT INTO ticket_inconveniente (id,descripcion) VALUES (4,'REPOSICION DE NUMERO');

-- Borrando permisos que son no necesarios
delete from auth_permission where id <= 18


-- Datos de Administrador
insert into ticket_persona(id,codigo, first_login, usuario_id)
values(nextval('ticket_persona_id_seq'), 1, true, 1)
