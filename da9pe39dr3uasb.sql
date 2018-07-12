-- Adminer 4.6.3-dev PostgreSQL dump

\connect "da9pe39dr3uasb";

DROP TABLE IF EXISTS "checkins";
DROP SEQUENCE IF EXISTS checkins_checkin_id_seq;
CREATE SEQUENCE checkins_checkin_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."checkins" (
    "checkin_id" integer DEFAULT nextval('checkins_checkin_id_seq') NOT NULL,
    "time" timestamp NOT NULL,
    "comment" text,
    "user_id" integer NOT NULL,
    "location_id" integer NOT NULL,
    CONSTRAINT "checkins_checkin_id" PRIMARY KEY ("checkin_id"),
    CONSTRAINT "checkins_location_id_fkey" FOREIGN KEY (location_id) REFERENCES locations(location_id) NOT DEFERRABLE,
    CONSTRAINT "checkins_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(user_id) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "locationnames";
DROP SEQUENCE IF EXISTS locationnames_locationname_id_seq;
CREATE SEQUENCE locationnames_locationname_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."locationnames" (
    "locationname_id" integer DEFAULT nextval('locationnames_locationname_id_seq') NOT NULL,
    "city" text NOT NULL,
    "state" text NOT NULL,
    CONSTRAINT "locationnames_city_state" UNIQUE ("city", "state"),
    CONSTRAINT "locationnames_pkey" PRIMARY KEY ("locationname_id")
) WITH (oids = false);


DROP TABLE IF EXISTS "locations";
DROP SEQUENCE IF EXISTS locations_location_id_seq;
CREATE SEQUENCE locations_location_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."locations" (
    "location_id" integer DEFAULT nextval('locations_location_id_seq') NOT NULL,
    "zipcode" text NOT NULL,
    "locationname_id" integer NOT NULL,
    "latitude" numeric NOT NULL,
    "longitude" numeric NOT NULL,
    "population" integer NOT NULL,
    CONSTRAINT "locations_location_id" PRIMARY KEY ("location_id"),
    CONSTRAINT "locations_locationname_id_fkey" FOREIGN KEY (locationname_id) REFERENCES locationnames(locationname_id) NOT DEFERRABLE
) WITH (oids = false);


DROP TABLE IF EXISTS "users";
DROP SEQUENCE IF EXISTS users_user_id_seq;
CREATE SEQUENCE users_user_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1 CACHE 1;

CREATE TABLE "public"."users" (
    "user_id" integer DEFAULT nextval('users_user_id_seq') NOT NULL,
    "username" text NOT NULL,
    "password_hash" text NOT NULL,
    "first_name" text NOT NULL,
    CONSTRAINT "users_user_id" PRIMARY KEY ("user_id"),
    CONSTRAINT "users_username" UNIQUE ("username")
) WITH (oids = false);


-- 2018-07-12 21:59:56.603827+00
