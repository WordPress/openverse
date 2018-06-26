--
-- PostgreSQL database dump
--

-- Dumped from database version 10.3
-- Dumped by pg_dump version 10.3 (Debian 10.3-1.pgdg90+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: image; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.image (
    id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    updated_on timestamp with time zone NOT NULL,
    identifier character varying(255),
    perceptual_hash character varying(255),
    provider character varying(80),
    source character varying(80),
    foreign_identifier character varying(80),
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
    meta_data jsonb
);


ALTER TABLE public.image OWNER TO deploy;

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

ALTER SEQUENCE public.image_id_seq OWNED BY public.image.id;


--
-- Name: image id; Type: DEFAULT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image ALTER COLUMN id SET DEFAULT nextval('public.image_id_seq'::regclass);


--
-- Name: image image_foreign_identifier_key; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_foreign_identifier_key UNIQUE (foreign_identifier);


--
-- Name: image image_identifier_key; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_identifier_key UNIQUE (identifier);


--
-- Name: image image_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_pkey PRIMARY KEY (id);


--
-- Name: image image_url_key; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_url_key UNIQUE (url);


--
-- Name: image_foreign_identifier_4c72d3ee_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_foreign_identifier_4c72d3ee_like ON public.image USING btree (foreign_identifier varchar_pattern_ops);


--
-- Name: image_identifier_d102a6e0_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_identifier_d102a6e0_like ON public.image USING btree (identifier varchar_pattern_ops);


--
-- Name: image_last_synced_with_source_187adf09; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_last_synced_with_source_187adf09 ON public.image USING btree (last_synced_with_source);


--
-- Name: image_perceptual_hash_0d126a7a; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_perceptual_hash_0d126a7a ON public.image USING btree (perceptual_hash);


--
-- Name: image_perceptual_hash_0d126a7a_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_perceptual_hash_0d126a7a_like ON public.image USING btree (perceptual_hash varchar_pattern_ops);


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
-- PostgreSQL database dump complete
--

