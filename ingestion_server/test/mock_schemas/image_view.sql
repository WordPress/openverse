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
-- Name: image_view; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.image_view (
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
    title character varying(2000),
    last_synced_with_source timestamp with time zone,
    removed_from_source boolean NOT NULL,
    meta_data jsonb,
    view_count integer DEFAULT 0,
    tags jsonb,
    watermarked boolean,
    filetype character varying(80),
    standardized_popularity double precision,
    ingestion_type character varying(1000)
);


ALTER TABLE public.image_view OWNER TO deploy;

--
-- Name: image_id_seq; Type: SEQUENCE; Schema: public; Owner: deploy
--

CREATE SEQUENCE public.image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.image_id_seq OWNER TO deploy;

--
-- Name: image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: deploy
--

ALTER SEQUENCE public.image_id_seq OWNED BY public.image_view.id;


--
-- Name: image_view id; Type: DEFAULT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image_view ALTER COLUMN id SET DEFAULT nextval('public.image_id_seq'::regclass);


--
-- Name: image_view image_identifier_key; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image_view
    ADD CONSTRAINT image_identifier_key UNIQUE (identifier);


--
-- Name: image_view image_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image_view
    ADD CONSTRAINT image_pkey PRIMARY KEY (id);


--
-- Name: image_view image_url_key; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image_view
    ADD CONSTRAINT image_url_key UNIQUE (url);


--
-- Name: image_view unique_provider_image; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image_view
    ADD CONSTRAINT unique_provider_image UNIQUE (foreign_identifier, provider);


--
-- Name: image_foreign_identifier_4c72d3ee; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_foreign_identifier_4c72d3ee ON public.image_view USING btree (foreign_identifier);


--
-- Name: image_foreign_identifier_4c72d3ee_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_foreign_identifier_4c72d3ee_like ON public.image_view USING btree (foreign_identifier varchar_pattern_ops);


--
-- Name: image_last_synced_with_source_187adf09; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_last_synced_with_source_187adf09 ON public.image_view USING btree (last_synced_with_source);


--
-- Name: image_provider_7d11f847; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_provider_7d11f847 ON public.image_view USING btree (provider);


--
-- Name: image_provider_7d11f847_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_provider_7d11f847_like ON public.image_view USING btree (provider varchar_pattern_ops);


--
-- Name: image_source_d5a89e97; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_source_d5a89e97 ON public.image_view USING btree (source);


--
-- Name: image_source_d5a89e97_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_source_d5a89e97_like ON public.image_view USING btree (source varchar_pattern_ops);


--
-- Name: image_url_c6aabda2_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_url_c6aabda2_like ON public.image_view USING btree (url varchar_pattern_ops);


--
-- PostgreSQL database dump complete
--
