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
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: api_deletedimage; Type: TABLE; Schema: public; Owner: deploy
--

CREATE TABLE public.api_deletedimage (
    created_on timestamp with time zone NOT NULL,
    updated_on timestamp with time zone NOT NULL,
    identifier uuid NOT NULL
);


ALTER TABLE public.api_deletedimage OWNER TO deploy;

--
-- Name: api_deletedimage api_deletedimages_pkey; Type: CONSTRAINT; Schema: public; Owner: deploy
--

ALTER TABLE ONLY public.api_deletedimage
    ADD CONSTRAINT api_deletedimages_pkey PRIMARY KEY (identifier);


--
-- PostgreSQL database dump complete
--
