-- Database generated with pgModeler (PostgreSQL Database Modeler).
-- pgModeler  version: 0.8.1
-- PostgreSQL version: 9.4
-- Project Site: pgmodeler.com.br
-- Model Author: ---

-- object: raspberry | type: ROLE --
-- DROP ROLE IF EXISTS raspberry;
CREATE ROLE raspberry WITH 
	LOGIN
	ENCRYPTED PASSWORD '00198500';
-- ddl-end --


-- Database creation must be done outside an multicommand file.
-- These commands were put in this file only for convenience.
-- -- object: placas | type: DATABASE --
-- -- DROP DATABASE IF EXISTS placas;
 CREATE DATABASE placas
 	ENCODING = 'UTF8'
 	OWNER = raspberry
 ;
-- -- ddl-end --
-- 

-- object: public.casas | type: TABLE --
-- DROP TABLE IF EXISTS public.casas CASCADE;
CREATE TABLE public.casas(
	cep varchar(8) NOT NULL,
	numero varchar(10) NOT NULL,
	compl varchar(100),
	responsavel varchar(255),
	telefone bigint,
	email varchar(255),
	password varchar(10),
	dt_created timestamp DEFAULT now(),
	CONSTRAINT pk_cep_numero PRIMARY KEY (cep,numero),
	CONSTRAINT un_email UNIQUE (email)

);
-- ddl-end --
ALTER TABLE public.casas OWNER TO raspberry;
-- ddl-end --

-- object: public.carros | type: TABLE --
-- DROP TABLE IF EXISTS public.carros CASCADE;
CREATE TABLE public.carros(
	cep varchar(8) NOT NULL,
	numero varchar(10) NOT NULL,
	placa varchar(15) NOT NULL,
	dt_created timestamp DEFAULT now(),
	CONSTRAINT pk_carros_id PRIMARY KEY (cep,numero,placa)

);
-- ddl-end --
ALTER TABLE public.carros OWNER TO raspberry;
-- ddl-end --

-- object: public.visitantes | type: TABLE --
-- DROP TABLE IF EXISTS public.visitantes CASCADE;
CREATE UNLOGGED TABLE public.visitantes(
	id serial NOT NULL,
	cep varchar(8) NOT NULL,
	numero varchar(10) NOT NULL,
	placa varchar(15),
	dt_entrada date,
	check_in boolean DEFAULT false,
	dt_created timestamp DEFAULT now(),
	CONSTRAINT pk_visitantes_id PRIMARY KEY (id,cep,numero)

);
-- ddl-end --
ALTER TABLE public.visitantes OWNER TO raspberry;
-- ddl-end --

-- object: idx_placas | type: INDEX --
-- DROP INDEX IF EXISTS public.idx_placas CASCADE;
CREATE UNIQUE INDEX idx_placas ON public.carros
	USING btree
	(
	  placa ASC NULLS LAST
	);
-- ddl-end --

-- object: idx_visitantes_placa | type: INDEX --
-- DROP INDEX IF EXISTS public.idx_visitantes_placa CASCADE;
CREATE UNIQUE INDEX idx_visitantes_placa ON public.visitantes
	USING btree
	(
	  dt_entrada DESC NULLS LAST,
	  placa ASC NULLS LAST
	);
-- ddl-end --

-- object: idx_email | type: INDEX --
-- DROP INDEX IF EXISTS public.idx_email CASCADE;
CREATE UNIQUE INDEX idx_email ON public.casas
	USING btree
	(
	  email ASC NULLS LAST
	);
-- ddl-end --

-- object: fk_carros_casas | type: CONSTRAINT --
-- ALTER TABLE public.carros DROP CONSTRAINT IF EXISTS fk_carros_casas CASCADE;
ALTER TABLE public.carros ADD CONSTRAINT fk_carros_casas FOREIGN KEY (cep,numero)
REFERENCES public.casas (cep,numero) MATCH FULL
ON DELETE CASCADE ON UPDATE NO ACTION;
-- ddl-end --

-- object: fk_visitantes_casas | type: CONSTRAINT --
-- ALTER TABLE public.visitantes DROP CONSTRAINT IF EXISTS fk_visitantes_casas CASCADE;
ALTER TABLE public.visitantes ADD CONSTRAINT fk_visitantes_casas FOREIGN KEY (cep,numero)
REFERENCES public.casas (cep,numero) MATCH FULL
ON DELETE CASCADE ON UPDATE NO ACTION;
-- ddl-end --


