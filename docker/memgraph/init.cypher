// Create constraints for entity uniqueness
CREATE CONSTRAINT ON (d:Domain) ASSERT d.value IS UNIQUE;
CREATE CONSTRAINT ON (ip:IP) ASSERT ip.value IS UNIQUE;
CREATE CONSTRAINT ON (e:Email) ASSERT e.value IS UNIQUE;
CREATE CONSTRAINT ON (h:Hash) ASSERT h.value IS UNIQUE;
CREATE CONSTRAINT ON (w:Wallet) ASSERT w.value IS UNIQUE;
CREATE CONSTRAINT ON (p:Person) ASSERT p.name IS UNIQUE;
CREATE CONSTRAINT ON (s:SocialHandle) ASSERT s.handle IS UNIQUE;
CREATE CONSTRAINT ON (df:DarknetForumPost) ASSERT df.post_id IS UNIQUE;

// Create indexes for performance
CREATE INDEX ON :Domain(value);
CREATE INDEX ON :IP(value);
CREATE INDEX ON :Email(value);
CREATE INDEX ON :Hash(value);
CREATE INDEX ON :Wallet(value);
CREATE INDEX ON :Person(name);
CREATE INDEX ON :SocialHandle(handle);
