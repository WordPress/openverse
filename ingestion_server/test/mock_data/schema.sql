--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: image; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.image (
    id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    updated_on timestamp with time zone NOT NULL,
    identifier uuid NOT NULL,
    provider character varying(80),
    source character varying(80),
    foreign_identifier character varying(1000),
    foreign_landing_url character varying(1000),
    url character varying(1000) NOT NULL,
    thumbnail character varying(1000),
    width integer,
    height integer,
    filesize integer,
    license character varying(50) NOT NULL,
    license_version character varying(25),
    creator character varying(2000),
    creator_url character varying(2000),
    title character varying(2000),
    tags_list character varying(255)[],
    last_synced_with_source timestamp with time zone,
    removed_from_source boolean NOT NULL,
    meta_data jsonb,
    view_count integer DEFAULT 0 NOT NULL,
    tags jsonb,
    watermarked boolean,
    standardized_popularity double precision
);


ALTER TABLE public.image OWNER TO deploy;

--
-- Name: image temp_import_image_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT temp_import_image_pkey PRIMARY KEY (id);


--
-- Name: temp_import_image_foreign_identifier_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_image_foreign_identifier_idx ON public.image USING btree (foreign_identifier);


--
-- Name: temp_import_image_foreign_identifier_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_image_foreign_identifier_idx1 ON public.image USING btree (foreign_identifier varchar_pattern_ops);


--
-- Name: temp_import_image_id_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_image_id_idx ON public.image USING btree (id);


--
-- Name: temp_import_image_identifier_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_image_identifier_idx ON public.image USING btree (identifier);


--
-- Name: temp_import_image_last_synced_with_source_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_image_last_synced_with_source_idx ON public.image USING btree (last_synced_with_source);


--
-- Name: temp_import_image_provider_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_image_provider_idx ON public.image USING btree (provider);


--
-- Name: temp_import_image_provider_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_image_provider_idx1 ON public.image USING btree (provider varchar_pattern_ops);


--
-- Name: temp_import_image_source_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_image_source_idx ON public.image USING btree (source);


--
-- Name: temp_import_image_source_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_image_source_idx1 ON public.image USING btree (source varchar_pattern_ops);


--
-- Name: temp_import_image_url_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_image_url_idx ON public.image USING btree (url);


--
-- Name: temp_import_image_url_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_image_url_idx1 ON public.image USING btree (url varchar_pattern_ops);


--
-- PostgreSQL database dump complete
--
