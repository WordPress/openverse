--
-- PostgreSQL database dump
--

-- Dumped from database version 13.3
-- Dumped by pg_dump version 13.3 (Debian 13.3-1.pgdg100+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
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
    url character varying(1000),
    thumbnail character varying(1000),
    width integer,
    height integer,
    filesize integer,
    license character varying(50) NOT NULL,
    license_version character varying(25),
    creator character varying(2000),
    creator_url character varying(2000),
    title character varying(5000),
    last_synced_with_source timestamp with time zone,
    removed_from_source boolean NOT NULL,
    meta_data jsonb,
    view_count integer DEFAULT 0,
    tags jsonb,
    watermarked boolean,
    filetype character varying(80),
    standardized_popularity double precision,
    category character varying(80)
);


ALTER TABLE public.image OWNER TO deploy;

--
-- Name: image image_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_pkey PRIMARY KEY (id);


--
-- Name: image_category_daa5d91c; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_category_daa5d91c ON public.image USING btree (category);


--
-- Name: image_category_daa5d91c_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_category_daa5d91c_like ON public.image USING btree (category varchar_pattern_ops);


--
-- Name: image_foreign_identifier_4c72d3ee; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_foreign_identifier_4c72d3ee ON public.image USING btree (foreign_identifier);


--
-- Name: image_foreign_identifier_4c72d3ee_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_foreign_identifier_4c72d3ee_like ON public.image USING btree (foreign_identifier varchar_pattern_ops);


--
-- Name: image_identifier_key; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX image_identifier_key ON public.image USING btree (identifier);


--
-- Name: image_last_synced_with_source_187adf09; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_last_synced_with_source_187adf09 ON public.image USING btree (last_synced_with_source);


--
-- Name: image_provider_7d11f847; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_provider_7d11f847 ON public.image USING btree (provider);


--
-- Name: image_provider_7d11f847_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_provider_7d11f847_like ON public.image USING btree (provider varchar_pattern_ops);


--
-- Name: image_source_d5a89e97; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_source_d5a89e97 ON public.image USING btree (source);


--
-- Name: image_source_d5a89e97_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_source_d5a89e97_like ON public.image USING btree (source varchar_pattern_ops);


--
-- Name: image_url_c6aabda2_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_url_c6aabda2_like ON public.image USING btree (url varchar_pattern_ops);


--
-- Name: image_url_key; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX image_url_key ON public.image USING btree (url);


--
-- Name: unique_provider_image; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX unique_provider_image ON public.image USING btree (foreign_identifier, provider);


--
-- PostgreSQL database dump complete
--
