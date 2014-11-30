league-circut
=============

school wide league service

ADD THESE TWO TO THE DATABASE AND PULL, SHOULD WORK, HAVE MY ALARM SET TO 9, IF SHIT HITS THE FAN, JUST WAIT FOR ME TO WAKE UP


CREATE TABLE "league"."teamlist"
(sumid bigint,
id text,
CONSTRAINT teamlist_pkey PRIMARY KEY(sumid, id)
);

CREATE TABLE "league"."matchlist"
(sumid bigint,
id text,
CONSTRAINT matchlist_pkey PRIMARY KEY(sumid, id)
);
