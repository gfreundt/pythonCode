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
	"LastUpdate" DATE,
	FOREIGN KEY (IdMember_FK) REFERENCES members(IdMember)
);
DROP TABLE IF EXISTS members;
CREATE TABLE "members" (
	"IdMember" INTEGER NOT NULL,
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
	"IdPlacas" INTEGER,
	"IdMember_FK" INTEGER NOT NULL,
	"Placa" TEXT NOT NULL UNIQUE,
	PRIMARY KEY(IdPlacas AUTOINCREMENT),
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
	FOREIGN KEY (Placa_FK) REFERENCES placas(idPlaca)
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
	FOREIGN KEY (IdPlaca_FK) REFERENCES placas(idPlaca)
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
	FOREIGN KEY (IdPlaca_FK) REFERENCES placas(idPlaca)
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
	FOREIGN KEY (IdPlaca_FK) REFERENCES placas(idPlaca)
);
DROP TABLE IF EXISTS tipoMensajes;
CREATE TABLE "tipoMensajes" (
	"IdTipoMensaje" INTEGER NOT NULL,
	"TipoMensaje" TEXT,
	"Alerta" INTEGER NOT NULL,
	PRIMARY KEY (IdTipoMensaje AUTOINCREMENT)
);
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('1', 'SOAT por Vencer', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('2', 'SOAT Vencido', '1 ');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('3', 'Revision Tecnica por Vencer', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('4', 'Revision Tecnica Vencida', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('5', 'Impuesto SAT en periodo de pago', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('6', 'Impuesto SAT vencido', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('7', 'Licencia de Conducir por Vencer', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('8', 'Licencia de Conducir Vencida', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('9', 'Nueva Multa SUTRAN', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('10', 'Nueva Multa Callao', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('11', 'SUNARP Tarjeta', '1');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
VALUES ('12', 'Bienvenida', '0');
INSERT INTO "main"."tipoMensajes" ("IdTipoMensaje", "TipoMensaje", "Alerta")
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
	FOREIGN KEY ("IdTipoMensaje_FK") REFERENCES "tipoMensajes"("IdTipoMensaje")
)