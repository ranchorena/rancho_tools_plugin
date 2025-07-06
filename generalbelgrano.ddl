-- generalbelgrano.barrios definition

-- Drop table

-- DROP TABLE barrios;

CREATE TABLE barrios (
	id int8 NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	nombre varchar(80) NULL,
	CONSTRAINT barrios_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_barrios_geometry ON generalbelgrano.barrios USING gist (geometry);


-- generalbelgrano.callejero definition

-- Drop table

-- DROP TABLE callejero;

CREATE TABLE callejero (
	id int4 NULL,
	the_geom public.geometry(linestring, 5347) NULL,
	"name" varchar(254) NULL,
	desde int8 NULL,
	hasta int8 NULL,
	calle varchar(60) NULL,
	calle2 varchar(60) NULL,
	tipo_calle int4 NULL,
	sentido int4 NULL,
	suelo int4 NULL,
	velocidad int4 NULL,
	"source" int4 NULL,
	target int4 NULL,
	"cost" float8 NULL,
	rcost float8 NULL,
	oneway varchar NULL,
	x1 float8 NULL,
	y1 float8 NULL,
	x2 float8 NULL,
	y2 float8 NULL,
	cost_len float8 NULL,
	rcost_len float8 NULL,
	speed_km float8 NULL,
	cost_time float8 NULL,
	rcost_time float8 NULL
);
CREATE INDEX callejero_id_idx ON generalbelgrano.callejero USING btree (id);
CREATE INDEX callejero_source_idx ON generalbelgrano.callejero USING btree (source);
CREATE INDEX callejero_target_idx ON generalbelgrano.callejero USING btree (target);
CREATE INDEX callejero_the_geom_idx ON generalbelgrano.callejero USING gist (the_geom);


-- generalbelgrano.callejero_vertices_pgr definition

-- Drop table

-- DROP TABLE callejero_vertices_pgr;

CREATE TABLE callejero_vertices_pgr (
	id bigserial NOT NULL,
	cnt int4 NULL,
	chk int4 NULL,
	ein int4 NULL,
	eout int4 NULL,
	the_geom public.geometry(point, 5347) NULL,
	CONSTRAINT callejero_vertices_pgr_pkey PRIMARY KEY (id)
);
CREATE INDEX callejero_vertices_pgr_the_geom_idx ON generalbelgrano.callejero_vertices_pgr USING gist (the_geom);


-- generalbelgrano.calles_nombres definition

-- Drop table

-- DROP TABLE calles_nombres;

CREATE TABLE calles_nombres (
	id serial4 NOT NULL,
	geometry public.geometry(pointz, 5347) NULL,
	"name" varchar(254) NULL,
	descriptio varchar(254) NULL,
	"timestamp" varchar(24) NULL,
	"begin" varchar(24) NULL,
	"end" varchar(24) NULL,
	altitudemo varchar(254) NULL,
	tessellate int8 NULL,
	extrude int8 NULL,
	visibility int8 NULL,
	draworder int8 NULL,
	icon varchar(254) NULL,
	CONSTRAINT calles_nombres_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_calles_nombres_geometry ON generalbelgrano.calles_nombres USING gist (geometry);


-- generalbelgrano.clientes definition

-- Drop table

-- DROP TABLE clientes;

CREATE TABLE clientes (
	id serial4 NOT NULL,
	geometria public.geometry(point, 5347) NULL,
	nombre varchar(60) NULL,
	direccion varchar(50) NULL,
	calle varchar(50) NULL,
	altura int4 NULL,
	tiene_pedido int4 NULL,
	telefono varchar(30) NULL,
	cantidad float4 NULL,
	horario time(0) NULL,
	nro_pao int4 NULL,
	observacion varchar(200) NULL,
	es_regalo int4 NULL,
	CONSTRAINT clientes_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_clientes_geometria ON generalbelgrano.clientes USING gist (geometria);


-- generalbelgrano.clientes_temporal definition

-- Drop table

-- DROP TABLE clientes_temporal;

CREATE TABLE clientes_temporal (
	id int4 NULL,
	geometria public.geometry(point, 5347) NULL,
	nombre varchar(60) NULL,
	direccion varchar(50) NULL,
	calle varchar(50) NULL,
	altura int4 NULL,
	tiene_pedido int4 NULL,
	telefono varchar(30) NULL,
	cantidad float4 NULL,
	horario time(0) NULL,
	nro_pao int4 NULL,
	observacion varchar(200) NULL
);


-- generalbelgrano.fracciones definition

-- Drop table

-- DROP TABLE fracciones;

CREATE TABLE fracciones (
	id serial4 NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	fraccion varchar(2) NULL,
	clavef varchar(7) NULL,
	CONSTRAINT fracciones_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_fracciones_geometry ON generalbelgrano.fracciones USING gist (geometry);


-- generalbelgrano.partido definition

-- Drop table

-- DROP TABLE partido;

CREATE TABLE partido (
	id int4 NULL,
	geometry public.geometry NULL
);
CREATE INDEX sidx_partido_geometry ON generalbelgrano.partido USING gist (geometry);


-- generalbelgrano.pedido definition

-- Drop table

-- DROP TABLE pedido;

CREATE TABLE pedido (
	id_pedido serial4 NOT NULL,
	fecha timestamp NOT NULL,
	id_cliente int8 NOT NULL,
	nombre varchar(60) NULL,
	turno int4 NOT NULL,
	cantidad float4 NULL,
	direccion varchar(50) NULL,
	calle varchar(50) NULL,
	altura int4 NULL,
	geometry public.geometry(point, 5347) NULL,
	observaciones varchar(30) NULL,
	precio_unitario float4 NULL,
	nro_pao int4 NULL,
	CONSTRAINT pedido_pkey PRIMARY KEY (id_pedido)
);
CREATE INDEX sidx_pedido_geometria ON generalbelgrano.pedido USING gist (geometry);


-- generalbelgrano.plazas definition

-- Drop table

-- DROP TABLE plazas;

CREATE TABLE plazas (
	id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 15 CACHE 1 NO CYCLE) NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	nombre varchar(80) NULL,
	CONSTRAINT plazas_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_plazas_geometry ON generalbelgrano.plazas USING gist (geometry);


-- generalbelgrano.provincia definition

-- Drop table

-- DROP TABLE provincia;

CREATE TABLE provincia (
	id serial4 NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	area float8 NULL,
	perimeter float8 NULL,
	partido varchar(40) NULL,
	cabecera varchar(40) NULL,
	cod_cen varchar(3) NULL,
	secc_elect int8 NULL,
	reg_educ int4 NULL,
	CONSTRAINT provincia_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_provincia_geometry ON generalbelgrano.provincia USING gist (geometry);


-- generalbelgrano.provincia_polyg definition

-- Drop table

-- DROP TABLE provincia_polyg;

CREATE TABLE provincia_polyg (
	id int4 NULL,
	geometry public.geometry NULL
);
CREATE INDEX sidx_provincia_polyg_geometry ON generalbelgrano.provincia_polyg USING gist (geometry);


-- generalbelgrano.punto_interes definition

-- Drop table

-- DROP TABLE punto_interes;

CREATE TABLE punto_interes (
	id_punto serial4 NOT NULL,
	nombre varchar(50) NULL,
	direccion varchar(80) NULL,
	calle varchar(50) NULL,
	altura int4 NULL,
	geometry public.geometry(point, 5347) NULL,
	observaciones varchar(30) NULL,
	tipo int4 NULL,
	CONSTRAINT punto_interes_pkey PRIMARY KEY (id_punto)
);
CREATE INDEX sidx_punto_interes_geometry ON generalbelgrano.punto_interes USING gist (geometry);


-- generalbelgrano.radios_censales definition

-- Drop table

-- DROP TABLE radios_censales;

CREATE TABLE radios_censales (
	id serial4 NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	clavera varchar(12) NULL,
	cod_part varchar(3) NULL,
	cod_loc varchar(3) NULL,
	fraccion varchar(2) NULL,
	radio varchar(2) NULL,
	tipo varchar(6) NULL,
	CONSTRAINT radios_censales_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_radios_censales_geometry ON generalbelgrano.radios_censales USING gist (geometry);


-- generalbelgrano.referencia definition

-- Drop table

-- DROP TABLE referencia;

CREATE TABLE referencia (
	id int4 NULL,
	geometry public.geometry(multilinestring, 5347) NULL,
	"name" varchar(254) NULL,
	desde int8 NULL,
	hasta int8 NULL,
	calle varchar(60) NULL,
	calle2 varchar(60) NULL,
	tipo_calle int4 NULL,
	sentido int4 NULL,
	suelo int4 NULL
);
CREATE INDEX sidx_referencia_geometry ON generalbelgrano.referencia USING gist (geometry);


-- generalbelgrano.subbarrios definition

-- Drop table

-- DROP TABLE subbarrios;

CREATE TABLE subbarrios (
	id int8 NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	nombre varchar(100) NULL,
	CONSTRAINT subbarrios_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_subbarrios_geometry ON generalbelgrano.subbarrios USING gist (geometry);


-- generalbelgrano.temp_zonas_reparto definition

-- Drop table

-- DROP TABLE temp_zonas_reparto;

CREATE TABLE temp_zonas_reparto (
	id int8 NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	nombre varchar(80) NULL
);


-- generalbelgrano.tramos definition

-- Drop table

-- DROP TABLE tramos;

CREATE TABLE tramos (
	id serial4 NOT NULL,
	geometry public.geometry(multilinestring, 5347) NULL,
	"name" varchar(254) NULL,
	desde int8 NULL,
	hasta int8 NULL,
	calle varchar(60) NULL,
	calle2 varchar(60) NULL,
	tipo_calle int4 DEFAULT 1 NULL,
	sentido int4 NULL,
	suelo int4 DEFAULT 1 NULL,
	velocidad int4 NULL,
	CONSTRAINT tramos_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_tramos_geometry ON generalbelgrano.tramos USING gist (geometry);


-- generalbelgrano.urbano definition

-- Drop table

-- DROP TABLE urbano;

CREATE TABLE urbano (
	id int8 NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	nombre varchar(80) NULL,
	CONSTRAINT urbano_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_urbano_geometry ON generalbelgrano.urbano USING gist (geometry);


-- generalbelgrano.zonas_reparto definition

-- Drop table

-- DROP TABLE zonas_reparto;

CREATE TABLE zonas_reparto (
	id int8 NOT NULL,
	geometry public.geometry(multipolygon, 5347) NULL,
	nombre varchar(80) NULL,
	CONSTRAINT zonas_reparto_pkey PRIMARY KEY (id)
);
CREATE INDEX sidx_zonas_reparto_geometry ON generalbelgrano.zonas_reparto USING gist (geometry);