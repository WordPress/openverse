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
-- Name: old_image; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.old_image (
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


ALTER TABLE public.old_image OWNER TO deploy;

--
-- Name: old_image_id_seq; Type: SEQUENCE; Schema: public; Owner: deploy
--

CREATE SEQUENCE public.old_image_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.old_image_id_seq OWNER TO deploy;

--
-- Name: old_image_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: deploy
--

ALTER SEQUENCE public.old_image_id_seq OWNED BY public.old_image.id;


--
-- Name: old_image id; Type: DEFAULT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.old_image ALTER COLUMN id SET DEFAULT nextval('public.old_image_id_seq'::regclass);


--
-- Name: old_image old_image_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.old_image
    ADD CONSTRAINT old_image_pkey PRIMARY KEY (id);


--
-- Name: old_image_9e9f3d70; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX old_image_9e9f3d70 ON public.old_image USING btree (provider);

CREATE UNIQUE INDEX old_image_provider_fid_key ON public.old_image USING btree (provider, md5((foreign_identifier)::text));


--
-- Name: old_image_url_key; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX old_image_url_key ON public.old_image USING btree (provider, md5((url)::text));


--
-- Name: uuid_index; Type: INDEX; Schema: public; Owner: deploy
--

CREATE INDEX uuid_index ON public.old_image USING btree (identifier);


--
-- PostgreSQL database dump complete
--
