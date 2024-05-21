DROP TABLE IF EXISTS brevetes;
CREATE TABLE "brevetes" (
	"IdMember_FK" INTEGER NOT NULL,
	"Clase" TEXT,
	"Numero" TEXT,
	"Tipo" TEXT,
	"FechaExp" DATE,
	"Restricciones" TEXT,
	"FechaHasta" DATE,
	"Centro" TEXT,
	"Puntos" TEXT,
	"Record" TEXT,
	"PapeletasImpagas" TEXT,
	"LastUpdate" DATE,
	FOREIGN KEY(IdMember_FK) REFERENCES members(IdMember)
) DROP TABLE IF EXISTS members;
CREATE TABLE "members" (
	"IdMember" INTEGER NOT NULL,
	"CodMember" TEXT NOT NULL,
	"NombreCompleto" TEXT NOT NULL,
	"DocTipo" TEXT NOT NULL,
	"DocNum" TEXT NOT NULL,
	"Celular" TEXT,
	"Correo" TEXT NOT NULL,
	PRIMARY KEY(IdMember AUTOINCREMENT)
);
DROP TABLE IF EXISTS jneMulta;
CREATE TABLE "jneMulta" (
	"IdMember_FK" INTEGER NOT NULL,
	"TODO" INTEGER,
	"LastUpdate" DATE,
	FOREIGN KEY (IdMember_FK) REFERENCES members(IdMember)
);
DROP TABLE IF EXISTS multasCallao;
CREATE TABLE "multasCallao" (
	"Placa_FK" TEXT NOT NULL,
	"TODO" INTEGER,
	"LastUpdate" DATE,
	FOREIGN KEY (Placa_FK) REFERENCES placas(Placa)
);
DROP TABLE IF EXISTS osiptelLineas;
CREATE TABLE "osiptelLineas" (
	"IdMember_FK" NUMERIC NOT NULL,
	"TODO" TEXT,
	"LastUpdate" DATE,
	FOREIGN KEY (IdMember_FK) REFERENCES members(IdMember)
);
DROP TABLE IF EXISTS placas;
CREATE TABLE "placas" (
	"IdPlaca" INTEGER,
	"IdMember_FK" INTEGER NOT NULL,
	"Placa" TEXT NOT NULL UNIQUE,
	PRIMARY KEY(IdPlaca AUTOINCREMENT),
	FOREIGN KEY (IdMember_FK) REFERENCES members(IdMember)
);
DROP TABLE IF EXISTS revtecs;
CREATE TABLE "revtecs" (
	"Placa_FK" TEXT NOT NULL,
	"PlacaValidate" TEXT,
	"Certificadora" TEXT,
	"Certificado" TEXT,
	"FechaDesde" DATE,
	"FechaHasta" DATE,
	"Resultado" TEXT,
	"Vigencia" TEXT,
	"LastUpdate" DATE,
	FOREIGN KEY (Placa_FK) REFERENCES placas(IdPlaca)
);
DROP TABLE IF EXISTS satimpCodigos;
CREATE TABLE "satimpCodigos" (
	"IdCodigo" INTEGER,
	"IdMember_FK" INTEGER NOT NULL,
	"Codigo" INTEGER NOT NULL,
	PRIMARY KEY (IdCodigo AUTOINCREMENT),
	FOREIGN KEY (IdMember_FK) REFERENCES members(IdMember)
);
DROP TABLE IF EXISTS satimpDeudas;
CREATE TABLE "satimpDeudas" (
	"IdCodigo_FK" TEXT NOT NULL,
	"Ano" INTEGER NOT NULL,
	"Periodo" INTEGER NOT NULL,
	"DocNum" TEXT NOT NULL,
	"TotalAPagar" DECIMAL(7, 2) NOT NULL,
	"LastUpdate" DATE,
	FOREIGN KEY (IdCodigo_FK) REFERENCES satimpCodigos(IdCodigo)
);
DROP TABLE IF EXISTS soats;
CREATE TABLE "soats" (
	"IdPlaca_FK" TEXT NOT NULL,
	"PlacaValidate" TEXT,
	"Aseguradora" TEXT,
	"FechaInicio" DATE,
	"FechaFin" DATE,
	"Certificado" TEXT,
	"Uso" TEXT,
	"Clase" TEXT,
	"Vigencia" TEXT,
	"Tipo" TEXT,
	"FechaVenta" DATE,
	"LastUpdate" DATE,
	"ImgFilename" TEXT,
	"ImgUpdate" DATE,
	FOREIGN KEY (IdPlaca_FK) REFERENCES placas(IdPlaca)
);
DROP TABLE IF EXISTS sunarps;
CREATE TABLE "sunarps" (
	"IdPlaca_FK" TEXT NOT NULL,
	"PlacaValidate" TEXT,
	"Serie" TEXT,
	"VIN" TEXT,
	"Motor" TEXT,
	"Color" TEXT,
	"Marca" TEXT,
	"Modelo" TEXT,
	"PlacaVigente" TEXT,
	"PlacaAnterior" TEXT,
	"Estado" TEXT,
	"Anotaciones" TEXT,
	"Sede" TEXT,
	"Propietarios" TEXT,
	"LastUpdate" DATE,
	"ImgFilename" TEXT,
	"ImgUpdate" DATE,
	FOREIGN KEY (IdPlaca_FK) REFERENCES placas(IdPlaca)
);
DROP TABLE IF EXISTS sutrans;
CREATE TABLE "sutrans" (
	"IdPlaca_FK" TEXT NOT NULL,
	"Documento" TEXT,
	"Tipo" TEXT,
	"FechaDoc" TEXT,
	"CodigoInfrac" TEXT,
	"Clasificacion" TEXT,
	"LastUpdate" DATE,
	FOREIGN KEY (IdPlaca_FK) REFERENCES placas(IdPlaca)
);
DROP TABLE IF EXISTS satmuls;
CREATE TABLE "satmuls" (
	"IdPlaca_FK" TEXT,
	"PlacaValidate" TEXT,
	"Falta" TEXT,
	"Documento" TEXT,
	"FechaEmision" DATE,
	"Importe" DECIMAL(7, 2),
	"Gastos" DECIMAL(7, 2),
	"Descuento" DECIMAL(7, 2),
	"Deuda" DECIMAL(7, 2),
	"Estado" TEXT,
	"Licencia" TEXT,
	"DocTipoSatmul" TEXT,
	"DocNumSatmul" TEXT
);
DROP TABLE IF EXISTS mensajeTipos;
CREATE TABLE "mensajeTipos" (
	"IdTipoMensaje" INTEGER NOT NULL,
	"TipoMensaje" TEXT,
	"Alerta" INTEGER NOT NULL,
	PRIMARY KEY (IdTipoMensaje AUTOINCREMENT)
);
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('1', 'SOAT por Vencer', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('2', 'SOAT Vencido', '1 ');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('3', 'Revision Tecnica por Vencer', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('4', 'Revision Tecnica Vencida', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('5', 'Impuesto SAT en periodo de pago', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('6', 'Impuesto SAT vencido', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('7', 'Licencia de Conducir por Vencer', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('8', 'Licencia de Conducir Vencida', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('9', 'Nueva Multa SUTRAN', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('10', 'Nueva Multa Callao', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('11', 'SUNARP Tarjeta', '1');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('12', 'Bienvenida', '0');
INSERT INTO "main"."mensajeTipos" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('13', 'Regular', '0');
DROP TABLE IF EXISTS mensajes;
CREATE TABLE "mensajes" (
	"IdMensaje" INTEGER,
	"IdMember_FK" INTEGER,
	"Fecha" DATE,
	"Hash" TEXT UNIQUE,
	PRIMARY KEY ("IdMensaje" AUTOINCREMENT),
	FOREIGN KEY("IdMember_FK") REFERENCES "members"("IdMember")
);
DROP TABLE IF EXISTS mensajeContenidos;
CREATE TABLE mensajeContenidos (
	"IdMensaje_FK" INTEGER,
	"IdTipoMensaje_FK" INTEGER,
	FOREIGN KEY ("IdMensaje_FK") REFERENCES "mensajes"("IdMensaje"),
	FOREIGN KEY ("IdTipoMensaje_FK") REFERENCES "mensajeTipos"("IdTipoMensaje")
);
-- TEMP
INSERT INTO "main"."mensajes" ("IdMensaje", "IdMember_FK", "Fecha", "Hash")
VALUES ('1', '17', '25/06/1973', 'cvcvcvcvcv');
INSERT INTO "main"."mensajes" ("IdMensaje", "IdMember_FK", "Fecha", "Hash")
VALUES ('2', '4', '12/12/2020', 'dfdfdfdfdf');
INSERT INTO "main"."mensajes" ("IdMensaje", "IdMember_FK", "Fecha", "Hash")
VALUES ('3', '9', '11/11/1985', 'eref454refdf');
INSERT INTO "main"."mensajes" ("IdMensaje", "IdMember_FK", "Fecha", "Hash")
VALUES ('4', '18', '12/09/1999', 'dfdfsdf');
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'1',
		'SAP-3AD4C0',
		'Gabriel Freundt-Thurne Sturmann',
		'DNI',
		'10059261',
		'989034311',
		'gfreundt@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'2',
		'SAP-969422',
		'Urpi Torrado',
		'DNI',
		'09343936',
		'999925531',
		'urpi@datum.com.pe'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'3',
		'SAP-EB859E',
		'Sergio Perez',
		'DNI',
		'10557545',
		'980311900',
		'sourcingroup.sp@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'4',
		'SAP-932788',
		'Carlos Ausejo',
		'DNI',
		'09856416',
		'999090454',
		'causejo@yahoo.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'5',
		'SAP-5D635C',
		'Patrick Lerner',
		'DNI',
		'09872067',
		'995742347',
		'patrick_lerner@yahoo.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'6',
		'SAP-4AD7BB',
		'Francisco Espinosa',
		'DNI',
		'09342827',
		'997913702',
		'fespinosar@espinosabellido.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'7',
		'SAP-23E548',
		'Santiago De La Piedra',
		'DNI',
		'10220909',
		'999287905',
		'santiago@penta.com.pe'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'8',
		'SAP-3447CD',
		'Javier Hanza',
		'DNI',
		'06674196',
		'991679166',
		'javierhanza@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'9',
		'SAP-533D1D',
		'Luis La Torre Costa',
		'DNI',
		'09341676',
		'976198992',
		'lucholtc@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'10',
		'SAP-85AB08',
		'Jaime Freundt-Thurne Freundt',
		'DNI',
		'08257907',
		'997522873',
		'jaime.freundt.thurne@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'11',
		'SAP-142D4E',
		'Sergio Guzmán',
		'DNI',
		'10609369',
		'991845965',
		'sergio@mectamo.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'12',
		'SAP-5A0652',
		'Jose Llerena',
		'DNI',
		'07760153',
		'955999029',
		'jllerena@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'13',
		'SAP-0FC660',
		'Alejandro Agois',
		'DNI',
		'10805548',
		'992708403',
		'aagois@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'14',
		'SAP-6FCEA4',
		'Bianca Cochella',
		'DNI',
		'40080207',
		'997908535',
		'bcochella@hotmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'15',
		'SAP-A55623',
		'José Luis Agramonte',
		'DNI',
		'29548887',
		'975158551',
		'jlagramonte@hotmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'16',
		'SAP-9A425A',
		'Guillermo Malqui',
		'DNI',
		'10263710',
		'979767777',
		'guillemalqui@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'17',
		'SAP-C3CBDD',
		'Jorge Yañez',
		'DNI',
		'09993024',
		'997102004',
		'jyanezgiles@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'18',
		'SAP-73954C',
		'Luis Carlos Merino',
		'DNI',
		'07865754',
		'994638204',
		'luiscarlosmerino@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'19',
		'SAP-CFCF84',
		'Rodrigo Parra Del Riego',
		'DNI',
		'08262214',
		'994660795',
		'rparra55@hotmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'20',
		'SAP-DCD32B',
		'Martha Santander',
		'DNI',
		'10301744',
		'989003188',
		'martha_santander@hotmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'21',
		'SAP-A8918E',
		'Paco Patiño',
		'DNI',
		'09993218',
		'943552175',
		'jf.patino.rivero@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'22',
		'SAP-132AD6',
		'Talia Graña',
		'DNI',
		'10610195',
		'989018420',
		't.grana@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'23',
		'SAP-FD90F6',
		'Jose Miguel Palma',
		'DNI',
		'06408257',
		'989056411',
		'jmpalmagz@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'24',
		'SAP-70D96D',
		'Patricia Rojas',
		'DNI',
		'07533070',
		'988051146',
		'patricia.rojas@ipsos.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'25',
		'SAP-EBB8E4',
		'Johnathan Sucksmith',
		'DNI',
		'10295376',
		'994889919',
		'jonathan37000@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'26',
		'SAP-1D88C1',
		'Gian Marco Pinasco',
		'DNI',
		'07884168',
		'999297604',
		'gianmarcopinasco@gmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'27',
		'SAP-D04BEB',
		'Ricardo Cossio',
		'DNI',
		'10058693',
		'997894666',
		'ricardocossio@hotmail.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'28',
		'SAP-CEEE2A',
		'Rafael Dangelo',
		'DNI',
		'09343616',
		'966314259',
		'rafaeldangelo@live.com'
	);
INSERT INTO "main"."members" (
		"IdMember",
		"CodMember",
		"NombreCompleto",
		"DocTipo",
		"DocNum",
		"Celular",
		"Correo"
	)
VALUES (
		'29',
		'SAP-7CC22B',
		'Carlos Domingo Hamann Garcia Belaunde',
		'DNI',
		'07629947',
		'992715048',
		'chgb@mac.com'
	);
---
INSERT INTO "main"."mensajeContenidos" ("IdMensaje_FK", "IdTipoMensaje_FK")
VALUES ('1', '11');
INSERT INTO "main"."mensajeContenidos" ("IdMensaje_FK", "IdTipoMensaje_FK")
VALUES ('2', '12');
INSERT INTO "main"."mensajeContenidos" ("IdMensaje_FK", "IdTipoMensaje_FK")
VALUES ('3', '12');
INSERT INTO "main"."mensajeContenidos" ("IdMensaje_FK", "IdTipoMensaje_FK")
VALUES ('4', '9');
---
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('1', '1', 'AMQ073');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('2', '1', 'D8R344');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('3', '2', 'CBW475');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('4', '3', '4536FC');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('5', '4', 'F4J162');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('6', '5', 'AJP209');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('7', '5', 'D5U002');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('8', '6', 'D5Y413');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('9', '7', 'CJM179');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('10', '8', 'APA503');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('11', '9', 'D7Z065');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('12', '9', 'F2L100');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('13', '10', 'BAW484');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('14', '11', 'AKE119');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('15', '12', 'A1L239');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('16', '13', 'BAV066');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('17', '13', 'B2Y297');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('18', '14', 'CHO571');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('19', '14', 'BJK193');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('20', '14', 'AZK376');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('21', '15', 'AHJ311');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('22', '15', 'BWT453');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('23', '16', 'ATR393');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('24', '17', 'A7X390');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('25', '18', 'LIA118');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('26', '19', 'BKI054');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('27', '19', 'CBF485');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('28', '20', 'CBU074');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('29', '21', 'AVN261');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('30', '22', 'BLB551');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('31', '23', 'CDH680');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('32', '23', 'BEX012');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('33', '24', 'CBA688');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('34', '25', 'BSL336');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('35', '26', 'C1P415');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('36', '26', 'AUK408');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('37', '27', 'CDN467');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('38', '27', 'F3H541');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('39', '28', '95817Y');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('40', '29', '94491F');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('41', '29', '60376D');
INSERT INTO "main"."placas" ("IdPlaca", "IdMember_FK", "Placa")
VALUES ('42', '29', 'Z6O593');