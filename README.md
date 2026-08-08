# WIRED

**The WIRED Protocol**
Wide Interconnected Redistribution and Exchange of Data Network
> As of now, The current WIRED implementation supports (FETCH, COPY)

---

## FETCH

Retrieve a resource.

### Request

```text
FETCH
LOCATION: WIRED://SERVER1/GLOBAL/INDEX.TXT
.
```

### Response

```text
200 OK
LOCATION: WIRED://SERVER1/GLOBAL/INDEX.TXT
SIZE: 1234
TYPE: text/plain
.
[file bytes]
```

---


## COPY

Copy an existing resource, potentially between different WIRED servers.

### Request

```text
COPY
TITLE: HELLO WORLD
DESCRIPTION: HELLO WORLD TEXT FILE
SOURCE: WIRED://SERVER2/GLOBAL/HELLO.TXT
DESTINATION: WIRED://SERVER1/GLOBAL/HELLO.TXT
.
```

### Response

```text
201 CREATED
SOURCE: WIRED://SERVER2/GLOBAL/MYSITE2/HELLO.TXT
DESTINATION: WIRED://SERVER1/GLOBAL/MYSITE/HELLO.TXT
SIZE: 13
MESSAGE: File copied good
.
```



## Methods


 `FETCH`       Retrieve a resource.                                                    
 `POST`      Create a resource.                                                      
 `COPY`      Copy an existing resource, potentially between different WIRED servers. 
 `EXCHANGE`  Offer one resource in exchange for another. Servers accept or decline.  
