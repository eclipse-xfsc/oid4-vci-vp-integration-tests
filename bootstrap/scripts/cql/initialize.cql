-- Create a keyspace
CREATE KEYSPACE IF NOT EXISTS tenant_space WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : '1' };

-- retrieval service
CREATE TABLE IF NOT EXISTS tenant_space.offerings (
                                                      partition text,
                                                      region text,
                                                      country text,
                                                      groupId text,
                                                      requestId text,
                                                      last_update_timestamp timestamp,
                                                      type text,
                                                      metadata text,
                                                      offerParams text,
                                                      status text,
                                                      PRIMARY KEY ((partition,region,country),groupid,requestId)
) WITH default_time_to_live = 17800;

-- storage service
CREATE TABLE IF NOT EXISTS tenant_space.credentials (
                                                        accountPartition text,
                                                        region text,
                                                        country text,
                                                        account text,
                                                        last_update_timestamp timestamp,
                                                        metadata map<text,text>,
                                                        credentials map<text,text>,
                                                        presentations map<text,text>,
                                                        id text,
                                                        recovery_nonce text,
                                                        device_key text,
                                                        nonce text,
                                                        locked boolean,
                                                        signature text,
                                                        PRIMARY KEY ((accountPartition,region,country),account)
);

CREATE INDEX IF NOT EXISTS ON tenant_space.credentials (locked);
CREATE INDEX IF NOT EXISTS ON tenant_space.credentials (id);

-- credential verification service
CREATE TABLE IF NOT EXISTS tenant_space.presentations (
                                                          region text,
                                                          country text,
                                                          id text,
                                                          requestId text,
                                                          groupId text,
                                                          presentationDefinition text,
                                                          presentation text,
                                                          redirectUri text,
                                                          responseUri text,
                                                          responseMode text,
                                                          responseType text,
                                                          clientId text,
                                                          state text,
                                                          last_update_timestamp timestamp,
                                                          nonce text,
                                                          PRIMARY KEY ((region,country),id)
);

CREATE INDEX IF NOT EXISTS ON tenant_space.presentations (groupId);
CREATE INDEX IF NOT EXISTS ON tenant_space.presentations (requestId);