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
-- Name: audioset; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.audioset (
    id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    updated_on timestamp with time zone NOT NULL,
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
-- Name: api_audioset_id_seq; Type: SEQUENCE; Schema: public; Owner: deploy
--

CREATE SEQUENCE public.api_audioset_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_audioset_id_seq OWNER TO deploy;

--
-- Name: api_audioset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: deploy
--

ALTER SEQUENCE public.api_audioset_id_seq OWNED BY public.audioset.id;


--
-- Name: audioset id; Type: DEFAULT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.audioset ALTER COLUMN id SET DEFAULT nextval('public.api_audioset_id_seq'::regclass);


--
-- Name: audioset api_audioset_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.audioset
    ADD CONSTRAINT api_audioset_pkey PRIMARY KEY (id);


--
-- Name: audioset api_audioset_url_key; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.audioset
    ADD CONSTRAINT api_audioset_url_key UNIQUE (url);


--
-- Name: audioset unique_foreign_identifier_provider; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.audioset
    ADD CONSTRAINT unique_foreign_identifier_provider UNIQUE (foreign_identifier, provider);


--
-- Name: api_audioset_foreign_identifier_28c1db59; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX api_audioset_foreign_identifier_28c1db59 ON public.audioset USING btree (foreign_identifier);


--
-- Name: api_audioset_foreign_identifier_28c1db59_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX api_audioset_foreign_identifier_28c1db59_like ON public.audioset USING btree (foreign_identifier varchar_pattern_ops);


--
-- Name: api_audioset_url_200f9fb4_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX api_audioset_url_200f9fb4_like ON public.audioset USING btree (url varchar_pattern_ops);


--
-- Name: audioset_provider_cc061f30; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX audioset_provider_cc061f30 ON public.audioset USING btree (provider);


--
-- Name: audioset_provider_cc061f30_like; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX audioset_provider_cc061f30_like ON public.audioset USING btree (provider varchar_pattern_ops);


--
-- PostgreSQL database dump complete
--
