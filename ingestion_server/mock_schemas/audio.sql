--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.3 (Debian 13.3-1.pgdg100+1)

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
-- Name: audio; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.audio (
    id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    updated_on timestamp with time zone NOT NULL,
    identifier uuid NOT NULL,
    foreign_identifier character varying(1000),
    title character varying(2000),
    foreign_landing_url character varying(1000),
    creator character varying(2000),
    creator_url character varying(2000),
    url character varying(1000),
    filesize integer,
    watermarked boolean,
    license character varying(50) NOT NULL,
    license_version character varying(25),
    provider character varying(80),
    source character varying(80),
    last_synced_with_source timestamp with time zone,
    removed_from_source boolean NOT NULL,
    view_count integer DEFAULT 0,
    tags jsonb,
    tags_list character varying(255)[],
    meta_data jsonb,
    audio_set_position integer,
    genres character varying(80)[],
    category character varying(80),
    duration integer,
    bit_rate integer,
    sample_rate integer,
    alt_files jsonb,
    thumbnail character varying(1000),
    filetype character varying(80),
    audio_set_foreign_identifier character varying(1000),
    standardized_popularity double precision
);


ALTER TABLE public.audio OWNER TO deploy;

--
-- Name: audio temp_import_audio_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.audio
    ADD CONSTRAINT temp_import_audio_pkey PRIMARY KEY (id);


--
-- Name: temp_import_audio_category_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_category_idx ON public.audio USING btree (category);


--
-- Name: temp_import_audio_category_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_category_idx1 ON public.audio USING btree (category varchar_pattern_ops);


--
-- Name: temp_import_audio_foreign_identifier_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_foreign_identifier_idx ON public.audio USING btree (foreign_identifier varchar_pattern_ops);


--
-- Name: temp_import_audio_foreign_identifier_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_foreign_identifier_idx1 ON public.audio USING btree (foreign_identifier);


--
-- Name: temp_import_audio_foreign_identifier_provider_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_audio_foreign_identifier_provider_idx ON public.audio USING btree (foreign_identifier, provider);


--
-- Name: temp_import_audio_genres_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_genres_idx ON public.audio USING btree (genres);


--
-- Name: temp_import_audio_id_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_audio_id_idx ON public.audio USING btree (id);


--
-- Name: temp_import_audio_identifier_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_audio_identifier_idx ON public.audio USING btree (identifier);


--
-- Name: temp_import_audio_last_synced_with_source_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_last_synced_with_source_idx ON public.audio USING btree (last_synced_with_source);


--
-- Name: temp_import_audio_provider_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_provider_idx ON public.audio USING btree (provider);


--
-- Name: temp_import_audio_provider_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_provider_idx1 ON public.audio USING btree (provider varchar_pattern_ops);


--
-- Name: temp_import_audio_source_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_source_idx ON public.audio USING btree (source);


--
-- Name: temp_import_audio_source_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_source_idx1 ON public.audio USING btree (source varchar_pattern_ops);


--
-- Name: temp_import_audio_url_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_audio_url_idx ON public.audio USING btree (url);


--
-- Name: temp_import_audio_url_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audio_url_idx1 ON public.audio USING btree (url varchar_pattern_ops);


--
-- PostgreSQL database dump complete
--
