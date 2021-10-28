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
-- Name: audioset; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.audioset (
    id integer NOT NULL,
    created_on timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_on timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    foreign_identifier character varying(1000),
    title character varying(2000),
    foreign_landing_url character varying(1000),
    creator character varying(2000),
    creator_url character varying(2000),
    url character varying(1000),
    filesize integer,
    filetype character varying(80),
    thumbnail character varying(1000),
    provider character varying(80)
);


ALTER TABLE public.audioset OWNER TO deploy;

--
-- Name: audioset temp_import_audioset_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.audioset
    ADD CONSTRAINT temp_import_audioset_pkey PRIMARY KEY (id);


--
-- Name: temp_import_audioset_foreign_identifier_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audioset_foreign_identifier_idx ON public.audioset USING btree (foreign_identifier varchar_pattern_ops);


--
-- Name: temp_import_audioset_foreign_identifier_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audioset_foreign_identifier_idx1 ON public.audioset USING btree (foreign_identifier);


--
-- Name: temp_import_audioset_foreign_identifier_provider_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_audioset_foreign_identifier_provider_idx ON public.audioset USING btree (foreign_identifier, provider);


--
-- Name: temp_import_audioset_id_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_audioset_id_idx ON public.audioset USING btree (id);


--
-- Name: temp_import_audioset_provider_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audioset_provider_idx ON public.audioset USING btree (provider);


--
-- Name: temp_import_audioset_provider_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audioset_provider_idx1 ON public.audioset USING btree (provider varchar_pattern_ops);


--
-- Name: temp_import_audioset_url_idx; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX temp_import_audioset_url_idx ON public.audioset USING btree (url);


--
-- Name: temp_import_audioset_url_idx1; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX temp_import_audioset_url_idx1 ON public.audioset USING btree (url varchar_pattern_ops);


--
-- PostgreSQL database dump complete
--
