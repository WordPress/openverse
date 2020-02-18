--
-- PostgreSQL database dump
--

-- Dumped from database version 10.9
-- Dumped by pg_dump version 10.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner:
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner:
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: image; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.image (
    id integer NOT NULL,
    created_on timestamp with time zone NOT NULL,
    updated_on timestamp with time zone NOT NULL,
    identifier uuid DEFAULT public.uuid_generate_v4(),
    perceptual_hash character varying(255),
    provider character varying(80),
    source character varying(80),
    foreign_identifier character varying(3000),
    foreign_landing_url character varying(1000),
    url character varying(3000) NOT NULL,
    thumbnail character varying(3000),
    width integer,
    height integer,
    filesize integer,
    license character varying(50) NOT NULL,
    license_version character varying(25),
    creator character varying(2000),
    creator_url character varying(2000),
    title character varying(5000),
    tags_list character varying(255)[],
    last_synced_with_source timestamp with time zone,
    removed_from_source boolean NOT NULL,
    meta_data jsonb,
    tags jsonb,
    watermarked boolean,
    view_count integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.image OWNER TO deploy;

--
-- Name: image_id_seq; Type: SEQUENCE; Schema: public; Owner: deploy
--

CREATE SEQUENCE public.image_id_seq
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
-- Name: image image_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.image
    ADD CONSTRAINT image_pkey PRIMARY KEY (id);


--
-- Name: image_9e9f3d70; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_9e9f3d70 ON public.image USING btree (provider);


--
-- Name: image_foreign_identifier_key; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_foreign_identifier_key ON public.image USING btree (provider, md5((foreign_identifier)::text));


--
-- Name: image_provider_fid_url_key; Type: INDEX; Schema: public; Owner: deploy
--

CREATE UNIQUE INDEX image_provider_fid_url_key ON public.image USING btree (provider, md5((foreign_identifier)::text), md5((url)::text));


--
-- Name: image_url_key; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX image_url_key ON public.image USING btree (provider, md5((url)::text));


--
-- Name: uuid_index; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX uuid_index ON public.image USING btree (identifier);


--
-- PostgreSQL database dump complete
--

