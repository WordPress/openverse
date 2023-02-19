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

--
-- Name: audioset_view; Type: VIEW; Schema: public; Owner: deploy
--

CREATE VIEW public.audioset_view AS
 SELECT DISTINCT ((audio_view.audio_set ->> 'foreign_identifier'::text))::character varying(1000) AS foreign_identifier,
    ((audio_view.audio_set ->> 'title'::text))::character varying(2000) AS title,
    ((audio_view.audio_set ->> 'foreign_landing_url'::text))::character varying(1000) AS foreign_landing_url,
    ((audio_view.audio_set ->> 'creator'::text))::character varying(2000) AS creator,
    ((audio_view.audio_set ->> 'creator_url'::text))::character varying(2000) AS creator_url,
    ((audio_view.audio_set ->> 'url'::text))::character varying(1000) AS url,
    ((audio_view.audio_set ->> 'filesize'::text))::integer AS filesize,
    ((audio_view.audio_set ->> 'filetype'::text))::character varying(80) AS filetype,
    ((audio_view.audio_set ->> 'thumbnail'::text))::character varying(1000) AS thumbnail,
    audio_view.provider
   FROM public.audio_view
  WHERE (audio_view.audio_set IS NOT NULL);


ALTER TABLE public.audioset_view OWNER TO deploy;

--
-- PostgreSQL database dump complete
--
